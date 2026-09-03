from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from app.rotas import request, tipsandcities
from starlette.middleware.sessions import SessionMiddleware


load_dotenv()

app = FastAPI(
    title="Alerta de clima",
    description="API de alerta de clima",
    version="0.0.1"
)

app.mount("/frontend", StaticFiles(directory="frontend"), name="alerta_clima")
app.mount("/css", StaticFiles(directory="frontend/css"), name="css")
app.mount("/js", StaticFiles(directory="frontend/js"), name="js")

app.include_router(request.router)
app.include_router(tipsandcities.router)

app.add_middleware(SessionMiddleware, secret_key="super-secret-key")

# Rota para acessar a página HTML do frontend
@app.get(
    "/",
    response_class=HTMLResponse,
    summary="Rota para acessar a página HTML",
    description="""Rota para acessar a página HTML do frontend. Solicita a cidade ao usuário. O usuário informa a cidade, a aplicação executa a rota /api/v1/city e, em seguida, exibe o menu com as opções:

1. Previsão atual — chama /api/v1/current e exibe a previsão atual. Ao final, carrega o menu com essas opções
2. Previsão dos próximos 7 dias — chama /api/v1/forecast e mostra a previsão semanal. Ao final, carrega o menu com essas opções
3. Trocar cidade — digita nova cidade e chama /api/v1/city. Ao final, carrega o menu com essas opções
4. Sair — limpa o chat e recarrega a página para informar a cidade novamente."""
)
async def frontend():
    return HTMLResponse(content=open("frontend/index.html", "r", encoding="utf-8").read(), status_code=200)

