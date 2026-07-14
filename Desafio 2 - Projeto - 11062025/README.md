# 🤖 Agente de Documentos Fiscais

Este projeto usa **Inteligência Artificial (LLMs)** com **LangChain**, **OpenAI/ChatGPT**, **Pandas**, **Streamlit**, **Docker**, **Tesseract**, **OpenCV** e **SQLAlchemy** pra analisar, extrair e responder perguntas sobre **Documentos fiscais** — direto de **PDFs, imagens (PNG), ou arquivos CSV**.

<a href="https://www.linkedin.com/in/antoniodantasia/" target="_blank">
  <img src="https://img.shields.io/badge/LinkedIn-Seguir-blue?logo=linkedin&style=for-the-badge">
</a>

## 🖥️ Quer só testar?

Sem instalar nada:
👉 [Acesse a versão online](https://agente-nfs-574973424283.us-central1.run.app)

---

## ⚙️ Tecnologias que dão vida a tudo isso

- 🧱 **Streamlit** – Interface web
- 🧩 **LangChain** – Orquestração de LLMs
- 🤖 **OpenAI/ChatGPT** **– O cérebro por trás das respostas
- 🔍 **Tesseract** – OCR pra ler notas
- 🎥 **OpenCV** – Processamento de imagem
- 🗄️ **SQLAlchemy + SQLite** – Banco de dados
- 📊 **Pandas** – Manipulação de dados
- 🔐 **Python-dotenv** – Variáveis de ambiente.
- 🐳 **Docker** – Application Container
- ⚙️ **GitHub Actions** (CI/CD) - ([YAML ](https://github.com/ajndantas/I2A2-Grupo_01/blob/master/.github/workflows/docker-image-agente_nfs.yml)que implementa a integraçãa com a GCP)
- ☁️ **Google Cloud Platform** – Infraestrutura em nuvem

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

## 🧩 Requisitos

- **Python 3.10+**
- **Chave de API** do OpenAI/ChatGPT (coloque no arquivo `.env`, dentro da pasta Scripts, se for rodar localmente).

---

## 🧾 Arquivos de teste:

- [PDFs](<https://github.com/ajndantas/I2A2-Grupo_01/raw/refs/heads/master/Desafio%202%20-%20Projeto%20-%2011062025/agente_nfs/PDFs%20Docfiscais.zip>)
- [Imagens PNG](<https://github.com/ajndantas/I2A2-Grupo_01/raw/refs/heads/master/Desafio%202%20-%20Projeto%20-%2011062025/agente_nfs/Imagens%20Docfiscais.zip>)
- [CSVs](<https://github.com/ajndantas/I2A2-Grupo_01/raw/refs/heads/master/Desafio%202%20-%20Projeto%20-%2011062025/agente_nfs/CSVs%20Docfiscais.zip>)

---

## 💻 Instalação Manual (modo raiz)

### 1️⃣ Instalar Tesseract e Poppler

**Linux:**

```bash
apt-get update && apt-get install -y --no-install-recommends tesseract-ocr tesseract-ocr-por poppler-utils file libmagic1 curl build-essential libgl1-mesa-glx
```

**Windows:**

1. Instale o [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki) (marque “Additional language data”).
2. Baixe o [Poppler.zip](https://drive.google.com/open?id=1wwuRo9LBfAcSmX-gcUmBkphttMl_p-w3&usp=drive_fs), descompacte e coloque a pasta `poppler` dentro da pasta Scripts

### 2️⃣ Criar o ambiente Python

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

Baixe os arquivos necessários e jogue tudo na pasta `Scripts`.

**1 - Dependências**: [requirements.txt](<https://github.com/ajndantas/I2A2-Grupo_01/blob/master/Desafio%202%20-%20Projeto%20-%2011062025/requirements.txt>) (Para Windows), [requirements_linux.txt](<https://github.com/ajndantas/I2A2-Grupo_01/blob/master/Desafio%202%20-%20Projeto%20-%2011062025/agente_nfs/Scripts/requirements_linux.txt>) (Para Linux)

**2 - Script Python**: [agente_nfe.py](<https://github.com/ajndantas/I2A2-Grupo_01/blob/master/Desafio%202%20-%20Projeto%20-%2011062025/agente_nfs/Scripts/agente_nfe.py>)

**3 - Script OCR**: [motor_ocr_otimizado.py](<https://github.com/ajndantas/I2A2-Grupo_01/blob/master/Desafio%202%20-%20Projeto%20-%2011062025/agente_nfs/Scripts/motor_ocr_otimizado.py>)

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

## 💡 Observações

- Projeto voltado pra **experimentar IA em documentos fiscais**.
- Sistema modular: cada agente faz sua parte, e fica fácil adicionar novos depois (como outros modelos OCR ou novas fontes de dados).

---

## 📃 Licença

Código aberto sob **licença MIT**
