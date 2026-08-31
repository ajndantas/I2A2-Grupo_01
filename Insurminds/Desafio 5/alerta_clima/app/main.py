from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from app.rotas import request


load_dotenv()

app = FastAPI(
    title="Alerta de clima",
    description="API de alerta de clima",
    version="0.0.1"
)

app.mount("/frontend", StaticFiles(directory="frontend"), name="alerta_clima")
app.include_router(request.router)

# Rota para acessar a página HTML do frontend
@app.get("/", response_class=HTMLResponse, summary="Rota para acessar a página HTML do frontend")
async def frontend():
    return HTMLResponse(content=open("frontend/index.html", "r", encoding="utf-8").read(), status_code=200)