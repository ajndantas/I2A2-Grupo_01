# ⚖️ Cotejo — Duas apólices, uma conversa

## 🛠️ O que este projeto faz

Aplicação web que permite **enviar duas ou mais apólices de seguro** (PDF, imagem, TXT ou CSV) e **conversar com elas em linguagem natural** para compará-las: coberturas, prêmios, franquias, vigência, exclusões e diferenças entre os documentos. As respostas podem vir em **texto, tabela, gráfico** ou uma combinação dos três.

O assistente é especializado em apólices **D&O (Directors and Officers)**, o seguro de responsabilidade civil para conselheiros, diretores e administradores.

Principais funcionalidades:

* 📤 **Upload de múltiplos documentos:** o frontend exige no mínimo 2 apólices (sem limite máximo) e aceita PDF, imagens, TXT e CSV.
* 🔍 **OCR automático:** PDFs e imagens são convertidos em texto com **Tesseract + OpenCV** (idioma português). Arquivos TXT/CSV são lidos diretamente.
* 🤖 **Agente de comparação com IA:** um LLM (via LangChain + ChatGPT) recebe o texto de todas as apólices como contexto e responde à pergunta do usuário, sempre citando os nomes dos arquivos.
* 📊 **Respostas estruturadas:** a saída segue um schema (`text`, `table`, `chart` ou `mixed`), renderizado pelo frontend como texto, tabela ou gráfico (barras ou rosca).
* 🛡️ **Proteções de domínio:** o agente recusa comparar apólices de tipos de bens diferentes e avisa quando os documentos não trazem informação suficiente.
* 🔄 **Nova análise:** botão que descarta a sessão atual e inicia uma nova.
* 🖥️ **Frontend simples (HTML/CSS/JS):** upload, tela de processamento e chat, servidos pelo próprio FastAPI.

---

## 🚀 Demonstração ao Vivo

O projeto está implantado na infraestrutura da **Google Cloud Platform (GCP)**:

