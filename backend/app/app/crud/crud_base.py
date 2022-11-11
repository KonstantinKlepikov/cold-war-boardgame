from typing import Type, TypeVar, Generic, List
from pydantic import BaseModel
from mongoengine import Document


ModelType = TypeVar("ModelType", bound=Document)
CRUDType = TypeVar("CRUDType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CRUDType]):

    def __init__(self, model: Type[ModelType], schema: Type[CRUDType]):
        """
        CRUD object with default methods to Create, Update, Delete and Read objects.

        **Parameters**

        * `model`: A MongoDB model class
        """
        self.model = model
        self.schema = schema


class CRUDBaseRead(Generic[ModelType, CRUDType]):

    def __init__(self, models: List[Type[ModelType]], schema: Type[CRUDType]):
        """
        CRUD object with default methods to Read cards.

        **Parameters**

        * `models`: A MongoDB models classes
        * `schema`: A pydantic schema of classes
        """
        self.models = models
        self.schema = schema
