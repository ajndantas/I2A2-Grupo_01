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
- Campo para perguntas em **Linguagem Natural**.
- Exibição de resultados em formato de tabela interativa.
- Feedback amigável em caso de erro ou ausência de resposta.

---

## 🛠️ Requisitos

- Python **3.10** ou superior
- Conta com **API Key do Google Gemini AI. (Informar uma chave do Gemini, no arquivo. env baixado no tópico de Instalação abaixo).**

---

## 📦 Instalação

### 2 - Utilizado o código fonte

### Instalando o Tesseract e o Poppler
---
**A) Linux**

apt-get update && apt-get install -y --no-install-recommends tesseract-ocr tesseract-ocr-por poppler-utils file libmagic1 curl build-essential libgl1-mesa-glx

**B) Windows**

1. Instalar o Tesseract -> https://github.com/UB-Mannheim/tesseract/wiki
2. Instalar o Poppler
   1. Baixar o arquivo poppler.zip -> https://drive.google.com/open?id=1wwuRo9LBfAcSmX-gcUmBkphttMl_p-w3&usp=drive_fs
   2. Descompactar o arquivo e colocar a pasta poppler dentro da pasta Script

### Instalando o Python
---
```bash
# Recomendado criar um ambiente virtual
python -m venv venv
venv\Scripts\activate   # Windows

# Faça o download dos arquivos a seguir para dentro da pasta Scripts
- requirements.txt (Windows) - https://drive.google.com/open?id=1phG0NWz-pMQS21C-Ovz9IY35wf5AgX0o&usp=drive_fs
- requirements_linux.txt (Linux) - https://drive.google.com/open?id=19SYi2ZhoRQqHDVYIOFlnlFVoldrdtgRp&usp=drive_fs
- agente_nfs.py - https://drive.google.com/open?id=1HJWherk86_tNA7U__xYSQakK7Cj6KvYu&usp=drive_fs 
- .env - https://drive.google.com/open?id=11qCEgQzQJ-ThvnABEDUAzgFuqEZDh-FS&usp=drive_fs

# Dentro da pasta Script, execute:
# Instale as dependências
pip install -qqqr requirements.txt
```

---

## ▶️ Execução

```bash
# A primeira execução demora um pouco.
streamlit run agente_nfs.py--server.port 8000

Abra o link http://localhost:8000
```

---

## 📈 Exemplo de Perguntas Suportadas

- Quem são os destinatários ?
- Qual o valor total da nota ?
- Qual é a descrição dos serviços e a natureza da operação da nf ?
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
