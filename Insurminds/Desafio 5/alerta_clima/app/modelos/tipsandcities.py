from pydantic import BaseModel, Field
from typing import List, Dict

class Tips(BaseModel):
    temp: List[str] = Field(description="lista de 5 dicas relacionadas a variação de temperatura")
    tempest: List[str] = Field(description="lista de 5 dicas relacionadas a tempestades")
    rain: List[str] = Field(description="lista de 5 dicas relacionadas a chuva")
    wind: List[str] = Field(description="lista de 5 dicas relacionadas a rajadas de vento")
    humidity: List[str] = Field(description="lista de 5 dicas relacionadas a umidade relativa")
    uv: List[str] = Field(description="lista de 5 dicas relacionadas a raios ultravioleta")
    eye: List[str] = Field(description="lista de 5 dicas relacionadas a saúde ocular")
    fog: List[str] = Field(description="lista de 5 dicas relacionadas a neblina")
    cold: List[str] = Field(description="lista de 5 dicas relacionadas a frio")
    flood: List[str] = Field(description="lista de 5 dicas relacionadas a inundação")
    
class Cities(BaseModel):
    cities_badges: List[Dict[str,str]] = Field(description="lista das cidades, SOMENTE o nome da cidade, e a correspondente sigla de seu estado, estado em maiuscula. Primeira letra da primeira e da última palavra da cidade em maiuscula")
    
class TipsandCities(BaseModel):
    tips: Tips = Field(description="O dicionário de dicas, com cada dica e suas respectivas listas")
    cities_badges: Cities = Field(description="A lista de cidades e suas respectivas badges")