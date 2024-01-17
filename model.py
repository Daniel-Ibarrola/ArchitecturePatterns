from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=False)
class OrderLine:
    orderid: str
    sku: str
    qty: int

    def __hash__(self):
        return hash((self.orderid, self.sku, self.qty))


class OutOfStock(ValueError):
    pass


class Batch:
    def __init__(self, ref: str, sku: str, qty: int, eta: Optional[date] = None):
        self.ref = ref
        self.sku = sku
        self.eta = eta

        self._purchased_qty = qty
        self._allocations: set[OrderLine] = set()

    def allocate(self, order_line: OrderLine) -> None:
        if self.can_allocate(order_line):
            self._allocations.add(order_line)

    def deallocate(self, order_line: OrderLine) -> None:
        if self.can_deallocate(order_line):
            self._allocations.remove(order_line)

    @property
    def allocated_quantity(self):
        return sum(line.qty for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_qty - self.allocated_quantity

    def can_allocate(self, order_line: OrderLine) -> bool:
        return self.sku == order_line.sku and self.available_quantity >= order_line.qty

    def can_deallocate(self, order_line: OrderLine) -> bool:
        return order_line in self._allocations

    def __eq__(self, other: "Batch"):
        if isinstance(other, Batch):
            return self.ref == other.ref
        return False

    def __gt__(self, other: "Batch"):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    def __hash__(self):
        return hash(self.ref)


def allocate(order_line: OrderLine, batches: list[Batch]) -> str:
    for batch in sorted(batches):
        if batch.can_allocate(order_line):
            batch.allocate(order_line)
            return batch.ref
    raise OutOfStock(f"Cannot allocate order line to batch")
