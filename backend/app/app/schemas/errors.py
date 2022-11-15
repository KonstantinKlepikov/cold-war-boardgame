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
                "next turn phase error": {
                    "detail":
                        "Need at least one query parameter for this request",
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


class HttpError409(HttpErrorMessage):
    """409 Conflict
    """

    class Config:
        schema_extra = {
            "example": {
                "next game phase error": {
                    "detail":
                        "This phase is last in a turn. Change turn number "
                        "before get next phase",
                        },
                "next turn phase error": {
                    "detail":
                        "Turn number can't be changed, because game is end",
                        },
                    }
                }
