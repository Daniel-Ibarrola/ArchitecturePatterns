from sqlalchemy import text

from model import OrderLine


def test_orderline_mapper_can_load_orderlines(session):
    order_lines = [
        {"sku": "RED-CHAIR", "qty": 5, "orderid": "order1"},
        {"sku": "BLUE-TABLE", "qty": 2, "orderid": "order2"},
        {"sku": "GRAY-SOFA", "qty": 3, "orderid": "order3"},
    ]
    session.execute(
        text(
            """INSERT INTO order_lines (sku, qty, orderid) VALUES (:sku, :qty, :orderid)"""
        ),
        params=order_lines,
    )

    order_lines = session.query(OrderLine).all()
    expected = [
        OrderLine("order1", "RED-CHAIR", 5),
        OrderLine("order2", "BLUE-TABLE", 2),
        OrderLine("order3", "GRAY-SOFA", 3),
    ]
    assert order_lines == expected


def test_orderline_mapper_can_save_orderlines(session):
    orderline1 = OrderLine("order1", "RED-CHAIR", 5)
    orderline2 = OrderLine("order2", "BLUE-TABLE", 2)

    session.add(orderline1)
    session.add(orderline2)
    session.commit()

    results = list(
        session.execute(text("""SELECT sku, qty, orderid FROM order_lines"""))
    )
    assert results == [
        ("RED-CHAIR", 5, "order1"),
        ("BLUE-TABLE", 2, "order2"),
    ]
