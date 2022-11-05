from typing import Type, TypeVar, Generic, List
from pydantic import BaseModel
from mongoengine import Document


ModelType = TypeVar("ModelType", bound=Document)
CreateUpdateSchemaType = TypeVar("CreateUpdateSchemaType", bound=BaseModel)
ReadSchemaType = TypeVar("ReadSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateUpdateSchemaType]):

    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A MongoDB model class
        """
        self.model = model


class CRUDBaseRead(Generic[ModelType, ReadSchemaType]):

    def __init__(self, models: List[Type[ModelType]], schema: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `models`: A MongoDB models classes
        """
        self.models = models
        self.schema = schema
