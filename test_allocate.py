from datetime import date, timedelta

import pytest

from model import Batch, OrderLine, allocate, OutOfStock


today = date.today()
tomorrow = today + timedelta(days=1)
later = today + timedelta(weeks=1)


def test_prefers_current_stock_batches_to_shipments():
    sku = "RED-CHAIR"
    in_stock_batch = Batch("batch-001", sku, 10, eta=None)
    shipment_batch = Batch("batch-002", sku, 12, eta=tomorrow)
    line = OrderLine("order-001", sku, 2)

    allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 8
    assert shipment_batch.available_quantity == 12


def test_prefers_earlier_batches():
    sku = "BLUE-VASE"
    earlier_batch = Batch("batch-001", sku, 10, eta=today)
    medium_batch = Batch("batch-002", sku, 10, eta=tomorrow)
    late_batch = Batch("batch-003", sku, 10, eta=later)
    line = OrderLine("order-001", sku, 2)

    batches = [earlier_batch, medium_batch, late_batch]
    allocate(line, batches)

    assert earlier_batch.available_quantity == 8
    assert medium_batch.available_quantity == 10
    assert late_batch.available_quantity == 10


def test_returns_allocated_batch_reference():
    sku = "RED-CHAIR"
    in_stock_batch = Batch("batch-001", sku, 10, eta=None)
    shipment_batch = Batch("batch-002", sku, 12, eta=tomorrow)
    line = OrderLine("order-001", sku, 2)

    line_ref = allocate(line, [in_stock_batch, shipment_batch])
    assert line_ref == in_stock_batch.ref


def test_raises_out_of_stock_exception_if_cannot_allocate():
    sku = "RED-CHAIR"
    in_stock_batch = Batch("batch-001", sku, 10, eta=None)
    shipment_batch = Batch("batch-002", sku, 12, eta=tomorrow)
    line = OrderLine("order-001", sku, 20)

    with pytest.raises(OutOfStock):
        allocate(line, [in_stock_batch, shipment_batch])
