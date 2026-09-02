from app.modelos.tipsandcities import Tips, Cities
from frontend.tipsandcities import TipsandCities
from app.rotas.request import router

@router.get("/tips", response_model=Tips, summary="Obtém dicas de clima", response_description="5 dicas de clima para cada tipo de dica")
async def getTips() -> Tips:

    tipsandcities = TipsandCities()

    return tipsandcities.getTips()    

@router.get("/cities", response_model=Cities, summary="Obtem cidades", response_description="Lista de cidades")
async def getCities() -> Cities:

    tipsandcities = TipsandCities()

    return tipsandcities.getCities()
    