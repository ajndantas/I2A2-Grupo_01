# Use uma imagem Python oficial e leve como base
FROM python:3.12-slim

# Defina variáveis de ambiente para evitar prompts interativos durante a instalação
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Defina o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copie o arquivo de dependências Python para o diretório de trabalho
# É assumido que um arquivo requirements.txt existe no seu projeto
COPY requirements.txt .

COPY agente_chatbotseguro.py .

# Copie os arquivos de dados para o contêiner.
COPY rag_docs/ ./rag_docs/
COPY rag_docs/Dúvidas\ frequentes\ sobre\ os\ seguros\ _ Zurich.html ./rag_docs/Dúvidas\ frequentes\ sobre\ os\ seguros\ _ Zurich.html

# Instale os pacotes Python
RUN pip install --no-cache-dir -r requirements.txt

# Exponha a porta 8000 para permitir a comunicação com a aplicação Streamlit
EXPOSE 8002

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