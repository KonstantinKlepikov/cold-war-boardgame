from mongoengine import Document, StringField, BooleanField


class User(Document):
    """User mapping
    """
    login = StringField(max_length=50, min_length=5, unique=True, required=True)
    password = StringField(max_length=50, min_length=8, required=True)
    is_active = BooleanField(default=True)
