# 🌦️ Alerta Clima

## 🛠️ O que este projeto faz

Aplicação web que fornece **previsão do tempo atual e dos próximos 7 dias** para qualquer cidade informada pelo usuário, além de **alertas meteorológicos inteligentes** gerados por IA sempre que há condições de risco (tempestades, chuva forte, nevoeiro, neve, granizo, etc).

Principais funcionalidades:

* 📍 **Identificação de localização por IA:** o usuário informa apenas o nome da cidade e um LLM resolve a latitude/longitude, dispensando serviços externos de geocodificação.
* 🌡️ **Previsão atual:** temperatura máxima/mínima, nascer e pôr do sol, precipitação, probabilidade de chuva e rajadas de vento.
* 📅 **Previsão de 7 dias**
* 🚨 **Alertas inteligentes:** quando o código meteorológico (padrão WMO) indica uma condição adversa, um LLM gera um conselho contextual de meteorologia junto ao alerta.
* 💡 **Dicas de clima e lista de cidades:** endpoint que gera, via IA, dicas categorizadas (temperatura, tempestade, chuva, vento, umidade, radiação UV, saúde ocular, neblina, frio e inundação) e sugestões de cidades para consulta.
* 🖥️ **Frontend simples (HTML/CSS/JS):** interface de chat guiado com menu de opções (previsão atual, previsão de 7 dias, trocar cidade, sair).

---

## Tecnologias Utilizadas

* 🐍 **Python 3.13**
* ⚡ **FastAPI** – Framework web para exposição da API REST.
* 🦜 **LangChain + LangChain-OpenAI** – Orquestração das chamadas ao LLM (resolução de lat/long, geração de conselhos e dicas de clima).
* 🌍 **Open-Meteo API** – Fonte de dados meteorológicos (clima atual e previsão de 7 dias).
* 🧱 **HTML, CSS e JavaScript puro** – Interface web (chat guiado por menu).
* 🐳 **Docker** – Containerização da aplicação.
* 🐙 **GitHub Actions (CI/CD)** – Build da imagem Docker (GHCR) e deploy automatizado.
* ☁️ **GCP Cloud Run** – Hospedagem da aplicação em produção.

---

## ☁️ Infraestrutura e Deploy (GCP)

O deploy é automatizado via **GitHub Actions**, disparado a cada push na branch `master` que afete o diretório do projeto:

1. Build da imagem **Docker** e push para o **GitHub Container Registry (GHCR)**.
2. Encaminhamento da imagem da **GHCR** para o **Artifact Register** na **GCP**.
3. Deploy da imagem no **Cloud Run**

A chave `API_KEY` é repassada como variável de ambiente do serviço no Cloud Run.

---

## Implantação Local

### 📋 Pré-requisitos

- Python 3.13
- Uma chave de API compatível com o modelo configurado em `app/llm.py` (ex.: OpenAI).

---

## 🧩 Arquitetura da Aplicação

```
alerta_clima/
├── app/                      # Backend FastAPI
│   ├── main.py                # Ponto de entrada da aplicação (rotas, static files, sessão)
│   ├── llm.py                  # Configuração do modelo de linguagem (LLM)
│   ├── advice.py                # Geração de conselhos meteorológicos via LLM
│   ├── latlong.py                # Resolução de latitude/longitude da cidade via LLM
│   ├── request.py                 # Integração com a API Open-Meteo (clima atual/previsão/alerta)
│   ├── rotas/
│   │   ├── request.py               # Rotas /api/v1/current, /api/v1/forecast, /api/v1/city
│   │   └── tipsandcities.py          # Rotas /api/v1/tips, /api/v1/cities
│   └── modelos/                # Modelos Pydantic (Current, Forecast, Alert, Tips, City...)
├── frontend/                 # Interface web
│   ├── index.html
│   ├── css/style.css
│   ├── js/script.js
│   └── tipsandcities.py        # Geração de dicas e cidades sugeridas via LLM
├── Dockerfile
└── requirements.txt
```

### 🛠️ 1 - Instalação dos códigos

```bash
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
# .venv\Scripts\activate       # Windows

pip install -r requirements.txt
```

### 📦 2 - Instalação das dependências

```bash
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
# .venv\Scripts\activate       # Windows

pip install -r requirements.txt
```

### 🔐 3 - Configuração das variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
API_KEY=SUACHAVE_API
```

### ▶️ 4 - Execução local

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
```

