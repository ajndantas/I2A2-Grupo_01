from app.rotas.request import router
from fastapi import Request
from typing import Dict
from app.modelos.tips import Tips
from app.modelos.cities import Cities
from frontend.tipsandcities import TipsandCities

tipsandcities = TipsandCities()

@router.get("/tips", response_model=Dict[Tips])
async def getTips(request: Request):
    pass


@router.get("/cities", response_model=Dict[Cities])
async def getCities(request: Request):
    pass
    