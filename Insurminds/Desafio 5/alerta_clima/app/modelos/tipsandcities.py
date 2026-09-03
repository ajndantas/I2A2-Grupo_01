from pydantic import BaseModel, Field
from typing import List
from typing_extensions import TypedDict

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


#class City(BaseModel):
class City(TypedDict): #class City(BaseModel):
    city: str
    badge: str
    type: str

class Cities(BaseModel):
    cities: List[City] = Field(description="lista de cidades e seus atributos")

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


class TipsandCities(BaseModel):
    tips: Tips = Field(description="lista de dicas para cada tipo")
    cities: Cities = Field(description="lista das cidades e seus atributos")