# SFMShop

Учебный backend интернет-магазина с гибридной архитектурой баз данных.

## Технологии

- FastAPI
- SQLAlchemy ORM
- PostgreSQL
- Alembic
- Redis
- MongoDB

## Архитектура

- PostgreSQL хранит пользователей, товары, заказы и отзывы.
- Redis используется для кэширования товаров и хранения сессий.
- MongoDB используется для логов и аналитических событий.
- Чтение может направляться в PostgreSQL Replica.
- Запись выполняется в PostgreSQL Primary.

## Установка

1. Создать виртуальное окружение.
2. Установить зависимости:

```bash
pip install -r requirements.txt