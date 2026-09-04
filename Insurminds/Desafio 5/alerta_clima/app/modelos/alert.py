from pydantic import BaseModel, Field

class Alert(BaseModel):
        message: str