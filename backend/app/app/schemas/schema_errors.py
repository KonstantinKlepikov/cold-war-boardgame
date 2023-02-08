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


class HttpError400(HttpErrorMessage):
    """400 Bad Request
    """

    class Config:
        schema_extra = {

            "example": {
                "autorisation error": {
                    "detail":
                        "Wrong login or password",
                        },
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


class HttpError404(HttpErrorMessage):
    """404 Not Found
    """

    class Config:
        schema_extra = {
            "example": {
                "detail": "Cant find current game data in db. For start "
                          "new game use /game/create endpoint",
            }
        }


class HttpError409(HttpErrorMessage):
    """409 Conflict
    """

    class Config:
        schema_extra = {
            "example": {
                "detail":
                    "Something wrong with client or server data",
            }
        }
