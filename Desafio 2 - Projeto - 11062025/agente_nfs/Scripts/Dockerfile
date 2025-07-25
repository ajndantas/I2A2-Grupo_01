# Use uma imagem Python oficial e leve como base
FROM python:3.11-slim

# Defina variáveis de ambiente para evitar prompts interativos durante a instalação
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

ARG GOOGLE_API_KEY
ENV GOOGLE_API_KEY=${GOOGLE_API_KEY}

# Tesseract para OCR, Poppler para processamento de PDF, e libmagic para detecção de tipo de arquivo
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-por \
    poppler-utils \
    file \
    libmagic1 \
    curl \
    build-essential \
    libgl1-mesa-glx \
 && rm -rf /var/lib/apt/lists/*

# Defina o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copie o arquivo de dependências Python para o diretório de trabalho
# É assumido que um arquivo requirements.txt existe no seu projeto
COPY requirements_linux.txt .

# Copie o restante do código da sua aplicação para o diretório de trabalho
COPY agente_nfs.py .
COPY motor_ocr_otimizado.py .

# Instale os pacotes Python
RUN pip install --no-cache-dir -r requirements_linux.txt

# Exponha a porta 8000 para permitir a comunicação com a aplicação Streamlit
EXPOSE 8000

# Defina o comando para executar a aplicação
# Adicionadas flags para lidar com CORS e XSRF, comuns ao rodar em contêineres
CMD ["streamlit", "run", "agente_nfs.py", "--server.port", "8000", "--server.enableCORS", "false", "--server.enableXsrfProtection", "false"]

# EXECUTAR O DOCKER COM: 
# Para baixar -> docker pull ghcr.io/ajndantas/agente_nfs:latest
# Para executar -> docker run -p 8000:8000 -e GOOGLE_API_KEY="AIzaSyAOhPIBGBJyhmQFGwcuMxGqS0MniA_7TQ8" ghcr.io/ajndantas/agente_nfs
# Tentar executar como -> docker run -p 8000:8000 --restart unless-stopped ghcr.io/ajndantas/agente_nfs