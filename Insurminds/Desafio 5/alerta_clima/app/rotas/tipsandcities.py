from app.modelos.tipsandcities import Tips, Cities
from frontend.tipsandcities import TipsandCities
from app.rotas.request import router
from fastapi.exceptions import HTTPException

@router.get("/tips", response_model=Tips, summary="Obtém dicas de clima", response_description="5 dicas de clima para cada tipo de dica")
async def getTips() -> Tips:

    try:
        tipsandcities = TipsandCities()

        return tipsandcities.getTips()
    
    except Exception:
        raise HTTPException(status_code=500, detail="Não foi possível obter as dicas de clima. Reinicie a aplicação")
    

@router.get(
        "/cities", 
        response_model=Cities, 
        summary="Obtém cidades e suas siglas de estado", 
        response_description="Lista de cidades e suas respectivas siglas de estado"        
)
async def getCities() -> Cities:

    try:
        tipsandcities = TipsandCities()

        return tipsandcities.getCities()
    
    except Exception:
        raise HTTPException(status_code=500, detail="Não foi possível obter as cidades. Reinicie a aplicação")
    