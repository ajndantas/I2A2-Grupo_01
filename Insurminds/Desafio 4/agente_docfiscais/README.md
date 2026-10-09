# 🤖 Agente de Documentos Fiscais

Este projeto usa **Inteligência Artificial (LLMs)** com **LangChain**, **OpenAI/ChatGPT**, **Pandas**, **Streamlit**, **Docker**, **Tesseract**, **OpenCV** e **SQLAlchemy** pra analisar, extrair e responder perguntas sobre **Documentos fiscais** — direto de **PDFs, imagens (PNG), ou arquivos CSV**.

<a href="https://www.linkedin.com/in/antoniodantasia/" target="_blank">
  <img src="https://img.shields.io/badge/LinkedIn-Seguir-blue?logo=linkedin&style=for-the-badge">
</a>

## 🖥️ Quer só testar?

Sem instalar nada:
👉 [Acesse a versão online](https://agente-nfs-574973424283.us-central1.run.app)

---

## Tecnologias Utilizadas

* 🐍 **Python 3.13**
* ⚡ **FastAPI + Uvicorn** – API REST e entrega do frontend estático.
* 🦜 **LangChain + LangChain-OpenAI** – Orquestração do LLM (prompt, chamada ao modelo e parser JSON com schema Pydantic), acessado via **OpenRouter**.
* 👁️ **Tesseract OCR (pytesseract) + OpenCV** – Pré-processamento (escala de cinza e binarização) e extração de texto.
* 📄 **pdf2image + Poppler** – Conversão das páginas de PDF em imagens.
* 🧬 **python-magic (libmagic)** – Detecção do tipo real do arquivo enviado.
* 🧱 **HTML, CSS e JavaScript puro** – Interface web.
* 🐳 **Docker** – Containerização da aplicação.
* 🐙 **GitHub Actions (CI/CD)** – Build da imagem (GHCR) e deploy automatizado.
* ☁️ **GCP Cloud Run + Artifact Registry** – Hospedagem em produção.

---

## ☁️ Infraestrutura e Deploy (GCP)

O deploy é automatizado pelo workflow [**`docker-image-agente_nfs.yml`**](https://github.com/ajndantas/I2A2-Grupo_01/blob/master/.github/workflows/docker-image-agente_nfs.yml) (GitHub Actions). Ele é disparado a cada **push na branch `master`** que altere `app/`, `frontend/`, `requirements.txt` ou `Dockerfile` do projeto.

1. Build da imagem **Docker** e push para o **GitHub Container Registry (GHCR)**.
2. Autenticação no GCP com a *Service Account* e disponibilização da imagem no **Artifact Registry**, via proxy da GHCR.
3. Deploy no **Cloud Run**

---

## 🧩 Arquitetura da Aplicação

```
<pasta do projeto>/
├── app/                           # Backend FastAPI (conteúdo do app.zip)
│   ├── main.py                    # Ponto de entrada (rotas, arquivos estáticos, sessão)
│   ├── agente_rag.py              # Agente LLM: prompt, chain e parser de saída
│   ├── motor_ocr_otimizado.py     # OCR (Tesseract + OpenCV + pdf2image)
│   ├── .env                       # Chaves de API (NÃO versionar)
│   ├── poppler/                   # Poppler para Windows (já incluído no app.zip)
│   ├── rotas/
│   │   └── datasets.py            # Rotas /api/datasets/*
│   └── modelos/
│       ├── datasetquery.py        # Modelo da pergunta
│       └── outputschema.py        # Schema da resposta (text/table/chart/mixed)
├── frontend/                      # Interface web (conteúdo do frontend.zip)
│   ├── index.html
│   ├── css/styles.css
│   └── js/
│       ├── config.js              # URL da API e parâmetros do frontend
│       ├── api.js                 # Chamadas HTTP ao backend
│       └── app.js                 # Comportamento da interface
├── requirements.txt               # Dependências Python
├── Dockerfile                     # Imagem Docker (porta 8004)
└── .github/workflows/
    └── docker-image-cotejo.yml    # CI/CD: GHCR + Cloud Run
```

## 🧩 Requisitos

- **Python 3.10+**
- **Chave de API** do OpenAI/ChatGPT

---

## Implantação Local

### 📋 Pré-requisitos

* **Python 3.13**
* **Tesseract OCR** com o pacote de idioma português (`por`)
* **Poppler** (utilitários de PDF)
* **libmagic** (detecção do tipo de arquivo)
* Uma chave de API do ChatGPT

#### 🪟 Windows

1. **Tesseract OCR**

   * Baixe o instalador em [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki).
   * Durante a instalação, em *Additional language data*, marque **Portuguese**.
   * Instale no caminho padrão `C:\Program Files\Tesseract-OCR\`, pois é o caminho esperado pelo código em `app/motor_ocr_otimizado.py`.
   * Confira em um terminal novo:

     ```powershell
     & "C:\Program Files\Tesseract-OCR\tesseract.exe" --list-langs
     ```

     A lista deve conter `por`.
2. **libmagic**

   * No Windows, o `python-magic` precisa da biblioteca nativa. Depois de instalar o `requirements.txt`, instale também:
     ```powershell
     pip install python-magic-bin
     ```

#### 🐧 Linux (Debian/Ubuntu)

```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-por poppler-utils libmagic1 libgl1
```

O código espera o Tesseract em `/usr/bin/tesseract` e o Poppler no `PATH`.

#### 🍎 macOS

```bash
brew install tesseract tesseract-lang poppler libmagic
```

> No macOS o Tesseract do Homebrew fica em `/opt/homebrew/bin/tesseract` (Apple Silicon). Como o código fixa `/usr/bin/tesseract` para sistemas POSIX, ajuste `self.tesseract_cmd` em `app/motor_ocr_otimizado.py`.

---

### 🛠️ 1 - Instalação dos códigos (ambiente virtual + arquivos zip)

Crie a pasta do projeto, o ambiente virtual e descompacte os arquivos `app.zip` e `frontend.zip` **cada um em sua própria subpasta**. Os zips não contêm uma pasta raiz, então o conteúdo precisa ser extraído dentro de `app/` e `frontend/`, o que resulta na estrutura mostrada em 🧩 **Arquitetura da Aplicação**.

Baixe os três arquivos e coloque-os na pasta do projeto:

* 📦 [app.zip](<https://github.com/ajndantas/I2A2-Grupo_01/raw/refs/heads/master/Insurminds/Desafio%204/agente_docfiscais/app.zip>) (backend)
* 📦 [frontend.zip](<https://github.com/ajndantas/I2A2-Grupo_01/raw/refs/heads/master/Insurminds/Desafio%204/agente_docfiscais/frontend.zip>) (interface web)
* 📄 [requirements.txt](<https://github.com/ajndantas/I2A2-Grupo_01/raw/refs/heads/master/Insurminds/Desafio%204/agente_docfiscais/requirements.txt>) (dependências Python; na página do GitHub, use o botão de download ou *Raw* e salve o arquivo)

**Linux / macOS**

```bash
mkdir agente_docfiscais && cd agente_docfiscais

# Download dos arquivos (ou baixe pelos links acima e copie para esta pasta)
curl -L -O "https://github.com/ajndantas/I2A2-Grupo_01/raw/refs/heads/master/Insurminds/Desafio%204/agente_docfiscais/app.zip"
curl -L -O "https://github.com/ajndantas/I2A2-Grupo_01/raw/refs/heads/master/Insurminds/Desafio%204/agente_docfiscais/frontend.zip"
curl -L -O "https://github.com/ajndantas/I2A2-Grupo_01/raw/refs/heads/master/Insurminds/Desafio%204/agente_docfiscais/requirements.txt"

python3.13 -m venv .venv
source .venv/bin/activate

unzip app.zip -d app
unzip frontend.zip -d frontend
```

**Windows (PowerShell)**

```powershell
mkdir agente_docfiscais; cd agente_docfiscais

# Download dos arquivos (ou baixe pelos links acima e copie para esta pasta)
Invoke-WebRequest -Uri "https://github.com/ajndantas/I2A2-Grupo_01/raw/refs/heads/master/Insurminds/Desafio%204/agente_docfiscais/app.zip" -OutFile app.zip
Invoke-WebRequest -Uri "https://github.com/ajndantas/I2A2-Grupo_01/raw/refs/heads/master/Insurminds/Desafio%204/agente_docfiscais/frontend.zip" -OutFile frontend.zip
Invoke-WebRequest -Uri "https://github.com/ajndantas/I2A2-Grupo_01/raw/refs/heads/master/Insurminds/Desafio%204/agente_docfiscais/requirements.txt" -OutFile requirements.txt

py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1

Expand-Archive -Path app.zip -DestinationPath app
Expand-Archive -Path frontend.zip -DestinationPath frontend
```

> Se o PowerShell bloquear a ativação do ambiente, execute uma vez: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`. No **cmd**, use `.venv\Scripts\activate.bat`.

### 📦 2 - Instalação das dependências

Com o ambiente virtual ativo:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

No Windows, instale também a biblioteca do libmagic:

```powershell
pip install python-magic-bin
```

### 🔐 3 - Configuração das variáveis de ambiente

Crie um arquivo  **.env** dentro da pasta `app :`

```env
API_KEY=SUA_CHAVE_API
```

* `API_KEY` é a chave usada hoje pelo LLM em `app/agente_rag.py`.

> ⚠️ **Nunca versione o `.env`.** Inclua `.env` no `.gitignore`.

### 🌐 4 - Configuração do frontend

Abra `frontend/js/config.js` e ajuste `apiBaseUrl`. Por padrão ele aponta para o serviço publicado no Cloud Run. Para rodar localmente, use o endereço do seu servidor:

```javascript
export const CONFIG = {
  apiBaseUrl: "http://127.0.0.1:8000", // Para testes locais
  demoMode: false,
  maxFileSize: 500 * 1024 * 1024,
  minFiles: 2,
  // ...
};
```

Como o FastAPI serve o próprio frontend, `apiBaseUrl: ""` (mesma origem) também funciona e evita problemas de CORS.

| Parâmetro      | Descrição                                             |
| --------------- | ------------------------------------------------------- |
| `apiBaseUrl`  | Endereço do backend, sem barra no final                |
| `maxFileSize` | Tamanho máximo de arquivo aceito pelo frontend         |
| `minFiles`    | Quantidade mínima de apólices exigida para a análise |

### ▶️ 5 - Execução local

Na **pasta raiz do projeto** (a que contém `app/` e `frontend/`), com o ambiente virtual ativo:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

A aplicação ficará disponível em:

```text
http://localhost:8000
```

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
