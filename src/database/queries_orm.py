from sqlalchemy import select
from sqlalchemy.exc import OperationalError
from src.database.connection_orm import get_session
from src.database.models import User, Product, Review, Order, OrderItem
from sqlalchemy.orm import joinedload


def create_user(name, email, balance):
    session = get_session()
    try:
        user = User(
            name=name,
            email=email,
            balance=balance,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_user(user_id):
    session = get_session(read_only=True)
    try:
        user = session.get(User, user_id)

        return user
    finally:
        session.close()


def get_all_users():
    session = get_session(read_only=True)
    try:
        stmt = select(User)
        users = session.execute(stmt).scalars().all()

        return users
    finally:
        session.close()


def create_product(name, price, stock):
    session = get_session()
    try:
        product = Product(name=name, price=price, stock=stock)
        session.add(product)
        session.commit()
        session.refresh(product)
        return product
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_product(product_id):
    session = get_session(read_only=True)
    try:
        product = session.get(Product, product_id)
        return product
    finally:
        session.close()


def get_all_products():
    session = get_session(read_only=True)
    try:
        stmt = select(Product)
        products = session.execute(stmt).scalars().all()
        return products
    finally:
        session.close()


def update_product(product_id, name, price, stock):
    session = get_session()

    try:
        product = session.get(Product, product_id)

        if product is None:
            return None

        product.name = name
        product.price = price
        product.stock = stock

        session.commit()
        session.refresh(product)

        return product

    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def update_user_balance(user_id, new_balance):
    session = get_session()
    try:
        user = session.get(User, user_id)

        if user is None:
            return None

        user.balance = new_balance

        session.commit()

        return user

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


def delete_product(product_id):
    session = get_session()
    try:
        product = session.get(Product, product_id)

        if product is None:
            return False

        session.delete(product)
        session.commit()

        return True
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def create_review(product_id, user_id, review_text, rating):
    session = get_session()
    try:
        review = Review(
            product_id=product_id,
            user_id=user_id,
            review_text=review_text,
            rating=rating,
        )

        session.add(review)
        session.commit()
        session.refresh(review)

        return review

    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_reviews_by_product(product_id):
    session = get_session(read_only=True)
    try:
        stmt = select(Review).where(Review.product_id == product_id)
        reviews = session.execute(stmt).scalars().all()

        return reviews
    finally:
        session.close()


def get_reviews_by_user(user_id):
    session = get_session(read_only=True)
    try:
        stmt = select(Review).where(Review.user_id == user_id)
        reviews = session.execute(stmt).scalars().all()

        return reviews
    finally:
        session.close()


def get_user_orders(user_id):
    session = get_session(read_only=True)
    try:
        stmt = select(Order).where(Order.user_id == user_id)
        user_orders = session.execute(stmt).scalars().all()

        return user_orders
    finally:
        session.close()


def get_user_orders_with_products(user_id):
    session = get_session(read_only=True)
    try:
        stmt = (
            select(Order)
            .where(Order.user_id == user_id)
            .options(joinedload(Order.items).joinedload(OrderItem.product))
        )

        orders = session.execute(stmt).unique().scalars().all()

        return orders
    finally:
        session.close()


def create_order(user_id, product_id, quantity=1):
    max_attempts = 3
    for attempt in range(max_attempts):
        session = get_session()
        try:
            session.connection(
                execution_options={
                    "isolation_level": "SERIALIZABLE",
                }
            )

            user_stmt = select(User).where(User.id == user_id).with_for_update()

            user = session.execute(user_stmt).scalar_one_or_none()

            if user is None:
                return None

            product_stmt = (
                select(Product).where(Product.id == product_id).with_for_update()
            )

            product = session.execute(product_stmt).scalar_one_or_none()

            if product is None:
                return None

            if quantity <= 0:
                return None

            if product.stock < quantity:
                return None

            total = product.price * quantity

            if user.balance < total:
                return None

            user.balance -= total
            product.stock -= quantity

            order = Order(
                user_id=user_id,
                total=total,
                status="pending",
            )

            session.add(order)
            session.flush()

            order_item = OrderItem(
                order_id=order.id,
                product_id=product_id,
                quantity=quantity,
                price=product.price,
            )

            session.add(order_item)
            session.commit()
            session.refresh(order)

            return order

        except OperationalError as error:
            session.rollback()

            sqlstate = getattr(
                error.orig,
                "pgcode",
                None,
            )

            is_serialization_error = sqlstate == "40001"

            last_attempt = attempt == max_attempts - 1

            if not is_serialization_error or last_attempt:
                raise

        except Exception:
            session.rollback()
            raise

        finally:
            session.close()
