# 📄 Agente Inteligente para Análise de Documentos Fiscais

Este projeto utiliza **Inteligência Artificial (LLMs)** com **LangChain**, **Tesseract, OpenCV, Streamlit **e** **SQLAlchemy** para analisar, extrair e responder perguntas sobre **Documentos Fiscais, tais como NF-e** a partir de arquivos PDF, PNG e CSV.**

---

## 🚀 Funcionalidades Principais

### 🧠 Agente 1: Aquisição e Validação de Documentos

- Responsável por obter documentos fiscais (NF-e) em formatos de imagem e PDF, provenientes de upload manual realizados pelo usuário ou download de órgãos governamentais.

---

### 🧪 Agente 2: Extração e Geração de Queries com IA

- Processa os documentos adquiridos, utilizando OCR para extrair dados e aprender novos layouts com apoio de LLM, garantindo a extração precisa de informações fiscais relevantes.

---

### 💬 Agente 3: Resposta Inteligente

- Acessa um Large Language Model (LLM) e, utilizando os  dados  da  Base  de  Conhecimento,  responde  às  perguntas  dos  usuários  sobre  as informações fiscais.

---

## 🖥️ Frontend: Interface com Streamlit

- Upload de arquivos PDF, PNG e CSV via interface web.
- Campo para perguntas em Linguagem Natural
- Exibição de resultados em formato de tabela interativa.
- Feedback amigável em caso de erro ou ausência de resposta.

---

## 🛠️ Requisitos

- Python **3.10** ou superior
- **API Key do Google Gemini AI. (Informar uma chave do Gemini no arquivo .env, para o caso de instalação utilizando o fonte).**

---

## 📦 Instalação

### 1 - Utilizando Docker (Mais fácil)

1. Baixe e instale o docker desktop para o seu sistema em https://www.docker.com/products/docker-desktop/
2. Abra o Docker Desktop
3. Como administrador, abra um terminal e execute os comandos:
   1. docker pull ghcr.io/ajndantas/agente_nfs
   2. docker run -d -p 8000:8000 ghcr.io/ajndantas/agente_nfs
4. Abra o link http://localhost:8000

Arquivos para teste:

* [PDF](https://drive.google.com/open?id=1x_deql_HqLn56_uELL7RyTNmHk2smTLI&usp=drive_fs)
* [PNG](https://drive.google.com/open?id=1MNs4WsvcKUcJ9Xz5vwsYBntbiC14Axhc&usp=drive_fs)

---

### 2 - Utilizando o código fonte

### Instalando o Tesseract e o Poppler

**A) Linux**

apt-get update && apt-get install -y --no-install-recommends tesseract-ocr tesseract-ocr-por poppler-utils file libmagic1 curl build-essential libgl1-mesa-glx

**B) Windows**

1. Instalar o [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki). Marcar "Aditional language data (download))"
2. Instalar o Poppler
   1. Baixar o arquivo [poppler.zip](https://drive.google.com/open?id=1wwuRo9LBfAcSmX-gcUmBkphttMl_p-w3&usp=drive_fs). (Caso perguntado pelo Google, insista em fazer o download)
   2. Descompactar o arquivo e colocar a pasta poppler dentro da pasta Script do ambiente virtual que será criado. Seção abaixo

### Instalando o Python

```bash
# Recomendado criar um ambiente virtual
python -m venv venv
cd venv
Scripts\activate # Windows

# Faça o download dos arquivos a seguir para dentro da pasta Scripts. (Caso perguntado pelo Google, insista em fazer o download)
- requirements.txt (Windows) - https://drive.google.com/open?id=1phG0NWz-pMQS21C-Ovz9IY35wf5AgX0o&usp=drive_fs
- requirements_linux.txt (Linux) - https://drive.google.com/open?id=19SYi2ZhoRQqHDVYIOFlnlFVoldrdtgRp&usp=drive_fs
- agente_nfs.py - https://drive.google.com/open?id=1HJWherk86_tNA7U__xYSQakK7Cj6KvYu&usp=drive_fs 
- motor_ocr_otimizado.py - https://drive.google.com/open?id=1zuB-Rz07RkM0CxlU-ATZ6qOA8-66MEOt&usp=drive_fs
- .env (Salvar com esse nome mesmo. Sem extensão. Informe sua chave para a Google API) - https://drive.google.com/open?id=11qCEgQzQJ-ThvnABEDUAzgFuqEZDh-FS&usp=drive_fs

# Dentro da pasta Script, execute:
# Instale as dependências
pip install -r requirements.txt

# Instale a biblioteca magic
- Faça o download de libmagic.ddl para dentro da pasta Scripts -> https://drive.google.com/open?id=1lfFjCqbq0kn3fJ2l6d-yUGh_S9ocxOvp&usp=drive_fs
- Faça o download de magic.mgc para dentro da pasta Scripts -> https://drive.google.com/open?id=139WhLxANdst59qId8iVm3iR5q5a9XIXk&usp=drive_fs

```

### Execução

1. Execute no terminal o comando -> streamlit run agente_nfs.py --server.port 8000
2. Abra o link http://localhost:8000

Arquivos para teste:

* [PDF](https://drive.google.com/open?id=1x_deql_HqLn56_uELL7RyTNmHk2smTLI&usp=drive_fs)
* [PNG](https://drive.google.com/open?id=1MNs4WsvcKUcJ9Xz5vwsYBntbiC14Axhc&usp=drive_fs)

---
## 📈 Exemplo de Perguntas Suportadas

- Quem são os destinatários ?
- Qual é o valor total da nota ?
- Qual é a descrição dos serviços ou itens ?
- Quem descobriu o Brasil? *(Teste para detectar perguntas não relacionadas)*

---

## ⚙️ Tecnologias Utilizadas

- **Streamlit** – Frontend Web
- **LangChain** – Orquestração de LLMs
- **Google Gemini API** – LLM
- **Tesseract**
- **OpenCV**
- **SQLAlchemy + SQLite** – Persistência de Dados
- **Pandas** – Manipulação de DataFrames
- **Python-dotenv** – Gestão de variáveis de ambiente

---

## 📌 Observações Importantes

- Este projeto está focado em **experimentação com IA aplicada a documentos fiscais**.
- O sistema foi estruturado com **agentes independentes** para facilitar futura expansão (OCR, aprendizado de layouts, etc).

---

## 📃 Licença

Este projeto é de código aberto e está sob a licença **MIT**.
