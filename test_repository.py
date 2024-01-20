from sqlalchemy import text
from sqlalchemy.orm import Session

import model
import repository


def test_repository_can_save_a_batch(session):
    batch = model.Batch("batch1", "RUSTY-SOAPDISH", 100, eta=None)

    repo = repository.SQLAlchemyRepository(session)
    repo.add(batch)
    session.commit()

    rows = session.execute(
        text("SELECT reference, sku, _purchased_quantity, eta from 'batches'")
    )
    assert list(rows) == [("batch1", "RUSTY-SOAPDISH", 100, None)]


def insert_order_line(session: Session):
    session.execute(
        text(
            "INSERT INTO order_lines (orderid, sku, qty) VALUES (:orderid, :sku, :qty)"
        ),
        params=dict(orderid="order1", sku="GENERIC-SOFA", qty=12),
    )

    [[orderline_id]] = session.execute(
        text(
            "SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku",
        ),
        params=dict(orderid="order1", sku="GENERIC-SOFA"),
    )
    return orderline_id


def insert_batch(session: Session, batch_ref: str):
    session.execute(
        text("INSERT INTO batches (ref, sku, qty) VALUES (:ref, :sku, :qty)"),
        params=dict(ref=batch_ref, sku="GENERIC-SOFA", qty=5),
    )

    [[batch_id]] = session.execute(
        text(
            "SELECT id FROM batches WHERE ref=:ref AND sku=:sku",
        ),
        params=dict(ref=batch_ref, sku="GENERIC-SOFA"),
    )
    return batch_id


def insert_allocation(session: Session, orderline_id: int, batch_id: int):
    pass


def test_repository_can_retrieve_a_batch_with_allocations(session: Session):
    orderline_id = insert_order_line(session)
    batch1_id = insert_batch(session, "batch1")
    insert_batch(session, "batch2")
    insert_allocation(session, orderline_id, batch1_id)  # (2)

    repo = repository.SqlAlchemyRepository(session)
    retrieved = repo.get("batch1")

    expected = model.Batch("batch1", "GENERIC-SOFA", 100, eta=None)
    assert retrieved == expected  # Batch.__eq__ only compares reference  #(3)
    assert retrieved.sku == expected.sku  # (4)
    assert retrieved._purchased_quantity == expected._purchased_quantity
    assert retrieved._allocations == {  # (4)
        model.OrderLine("order1", "GENERIC-SOFA", 12),
    }
