class SaleRecord:
    """представлення одного запису продажу"""
    def __init__(self, sale_id, product, category, quantity, price, status):
        self.id = sale_id
        self.product = product
        self.category = category
        self.quantity = quantity
        self.price = price
        self.status = status

    @property
    def revenue(self):
        """виручка за запис"""
        return self.quantity * self.price

    def __repr__(self):
        return (
            f"SaleRecord(sale_id={self.id!r}, product={self.product!r}, "
            f"category={self.category!r}, quantity={self.quantity!r}, "
            f"price={self.price!r}, status={self.status!r})"
        )

    def __eq__(self, other):
        if not isinstance(other, SaleRecord):
            return NotImplemented
        return (
            self.id == other.id
            and self.product == other.product
            and self.category == other.category
            and self.quantity == other.quantity
            and self.price == other.price
            and self.status == other.status
        )


class SalesIterator:
    """ітератор для послідовного обходу колекції продажів із фільтрацією категорією"""
    def __init__(self, sales, category=None):
        """ініціалізує ітератор колекцією продажів та необов'язковою категорією"""
        target_category = category.strip().lower() if category else None
        self._items = [
            sale
            for sale in sales
            if target_category is None or sale.category.strip().lower() == target_category
        ]
        self._index = 0

    def __iter__(self):
        """повертає ітератор і скидає позицію обходу на початок"""
        self._index = 0
        return self

    def __next__(self):
        """повертає наступний запис або StopIteration"""
        if self._index >= len(self._items):
            raise StopIteration
        item = self._items[self._index]
        self._index += 1
        return item