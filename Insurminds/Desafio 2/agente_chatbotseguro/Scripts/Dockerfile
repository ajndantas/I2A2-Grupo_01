# Use uma imagem Python oficial e leve como base
FROM python:3.13-slim

# Defina variáveis de ambiente para evitar prompts interativos durante a instalação
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Defina o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copie o arquivo de dependências Python para o diretório de trabalho
# É assumido que um arquivo requirements.txt existe no seu projeto
COPY requirements.txt .
COPY agente_chatbotseguro.py app.py . 

# Copie os arquivos de dados para o contêiner.
COPY rag_docs/ ./rag_docs/ 

# Instale os pacotes Python globalmente no builder (REMOVIDO O --user)
# Sem o --user, o pip compila e vincula corretamente as extensões C/Rust (como _pydantic_core)
# AGORA NÃO PRECISAMOS MAIS DO PYTHONPATH, POIS AS EXTENSÕES C/RUST ESTARÃO CORRETAMENTE VINCULADAS NA PASTA GLOBAL DE PACOTES DO PYTHON (site-packages) DO BUILDER.
RUN pip install --no-cache-dir -r requirements.txt

# DOWNLOAD DO MODELO DE EMBEDDING LOCALMENTE
# AS LINHAS ABAIXO TÊM A FUNÇÃO DE BAIXAR O MODELO DE EMBEDDING LOCALMENTE.
COPY huggingface_models_download.py . 

RUN python huggingface_models_download.py

# WARM UP DE CRIAÇÃO DO BANCO DE DADOS VETORIAL - PASTA CACHE
ARG API_KEY_OPENROUTER
ENV API_KEY_OPENROUTER=$API_KEY_OPENROUTER
RUN python agente_chatbotseguro.py

EXPOSE 8002

CMD ["streamlit", "run", "app.py", "--server.port", "8002", "--server.enableCORS", "false", "--server.enableXsrfProtection", "false"]