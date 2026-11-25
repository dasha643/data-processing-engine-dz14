class SaleRecord:
    """представлення одного запису продажу"""
    def __init__(
        self,
        sale_id: int,
        product: str,
        category: str,
        quantity: int,
        price: float,
        status: str,
    ) -> None:
        self.id: int = sale_id
        self.product: str = product
        self.category: str = category
        self.quantity: int = quantity
        self.price: float = price
        self.status: str = status

    @property
    def revenue(self) -> float:
        """виручка за запис"""
        return self.quantity * self.price

    def __repr__(self) -> str:
        return (
            f"SaleRecord(sale_id={self.id!r}, product={self.product!r}, "
            f"category={self.category!r}, quantity={self.quantity!r}, "
            f"price={self.price!r}, status={self.status!r})"
        )

    def __eq__(self, other: object) -> bool:
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

    def __init__(self, sales, category: str | None = None) -> None:
        """ініціалізує ітератор колекцією продажів та необов'язковою категорією"""
        target_category: str | None = category.strip().lower() if category else None
        self._items: list[SaleRecord] = [
            sale
            for sale in sales
            if target_category is None or sale.category.strip().lower() == target_category
        ]
        self._index: int = 0

    def __iter__(self) -> "SalesIterator":
        """повертає ітератор і скидає позицію обходу на початок"""
        self._index = 0
        return self

    def __next__(self) -> SaleRecord:
        """повертає наступний запис або StopIteration"""
        if self._index >= len(self._items):
            raise StopIteration
        item: SaleRecord = self._items[self._index]
        self._index += 1
        return item