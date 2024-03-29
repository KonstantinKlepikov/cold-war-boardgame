from mongoengine import Document, StringField, BooleanField


class User(Document):
    """User
    """
    login = StringField(max_length=50, min_length=5, unique=True, required=True)
    hashed_password = StringField(required=True)
    is_active = BooleanField(default=True)

    meta = {
        'indexes': ['login', ],
        }
