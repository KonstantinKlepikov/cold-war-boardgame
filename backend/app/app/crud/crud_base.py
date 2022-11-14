from typing import Type, TypeVar, Generic
from pydantic import BaseModel
from mongoengine import Document


ModelType = TypeVar("ModelType", bound=Document)
CRUDType = TypeVar("CRUDType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CRUDType]):

    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Update, Delete and Read objects.

        **Parameters**

        * `model`: A MongoDB model class
        """
        self.model = model
