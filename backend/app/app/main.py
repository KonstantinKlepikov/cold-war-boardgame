from fastapi import FastAPI
import app.models as models
import app.schemas as schemas


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}
