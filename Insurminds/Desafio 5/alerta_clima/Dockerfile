# Use uma imagem Python oficial e leve como base
FROM python:3.13-slim

# Defina variáveis de ambiente para evitar prompts interativos durante a instalação
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Defina o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copie o arquivo de dependências Python para o diretório de trabalho
COPY requirements.txt . 

# Copie os scripts para o contêiner.
COPY app/ ./app/
COPY frontend/ ./frontend/ 

RUN pip install --no-cache-dir -r requirements.txt

ARG API_KEY_OPENROUTER
ENV API_KEY_OPENROUTER=${API_KEY_OPENROUTER}
ARG API_KEY
ENV API_KEY=${API_KEY}

# Exponha a porta 8002 para o acesso externo
EXPOSE 8003

# Inicie o servidor FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]