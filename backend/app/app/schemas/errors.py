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
