from fastapi import APIRouter, File, UploadFile, Depends
from pydantic import BaseModel
import random
from magic import from_buffer 
from app.modelos.datasetquery import DatasetQuery
from app.agente_rag import AgenteRag
from app.motor_ocr_otimizado import NotaFiscalOCR
from os import makedirs, listdir
from pathlib import Path
import shutil
import json

ENV_PATH = (
                 Path(__file__) # O CAMINHO DO ARQUIVO ATUAL
                .resolve() # RESOLVE O CAMINHO ABSOLUTO
                .parent # RETORNA O CAMINHO DA PASTA PAI DO ARQUIVO ATUAL
                .parent # RETORNA O CAMINHO DA PASTA PAI DO ARQUIVO ATUAL
            )

#print("ENV_PATH: ", ENV_PATH)

router = APIRouter(
    prefix="/api/datasets"
)


datasets = {} # Dicionário para armazenar os datasets. Localizado aqui, para ser acessado em todas as rotas

class DatasetQuery(BaseModel):
    question: str

@router.post("/upload")
async def upload(file: UploadFile = File(...), ocr = Depends(NotaFiscalOCR)):

    random_number = str(random.randint(1,9999)).zfill(3)    
    dataset_id = f'ds_{random_number}'

    print("dataset_id: ", dataset_id)
    
    datasets[dataset_id] = await file.read()
    uploaded_file = datasets.get(dataset_id)
    filename = file.filename
   
    file_type = from_buffer(uploaded_file, mime=True)
    print("Filetype: ",file_type)    

    if "rag_docs" in listdir(f"{ENV_PATH}"):
        shutil.rmtree(f"{ENV_PATH}/rag_docs")

    makedirs(f"{ENV_PATH}/rag_docs", exist_ok=True)

    extracted_text = ""

    if file_type not in ["text/plain", "text/csv"]: # Se o arquivo for PDF ou imagem, o OCR irá extrair o texto
        extracted_text = ocr.main(uploaded_file)

        with open(f"{ENV_PATH}/rag_docs/extracted_text.txt", "w", encoding="utf-8") as f: # Grava o texto extraído no arquivo
            f.write(extracted_text)

    else: # Se o arquivo for CSV ou TXT, o texto é lido diretamente do arquivo
        with open(f"{ENV_PATH}/rag_docs/{filename}", "r") as f2:
            extracted_text = f2.read()

        with open(f"{ENV_PATH}/rag_docs/extracted_text.txt", "w", encoding="utf-8") as f: # Grava o texto extraído no arquivo chamado "extracted_text.txt"
            f.write(extracted_text)

    # Fornece o dataset_id para o frontend e para preparar a proxima rota
    return {
                "dataset_id": dataset_id, 
                "status": "ready",
                "name": filename
            }        
    
@router.post("/{dataset_id}/query")
async def query_dataset(dataset_id: str, payload: DatasetQuery, ag = Depends(AgenteRag)): # O segundo parâmetro é o payload e não
                                                                                          # deve ser de tipo primitivo, porque o 
                                                                                          # frontend irá enviar no CORPO do JSON.
                                                                                          #
                                                                                          # Também poderia ser question: str = Body[...]        
    

    answer = json.loads(ag.query(payload.question))
    
    print("Pergunta: ", payload.question, "Resposta: ", answer['resposta'])


    return {
        "dataset_id": dataset_id,
        "type": answer['tipo'],
        "request": payload.question,
        "status": "ready",
        "answer": answer['resposta']
    }  