# Развёртывание SFMShop

## Требования

Для локального запуска необходимы:

- Python 3.12;
- Docker;
- Docker Compose;
- Git.

## Подготовка переменных окружения

Создайте локальный файл `.env` на основе шаблона:

```powershell
Copy-Item .env.example .env
```

Укажите в `.env` собственные значения. Файл `.env` содержит конфиденциальные настройки и не должен добавляться в Git.

Основные переменные:

- `DB_USER` — пользователь PostgreSQL;
- `DB_PASSWORD` — пароль PostgreSQL;
- `DB_NAME` — название базы данных;
- `DB_PRIMARY_HOST` — адрес основной базы данных;
- `DB_PRIMARY_PORT` — порт основной базы данных;
- `DB_REPLICA_HOST` — адрес реплики;
- `DB_REPLICA_PORT` — порт реплики;
- `REDIS_HOST` — адрес Redis;
- `REDIS_PORT` — порт Redis;
- `MONGO_HOST` — адрес MongoDB;
- `MONGO_PORT` — порт MongoDB;
- `RABBITMQ_HOST` — адрес RabbitMQ;
- `RABBITMQ_PORT` — порт RabbitMQ;
- `SECRET_KEY` — секретный ключ для JWT;
- `DEBUG` — режим отладки.

## Локальный запуск без Docker

Создайте виртуальное окружение:

```powershell
python -m venv venv
```

Активируйте его в Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Для Linux или macOS:

```bash
source venv/bin/activate
```

Установите зависимости:

```powershell
python -m pip install -r requirements.txt
```

Примените миграции базы данных:

```powershell
python -m alembic upgrade head
```

Запустите приложение:

```powershell
python -m uvicorn src.api.main:app --reload
```

После запуска документация API будет доступна по адресу:

```text
http://127.0.0.1:8000/docs
```

## Запуск через Docker Compose

Из корня проекта выполните:

```powershell
docker compose --env-file .env -f docker/docker-compose.yml up --build
```

Docker Compose запускает:

- приложение SFMShop;
- consumer фоновых задач;
- PostgreSQL;
- Redis;
- MongoDB;
- RabbitMQ с панелью управления.

Миграции Alembic применяются автоматически перед запуском приложения.

Приложение доступно по адресу:

```text
http://localhost:8000
```

Документация API:

```text
http://localhost:8000/docs
```

Панель управления RabbitMQ:

```text
