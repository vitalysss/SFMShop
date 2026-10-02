from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config import PRIMARY_DATABASE_URL, REPLICA_DATABASE_URL

primary_engine = create_engine(PRIMARY_DATABASE_URL)

replica_engine = create_engine(REPLICA_DATABASE_URL)

PrimarySessionLocal = sessionmaker(bind=primary_engine)

ReplicaSessionLocal = sessionmaker(bind=replica_engine)


def get_session(read_only: bool = False):
    if read_only:
        return ReplicaSessionLocal()

    return PrimarySessionLocal()
