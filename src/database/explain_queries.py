from sqlalchemy import text

from src.database.connection_orm import primary_engine


def explain_user_orders(user_id: int) -> None:
    query = text(
        """
        EXPLAIN ANALYZE
        SELECT *
        FROM orders
        WHERE user_id = :user_id
        """
    )

    with primary_engine.connect() as connection:
        result = connection.execute(
            query,
            {
                "user_id": user_id,
            },
        )

        for row in result:
            print(row[0])


def explain_orders_by_date() -> None:
    query = text(
        """
        EXPLAIN ANALYZE
        SELECT *
        FROM orders
        ORDER BY order_date DESC
        LIMIT 20
        """
    )

    with primary_engine.connect() as connection:
        result = connection.execute(query)

        for row in result:
            print(row[0])


def explain_product_order_items(product_id: int) -> None:
    query = text(
        """
        EXPLAIN ANALYZE
        SELECT *
        FROM order_items
        WHERE product_id = :product_id
        """
    )

    with primary_engine.connect() as connection:
        result = connection.execute(
            query,
            {
                "product_id": product_id,
            },
        )

        for row in result:
            print(row[0])


if __name__ == "__main__":
    print("Заказы пользователя:")
    explain_user_orders(1)

    print("\nЗаказы по дате:")
    explain_orders_by_date()

    print("\nПозиции по товару:")
    explain_product_order_items(1)
