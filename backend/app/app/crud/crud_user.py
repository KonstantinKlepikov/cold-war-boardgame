from typing import Optional
from app.crud.crud_base import CRUDBase
from app.models import model_user
from app.schemas import schema_user


class CRUDUser(CRUDBase[model_user.User, schema_user.UserCreateUpdate]):
    """CRUD for User docunent
    """

    def get_by_login(self, login: str) -> Optional[model_user.User]:
        """Return user by login

        Args:
            login (str): login to query

        Returns:
            Optional[User]: User object from db
        """
        return self.model.objects(login=login).first()


user = CRUDUser(model_user.User, schema_user.UserCreateUpdate)
