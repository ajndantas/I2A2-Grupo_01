# 📄 Agente Inteligente para Análise de Notas Fiscais Eletrônicas (NFe)

Este projeto utiliza **Inteligência Artificial (LLMs)** com **LangChain**, **Streamlit** e **SQLAlchemy** para analisar, extrair e responder perguntas sobre **Notas Fiscais Eletrônicas (NFe)** a partir de arquivos CSV compactados em ZIP.

---

## 🚀 Funcionalidades Principais

### 🧠 Agente 1: Aquisição e Validação de Documentos

- Upload de arquivos ZIP contendo CSVs de **cabeçalho** e **itens**.
- Validação automática da estrutura dos arquivos.
- Armazenamento dos dados em um banco de dados **SQLite** apenas se forem úteis para responder à pergunta do usuário.

---

### 🧪 Agente 2: Extração e Geração de Queries com IA

- Utiliza **LLMs (Google Gemini via LangChain)** para criar **queries SQL dinâmicas** baseadas na pergunta do usuário.
- Executa a consulta sobre o banco de dados SQLite e retorna os resultados.

---

### 💬 Agente 3: Resposta Inteligente

- Faz a integração entre validação, geração de queries e exibição de resultados.
- Se os arquivos enviados não forem suficientes para responder, o sistema informa o usuário.

---

## 🖥️ Frontend: Interface com Streamlit

- Upload de arquivos ZIP via interface web.
- Campo para perguntas em **Linguagem Natural**.
- Exibição de resultados em formato de tabela interativa.
- Feedback amigável em caso de erro ou ausência de resposta.

---

## 🛠️ Requisitos

- Python **3.10** ou superior
- Conta com **API Key do Google Gemini AI. (Informar uma chave do Gemini, no arquivo. env baixado no tópico de Instalação abaixo).**

---

## 📦 Instalação

```bash
# Recomendado criar um ambiente virtual
python -m venv venv
venv\Scripts\activate   # Windows

# Faça o download dos arquivos a seguir para dentro da pasta Scripts
- requirements.txt - https://drive.google.com/open?id=1l8wVOPQ8FbJ6KtfNlPCJR5hYS2jsrkFh&usp=drive_fs
- agente_nfs.py - https://drive.google.com/open?id=1tjYu1NlxNrG4TSPIFY4vz6M495uRD-ba&usp=drive_fs 
- frontend.py - https://drive.google.com/open?id=16XIIyC65AnpDk_GYVPxYdSvuQwLmOLbt&usp=drive_fs
- .env - https://drive.google.com/open?id=11qCEgQzQJ-ThvnABEDUAzgFuqEZDh-FS&usp=drive_fs

# Dentro da pasta Script, execute:
# Instale as dependências
pip install -qqqr requirements.txt
```

---

## ▶️ Execução

```bash
# A primeira execução demora um pouco. Em torno de 10 min.
streamlit run frontend.py
```

---

## 📂 Estrutura esperada do ZIP de Entrada

O arquivo ZIP precisa conter pelo menos dois arquivos CSV com os seguintes nomes:

- ...cabecalho.csv
- ...itens.csv

> **Importante:** Os nomes podem variar, mas devem conter as palavras-chave **"cabecalho"** e **"itens"**.
>
> **[Ex de arquivo zip com notas fiscais](https://drive.google.com/open?id=1kmQo2JkWJ2UXr46PJrNI95jlLUv1LQca&usp=drive_fs)**

---

## 📈 Exemplo de Perguntas Suportadas

- Qual é a chave de acesso da nota 3510129?
- Qual é a descrição dos serviços da nota com número 2525?
- Qual é a descrição dos serviços e a natureza da operação da nf com número 2525 ?
- Quem descobriu o Brasil? *(Teste para detectar perguntas não relacionadas)*

---

## ⚙️ Tecnologias Utilizadas

- **Streamlit** – Frontend Web
- **LangChain** – Orquestração de LLMs
- **Google Gemini API** – LLM
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
