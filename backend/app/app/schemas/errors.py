from pydantic import BaseModel


class HttpErrorMessage(BaseModel):
    """Http error
    """
    message: str

    class Config:
        schema_extra = {
            "example": {
                "detail": "Some information about error",
            }
        }


class HttpError401(HttpErrorMessage):
    """401 Unauthorized
    """

    class Config:
        schema_extra = {
            "example": {
                "detail": "Not authenticated",
            }
        }


class HttpError400(HttpErrorMessage):
    """400 Bad Request
    """

    class Config:
        schema_extra = {
            "example": {
                "detail": "Wrong login or password",
            }
        }


class HttpError409GameTurn(HttpErrorMessage):
    """409 Conflict
    """

    class Config:
        schema_extra = {
            "example": {
                "detail":
                    "Turn number can't be changed, because game is ended",
            }
        }


class HttpError409GamePhase(HttpErrorMessage):
    """409 Conflict
    """

    class Config:
        schema_extra = {
            "example": {
                "detail":
                    "This phase is last in a turn. Change turn number "
                    "before get next phase",
            }
        }
