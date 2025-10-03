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
- **API Key do provedor OpenRouter. (Informar uma chave do [OpenRouter ](https://openrouter.ai/)no arquivo .env, para o caso de instalação utilizando o fonte).**

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

* [PDF](https://github.com/ajndantas/I2A2-Grupo_01/raw/refs/heads/master/Desafio%202%20-%20Projeto%20-%2011062025/agente_nfs/PDFs%20Docfiscais.zip)
* [PNG](https://github.com/ajndantas/I2A2-Grupo_01/raw/refs/heads/master/Desafio%202%20-%20Projeto%20-%2011062025/agente_nfs/Imagens%20Docfiscais.zip)

---

### 2 - Utilizando o código fonte

### Instalando o Tesseract e o Poppler

**A) Linux**

apt-get update && apt-get install -y --no-install-recommends tesseract-ocr tesseract-ocr-por poppler-utils file libmagic1 curl build-essential libgl1-mesa-glx

**B) Windows**

1. Instalar o [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki). Marcar "Additional language data (download)"
2. Instalar o Poppler
   1. Baixar o arquivo [poppler.zip](https://github.com/ajndantas/I2A2-Grupo_01/raw/refs/heads/master/Desafio%202%20-%20Projeto%20-%2011062025/agente_nfs/poppler.zip). (Caso perguntado pelo Google, insista em fazer o download)
   2. Descompactar o arquivo e colocar a pasta poppler dentro da pasta Script do ambiente virtual que será criado. Seção abaixo

### Instalando o Python

**Recomendado criar um ambiente virtual. Execute os comandos**

```
python -m venv venv
venv\Scripts\activate # Windows
```

**Faça o download dos arquivos a seguir para dentro da pasta Scripts. (Caso perguntado pelo Google, insista em fazer o download)**

- [requirements.txt (Windows)](https://github.com/ajndantas/I2A2-Grupo_01/blob/master/Desafio%202%20-%20Projeto%20-%2011062025/agente_nfs/requirements.txt)
- [requirements_linux.txt (Linux)](https://github.com/ajndantas/I2A2-Grupo_01/blob/master/Desafio%202%20-%20Projeto%20-%2011062025/agente_nfs/Scripts/requirements_linux.txt)
- [agente_nfs.py](https://github.com/ajndantas/I2A2-Grupo_01/blob/master/Desafio%202%20-%20Projeto%20-%2011062025/agente_nfs/Scripts/agente_nfs.py)
- [motor_ocr_otimizado.py](https://github.com/ajndantas/I2A2-Grupo_01/blob/master/Desafio%202%20-%20Projeto%20-%2011062025/agente_nfs/Scripts/motor_ocr_otimizado.py)
- [libmagic.ddl (Windows) ](https://github.com/ajndantas/I2A2-Grupo_01/raw/refs/heads/master/Desafio%202%20-%20Projeto%20-%2011062025/agente_nfs/Lib/site-packages/magic/libmagic/libmagic.dll)
- [magic.mgc (Windows)](https://github.com/ajndantas/I2A2-Grupo_01/raw/refs/heads/master/Desafio%202%20-%20Projeto%20-%2011062025/agente_nfs/Lib/site-packages/magic/libmagic/magic.mgc)
- [.env](https://github.com/ajndantas/I2A2-Grupo_01/blob/master/Desafio%202%20-%20Projeto%20-%2011062025/agente_nfs/Scripts/.env) (Salvar com esse nome mesmo. Sem extensão. Informe sua chave para a Google API)

**Dentro da pasta Script, execute:**

```
1 - Execute no terminal o comando -> streamlit run agente_nfs.py --server.port 8000
2 - Abra o link http://localhost:8000
```

Arquivos para teste:

* [PDF](https://github.com/ajndantas/I2A2-Grupo_01/raw/refs/heads/master/Desafio%202%20-%20Projeto%20-%2011062025/agente_nfs/PDFs%20Docfiscais.zip)
* [PNG](https://github.com/ajndantas/I2A2-Grupo_01/raw/refs/heads/master/Desafio%202%20-%20Projeto%20-%2011062025/agente_nfs/Imagens%20Docfiscais.zip)

---

## 📈 Exemplo de Perguntas Suportadas

- Quem são os destinatários ou tomadores de serviço ?
- Qual é o valor total da nota ?
- Qual é a descrição dos serviços ou itens ?
- Quem descobriu o Brasil? *(Teste para detectar perguntas não relacionadas)*

---

## ⚙️ Tecnologias Utilizadas

- **Streamlit** – Frontend Web
- **LangChain** – Orquestração de LLMs
- **Grok4 - Fast** – LLM
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
