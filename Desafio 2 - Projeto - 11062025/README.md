# 🤖 Agente Inteligente de Documentos Fiscais

Este projeto usa **Inteligência Artificial (LLMs)** com **LangChain**, **Tesseract**, **OpenCV**, **Streamlit** e **SQLAlchemy** pra analisar, extrair e responder perguntas sobre **Documentos fiscais** — direto de **PDFs, imagens (PNG), arquivos CSV ou XMLs**.

**[PROJETO FINAL ARTEFATOS](https://github.com/ajndantas/I2A2-Grupo_01/tree/master/Desafio%202%20-%20Projeto%20-%2011062025/Projeto%20Final%20-%20Artefatos)**

## 🖥️ Quer só testar?

Sem instalar nada:
👉 [Acesse a versão online](https://agente-nfe.streamlit.app/)

---

## 🚀 O que esse projeto faz

### 🧠 Agente 1 — Caçador de Documentos

Pega as notas fiscais (NF-e) enviadas pelo usuário ou baixadas de órgãos oficiais. Aceita PDF e imagem, sem frescura.

---

### 🧪 Agente 2 — O “Decifrador”

Usa OCR pra extrair dados e o poder das LLMs pra entender diferentes formatos de nota. Ou seja: quanto mais usa, melhor ele fica!

---

### 💬 Agente 3 — O Sabe-Tudo

Conecta-se a um modelo de linguagem e responde perguntas sobre os dados extraídos — tudo baseado na base de conhecimento criada pelos outros agentes.

---

## 🖥️ Interface Web (Streamlit)

- Suba seus arquivos (PDF, PNG, CSV ou XML) direto pelo navegador.
- Faça perguntas em **linguagem natural** (“Qual o valor total da nota?”, por exemplo).
- Veja os resultados em uma **tabela interativa**.
- E, se algo der errado, receba um feedback simpático em vez de um erro indecifrável.

---

## 🧩 Requisitos

- **Python 3.10+**
- **Chave de API** do [OpenRouter](https://openrouter.ai/) (coloque no arquivo `.env`, dentro da pasta Scripts, se for rodar localmente).

---

## 🐳 Instalação com Docker (modo fácil)

1. Instale o [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. Abra o Docker
3. No terminal (como admin), rode:
   ```bash
   docker pull ghcr.io/ajndantas/agente_nfe
   docker run -d -p 8000:8000 ghcr.io/ajndantas/agente_nfe
   ```
4. Pronto! Acesse [http://localhost:8000](http://localhost:8000)

🧾 Arquivos de teste:

- [PDFs](https://github.com/ajndantas/I2A2-Grupo_01/raw/refs/heads/master/Desafio%202%20-%20Projeto%20-%2011062025/agente_nfs/PDFs%20Docfiscais.zip)
- [Imagens PNG](https://github.com/ajndantas/I2A2-Grupo_01/raw/refs/heads/master/Desafio%202%20-%20Projeto%20-%2011062025/agente_nfs/Imagens%20Docfiscais.zip)
- [CSVs](https://github.com/ajndantas/I2A2-Grupo_01/raw/refs/heads/master/Desafio%202%20-%20Projeto%20-%2011062025/agente_nfs/CSVs%20Docfiscais.zip)
- [XMLs](https://github.com/ajndantas/I2A2-Grupo_01/raw/refs/heads/master/Desafio%202%20-%20Projeto%20-%2011062025/agente_nfs/Docs%20Fiscais%20XML.zip)

---

## 💻 Instalação Manual (modo raiz)

### 1️⃣ Instalar Tesseract e Poppler

**Linux:**

```bash
apt-get update && apt-get install -y --no-install-recommends tesseract-ocr tesseract-ocr-por poppler-utils file libmagic1 curl build-essential libgl1-mesa-glx
```

**Windows:**

1. Instale o [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki) (marque “Additional language data”).
2. Baixe o [Poppler.zip](https://github.com/ajndantas/I2A2-Grupo_01/raw/refs/heads/master/Desafio%202%20-%20Projeto%20-%2011062025/agente_nfs/poppler.zip), descompacte e coloque a pasta `poppler` dentro da pasta Scripts

### 2️⃣ Criar o ambiente Python

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

Baixe os arquivos necessários e jogue tudo na pasta `Scripts`.

**1 - Dependências**: [requirements.txt](https://github.com/ajndantas/I2A2-Grupo_01/blob/master/Desafio%202%20-%20Projeto%20-%2011062025/requirements.txt) (Para Windows), [requirements_linux.txt](https://github.com/ajndantas/I2A2-Grupo_01/blob/master/Desafio%202%20-%20Projeto%20-%2011062025/agente_nfs/Scripts/requirements_linux.txt) (Para Linux)

**2 - Script Python**: [agente_nfe.py](https://github.com/ajndantas/I2A2-Grupo_01/blob/master/Desafio%202%20-%20Projeto%20-%2011062025/agente_nfs/Scripts/agente_nfe.py)

**3 - Script OCR**: [motor_ocr_otimizado.py](https://github.com/ajndantas/I2A2-Grupo_01/blob/master/Desafio%202%20-%20Projeto%20-%2011062025/agente_nfs/Scripts/motor_ocr_otimizado.py)

Depois, instale as dependências:

```bash
pip install -r requirements.txt     # Windows
pip install -r requirements_linux.txt  # Linux
```

E rode o app:

```bash
streamlit run agente_nfe.py --server.port 8000
```

Acesse: [http://localhost:8000](http://localhost:8000)

---

## 🧠 Exemplos de perguntas

- “Qual o valor total?”
- “Quais os produtos ou serviços listados?”
- “Quem descobriu o Brasil?” (Sim, ele vai saber que isso não tem nada a ver 😅)

---

## ⚙️ Tecnologias que dão vida a tudo isso

- 🧱 **Streamlit** – Interface web
- 🧩 **LangChain** – Orquestração de LLMs
- 🤖 **[Mistral-Small-3.2-24B-Instruct-2506](https://huggingface.co/mistralai/Mistral-Small-3.2-24B-Instruct-2506) **– O cérebro por trás das respostas
- 🔍 **Tesseract** – OCR pra ler notas
- 🎥 **OpenCV** – Processamento de imagem
- 🗄️ **SQLAlchemy + SQLite** – Banco de dados
- 📊 **Pandas** – Manipulação de dados
- 🔐 **Python-dotenv** – Variáveis de ambiente

---

## 💡 Observações

- Projeto voltado pra **experimentar IA em documentos fiscais**.
- Sistema modular: cada agente faz sua parte, e fica fácil adicionar novos depois (como outros modelos OCR ou novas fontes de dados).

---

## 📃 Licença

Código aberto sob **licença MIT**
