from typing import Type, TypeVar, Generic, List
from pydantic import BaseModel
from mongoengine import Document


ModelType = TypeVar("ModelType", bound=Document)
CreateUpdateSchemaType = TypeVar("CreateUpdateSchemaType", bound=BaseModel)
ReadSchemaType = TypeVar("ReadSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateUpdateSchemaType]):

    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete ysers.

        **Parameters**

        * `model`: A MongoDB model class
        """
        self.model = model


class CRUDBaseRead(Generic[ModelType, ReadSchemaType]):

    def __init__(self, models: List[Type[ModelType]], schema: Type[ReadSchemaType]):
        """
        CRUD object with default methods to Read cards.

        **Parameters**

        * `models`: A MongoDB models classes
        * `schema`: A pydantic schema of classes
        """
        self.models = models
        self.schema = schema
