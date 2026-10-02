from fastapi import APIRouter, File, UploadFile, Depends
from pydantic import BaseModel
from app.modelos.datasetquery import DatasetQuery
from app.modelos.outputschema import OutputSchema
from app.motor_ocr_otimizado import NotaFiscalOCR
from pathlib import Path
from functools import lru_cache
from typing import List
from fastapi import Request

""" 
    Modifique os códigos de app.zip e frontend.zip, para que as seguintes ações possam ser realizadas:

    1 - Possa ser feito o upload de mais de um arquivo 
    2 - Ao se realizar o upload, possa ser associado um dataset para cada um deles, aonde esse dataset_id é gerado pelo código dataset.py, endpoint/api/datasets/uploads
    3 - No momento em que a pergunta foi submetida, os dataset_ids que foram gerados, sejam enviados para o endpoint "/{dataset_ids}/query" 
"""

ENV_PATH = (
                 Path(__file__) # O CAMINHO DO ARQUIVO ATUAL
                .resolve() # RESOLVE O CAMINHO ABSOLUTO
                .parent # RETORNA O CAMINHO DA PASTA PAI DO ARQUIVO ATUAL
                .parent # RETORNA O CAMINHO DA PASTA PAI DO ARQUIVO ATUAL
            )

#print("ENV_PATH: ", ENV_PATH)

@lru_cache
def getAgenteRag():

    from app.agente_rag import AgenteRag
    
    return AgenteRag()


router = APIRouter(
    prefix="/api/datasets"
)


datasets = {} # Dicionário para armazenar os datasets identificados pelos dataset_ids. Localizado aqui, para ser acessado em todas as rotas
extracted_text = {}
context = {}

class DatasetQuery(BaseModel):
    question: str

@router.post("/uploads")
async def uploads(request: Request, files: List[UploadFile] = File(...), ocr = Depends(NotaFiscalOCR)):

    from magic import from_buffer 
    import random

    for file in files:

        random_number = str(random.randint(1,9999)).zfill(3)    
        dataset_id = f'ds_{random_number}'

        print("dataset_id: ", dataset_id)
    
        datasets[dataset_id] = await file.read()
        uploaded_file = datasets.get(dataset_id) # EM MEMÓRIA

        filename = file.filename
        
        file_type = from_buffer(uploaded_file, mime=True)
        print("Filetype: ",file_type)

        if file_type not in ["text/plain", "text/csv"]: # Se o arquivo for PDF ou imagem, o OCR irá extrair o texto
            extracted_text[dataset_id] = ocr.main(uploaded_file)        

        else: # Se o arquivo for CSV ou TXT, o texto é lido diretamente da memória
            extracted_text[dataset_id] = uploaded_file.decode("utf-8")

        context[filename] = extracted_text[dataset_id]

    request.session["dataset_ids"] = list(datasets.keys()) # Armazena os dataset_ids na sessão do request
    request.session["filenames"] = list(context.keys()) # Armazena os filenames na sessão do request

    return {
                "dataset_ids": request.session.get("dataset_ids"), 
                "status": "ready",
                "filenames": request.session.get("filenames")
            }


@router.post(
            "/{dataset_ids}/query",
            summary="Consultar datasets",
            description=(
                "Informe os IDs dos datasets separados por vírgula no caminho. "
                "Exemplo: `/api/datasets/ds_123,ds_456/query`."
            ),
            response_model=OutputSchema
        ) # Dataset_ids recebe uma string com os dataset_ids separados por vírgula
async def query_dataset(payload: DatasetQuery, ag = Depends(getAgenteRag)) -> OutputSchema: # O segundo parâmetro é o payload e não
                                                                                              # deve ser de tipo primitivo, porque o 
                                                                                              # frontend irá enviar no CORPO do JSON.
                                                                                              #
    import json                                                                               # Também poderia ser question: str = Body[...]        

        
    answer = json.loads(ag.query(question=payload.question, context=context))

    if answer.type == "table":
        output = OutputSchema(answer=answer.answer, type=answer.type, columns=answer.table.columns, rows=answer.table.rows, chart=None)
        
    elif answer.type == "chart":
        output = OutputSchema(answer=answer.answer, type=answer.type, columns=answer.chart.labels, datasets=answer.chart.datasets, table=None)
        
    elif answer.type == "mixed":
        output = OutputSchema(answer=answer.answer, type=answer.type, columns=answer.table.columns, rows=answer.table.rows, chart=answer.chart)
        
    elif answer.type == "text":
        output = OutputSchema(answer=answer.answer, type=answer.type, table=None, chart=None)

    output.model_dump(exclude_none=True) # Remove os campos nulos da resposta
    
    #print("Pergunta: ", payload.question, "Resposta: ", answer['resposta'])

    datasets.clear()
    context.clear()

    return output