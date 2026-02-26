# Use uma imagem Python oficial e leve como base
FROM python:3.12.12-slim-bookworm

# Defina variáveis de ambiente para evitar prompts interativos durante a instalação
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

ARG API_KEY
ENV API_KEY=${API_KEY}

ARG API_KEY_OPENROUTER
ENV API_KEY_OPENROUTER=${API_KEY_OPENROUTER}

# Defina o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copie o arquivo de dependências Python para o diretório de trabalho
# É assumido que um arquivo requirements.txt existe no seu projeto
COPY requirements_linux.txt .

# Instale o Jupyter Notebook para converter o notebook em script Python
RUN pip install --no-cache-dir jupyter

# Copie o restante do código da sua aplicação para o diretório de trabalho
COPY agente_eda.ipynb .
COPY tokenizer_config.json .
COPY tokenizer.json .

# Converte o notebook para script Python que será utilizado em CMD abaixo
RUN jupyter nbconvert --to script agente_eda.ipynb

# Instale os pacotes Python
RUN pip install --no-cache-dir -r requirements_linux.txt

# Exponha a porta 8000 para permitir a comunicação com a aplicação Streamlit
EXPOSE 8001

# Defina o comando para executar a aplicação
# Adicionadas flags para lidar com CORS e XSRF, comuns ao rodar em contêineres
CMD ["streamlit", "run", "agente_eda.py", "--server.port", "8001", "--server.enableCORS", "false", "--server.enableXsrfProtection", "false"]

# EXECUTAR O DOCKER COM: 
# Para baixar -> docker pull ghcr.io/ajndantas/agente_eda:latest
# Executar como -> docker run -d -p 8001:8001 ghcr.io/ajndantas/agente_eda
#
# SE FOR FAZER O BUILD LOCAL, RODAR docker build --build-arg API_KEY="minha chave" --build-arg API_KEY_OPENROUTER="minha outra chave" -t agente_eda .