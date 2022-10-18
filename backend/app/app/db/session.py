import os
from mongoengine import connect


MONGODB_URL = os.environ.get('MONGODB_URL')


connect(host=MONGODB_URL)
