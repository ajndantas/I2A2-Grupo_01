from unittest.mock import Base

from pydantic import BaseModel, Field
from typing import List

class Tips(BaseModel):
    temp: List[str] = Field(description="lista de dicas relacionadas ao tipo variação de temperatura")
    tempest: List[str] = Field(description="lista de dicas relacionadas ao tipo tempestades")
    rain: List[str] = Field(description="lista de dicas relacionadas ao tipo chuva")
    wind: List[str] = Field(description="lista de dicas relacionadas ao tipo rajadas de vento")
    humidity: List[str] = Field(description="lista de dicas relacionadas ao tipo umidade relativa")
    uv: List[str] = Field(description="lista de dicas relacionadas ao tipo raios ultravioleta")
    eye: List[str] = Field(description="lista de dicas relacionadas ao tipo saúde ocular")
    fog: List[str] = Field(description="lista de dicas relacionadas ao tipo neblina")
    cold: List[str] = Field(description="lista de dicas relacionadas ao tipo frio")
    flood: List[str] = Field(description="lista de dicas relacionadas ao tipo inundação")


class City(BaseModel):
    cidade: str = Field(description="O nome da cidade. Primeira letra da primeira e da última palavra da cidade em maiuscula")
    badge: str = Field(description="A sigla")
    type: str = Field(description="O tipo de cidade, brasileira ou global")

class Cities(City):
    cities: List[City] = Field(description="lista das cidades")

    # MODIFICANDO O EXEMPLO DA RESPOSTA DO ENDPOINT NO SWAGGER
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "cities": [
                        {
                            "cidade": "Rio de Janeiro",
                            "badge": "RJ",
                            "type": "brasileira"
                        },
                        {
                            "cidade": "Londres",
                            "badge": "GB",
                            "type": "global"
                        }
                    ]
                }
            ]            
        }
    }

    class TipsandCities(Base):
        tips: Tips
        cities: Cities