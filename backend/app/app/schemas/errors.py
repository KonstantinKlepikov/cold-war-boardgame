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
