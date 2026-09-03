from fastapi import Body, HTTPException, APIRouter, Request, Depends
from app.request import CurrentRequest, ForecastRequest, AlertRequest
from app.modelos.current import Current
from app.latlong import LatLong
from app.modelos.forecast import Forecast
from app.modelos.alert import Alert
from typing import List
from functools import lru_cache

from httpx import get 

router = APIRouter(
    prefix="/api/v1"
)

# latlong = LatLong() # TODA HORA QUE O PROGRAMA PRECISAR DE UMA ROTA, ELE VAI CHAMAR O LATLONG. ISSO ESTAVA QUEBRANDO O DEPLOY NA GCP

@lru_cache # ISSO EVITA QUE O LATLONG SEJA CRIADO VÁRIAS VEZES. É COMO SE FOSSE UM SINGLETON
           # LRU significa Least Recently Used
def getLatLong():
    return LatLong()

@router.get(
    "/current",
    response_model=Current,
    summary="Obter informações atuais do clima",
    description="Retorna a previsão meteorológica atual para a cidade informada."
)
async def getCurrent(request: Request, latlong: LatLong = Depends(getLatLong)) -> Current: 
    try:

        city = request.session.get('city', None)

        if city is None: 
            raise HTTPException(status_code=500, detail="Nenhuma cidade informada")
        
        latlong_obj = latlong.getLatLong(city) 
        
        latitude = latlong_obj["latitude"]
        longitude = latlong_obj["longitude"]
        
        current = CurrentRequest(latitude = latitude, longitude = longitude).getCurrent()

        return current

    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.get(
    "/forecast",
    response_model=List[Forecast],
    summary="Obter previsão de 7 dias do clima",
    description="Retorna a previsão do tempo para os próximos 7 dias da cidade informada."
)
async def getForecast(request: Request, latlong: LatLong = Depends(getLatLong)) -> List[Forecast]: 

    try:
        city = request.session.get('city', None)

        if city is None: 
            raise HTTPException(status_code=500, detail="Nenhuma cidade informada")

        latlong_obj = latlong.getLatLong(city)

        latitude = latlong_obj["latitude"]
        longitude = latlong_obj["longitude"]
    
        forecast = ForecastRequest(latitude = latitude, longitude = longitude).getForecast()

        return forecast

    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.get(
    "/alert",
    response_model=Alert,
    summary="Obter alerta de clima",
    description="Retorna os alertas meteorológicos relevantes para a cidade informada."    
)
async def getAlert(request: Request, latlong: LatLong = Depends(getLatLong)) -> Alert:

    try:
        city = request.session.get('city', None)

        if city is None: 
            raise HTTPException(status_code=500, detail="Nenhuma cidade informada")
        
        latlong_obj = latlong.getLatLong(city)

        latitude = latlong_obj["latitude"]
        longitude = latlong_obj["longitude"]
    
        alert = AlertRequest(latitude = latitude, longitude = longitude).getAlert()

        return alert

    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.post(
    "/city",
    summary="Rota para obter a cidade",
    description="Armazena a cidade informada na sessão do usuário para que as próximas interações da aplicação utilizem esse valor.",
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                "text/plain": {
                    "schema": {"type": "string"},
                    "example": "Rio de Janeiro"
                }
            }
        }
    }    
)
async def setCity(request: Request, city: str = Body(..., media_type="text/plain")) -> str: # O media_type no Body, indica que o 
                                                                                            # corpo da requisição deve ser do tipo 
                                                                                            # text/plain
                                                                                            #
                                                                                            # No swagger, o combo vai indicar que 
                                                                                            # o corpo da requisição deve ser do 
                                                                                            # tipo text/plain 

    request.session['city'] = city

    return f"Cidade armazenada: {city}"