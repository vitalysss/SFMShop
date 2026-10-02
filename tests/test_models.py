from types import SimpleNamespace

import pytest

from src.models.cart import ShoppingCart
from src.models.delivery_strategy import (
    ExpressDelivery,
    StandardDelivery,
    process_delivery,
)
from src.models.notifications import (
    EmailNotification,
    SMSNotification,
    send_notifications,
)
from src.models.order import Order as DomainOrder
from src.models.order_factory import OrderFactory
from src.models.payment import (
    BankTransferPaymentMethod,
    CardPayment,
    CardPaymentMethod,
    PayPalPaymentMethod,
)
from src.models.product import Product as DomainProduct
from src.models.user import User as DomainUser
from src.services.discounts import FixedDiscount, PercentDiscount


@pytest.fixture
def domain_user():
    return DomainUser(
        user_id=1,
        name="Alice",
        email="alice@example.com",
        age=25,
        balance=10000,
    )


@pytest.fixture
def domain_product():
    return DomainProduct(
        name="Keyboard",
        price=2000,
        quantity=3,
    )


@pytest.fixture
def domain_order(domain_user, domain_product):
    return DomainOrder(
        order_id=1,
        user=domain_user,
        products=[domain_product],
    )


def test_domain_user_creation(domain_user):
    assert domain_user.user_id == 1
    assert domain_user.name == "Alice"
    assert domain_user.email == "alice@example.com"
    assert domain_user.age == 25
    assert domain_user.balance == 10000
    assert domain_user.orders == []
    assert domain_user.is_active is True


@pytest.mark.parametrize(
    "field, value",
    [
        ("user_id", -1),
        ("age", -1),
        ("balance", -1),
    ],
)
def test_domain_user_rejects_negative_values(field, value):
    data = {
        "user_id": 1,
        "name": "Alice",
        "email": "alice@example.com",
        "age": 25,
        "balance": 1000,
    }
    data[field] = value

    with pytest.raises(
        ValueError,
        match="Значение не может быть отрицательным",
    ):
        DomainUser(**data)


def test_domain_product_creation(domain_product):
    assert domain_product.name == "Keyboard"
    assert domain_product.price == 2000
    assert domain_product.quantity == 3
    assert domain_product.validate() is True


def test_domain_product_from_dict():
    product = DomainProduct.from_dict(
        {
            "name": "Mouse",
            "price": 1000,
            "quantity": 5,
        }
    )

    assert product.name == "Mouse"
    assert product.price == 1000
    assert product.quantity == 5


def test_domain_product_rejects_empty_name():
    with pytest.raises(
        ValueError,
        match="Название товара не может быть пустым",
    ):
        DomainProduct(
            name="",
            price=1000,
            quantity=1,
        )


@pytest.mark.parametrize(
    "price, quantity",
    [
        (-1, 1),
        (1000, -1),
    ],
)
def test_domain_product_rejects_negative_values(
    price,
    quantity,
):
    with pytest.raises(
        ValueError,
        match="Значение не может быть отрицательным",
    ):
        DomainProduct(
            name="Mouse",
            price=price,
            quantity=quantity,
        )


def test_product_total_value_is_cached(domain_product):
    assert domain_product.total_value == 6000

    domain_product.price = 3000

    assert domain_product.total_value == 6000


def test_product_discount_strategies(domain_product):
    assert domain_product.calculate_price(PercentDiscount(10)) == 1800

    assert domain_product.calculate_price(FixedDiscount(500)) == 1500

    assert FixedDiscount(5000).apply(1000) == 0


def test_domain_order_behaviour(
    domain_user,
    domain_product,
    domain_order,
):
    second_product = DomainProduct(
        name="Mouse",
        price=1000,
        quantity=2,
    )
    second_order = DomainOrder(
        order_id=2,
        user=domain_user,
        products=[second_product],
    )

    assert str(domain_order) == "Заказ 1 пользователя Alice"
    assert len(domain_order) == 1
    assert domain_product in domain_order
    assert "Keyboard" in domain_order
    assert "Monitor" not in domain_order
    assert domain_order == DomainOrder(
        order_id=1,
        user=domain_user,
        products=[],
    )
    assert domain_order != second_order
    assert domain_order != object()
    assert domain_order < second_order

    combined = domain_order + second_order

    assert len(combined) == 2
    assert domain_product in combined
    assert second_product in combined
    assert domain_order.__add__(object()) is NotImplemented
    assert domain_order.__lt__(object()) is NotImplemented


def test_domain_order_serialization(domain_order):
    result = domain_order.to_json()

    assert result["class"] == "Order"
    assert result["data"]["_order_id"] == 1


def test_shopping_cart(domain_product):
    empty_cart = ShoppingCart()
    filled_cart = empty_cart + domain_product

    assert len(empty_cart) == 0
    assert len(filled_cart) == 1
    assert list(filled_cart) == [domain_product]


@pytest.mark.parametrize(
    "strategy, distance, expected",
    [
        (StandardDelivery(), 10, 100),
        (ExpressDelivery(), 10, 200),
    ],
)
def test_delivery_strategies(
    strategy,
    distance,
    expected,
):
    assert process_delivery(strategy, distance) == expected


def test_notifications(capsys):
    send_notifications(
        [EmailNotification(), SMSNotification()],
        "Заказ создан",
    )

    output = capsys.readouterr().out

    assert "Отправка email: Заказ создан" in output
    assert "Отправка SMS: Заказ создан" in output


def test_card_payment():
    payment = CardPayment(1000)

    assert payment.process() is True
    assert payment.to_json() == {
        "type": "CardPayment",
        "amount": 1000,
    }


@pytest.mark.parametrize(
    "method",
    [
        CardPaymentMethod(),
        PayPalPaymentMethod(),
        BankTransferPaymentMethod(),
    ],
)
def test_payment_methods(method):
    payment = SimpleNamespace(amount=15000)

    assert method.process(payment) is True


def test_order_factory(domain_user, domain_product):
    order = OrderFactory.create_order(
        10,
        domain_user,
        [domain_product],
    )

    assert order.order_id == 10
    assert order.user is domain_user
    assert order.products == [domain_product]


def test_order_factory_from_dict(
    domain_user,
    domain_product,
):
    order = OrderFactory.create_order_from_dict(
        {
            "order_id": 11,
            "user": domain_user,
            "products": [domain_product],
        }
    )

    assert order.order_id == 11


def test_order_factory_rejects_missing_user(
    domain_product,
):
    with pytest.raises(
        ValueError,
        match="У заказа должен быть пользователь",
    ):
        OrderFactory.create_order(
            1,
            None,
            [domain_product],
        )


def test_order_factory_rejects_empty_order(
    domain_user,
):
    with pytest.raises(
        ValueError,
        match="Заказ не может быть пустым",
    ):
        OrderFactory.create_order(
            1,
            domain_user,
            [],
        )


def test_order_factory_rejects_zero_quantity(
    domain_user,
):
    product = DomainProduct(
        name="Mouse",
        price=1000,
        quantity=0,
    )

    with pytest.raises(
        ValueError,
        match="Количество товара должно быть больше 0",
    ):
        OrderFactory.create_order(
            1,
            domain_user,
            [product],
        )