A aplicação ficará disponível em:

```text
http://localhost:8003
```

---

## 📡 Endpoints da API

| Método | Rota                 | Descrição                                                      |
| ------- | -------------------- | ---------------------------------------------------------------- |
| GET     | `/`                | Retorna a página HTML do frontend                               |
| POST    | `/api/v1/city`     | Armazena a cidade informada na sessão do usuário               |
| GET     | `/api/v1/current`  | Retorna a previsão meteorológica atual da cidade em sessão    |
| GET     | `/api/v1/forecast` | Retorna a previsão dos próximos 7 dias da cidade em sessão    |
| GET     | `/api/v1/tips`     | Retorna dicas de clima geradas por IA, organizadas por categoria |
| GET     | `/api/v1/cities`   | Retorna uma lista de cidades sugeridas (brasileiras e globais)   |

A documentação interativa (Swagger) fica disponível em `/docs` após a aplicação estar em execução.

### 🔎 Detalhamento dos endpoints

#### `POST /api/v1/city`

Armazena a cidade na sessão do usuário. Corpo da requisição em `text/plain`:

```
Rio de Janeiro
```

Resposta (`200`): string de confirmação. Resposta (`422`): erro de validação (`HTTPValidationError`).

#### `GET /api/v1/current`

Retorna o objeto `Current` com a previsão atual da cidade em sessão:

```json
{
  "description": "Céu limpo",
  "weather_code": 0,
  "weather_icon": "☀️",
  "alert": { "message": "Céu limpo ☀️ - Nenhum alerta encontrado" },
  "temp_max": "29.5°C",
  "temp_min": "21.3°C",
  "sunrise": "06:12:00 no horário de Brasília",
  "sunset": "17:45:00 no horário de Brasília",
  "precip_prob": "10%",
  "precip": "0.0 mm",
  "wind_gusts": "18.4 km/h"
}
```

#### `GET /api/v1/forecast`

Retorna uma lista de objetos `Forecast` (um por dia, 7 dias), que estende `Current` com o campo `date`.

#### `GET /api/v1/tips`

Retorna o objeto `Tips`, com listas de dicas por categoria: `temp`, `tempest`, `rain`, `wind`, `humidity`, `uv`, `eye`, `fog`, `cold` e `flood`.

#### `GET /api/v1/cities`

Retorna uma lista de objetos `City`:

```json
[
  { "city": "Rio de Janeiro", "badge": "RJ", "type": "brasileira" },
  { "city": "Londres", "badge": "GB", "type": "global" }
]
```

### 🧬 Schemas principais

| Schema       | Campos                                                                                                                                                           |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Alert`    | `message`                                                                                                                                                      |
| `Current`  | `description`, `weather_code`, `weather_icon`, `alert`, `temp_max`, `temp_min`, `sunrise`, `sunset`, `precip_prob`, `precip`, `wind_gusts` |
| `Forecast` | Todos os campos de`Current` + `date`                                                                                                                         |
| `City`     | `city`, `badge`, `type` (`brasileira` ou `global`)                                                                                                     |
| `Tips`     | `temp`, `tempest`, `rain`, `wind`, `humidity`, `uv`, `eye`, `fog`, `cold`, `flood` (listas de strings)                                       |

O schema completo em OpenAPI 3.1 pode ser consultado em `/openapi.json` (ou `/docs`) após a aplicação estar em execução.

---

## 🔐 Variáveis de Ambiente

| Variável              | Descrição                                                                      |
| ---------------------- | -------------------------------------------------------------------------------- |
| `API_KEY`            | Chave de autenticação usada pelo LLM configurado em`app/llm.py`              |
| `API_KEY_OPENROUTER` | Chave alternativa para uso via OpenRouter (opcional, configurável em`llm.py`) |

As chaves sensíveis são armazenadas como **GitHub Secrets** e injetadas no build da imagem Docker via `--build-arg`.

---

## 💻

## 🛠️ Observações Importantes

- Os dados meteorológicos são obtidos em tempo real da API pública **Open-Meteo**, sem necessidade de chave de API.
- A resolução de latitude/longitude da cidade informada é feita por um LLM, portanto está sujeita à disponibilidade e precisão do modelo configurado.
- A cidade selecionada é mantida em **sessão** (`SessionMiddleware`), portanto é necessário que o cliente aceite cookies de sessão para o correto funcionamento do fluxo de navegação.

## 📃 Licença

Código aberto sob **licença MIT**.
