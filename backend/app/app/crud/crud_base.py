from typing import Type, TypeVar, Generic
from pydantic import BaseModel
from mongoengine import Document


ModelType = TypeVar("ModelType", bound=Document)
CreateUpdateSchemaType = TypeVar("CreateUpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateUpdateSchemaType]):

    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A MongoDB model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model
