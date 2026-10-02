import os

from dotenv import load_dotenv

load_dotenv()


def get_required_env(name: str) -> str:
    value = os.getenv(name)

    if value is None:
        raise RuntimeError(f"Не задана переменная окружения {name}")

    return value


SECRET_KEY = get_required_env("SECRET_KEY")


DB_USER = get_required_env("DB_USER")
DB_PASSWORD = get_required_env("DB_PASSWORD")
DB_NAME = get_required_env("DB_NAME")

DB_PRIMARY_HOST = get_required_env("DB_PRIMARY_HOST")
DB_PRIMARY_PORT = get_required_env("DB_PRIMARY_PORT")

DB_REPLICA_HOST = get_required_env("DB_REPLICA_HOST")
DB_REPLICA_PORT = get_required_env("DB_REPLICA_PORT")

REDIS_HOST = get_required_env("REDIS_HOST")
REDIS_PORT = get_required_env("REDIS_PORT")

MONGO_HOST = get_required_env("MONGO_HOST")
MONGO_PORT = get_required_env("MONGO_PORT")

RABBITMQ_HOST = os.getenv(
    "RABBITMQ_HOST",
    "127.0.0.1",
)
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))

PRIMARY_DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_PRIMARY_HOST}:{DB_PRIMARY_PORT}/{DB_NAME}"
)

REPLICA_DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_REPLICA_HOST}:{DB_REPLICA_PORT}/{DB_NAME}"
)

REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"

DEBUG = os.getenv("DEBUG", "False").lower() == "true"
