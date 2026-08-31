from pydantic import BaseModel

class Weather(BaseModel):
        description: str
        weather_code: int
        weather_icon: str  
           