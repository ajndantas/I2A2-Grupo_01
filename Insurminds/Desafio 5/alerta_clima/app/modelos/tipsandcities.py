from pydantic import BaseModel, Field
from typing import List, Dict

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
    
class Cities(BaseModel):
    cities_badges: List[Dict[str,str,['brasileira','global']]] = Field(description="lista das cidades, SOMENTE o nome da cidade, e a correspondente sigla e o seu tipo (brasileira ou global). Estado e sigla em maiusculas. Primeira letra da primeira e da última palavra da cidade em maiuscula")

    # MODIFICANDO O EXEMPLO DA RESPOSTA DO ENDPOINT NO SWAGGER
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "cities_badges": [
                        {"Rio de Janeiro": "RJ", "tipo": "brasileira"},
                        {"Los Angeles": "CA", "tipo": "global"},                        
                    ]
                }
            ]            
        }
    }

class TipsandCities(BaseModel):
    tips: Tips = Field(description="O dicionário de dicas, com cada tipo de dica e suas respectivas listas")
    cities_badges: Cities = Field(description="A lista de cidades, suas respectivas badges e tipos")