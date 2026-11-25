import tracemalloc

from generators.sales_generator import filter_sales
from iterators.sales_iterator import SaleRecord


def infinite_sale_id_generator(start: int = 1):
    """нескінченно генерує унікальні ID продажів"""
    current: int = start
    while True:
        yield current
        current += 1


def fibonacci_generator(n: int):
    """генерує перші n чисел Фібоначчі"""
    if n < 0:
        raise ValueError("n має бути невід'ємним")
    a: int = 0
    b: int = 1
    for step in range(n):
        yield a
        a, b = b, a + b


def recursive_structure_generator(data: object):
    """рекурсивно обходить вкладені структури даних"""
    if isinstance(data, dict):
        for value in data.values():
            yield from recursive_structure_generator(value)
    elif isinstance(data, (list, tuple, set, frozenset)):
        for item in data:
            yield from recursive_structure_generator(item)
    else:
        yield data


def _parse_line(line: str, headers: list[str]) -> SaleRecord:
    """розбирає один рядок csv у SaleRecord"""
    parts: list[str] = [part.strip() for part in line.rstrip("\r\n").split(",")]
    row: dict[str, str] = dict(zip(headers, parts))
    return SaleRecord(
        sale_id=int(row["id"]),
        product=row["product"],
        category=row["category"],
        quantity=int(row["quantity"]),
        price=float(row["price"]),
        status=row["status"].lower(),
    )


def compare_memory(csv_path: str) -> tuple[float, float]:
    """порівнює використання пам'яті списку та генератора через tracemalloc"""
    tracemalloc.start()
    with open(csv_path, "r", encoding="utf-8") as csv_file:
        header_line: str = csv_file.readline()
        headers: list[str] = [h.strip() for h in header_line.rstrip("\r\n").split(",")]
        records_list: list[SaleRecord] = [
            _parse_line(line, headers)
            for line in csv_file
            if line.strip()
        ]
    list_revenue_total: float = sum(item.revenue for item in records_list if item.status == "completed")
    list_memory_info: tuple[int, int] = tracemalloc.get_traced_memory()
    list_peak: int = list_memory_info[1]
    tracemalloc.stop()

    tracemalloc.start()
    with open(csv_path, "r", encoding="utf-8") as csv_file:
        header_line = csv_file.readline()
        headers = [h.strip() for h in header_line.rstrip("\r\n").split(",")]
        gen_records = (
            _parse_line(line, headers)
            for line in csv_file
            if line.strip()
        )
        gen_revenue_total: float = sum(item.revenue for item in gen_records if item.status == "completed")
    gen_memory_info: tuple[int, int] = tracemalloc.get_traced_memory()
    gen_peak: int = gen_memory_info[1]
    tracemalloc.stop()

    print(f"перевірена виручка {list_revenue_total:.2f} / {gen_revenue_total:.2f}")
    return list_peak / 1024, gen_peak / 1024


def csv_reader_stage(csv_path: str):
    """етап CSV Reader"""
    with open(csv_path, "r", encoding="utf-8") as csv_file:
        header_line: str = csv_file.readline()
        if not header_line:
            return
        headers: list[str] = [h.strip() for h in header_line.rstrip("\r\n").split(",")]
        for line in csv_file:
            if line.strip():
                parts: list[str] = [part.strip() for part in line.rstrip("\r\n").split(",")]
                yield dict(zip(headers, parts))


def data_validator_stage(rows):
    """етап Data Validator"""
    for row in rows:
        try:
            sale = SaleRecord(
                sale_id=int(row["id"]),
                product=row["product"].strip(),
                category=row["category"].strip(),
                quantity=int(row["quantity"]),
                price=float(row["price"]),
                status=row["status"].strip().lower(),
            )
        except (KeyError, TypeError, ValueError):
            continue

        if sale.id > 0 and sale.quantity > 0 and sale.price >= 0 and sale.product and sale.category:
            yield sale


def data_filter_stage(sales, status: str = "completed"):
    """етап Data Filter"""
    yield from filter_sales(sales, status)


def data_transformer_stage(sales):
    """етап Data Transformer"""
    for sale in sales:
        yield {
            "id": sale.id,
            "product": sale.product,
            "category": sale.category,
            "quantity": sale.quantity,
            "price": sale.price,
            "status": sale.status,
            "revenue": round(sale.revenue, 2),
        }


def batch_generator_stage(items, batch_size: int = 10):
    """етап Batch Generator"""
    if batch_size <= 0:
        raise ValueError("batch_size має бути більшим за 0")
    batch: list[dict[str, object]] = []
    for item in items:
        batch.append(item)
        if len(batch) == batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


def analytics_stage(batches) -> dict[str, int | float]:
    """етап Analytics"""
    batches_count: int = 0
    records_count: int = 0
    total_rev: float = 0.0
    for batch in batches:
        batches_count += 1
        for item in batch:
            records_count += 1
            total_rev += float(item["revenue"])
    return {
        "batches": batches_count,
        "records": records_count,
        "revenue": round(total_rev, 2),
    }


def run_pipeline(csv_path: str, batch_size: int = 10, status: str = "completed") -> dict[str, int | float]:
    """запускає повний конвеєр генераторів"""
    reader = csv_reader_stage(csv_path)
    validator = data_validator_stage(reader)
    filtered = data_filter_stage(validator, status=status)
    transformed = data_transformer_stage(filtered)
    batches = batch_generator_stage(transformed, batch_size=batch_size)
    return analytics_stage(batches)