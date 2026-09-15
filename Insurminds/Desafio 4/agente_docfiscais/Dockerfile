# Use uma imagem Python oficial e leve como base
FROM python:3.11-slim

# Defina variáveis de ambiente para evitar prompts interativos durante a instalação
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Tesseract para OCR, Poppler para processamento de PDF, e libmagic para detecção de tipo de arquivo
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-por \
    poppler-utils \
    file \
    libmagic1 \
    curl \
    build-essential \
    #libgl1-mesa-glx \ # DEVIDO A VERSÃO DO UBUNTU DO YAML docker-image.yml
    libgl1 \
    libglx-mesa0 \
 && rm -rf /var/lib/apt/lists/*

# Defina o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copie o arquivo de dependências Python para o diretório de trabalho
# É assumido que um arquivo requirements.txt existe no seu projeto
COPY requirements.txt .


# Copie o restante do código da sua aplicação para o diretório de trabalho
COPY app/ .
COPY frontend/ .

# Instale os pacotes Python
RUN pip install --no-cache-dir -r requirements.txt

ARG API_KEY_OPENROUTER
ENV API_KEY_OPENROUTER=${API_KEY_OPENROUTER}
ARG API_KEY
ENV API_KEY=${API_KEY}

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# EXECUTAR O DOCKER COM: 
# Para baixar do GITHUB -> docker pull ghcr.io/ajndantas/agente_nfs:latest
# Executar como -> docker run -d -p 8000:8000 ghcr.io/ajndantas/agente_nfs
#
# ❗ Importante:
# SE FOR FAZER O BUILD LOCAL, RODAR docker build --build-arg API_KEY=abc123 -t minha-imagem .

# SE FOR E X E C U T A R O BUILD LOCAL. MANEIRA MAIS SEGURA DE PASSAR AS VARIÁVEIS DE AMBIENTE PARA O CONTAINER É USANDO UM ARQUIVO .env
# docker run -d --env-file .env -p 8000:8000 --name bi_corporativo_csv minha-imagem

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
#
# Passar como --build-args em docker build, substitui ter os parâmetros abaixo no Dockerfile ?

# ARG API_KEY_OPENROUTER
# ENV API_KEY_OPENROUTER=${API_KEY_OPENROUTER}
# ARG API_KEY
# ENV API_KEY=${API_KEY}
# Explicando a diferença entre build-args e ARG/ENV no Docker.
# Explicando a diferença entre build-args e ARG/ENV no Docker.
# Não exatamente — são coisas complementares, não substitutas uma da outra. Deixa eu detalhar:

# O que cada coisa faz
# ARG no Dockerfile: declara que existe uma variável que pode ser recebida durante o build (via --build-arg). Sem essa declaração no Dockerfile, o --build-arg que você passar na linha de comando é ignorado (o Docker até avisa: "one or more build-args were not consumed").
# --build-arg no docker build: fornece o valor para um ARG já declarado no Dockerfile.
# ENV: torna a variável disponível dentro do container em runtime, não só durante o build.