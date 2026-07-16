from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()
primary_database_url = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_PRIMARY_HOST')}:{os.getenv('DB_PRIMARY_PORT')}/{os.getenv('DB_NAME')}"
)
replica_database_url = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_REPLICA_HOST')}:{os.getenv('DB_REPLICA_PORT')}/{os.getenv('DB_NAME')}"
)
primary_engine = create_engine(primary_database_url)

replica_engine = create_engine(replica_database_url)

PrimarySessionLocal = sessionmaker(bind=primary_engine)
ReplicaSessionLocal = sessionmaker(bind=replica_engine)


def get_session(read_only=False):
    if read_only:
        return ReplicaSessionLocal()

    return PrimarySessionLocal()
