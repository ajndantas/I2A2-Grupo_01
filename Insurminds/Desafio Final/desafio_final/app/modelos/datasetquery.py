from pydantic import BaseModel

class DatasetQuery(BaseModel):
    question: str