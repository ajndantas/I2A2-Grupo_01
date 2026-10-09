from pydantic import BaseModel, Field
from typing import Literal, List

class TableSchema(BaseModel):
    columns: List[str] = Field(description="Informe columns na ordem em que aparecem na tabela")
    rows: List[List[str]] = Field(description="Informe os dados como uma lista de listas: cada lista interna representa uma linha, e seus valores devem seguir a mesma ordem de 'columns'")

class DatasetSchema(BaseModel):
    label: str = Field(description="Informe o label para o dataset")
    data: List[float] = Field(description="Informe os dados para o dataset")

class ChartSchema(BaseModel):
    type: Literal['bar','doughnut'] = Field(description="Informe type 'bar' para gráfico de barras ou 'doughnut' para gráfico de rosca")
    labels: List[str] = Field(description="Informe os labels para o gráfico")
    datasets: List[DatasetSchema] = Field(description="Informe os datasets para o gráfico")

class OutputSchema(BaseModel):
    answer: str = Field(description="A resposta para a pergunta no formato texto")
    type: Literal['text','table','chart','mixed'] = Field(description="Classifique o conteúdo da resposta: use 'text' quando houver apenas texto; 'table' quando houver texto e uma tabela; 'chart' quando houver texto e um gráfico; e 'mixed' quando houver texto, tabela e gráfico.")
    table: TableSchema|None = Field(description="Quando 'type' for 'table' ou 'mixed', informe as linhas e nome das colunas, do contrário, não informar")
    chart: ChartSchema|None = Field(description="Quando 'type' for 'chart' ou 'mixed', informe os labels e datasets, do contrário, não informar")