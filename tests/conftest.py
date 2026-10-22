import os

TEST_ENV = {
    "SECRET_KEY": "test-secret-key",
    "DB_USER": "postgres",
    "DB_PASSWORD": "postgres",
    "DB_NAME": "sfmshop_test",
    "DB_PRIMARY_HOST": "localhost",
    "DB_PRIMARY_PORT": "5432",
    "DB_REPLICA_HOST": "localhost",
    "DB_REPLICA_PORT": "5432",
    "REDIS_HOST": "localhost",
    "REDIS_PORT": "6379",
    "MONGO_HOST": "localhost",
    "MONGO_PORT": "27017",
    "RABBITMQ_HOST": "localhost",
    "RABBITMQ_PORT": "5672",
    "DEBUG": "False",
}

for name, value in TEST_ENV.items():
    os.environ.setdefault(name, value)
