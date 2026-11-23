import tracemalloc

from bonus_task.task import (
    fibonacci_generator,
    infinite_sale_id_generator,
    recursive_structure_generator,
    run_pipeline,
)
from generators.sales_generator import calculate_revenue, filter_sales, generate_batches, read_sales
from iterators.sales_iterator import SaleRecord, SalesIterator
from services.analytics import (
    average_check,
    most_popular_product,
    most_profitable_category,
    top_5_products_by_revenue,
    total_revenue,
    total_sales_count,
)


def _parse_line_to_sale(line, headers):
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


def print_analytics(csv_path):
    """виводить аналітику продажів без завантаження всього файлу"""
    sales_count = total_sales_count(read_sales(csv_path))
    completed_count = sum(1 for item in filter_sales(read_sales(csv_path), "completed"))
    revenue_total = total_revenue(read_sales(csv_path), only_completed=True)
    avg_check = average_check(read_sales(csv_path), only_completed=True)
    popular_product = most_popular_product(read_sales(csv_path), only_completed=True)
    profitable_category = most_profitable_category(read_sales(csv_path), only_completed=True)
    top_5 = top_5_products_by_revenue(read_sales(csv_path), only_completed=True)

    print("аналітика продажів")
    print(f"усього продажів {sales_count}")
    print(f"завершених продажів {completed_count}")
    print(f"загальна виручка {revenue_total:.2f}")
    print(f"середній чек {avg_check:.2f}")
    print("найпопулярніший товар")
    print(popular_product or "")
    print("найприбутковіша категорія")
    print(profitable_category or "")
    print("топ 5 товарів за виручкою")
    for index, (product, revenue) in enumerate(top_5, start=1):
        print(f"{index}. {product} — {revenue:.2f}")


def compare_memory_usage(csv_path):
    """порівнює використання пам'яті списку та генератора через tracemalloc"""
    tracemalloc.start()
    with open(csv_path, "r", encoding="utf-8") as csv_file:
        header_line = csv_file.readline()
        headers = [h.strip() for h in header_line.rstrip("\r\n").split(",")]
        records_list = [
            _parse_line_to_sale(line, headers)
            for line in csv_file
            if line.strip()
        ]
    list_revenue_total = sum(item.revenue for item in records_list if item.status == "completed")
    list_memory_info = tracemalloc.get_traced_memory()
    list_peak = list_memory_info[1]
    tracemalloc.stop()

    tracemalloc.start()
    with open(csv_path, "r", encoding="utf-8") as csv_file:
        header_line = csv_file.readline()
        headers = [h.strip() for h in header_line.rstrip("\r\n").split(",")]
        gen_records = (
            _parse_line_to_sale(line, headers)
            for line in csv_file
            if line.strip()
        )
        gen_revenue_total = sum(item.revenue for item in gen_records if item.status == "completed")
    gen_memory_info = tracemalloc.get_traced_memory()
    gen_peak = gen_memory_info[1]
    tracemalloc.stop()

    print(f"перевірена виручка {list_revenue_total:.2f} / {gen_revenue_total:.2f}")
    return list_peak / 1024, gen_peak / 1024


def main():
    """запускає основну програму та всі доп.завдання"""
    csv_path = "data/sales.csv"

    print_analytics(csv_path)

    it = SalesIterator(read_sales(csv_path))
    first_item = next(it)
    print("перший запис з ітератора продажів", first_item)

    it_cat = SalesIterator(read_sales(csv_path), category="Electronics")
    electronics_items = list(it_cat)
    print("кількість записів у категорії Electronics", len(electronics_items))

    running_revenues = list(calculate_revenue(filter_sales(read_sales(csv_path), "completed")))
    print("кількість проміжних значень виручки", len(running_revenues))

    batches = list(generate_batches(read_sales(csv_path), batch_size=25))
    print("кількість пакетів", len(batches))

    id_gen = infinite_sale_id_generator(start=1000)
    generated_ids = []
    for _ in range(3):
        generated_ids.append(next(id_gen))
    print("нескінченні ID", generated_ids)

    print("фібоначчі", list(fibonacci_generator(7)))
    print("рекурсивний обхід", list(recursive_structure_generator({"a": [1, (2, {"b": 3})], "c": 4})))

    list_kb, gen_kb = compare_memory_usage(csv_path)
    print(f"пікова пам'ять {list_kb:.2f} проти {gen_kb:.2f}")
    print(
        "висновок. список тримає всі записи в пам'яті одночасно, а генератор обробляє їх по черзі"
    )

    pipeline_result = run_pipeline(csv_path, batch_size=10, status="completed")
    print("аналітика конвеєра", pipeline_result)


if __name__ == "__main__":
    main()