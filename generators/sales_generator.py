from iterators.sales_iterator import SaleRecord


def _line_to_sale(line, headers):
    """перетворює рядок csv на SaleRecord"""
    parts = [part.strip() for part in line.rstrip("\r\n").split(",")]
    row = dict(zip(headers, parts))
    return SaleRecord(
        sale_id=int(row["id"]),
        product=row["product"],
        category=row["category"],
        quantity=int(row["quantity"]),
        price=float(row["price"]),
        status=row["status"].lower(),
    )


def read_sales(file_path):
    """читає csv файл і повертає записи"""
    with open(file_path, "r", encoding="utf-8") as csv_file:
        header_line = csv_file.readline()
        if not header_line:
            return
        headers = [h.strip() for h in header_line.rstrip("\r\n").split(",")]
        for line in csv_file:
            if line.strip():
                yield _line_to_sale(line, headers)


def filter_sales(sales, status):
    """фільтрує продажі за статусом"""
    target_status = status.strip().lower()
    for sale in sales:
        if sale.status.lower() == target_status:
            yield sale


def calculate_revenue(sales):
    """повертає послідовність проміжних значень виручки"""
    running_revenue = 0.0
    for sale in sales:
        running_revenue += sale.revenue
        yield running_revenue


def generate_batches(sales, batch_size):
    """розбиває записи на пакети заданого розміру"""
    if batch_size <= 0:
        raise ValueError("batch_size має бути більшим за 0")

    batch = []
    for sale in sales:
        batch.append(sale)
        if len(batch) == batch_size:
            yield batch
            batch = []

    if batch:
        yield batch


def generate_top_products(sales, top_n=5, by="revenue"):
    """формує послідовність топ товарів за виручкою або кількістю"""
    if top_n <= 0:
        raise ValueError("top_n має бути більшим за 0")
    if by not in {"revenue", "quantity"}:
        raise ValueError("by має бути 'revenue' або 'quantity'")

    totals = {}
    for sale in sales:
        if by == "revenue":
            totals[sale.product] = totals.get(sale.product, 0.0) + sale.revenue
        else:
            totals[sale.product] = totals.get(sale.product, 0) + sale.quantity

    top_items = sorted(totals.items(), key=lambda item: item[1], reverse=True)[:top_n]
    for product, value in top_items:
        yield product, value