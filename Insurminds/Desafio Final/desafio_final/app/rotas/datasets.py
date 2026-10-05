from fastapi import APIRouter, File, UploadFile, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel
from app.modelos.datasetquery import DatasetQuery
from app.modelos.outputschema import OutputSchema
from app.motor_ocr_otimizado import NotaFiscalOCR
from pathlib import Path
from functools import lru_cache
from typing import List
from fastapi import Request, HTTPException
from uuid import uuid4


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


#datasets = {} # Dicionário para armazenar os datasets identificados pelos dataset_ids. Localizado aqui, para ser acessado em todas as rotas

contexts_by_session = {}

class DatasetQuery(BaseModel):
    question: str

@router.get("/sessions/new", summary="Iniciar uma nova sessão")
async def new_session(request: Request):
    """Chamado pelo botão 'Nova análise': descarta a sessão atual (e seus datasets) e cria uma nova."""

    contexts_by_session.pop(request.session.get("session_id"), None)

    request.session.clear()

    request = RedirectResponse(url="/", status_code=300)
    
    return request


@router.post("/uploads")
async def uploads(request: Request, files: List[UploadFile] = File(...), ocr = Depends(NotaFiscalOCR)):

    from magic import from_buffer 
    import random

    dataset_ids = []
    context = {}

    for file in files:

        random_number = str(random.randint(1,9999)).zfill(3)    
        dataset_id = f'ds_{random_number}'

        print("dataset_id: ", dataset_id)
        print("filename: ", file.filename)
    
        dataset_ids.append(dataset_id)
        uploaded_file = await file.read()

        filename = file.filename
        
        file_type = from_buffer(uploaded_file, mime=True)
        print("Filetype: ",file_type)

        if file_type not in ["text/plain", "text/csv"]: # Se o arquivo for PDF ou imagem, o OCR irá extrair o texto

            try:
                document_text = ocr.main(uploaded_file)

            except HTTPException as e:
                raise HTTPException(status_code=e.status_code, detail=str(e))


        else: # Se o arquivo for CSV ou TXT, o texto é lido diretamente da memória
            document_text = uploaded_file.decode("utf-8")

        context[filename] = document_text

    session_id = request.session.get("session_id") or uuid4().hex
    request.session["session_id"] = session_id
    contexts_by_session[session_id] = context
    request.session["dataset_ids"] = dataset_ids # Armazena os dataset_ids na sessão do request
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
            response_model=OutputSchema,
            response_description="""
                                    type: ['text','table','chart','mixed']\n
                                    table: "Quando 'type' for 'table' ou 'mixed', informe as linhas e nome das colunas, do contrário, não informar"\n
                                    chart: "Quando 'type' for 'chart' ou 'mixed', informe os labels e datasets, do contrário, não informar
                                 """
        )
async def query_dataset(request: Request, payload: DatasetQuery, ag = Depends(getAgenteRag)) -> OutputSchema: # O segundo parâmetro é o payload e não
                                                                                              # deve ser de tipo primitivo, porque o 
                                                                                              # frontend irá enviar no CORPO do JSON.
                                                                                              #
    import json                                                                               # Também poderia ser question: str = Body[...]        


    session_id = request.session.get("session_id")
    context = contexts_by_session.get(session_id)
    if context is None:
        raise HTTPException(status_code=500, detail="Envie os documentos novamente para iniciar a análise.")

    answer = json.loads(ag.query(question=payload.question, context=context))
    
    if answer["type"] == "table":
        output = OutputSchema(answer=answer["answer"], type=answer["type"], table=answer["table"], chart=None)
        
    elif answer["type"] == "chart":
        output = OutputSchema(answer=answer["answer"], type=answer["type"], table=None, chart=answer["chart"])
        
    elif answer["type"] == "mixed":
        output = OutputSchema(answer=answer["answer"], type=answer["type"], table=answer["table"], chart=answer["chart"])
        
    elif answer["type"] == "text":
        output = OutputSchema(answer=answer["answer"], type=answer["type"], table=None, chart=None)

    output.model_dump(exclude_none=True) # Remove os campos nulos da resposta
    
    #print("Pergunta: ", payload.question, "Resposta: ", answer['resposta'])


    return output