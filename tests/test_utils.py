from types import SimpleNamespace

import pytest

from src.utils.calculations import (
    calculate_delivery,
    calculate_discount,
    calculate_final_price,
    create_products_catalog,
    find_product_in_dict,
    find_product_in_list,
)
from src.utils.order_processor import (
    analyze_orders,
    calculate_order_total,
    get_discount_by_total,
    load_orders_from_file,
    process_order_file,
    process_orders,
)
from src.utils.validators import validate_age, validate_email


@pytest.mark.parametrize(
    "price, discount_rate, expected",
    [
        (1000, 0.05, 50),
        (10000, 0.1, 1000),
        (15000, 0.15, 2250),
    ],
)
def test_calculate_discount(price, discount_rate, expected):
    assert calculate_discount(price, discount_rate) == expected


@pytest.mark.parametrize(
    "weight, distance, expected",
    [
        (1, 10, 160),
        (5, 50, 400),
        (10, 100, 700),
        (5, 200, 1150),
    ],
)
def test_calculate_delivery(weight, distance, expected):
    assert calculate_delivery(weight, distance) == expected


def test_calculate_final_price():
    assert calculate_final_price(1000, 100, 250) == 1150


def test_product_catalog_and_search():
    product_1 = SimpleNamespace(id=1, name="Keyboard")
    product_2 = SimpleNamespace(id=2, name="Mouse")
    products = [product_1, product_2]

    assert find_product_in_list(products, 2) is product_2
    assert find_product_in_list(products, 99) is None

    catalog = create_products_catalog(products)

    assert catalog == {1: product_1, 2: product_2}
    assert find_product_in_dict(catalog, 1) is product_1
    assert find_product_in_dict(catalog, 99) is None


@pytest.mark.parametrize(
    "age, expected",
    [
        (17, False),
        (18, True),
        (25, True),
    ],
)
def test_validate_age(age, expected):
    assert validate_age(age) is expected


@pytest.mark.parametrize(
    "email, expected",
    [
        ("user@example.com", True),
        ("user@example", False),
        ("example.com", False),
    ],
)
def test_validate_email(email, expected):
    assert validate_email(email) is expected


@pytest.mark.parametrize(
    "total, expected",
    [
        (-1, 0),
        (0, 0),
        (1000, 0.05),
        (5000, 0.05),
        (5001, 0.1),
        (10000, 0.1),
        (10001, 0.15),
    ],
)
def test_get_discount_by_total(total, expected):
    assert get_discount_by_total(total) == expected


def test_calculate_order_total():
    assert calculate_order_total(1000, 0.1) == 900
    assert calculate_order_total(1234.56, 0.05) == 1172.83


def test_process_orders():
    source = [
        "1:1000:new:Alice",
        "2:10000:paid:Bob",
        "incorrect line",
        "3:not-a-number:new:Alice",
    ]

    result = process_orders(source)

    assert result == [
        {
            "order_id": "1",
            "total": 950.0,
            "status": "new",
            "user": "Alice",
        },
        {
            "order_id": "2",
            "total": 9000.0,
            "status": "paid",
            "user": "Bob",
        },
    ]


def test_analyze_orders():
    orders = [
        {
            "order_id": "1",
            "total": 950,
            "status": "new",
            "user": "Alice",
        },
        {
            "order_id": "2",
            "total": 900,
            "status": "paid",
            "user": "Bob",
        },
        {
            "order_id": "3",
            "total": 500,
            "status": "new",
            "user": "Alice",
        },
    ]

    result = analyze_orders(orders)

    assert result["total_orders"] == 3
    assert result["total_sum"] == 2350
    assert result["by_status"] == {"new": 2, "paid": 1}
    assert set(result["unique_users"]) == {"Alice", "Bob"}


def test_load_orders_from_file(tmp_path):
    input_file = tmp_path / "orders.txt"
    input_file.write_text(
        "1:1000:new:Alice\n2:500:paid:Bob\n",
        encoding="utf-8",
    )

    assert load_orders_from_file(input_file) == [
        "1:1000:new:Alice",
        "2:500:paid:Bob",
    ]


def test_load_orders_from_missing_file(tmp_path):
    missing_file = tmp_path / "missing.txt"

    assert load_orders_from_file(missing_file) == []


def test_process_order_file(tmp_path):
    input_file = tmp_path / "orders.txt"
    output_file = tmp_path / "report.txt"

    input_file.write_text(
        "1:1000:new:Alice\n2:500:paid:Bob\n",
        encoding="utf-8",
    )

    process_order_file(input_file, output_file)

    report = output_file.read_text(encoding="utf-8")

    assert "Обработано заказов: 2" in report
    assert "Общая сумма: 1425.0 руб." in report
    assert "new: 1" in report
    assert "paid: 1" in report
    assert "Уникальных пользователей: 2" in report
