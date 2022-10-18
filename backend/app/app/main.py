from fastapi import FastAPI
from app.db.collection import get_collection


get_collection()
app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}
