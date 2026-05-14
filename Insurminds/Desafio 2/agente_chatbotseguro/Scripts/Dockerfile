# Use uma imagem Python oficial e leve como base
FROM python:3.13-slim
#FROM python:3.13-alpine

# Defina variáveis de ambiente para evitar prompts interativos durante a instalação
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Defina o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copie o arquivo de dependências Python para o diretório de trabalho
# É assumido que um arquivo requirements.txt existe no seu projeto
COPY requirements.txt .

COPY agente_chatbotseguro.py .
COPY app.py .

# Copie os arquivos de dados para o contêiner.
COPY rag_docs/ ./rag_docs/

# Instale os pacotes Python
RUN pip install --no-cache-dir -r requirements.txt

# DOWNLOAD DO MODELO DE EMBEDDING LOCALMENTE
#
# AS DUAS LINHAS ABAIXO TÊM A FUNÇÃO DE BAIXAR O MODELO DE EMBEDDING LOCALMENTE. FEZ-SE ISSO PARA EVITAR QUE O MODELO TENHA QUE SER BAIXADO TODA VEZ QUE O CONTÊINER FOR INICIADO E 
# PELO FATO DE NÃO TER QUE ENVIAR O MODELO PARA O GITHUB POR SER MUITO GRANDE.
COPY huggingface_models_download.py .
RUN python huggingface_models_download.py

# WARM UP DE CRIAÇÃO DO BANCO DE DADOS VETORIAL - PASTA CACHE
ARG API_KEY_OPENROUTER
ENV API_KEY_OPENROUTER=$API_KEY_OPENROUTER
RUN python agente_chatbotseguro.py

# Defina o comando para executar a aplicação
# Adicionadas flags para lidar com CORS e XSRF, comuns ao rodar em contêineres
# CMD ["streamlit", "run", "agente_chatbotseguro.py", "--server.port", "8002", "--server.enableCORS", "false", "--server.enableXsrfProtection", "false"]

# EXECUTAR O DOCKER COM: 
# Para baixar do GITHUB -> docker pull ghcr.io/ajndantas/agente_nfs:latest
# Executar como -> docker run -d -p 8000:8000 ghcr.io/ajndantas/agente_nfs
#
# SE FOR FAZER O BUILD LOCAL, RODAR docker build --build-arg API_KEY=abc123 -t minha-imagem .
# ❗ Importante:

# SE FOR EXECUTAR O BUILD LOCAL. MANEIRA MAIS SEGURA DE PASSAR AS VARIÁVEIS DE AMBIENTE PARA O CONTAINER É USANDO UM ARQUIVO .env
# docker run -d --env-file .env -p 8000:8000 --name bi_corporativo_csv minha-imagem

# Depois que o build termina, o ARG não existe mais dentro do container — a menos que você copie ele para um ENV.

# 🔹 O que faz ENV?
# ENV API_KEY=${API_KEY}
# ✅ O que é:

# ENV define uma variável de ambiente permanente dentro da imagem.

# Ela:

# Fica salva na imagem

# Fica disponível quando o container roda

# Pode ser acessada no Python via:

# import os
# os.getenv("API_KEY")