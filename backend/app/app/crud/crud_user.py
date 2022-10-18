from typing import Optional
from app.crud.crud_base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreateUpdate


class CRUDUser(CRUDBase[User, UserCreateUpdate]):
    """CRUD for User docunent
    """

    def get_by_login(self, login: str) -> Optional[User]:
        """Return user by login

        Args:
            login (str): login to query

        Returns:
            Optional[User]: User object from db
        """
        return User.objects(login=login).first()


user = CRUDUser(User)
