from generators.sales_generator import filter_sales, generate_top_products


def total_sales_count(sales):
    """повертає загальну кількість продажів"""
    count = 0
    for sale in sales:
        count += 1
    return count


def total_revenue(sales, only_completed=True):
    """повертає загальну виручку"""
    stream = filter_sales(sales, "completed") if only_completed else sales
    return sum(sale.revenue for sale in stream)


def average_check(sales, only_completed=True):
    """повертає середній чек"""
    stream = filter_sales(sales, "completed") if only_completed else sales
    count = 0
    revenue_sum = 0.0
    for sale in stream:
        count += 1
        revenue_sum += sale.revenue
    return (revenue_sum / count) if count > 0 else 0.0


def most_popular_product(sales, only_completed=True):
    """повертає найпопулярніший товар за кількістю продажів"""
    stream = filter_sales(sales, "completed") if only_completed else sales
    quantities = {}
    for sale in stream:
        quantities[sale.product] = quantities.get(sale.product, 0) + sale.quantity

    if not quantities:
        return None
    return max(quantities.items(), key=lambda item: item[1])[0]


def most_profitable_category(sales, only_completed=True):
    """повертає найприбутковішу категорію"""
    stream = filter_sales(sales, "completed") if only_completed else sales
    revenues = {}
    for sale in stream:
        revenues[sale.category] = revenues.get(sale.category, 0.0) + sale.revenue

    if not revenues:
        return None
    return max(revenues.items(), key=lambda item: item[1])[0]


def top_5_products_by_revenue(sales, only_completed=True):
    """повертає топ 5 товарів за виручкою"""
    stream = filter_sales(sales, "completed") if only_completed else sales
    return list(generate_top_products(stream, top_n=5, by="revenue"))