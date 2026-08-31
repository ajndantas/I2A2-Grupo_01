from app.modelos.weather import Weather

class Current(Weather):
    temp_max: str
    temp_min: str
    sunrise: str
    sunset: str        
    precip_prob: str
    precip: str
    wind_gusts: str        
    weather_code: int
    weather_icon: str  