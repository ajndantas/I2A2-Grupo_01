# Use uma imagem Python oficial e leve como base
FROM python:3.11-slim

# Defina variáveis de ambiente para evitar prompts interativos durante a instalação
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Defina o argumento de construção para a API_KEY e configure-o como uma variável de ambiente
#ARG API_KEY

# O ARG é apenas para o processo de construção da imagem. Para que a variável de ambiente esteja disponível em tempo de execução, precisamos copiá-la para um ENV.
#ENV API_KEY=${API_KEY} 

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
COPY requirements_linux.txt .

# Instale o Jupyter Notebook para converter o notebook em script Python
RUN pip install --no-cache-dir jupyter

# Copie o restante do código da sua aplicação para o diretório de trabalho

COPY agente_nfe.ipynb .

# Converte o notebook para script Python
RUN jupyter nbconvert --to script agente_nfe.ipynb

COPY motor_ocr_otimizado.py .

# Instale os pacotes Python
RUN pip install --no-cache-dir -r requirements_linux.txt

# Exponha a porta 8000 para permitir a comunicação com a aplicação Streamlit
EXPOSE 8000

# Defina o comando para executar a aplicação
# Adicionadas flags para lidar com CORS e XSRF, comuns ao rodar em contêineres
CMD ["streamlit", "run", "agente_nfe.py", "--server.port", "8000", "--server.enableCORS", "false", "--server.enableXsrfProtection", "false"]

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