🔗 **[Acessar o Cotejo](https://cotejo-574973424283.us-central1.run.app/)**

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

### 🔄 Fluxo de funcionamento

1. O usuário envia as apólices em `POST /api/datasets/uploads`.
2. O backend identifica o tipo de cada arquivo (libmagic). PDFs e imagens passam pelo OCR; TXT e CSV são lidos diretamente.
3. O texto extraído de cada apólice é guardado em memória, associado ao nome do arquivo.
4. A cada pergunta (`POST /api/datasets/{dataset_ids}/query`), o texto de todas as apólices é enviado ao LLM como contexto.
5. O LLM responde em JSON no formato do `OutputSchema`, e o frontend renderiza texto, tabela e/ou gráfico.

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
2. **Poppler**

   * O `app.zip` já traz o Poppler 24.08.0 em `app\poppler\poppler\poppler-24.08.0\Library\bin`, que é o caminho que o código usa no Windows. Ao descompactar o zip (passo 1 abaixo), nada mais precisa ser feito.
   * Se preferir instalar por conta própria, baixe o pacote em [https://github.com/oschwartz10612/poppler-windows/releases](https://github.com/oschwartz10612/poppler-windows/releases), extraia-o e deixe a pasta `Library\bin` no mesmo caminho acima, ou ajuste a variável `poppler_path` em `app/motor_ocr_otimizado.py`.
   * Para testar: `pdftoppm -h` deve funcionar a partir da pasta `Library\bin`.
3. **libmagic**

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

* 📦 [app.zip](<https://github.com/ajndantas/I2A2-Grupo_01/raw/refs/heads/master/Insurminds/Desafio%20Final/desafio_final/app.zip>) (backend)
* 📦 [frontend.zip](<https://github.com/ajndantas/I2A2-Grupo_01/raw/refs/heads/master/Insurminds/Desafio%20Final/desafio_final/frontend.zip>) (interface web)
* 📄 [requirements.txt](<https://github.com/ajndantas/I2A2-Grupo_01/blob/master/Insurminds/Desafio%20Final/desafio_final/requirements.txt>) (dependências Python; na página do GitHub, use o botão de download ou *Raw* e salve o arquivo)

**Linux / macOS**

```bash
mkdir cotejo && cd cotejo

# Download dos arquivos (ou baixe pelos links acima e copie para esta pasta)
curl -L -O "https://github.com/ajndantas/I2A2-Grupo_01/raw/refs/heads/master/Insurminds/Desafio%20Final/desafio_final/app.zip"
curl -L -O "https://github.com/ajndantas/I2A2-Grupo_01/raw/refs/heads/master/Insurminds/Desafio%20Final/desafio_final/frontend.zip"
curl -L -O "https://github.com/ajndantas/I2A2-Grupo_01/raw/refs/heads/master/Insurminds/Desafio%20Final/desafio_final/requirements.txt"

python3.13 -m venv .venv
source .venv/bin/activate

unzip app.zip -d app
unzip frontend.zip -d frontend
```

**Windows (PowerShell)**

```powershell
mkdir cotejo; cd cotejo

# Download dos arquivos (ou baixe pelos links acima e copie para esta pasta)
Invoke-WebRequest -Uri "https://github.com/ajndantas/I2A2-Grupo_01/raw/refs/heads/master/Insurminds/Desafio%20Final/desafio_final/app.zip" -OutFile app.zip
Invoke-WebRequest -Uri "https://github.com/ajndantas/I2A2-Grupo_01/raw/refs/heads/master/Insurminds/Desafio%20Final/desafio_final/frontend.zip" -OutFile frontend.zip
Invoke-WebRequest -Uri "https://github.com/ajndantas/I2A2-Grupo_01/raw/refs/heads/master/Insurminds/Desafio%20Final/desafio_final/requirements.txt" -OutFile requirements.txt

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

| Parâmetro      | Descrição                                                   |
| --------------- | ---------------------------------------------------------- |
| `apiBaseUrl`  | Endereço do backend, sem barra no final                      |
| `maxFileSize` | Tamanho máximo de arquivo aceito pelo frontend               |
| `minFiles`    | Quantidade mínima de apólices exigida para a análise         |

### ▶️ 5 - Execução local

Na **pasta raiz do projeto** (a que contém `app/` e `frontend/`), com o ambiente virtual ativo:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

> É importante executar a partir da raiz, pois o `main.py` lê os arquivos do frontend pelo caminho relativo `frontend/`.

A aplicação ficará disponível em:

```text
http://localhost:8000
```

A documentação interativa (Swagger) fica em `http://localhost:8000/docs`.

---

## 🐳 Execução com Docker

O `Dockerfile` usa `python:3.13-slim` e instala, dentro da imagem, o **Tesseract (com idioma português)**, o **Poppler**, o **libmagic** e as bibliotecas gráficas exigidas pelo OpenCV. A aplicação sobe na porta **8004**.

A pasta de contexto do build deve conter `app/`, `frontend/`, `requirements.txt` e o `Dockerfile`.

**Build local**

```bash
docker build \
  --build-arg API_KEY=sua_chave_api \
  -t cotejo .
```

**Execução**

```bash
docker run -d -p 8004:8004 --name cotejo cotejo
# Frontend e API em http://localhost:8004
```

Para não gravar as chaves na imagem, use um arquivo de variáveis de ambiente em tempo de execução:

```bash
docker run -d --env-file app/.env -p 8004:8004 --name cotejo cotejo
```

---

## ☁️ Infraestrutura e Deploy (GCP)

O deploy é automatizado pelo workflow [**`docker-image-cotejo.yml`**](https://github.com/ajndantas/I2A2-Grupo_01/blob/master/.github/workflows/docker-image-cotejo.yml) (GitHub Actions). Ele é disparado a cada **push na branch `master`** que altere `app/`, `frontend/`, `requirements.txt`, `Dockerfile` ou a pasta `Exemplos de documentos` do projeto.

1. Build da imagem **Docker**, com as chaves recebidas por `--build-arg`, e push para o **GitHub Container Registry (GHCR)**.
2. Autenticação no GCP com a *Service Account* e disponibilização da imagem no **Artifact Registry**, via proxy da GHCR.
3. Deploy no **Cloud Run**, com `--memory=2Gi`, `--cpu=4, --timeout=10m`, `--allow-unauthenticated` e as chaves repassadas como variáveis de ambiente.

### Configuração do workflow

| Variável (`env`) | Valor / Descrição                                                          |
| ------------------- | ---------------------------------------------------------------------------- |
| `PROJECT_ID`      | ID do projeto no GCP                                                         |
| `REGION`          | Região do Cloud Run (`us-central1`)                                       |
| `SERVICE_NAME`    | Nome do serviço no Cloud Run (`cotejo`)                                   |
| `REPO_NAME`       | Repositório no Artifact Registry (`cotejo`), que deve existir previamente |
| `PORT`            | Porta do container (`8004`), a mesma exposta no `Dockerfile`             |
| `GHIMAGE_ID`      | Imagem na GHCR (`ghcr.io/<owner>/cotejo`)                                  |
| `TAG`             | Tag da imagem (`latest`)                                                   |

### GitHub Secrets necessários

| Secret         | Descrição                                                   |
| -------------- | ------------------------------------------------------------- |
| `API_KEY`    | Chave de API usada pelo LLM                                   |
| `GCP_SA_KEY` | JSON da*Service Account* do GCP com permissão no Cloud Run |

> O `GITHUB_TOKEN` é fornecido automaticamente pelo GitHub Actions e usado no login da GHCR.

---

## 📡 Endpoints da API

| Método | Rota                                  | Descrição                                               |
| ------- | ------------------------------------- | --------------------------------------------------------- |
| GET     | `/`                                 | Retorna a página HTML do frontend                        |
| POST    | `/api/datasets/uploads`             | Recebe as apólices, executa o OCR e registra os datasets |
| POST    | `/api/datasets/{dataset_ids}/query` | Faz uma pergunta sobre as apólices enviadas              |
| POST    | `/api/datasets/sessions/new`        | Descarta a sessão atual ("Nova análise")                |

### 🔎 Detalhamento dos endpoints

#### `POST /api/datasets/uploads`

Corpo `multipart/form-data`, com um ou mais arquivos no campo `files`.

Resposta (`200`):

```json
{
  "dataset_ids": ["ds_123", "ds_456"],
  "status": "ready",
  "filenames": ["apolice_1.pdf", "apolice_2.png"]
}
```

#### `POST /api/datasets/{dataset_ids}/query`

Informe os IDs dos datasets separados por vírgula no caminho (por exemplo, `/api/datasets/ds_123,ds_456/query`). Corpo (`application/json`):

```json
{ "question": "Qual apólice tem a maior cobertura para custos de defesa?" }
```

Resposta (`200`), no formato `OutputSchema`:

```json
{
  "answer": "A apólice apolice_1.pdf possui limite maior de cobertura para custos de defesa.",
  "type": "mixed",
  "table": {
    "columns": ["Apólice", "Limite de defesa"],
    "rows": [["apolice_1.pdf", "R$ 5.000.000,00"], ["apolice_2.png", "R$ 3.000.000,00"]]
  },
  "chart": {
    "type": "bar",
    "labels": ["apolice_1.pdf", "apolice_2.png"],
    "datasets": [{ "label": "Limite de defesa", "data": [5000000, 3000000] }]
  }
}
```

#### `POST /api/datasets/sessions/new`

Limpa a sessão do usuário. Chamado pelo botão **Nova análise**.

### 🧬 Schemas principais

| Schema            | Campos                                                                                                         |
| ----------------- | -------------------------------------------------------------------------------------------------------------- |
| `DatasetQuery`  | `question`                                                                                                   |
| `OutputSchema`  | `answer`, `type` (`text`, `table`, `chart` ou `mixed`), `table` (opcional), `chart` (opcional) |
| `TableSchema`   | `columns` (lista de strings), `rows` (lista de listas de strings)                                          |
| `ChartSchema`   | `type` (`bar` ou `doughnut`), `labels`, `datasets`                                                   |
| `DatasetSchema` | `label`, `data` (lista de números)                                                                        |

O schema completo em OpenAPI pode ser consultado em `/openapi.json` (ou `/docs`) com a aplicação em execução.

---

## 🔐 Variáveis de Ambiente

| Variável   | Descrição                                                                            |
| ----------- | -------------------------------------------------------------------------------------- |
| `API_KEY` | Chave de API alternativa (para uso direto de outro provedor, configurável no código) |

Em produção, as chaves ficam armazenadas como **GitHub Secrets**, são injetadas no build da imagem por `--build-arg` e repassadas ao Cloud Run como variáveis de ambiente.

---

## 🛠️ Observações Importantes

* **OCR e idioma:** o Tesseract precisa do pacote de idioma `por` instalado. Sem ele, a extração de texto falha.
* **Imagens muito grandes:** se o Tesseract devolver o erro *image too large*, converta a imagem para PDF e envie novamente.
* **Qualidade das respostas:** o modelo configurado é o `gpt-5.6-luna`, sujeito à disponibilidade e à precisão da OpenAI.
* **Apólices de tipos diferentes:** o agente responde que não é possível comparar apólices de tipos de bens diferentes.
* **Documentos de exemplo:** . O frontend oferece exemplos de apólices na tela de upload.

## 📃 Licença

Código aberto sob **licença MIT**.
