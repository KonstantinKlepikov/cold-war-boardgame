from mongoengine import (
    Document, StringField, BooleanField, EmbeddedDocument,
    )


class UserName(EmbeddedDocument):
    """User name
    """
    login = StringField()


class User(Document):
    """User mapping
    """
    login = StringField(max_length=50, min_length=5, unique=True, required=True)
    hashed_password = StringField(required=True)
    is_active = BooleanField(default=True)

    meta = {
        'indexes': ['login', ],
        }
