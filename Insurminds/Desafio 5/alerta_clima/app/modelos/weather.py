from pydantic import BaseModel
from app.modelos.alert import Alert

class Weather(BaseModel):
        description: str
        weather_code: int
        weather_icon: str
        alert: Alert  
           