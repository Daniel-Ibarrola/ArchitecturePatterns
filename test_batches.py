from model import Batch, OrderLine


class TestAllocate:
    def test_allocating_to_a_batch_reduces_available_quantity(self):
        batch = Batch("batch-001", "SMALL-TABLE", 20)
        order_line = OrderLine("order-001", "SMALL-TABLE", 2)

        batch.allocate(order_line)

        assert batch.available_quantity == 18

    def test_allocation_is_idempotent(self):
        batch = Batch("batch-03", "BLUE-VASE", 10)
        order_line_1 = OrderLine("order-002", "BLUE-VASE", 2)
        order_line_2 = OrderLine("order-002", "BLUE-VASE", 2)

        batch.allocate(order_line_1)
        batch.allocate(order_line_2)

        assert batch.available_quantity == 8


class TestDeallocate:
    def test_deallocating_a_line_increases_available_quantity(self):
        batch = Batch("batch-001", "SMALL-TABLE", 20)
        order_line = OrderLine("order-001", "SMALL-TABLE", 2)
        batch.allocate(order_line)

        assert batch.available_quantity == 18

        batch.deallocate(order_line)
        assert batch.available_quantity == 20

    def test_can_only_deallocate_allocated_lines(self):
        batch = Batch("batch-001", "SMALL-TABLE", 20)
        unallocated_line = OrderLine("order-001", "SMALL-TABLE", 2)

        batch.deallocate(unallocated_line)
        assert batch.available_quantity == 20


class TestBatchCanAllocate:
    def test_can_allocate_if_available_greater_than_required(self):
        batch = Batch("batch-001", "SMALL-TABLE", 20)
        order_line = OrderLine("order-001", "SMALL-TABLE", 2)
        assert batch.can_allocate(order_line)

    def test_can_allocate_if_available_equal_to_required(self):
        batch = Batch("batch-001", "SMALL-TABLE", 20)
        order_line = OrderLine("order-001", "SMALL-TABLE", 20)
        assert batch.can_allocate(order_line)

    def test_cannot_allocate_to_batch_if_available_quantity_is_less_than_order_line(
        self,
    ):
        batch = Batch("batch-002", "BLUE-CUSHION", 1)
        order_line = OrderLine("order-002", "BLUE-CUSHION", 2)

        assert batch.can_allocate(order_line) is False

    def test_cannot_allocate_line_with_different_sku(self):
        batch = Batch("batch-002", "BLUE-CUSHION", 10)
        order_line = OrderLine("order-002", "SMALL-TABLE", 2)

        assert batch.can_allocate(order_line) is False
