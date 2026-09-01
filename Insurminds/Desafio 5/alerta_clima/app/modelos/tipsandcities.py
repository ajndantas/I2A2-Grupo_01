from pydantic import BaseModel, Field
from typing import List, Dict

class Tips(BaseModel):
    temp: List[str] = Field(description="lista de 5 dicas relacionadas a variação de temperatura")
    rain: List[str] = Field(description="lista de 5 dicas relacionadas a chuva")
    wind: List[str] = Field(description="lista de 5 dicas relacionadas a rajadas de vento")
    humidity: List[str] = Field(description="lista de 5 dicas relacionadas a umidade relativa")
    eye: List[str] = Field(description="lista de 5 dicas relacionadas a saúde ocular")
    
class Cities(BaseModel):
    brcities: List[str] = Field(description="lista das cidades brasileiras. Primeira palavra e a última em maiuscula")
    worldcities: List[str] = Field(description="lista das cidades do mundo. Primeira palavra e a última em maiuscula")

class TipsandCities(BaseModel):
    tips: Dict[str,Tips] = Field(description="dicas")
    cities: Dict[str,Cities] = Field(description="cidades")