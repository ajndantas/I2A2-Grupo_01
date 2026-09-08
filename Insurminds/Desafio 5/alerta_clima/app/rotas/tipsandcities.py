from app.modelos.tipsandcities import Tips as TipsModel, City
from frontend.tipsandcities import Tips as TipsService, Cities as CitiesService
from app.rotas.request import router
from fastapi.exceptions import HTTPException
from fastapi import Depends
from typing import List


@router.get(
                "/tips", 
                response_model=TipsModel, 
                summary="Obtém dicas de clima", 
                response_description="3 dicas de clima para cada tipo de dica"                
)
async def getTips(tips: TipsService = Depends(TipsService)) -> TipsModel:

    try:
        return tips.getTips()
    
    except Exception:
        raise HTTPException(status_code=500, detail="Não foi possível obter as dicas de clima. Reinicie a aplicação")
    

@router.get(
            "/cities", 
            response_model=List[City], 
            summary="Obtém cidades e suas siglas de estado", 
            response_description="Lista de cidades e seus atributos"        
)
async def getCities(cities: CitiesService = Depends(CitiesService)) -> List[City]:

    try:
        return cities.getCities()
    
    except Exception:
        raise HTTPException(status_code=500, detail="Não foi possível obter as cidades. Reinicie a aplicação")
    