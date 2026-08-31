from fastapi import Body, HTTPException, APIRouter
from app.request import CurrentRequest, ForecastRequest, AlertRequest
from app.modelos.current import Current
from app.latlong import LatLong
from app.modelos.forecast import Forecast
from app.modelos.alert import Alert
from app.modelos.weather import Weather
from typing import List

router = APIRouter(
    prefix="/api/v1"
)

latlong = LatLong()

@router.post("/current", response_model=Current, summary="Obter informações atuais do clima", 
openapi_extra={
        "requestBody": {
            "description": "Nome da cidade",
            "required": True,
            "content": {
                "text/plain" : {
                    "schema": {
                        "type": "string",
                        "example": "Rio de Janeiro"
                    }
                }
            }           
        }
})
async def getCurrent(city: str = Body(..., media_type="text/plain")) -> Current: # O media_type indica que o corpo da requisição deve ser do tipo text/plain
                                                                                 # No swagger, o combo vai indicar que o corpo da requisição deve ser do tipo text/plain 

    latlong_obj = latlong.getLatLong(city) 

    latitude = latlong_obj["latitude"]
    longitude = latlong_obj["longitude"]

    try:
        current = CurrentRequest(latitude = latitude, longitude = longitude).getCurrent()

        return current

    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.post("/forecast", response_model=List[Forecast], summary="Obter previsão de 7 dias do clima", 
openapi_extra={
        "requestBody": {
            "description": "Nome da cidade",
            "required": True,
            "content": {
                "text/plain" : {
                    "schema": {
                        "type": "string",
                        "example": "Rio de Janeiro"
                    }
                }
            }           
        }
})
async def getForecast(city: str = Body(..., media_type="text/plain")) -> List[Forecast]: # O media_type indica que o corpo da requisição deve ser do tipo text/plain
                                                                                         # No swagger, o combo vai indicar que o corpo da requisição deve ser do tipo text/plain

    latlong_obj = latlong.getLatLong(city)

    latitude = latlong_obj["latitude"]
    longitude = latlong_obj["longitude"]

    try:
        forecast = ForecastRequest(latitude = latitude, longitude = longitude).getForecast()

        return forecast

    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.post("/alert", response_model=Alert, summary="Obter alerta de clima", 
openapi_extra={
        "requestBody": {
            "description": "Nome da cidade",
            "required": True,
            "content": {
                "text/plain" : {
                    "schema": {
                        "type": "string",
                        "example": "Rio de Janeiro"
                    }
                }
            }           
        }        
})
async def getAlert(city: str = Body(..., media_type="text/plain")) -> Alert: # O media_type indica que o corpo da requisição deve ser do tipo text/plain
                                                                             # No swagger, o combo vai indicar que o corpo da requisição deve ser do tipo text/plain

    latlong = LatLong().getLatLong(city)

    latitude = latlong["latitude"]
    longitude = latlong["longitude"]

    try:
        alert = AlertRequest(latitude = latitude, longitude = longitude).getAlert()

        return alert

    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)