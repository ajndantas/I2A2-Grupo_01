from app.modelos.current import Current
from app.modelos.forecast import Forecast
from fastapi import HTTPException
import requests
from datetime import datetime
from app.modelos.current import Current 
from app.modelos.forecast import Forecast
from app.modelos.alert import Alert
from typing import List

class CurrentRequest(): # Request para previsão de 7 dias
    def __init__(self, latitude: float, longitude: float):

        self._URL = "https://api.open-meteo.com/v1/forecast"

        current_params = {
            "latitude": latitude,
            "longitude": longitude,
            "models": "ncep_gfs_seamless", # Modelo de previsão do NCEP (National Center for Environmental Prediction)
            "current": ["precipitation", "precipitation_probability", "weather_code", "wind_gusts_10m"],
            "timezone": "America/Sao_Paulo"            
        }

        daily_params = {
            "latitude": latitude,
            "longitude": longitude,
            "models": "ncep_gfs_seamless", # Modelo de previsão do NCEP (National Center for Environmental Prediction)
            "daily": ["sunrise", "sunset", "temperature_2m_max","temperature_2m_min"],
            "timezone": "America/Sao_Paulo"            
        }

        daily_response = requests.get(url=self._URL, params=daily_params)
        current_response = requests.get(url=self._URL, params=current_params)

        if daily_response.status_code != 200:
            raise HTTPException(status_code=404, detail=daily_response.json()) 

        elif current_response.status_code != 200:
            raise HTTPException(status_code=404, detail=current_response.json())
        
        self.__daily_json = daily_response.json()['daily'] # Primeiro dia da previsão, que será o dia atual 
        self._current_json = current_response.json()['current']
        
        self.__WMO_CODES = {
                                0: {"descricao": "Céu limpo", "icone": "☀️"},
                                1: {"descricao": "Predominantemente limpo", "icone": "🌤️"},
                                2: {"descricao": "Parcialmente nublado", "icone": "⛅"},
                                3: {"descricao": "Encoberto", "icone": "☁️"},
                                45: {"descricao": "Nevoeiro", "icone": "🌫️"},
                                48: {"descricao": "Nevoeiro com geada", "icone": "🌫️❄️"},
                                51: {"descricao": "Garoa leve", "icone": "🌦️"},
                                53: {"descricao": "Garoa moderada", "icone": "🌦️"},
                                55: {"descricao": "Garoa densa", "icone": "🌧️"},
                                56: {"descricao": "Garoa congelante leve", "icone": "🥶🌧️"},
                                57: {"descricao": "Garoa congelante densa", "icone": "🥶🌧️"},
                                61: {"descricao": "Chuva leve", "icone": "🌧️"},
                                63: {"descricao": "Chuva moderada", "icone": "🌧️"},
                                65: {"descricao": "Chuva forte", "icone": "🌧️🌧️"},
                                66: {"descricao": "Chuva congelante leve", "icone": "🧊🌧️"},
                                67: {"descricao": "Chuva congelante forte", "icone": "🧊🌧️"},
                                71: {"descricao": "Queda de neve leve", "icone": "🌨️"},
                                73: {"descricao": "Queda de neve moderada", "icone": "🌨️"},
                                75: {"descricao": "Queda de neve forte", "icone": "❄️❄️"},
                                77: {"descricao": "Grãos de neve", "icone": "❄️"},
                                80: {"descricao": "Pancadas de chuva leves", "icone": "🌦️"},
                                81: {"descricao": "Pancadas de chuva moderadas", "icone": "🌧️"},
                                82: {"descricao": "Pancadas de chuva violentas", "icone": "⛈️"},
                                85: {"descricao": "Pancadas de neve leves", "icone": "🌨️"},
                                86: {"descricao": "Pancadas de neve fortes", "icone": "❄️"},
                                95: {"descricao": "Tempestade", "icone": "⚡"},
                                96: {"descricao": "Tempestade com granizo leve", "icone": "⚡🧊"},
                                99: {"descricao": "Tempestade com granizo forte", "icone": "⚡🧊"}
                            }

    
    def _getDescriptions(self, weather_code: int):
        return self.__WMO_CODES.get(weather_code)['descricao']

    def _getIcons(self, weather_code: int):
        return self.__WMO_CODES.get(weather_code)['icone'] 
    
    def getCurrent(self) -> Current:

        sunrise = self.__daily_json['sunrise'][0] # Primeiro dia da previsão
        sunrise_hour = datetime.fromisoformat(sunrise).time()

        sunset = self.__daily_json['sunset'][0] # Primeiro dia da previsão
        sunset_hour = datetime.fromisoformat(sunset).time()

        if sunrise_hour > sunset_hour:
            sunrise = f'{sunrise_hour} do dia anterior no horário de Brasília'

        else:
            sunrise = f'{sunrise_hour} no horário de Brasília'                
            
        return Current(
                        sunrise = sunrise,
                        sunset = f'{sunset_hour} no horário de Brasília',
                        temp_max = f'{self.__daily_json["temperature_2m_max"][0]}°C',
                        temp_min = f'{self.__daily_json["temperature_2m_min"][0]}°C', 
                        precip = f'{self._current_json['precipitation']} mm',                        
                        precip_prob = f'{self._current_json['precipitation_probability']}%',
                        wind_gusts = f'{round(self._current_json['wind_gusts_10m']*3.6, 2)} km/h',
                        weather_code = self._current_json['weather_code'],
                        description = self._getDescriptions(self._current_json['weather_code']),
                        weather_icon = self._getIcons(self._current_json['weather_code'])
                     )
                
    
