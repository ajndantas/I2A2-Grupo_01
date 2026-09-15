from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from app.rotas import datasets

app = FastAPI()

app.mount("/css", StaticFiles(directory="frontend/css"), name="css")
app.mount("/js", StaticFiles(directory="frontend/js"), name="js")

app.include_router(datasets.router)

"""
allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000"
        "https://ENDERECO-PUBLICADO-DO-FRONTEND"
    ],"""

""" app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://agente-nfs-574973424283.us-central1.run.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
) """

@app.get("/", response_class=HTMLResponse)
async def frontpage():

    return HTMLResponse(content=open("frontend/index.html", "r", encoding="utf-8").read(), status_code=200)


