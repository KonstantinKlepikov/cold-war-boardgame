from mongoengine import connect
from app.config import settings


def get_collection():
    connect(
        host=settings.mongodb_url,
        name=settings.db_name,
        )