class ForecastRequest(CurrentRequest):    
    def __init__(self, latitude: float, longitude: float):
        super().__init__(latitude, longitude)

        daily_params = {
                            "latitude": latitude,
                            "longitude": longitude,
                            "models": "ncep_gfs_seamless", # Modelo de previsão do NCEP (National Center for Environmental Prediction)
                            "daily": ["sunrise", "sunset", "weather_code", "temperature_2m_max", "temperature_2m_min", "precipitation_probability_max", "wind_gusts_10m_max", "precipitation_sum"],
                            "timezone": "America/Sao_Paulo"            
                        }

        response = requests.get(self._URL, params=daily_params)

        if response.status_code != 200:
            raise HTTPException(status_code=404, detail=response.json())
        
        self.__json = response.json()['daily']
        
    def getForecast(self) -> List[Forecast]:            
            
            days = []
    
            for r in zip(
                         self.__json['time'],
                         self.__json['weather_code'], 
                         self.__json['sunrise'], 
                         self.__json['sunset'], 
                         self.__json['temperature_2m_max'], 
                         self.__json['temperature_2m_min'], 
                         self.__json['precipitation_probability_max'], 
                         self.__json['precipitation_sum'],
                         self.__json['wind_gusts_10m_max']
                        ):
    
                sunrise_hour = datetime.fromisoformat(r[2]).time()
                sunset_hour = datetime.fromisoformat(r[3]).time()
    
                if sunrise_hour > sunset_hour:
                    sunrise = f'{sunrise_hour} do dia anterior no horário de Brasília'
    
                else:
                    sunrise = f'{sunrise_hour} no horário de Brasília'                
                
                d = {
                        "date": r[0],
                        "weather_code": r[1],
                        "sunrise": sunrise,
                        "sunset": f'{sunset_hour} no horário de Brasília',
                        "temp_max": r[4],
                        "temp_min": r[5],
                        "precipitation_probability_max": r[6],
                        "precipitation_sum": r[7],
                        "wind_gusts_10m_max": r[8]
                    }
    
                days.append(d)
    
    
            return [Forecast(
                                    date = days[i]['date'],
                                    description = self._getDescriptions(days[i]['weather_code']),
                                    sunrise = days[i]['sunrise'],
                                    sunset = days[i]['sunset'],
                                    temp_max = f'{days[i]['temp_max']}°C',
                                    temp_min = f'{days[i]['temp_min']}°C', 
                                    precip = f'{days[i]["precipitation_sum"]} mm',
                                    precip_prob = f'{days[i]["precipitation_probability_max"]}%',
                                    wind_gusts = f'{round(days[i]['wind_gusts_10m_max'], 2)} km/h',
                                    weather_code = days[i]['weather_code'],
                                    weather_icon = self._getIcons(days[i]['weather_code'])            
                            ) for i in range(len(days))
                    ]       
    

class AlertRequest(CurrentRequest):
    def __init__(self, latitude: float, longitude: float):
        super().__init__(latitude, longitude)      
             

    def getAlert(self) -> Alert:

        current = super().getCurrent()

        if (
                current.weather_code in [45,48,56,57,65,66,67,71,73,75,77] 
                or current.weather_code > 82
            ):

            return Alert(
                            description = current.description,
                            weather_code = current.weather_code,
                            weather_icon = current.weather_icon 
                        )
        
        else:
            raise HTTPException(status_code=404, detail=(f"Clima: {current.description} - Nenhum alerta encontrado"))
            

# TESTE
if __name__ == "__main__":
    request = AlertRequest(latitude = -22.9068, longitude = -43.1729) # Coordenadas 
    print(request.getAlert())