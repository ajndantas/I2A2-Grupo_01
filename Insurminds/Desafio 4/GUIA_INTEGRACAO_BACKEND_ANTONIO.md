# FiscalMind - Guia de integração do frontend com o FastAPI

Este documento descreve como conectar o frontend do FiscalMind ao backend FastAPI. O frontend foi desenvolvido em HTML, CSS e JavaScript, sem Streamlit, e já oferece:

- upload de arquivo ZIP;
- tela de processamento;
- resumo da base carregada;
- chat para perguntas em linguagem natural;
- respostas em texto, tabela e gráfico;
- tratamento de erros e estados de carregamento.

## 1. Arquivos relevantes

```text
frontend/
├── index.html
├── css/
│   └── styles.css
└── js/
    ├── config.js     # URL da API e ativação do modo real
    ├── api.js        # Chamadas HTTP ao FastAPI
    ├── app.js        # Comportamento da interface
    └── mock.js       # Respostas usadas somente no modo demonstração
```

Para integrar o backend, normalmente será necessário modificar apenas `frontend/js/config.js`. Se os endpoints existentes utilizarem outro formato, será necessário adaptar também `frontend/js/api.js`.

## 2. Configuração do frontend

Abra `frontend/js/config.js` e altere:

```javascript
export const CONFIG = {
  apiBaseUrl: "https://ENDERECO-DO-BACKEND",
  demoMode: false,
  maxFileSize: 500 * 1024 * 1024
};
```

- `apiBaseUrl`: endereço público do FastAPI, sem barra no final;
- `demoMode: false`: desativa as respostas simuladas e utiliza a API real;
- `maxFileSize`: tamanho máximo permitido pelo frontend.

## 3. Endpoint de upload

### Requisição

```http
POST /api/datasets/upload
Content-Type: multipart/form-data
```

O arquivo deve ser enviado no campo `file`:

```python
@app.post("/api/datasets/upload")
def upload_dataset(file: UploadFile = File(...)):
    ...
```

### Resposta esperada

```json
{
  "dataset_id": "ds_123",
  "status": "ready",
  "name": "202401_NFs.zip",
  "summary": {
    "files": 2,
    "invoices": 100,
    "items": 565,
    "period": "01/2024",
    "quality_score": 98,
    "quality_message": "Estrutura válida e pronta para consulta.",
    "detected_files": [
      "202401_NFs_Cabecalho.csv",
      "202401_NFs_Itens.csv"
    ]
  }
}
```

### Campos obrigatórios

| Campo                       | Tipo               | Finalidade                                  |
| --------------------------- | ------------------ | ------------------------------------------- |
| `dataset_id`              | string             | Identificar a base nas consultas seguintes  |
| `status`                  | string             | Informar que o processamento foi concluído |
| `name`                    | string             | Mostrar o nome do ZIP no frontend           |
| `summary.files`           | inteiro            | Quantidade de CSVs encontrados              |
| `summary.invoices`        | inteiro            | Quantidade de notas fiscais                 |
| `summary.items`           | inteiro            | Quantidade de itens                         |
| `summary.period`          | string             | Período identificado                       |
| `summary.quality_score`   | inteiro de 0 a 100 | Indicador de qualidade                      |
| `summary.quality_message` | string             | Explicação resumida da qualidade          |
| `summary.detected_files`  | lista de strings   | Nomes dos arquivos processados              |

O frontend só deve receber a resposta de sucesso quando a base estiver pronta para consulta. Caso o processamento seja assíncrono, será necessário criar um endpoint de acompanhamento e adaptar `api.js`.

## 4. Endpoint de consulta

### Requisição

```http
POST /api/datasets/{dataset_id}/query
Content-Type: application/json
```

Corpo:

```json
{
  "question": "Quais foram os cinco maiores fornecedores?"
}
```

Exemplo FastAPI:

```python
from pydantic import BaseModel

class QuestionRequest(BaseModel):
    question: str

@app.post("/api/datasets/{dataset_id}/query")
def query_dataset(dataset_id: str, request: QuestionRequest):
    ...
```

## 5. Formatos de resposta

O campo `type` aceita `text`, `table`, `chart` ou `mixed`.

### Somente texto

```json
{
  "answer": "A base contém 100 notas fiscais, totalizando R$ 3.371.754,84.",
  "type": "text"
}
```

### Texto com tabela

```json
{
  "answer": "Estes são os cinco maiores fornecedores.",
  "type": "table",
  "table": {
    "columns": ["Fornecedor", "Valor total", "Notas"],
    "rows": [
      ["Empresa A", "R$ 1.250.000,00", 35],
      ["Empresa B", "R$ 980.000,00", 28]
    ]
  }
}
```

### Texto com gráfico

```json
{
  "answer": "São Paulo apresentou o maior valor total.",
  "type": "chart",
  "chart": {
    "type": "bar",
    "labels": ["SP", "RJ", "MG"],
    "datasets": [
      {
        "label": "Valor total (R$)",
        "data": [1250000, 980000, 760000]
      }
    ]
  }
}
```

### Texto, tabela e gráfico

```json
{
  "answer": "Os cinco maiores fornecedores concentram 42% do valor total.",
  "type": "mixed",
  "table": {
    "columns": ["Fornecedor", "Valor total", "Notas"],
    "rows": [
      ["Empresa A", "R$ 1.250.000,00", 35],
      ["Empresa B", "R$ 980.000,00", 28]
    ]
  },
  "chart": {
    "type": "bar",
    "labels": ["Empresa A", "Empresa B"],
    "datasets": [
      {
        "label": "Valor total (R$)",
        "data": [1250000, 980000]
      }
    ]
  }
}
```

### Tipos de gráficos aceitos

- `bar`;
- `line`;
- `doughnut`;
- `pie`.

Os valores de `chart.datasets[].data` devem ser numéricos, sem `R$`, separadores de milhar ou outros textos. Os valores exibidos nas tabelas podem chegar formatados.

## 6. Configuração de CORS

O FastAPI precisa autorizar o endereço em que o frontend será executado:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "https://ENDERECO-PUBLICADO-DO-FRONTEND"
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"]
)
```

Evitar `allow_origins=["*"]` na versão publicada. Utilizar as origens específicas do frontend.

## 7. Tratamento de erros

O frontend tenta ler mensagens nos campos `detail` ou `message`.

Exemplo:

```json
{
  "detail": "Nenhum arquivo CSV foi encontrado no ZIP."
}
```

Status HTTP recomendados:

| Status | Situação                               |
| -----: | ---------------------------------------- |
|    400 | ZIP inválido ou conteúdo incompatível |
|    404 | `dataset_id` inexistente ou expirado   |
|    413 | Arquivo acima do limite                  |
|    422 | Pergunta ou requisição inválida       |
|    500 | Falha interna de processamento           |

## 8. Requisitos para arquivos grandes

O arquivo `202505_NFe.zip` possui aproximadamente 381 MB descompactado, com:

- 150.976 notas fiscais;
- 549.431 itens.

Por isso:

- não carregar todo o conteúdo simultaneamente na memória;
- processar os CSVs em blocos ou utilizar um banco analítico;
- configurar o limite de upload no Cloud Run ou serviço utilizado;
- evitar que proxies encerrem a requisição antes do fim;
- manter o `dataset_id` associado à base já processada;
- excluir arquivos temporários após a expiração da sessão.

## 9. Se o backend existente possuir outro contrato

Não é obrigatório modificar toda a API. Existem duas alternativas:

1. adaptar os endpoints do FastAPI ao contrato descrito neste documento; ou
2. adaptar somente `frontend/js/api.js` para converter as respostas existentes ao formato esperado pela interface.

Para a segunda alternativa, enviar:

- link do `/docs` do FastAPI;
- arquivo ou link do `/openapi.json`;
- exemplo real da resposta do upload;
- exemplo real da resposta de consulta;
- informação sobre processamento síncrono ou assíncrono.

## 10. Teste rápido de integração

1. Iniciar o FastAPI na porta 8000.
2. Configurar `apiBaseUrl: "http://localhost:8000"`.
3. Configurar `demoMode: false`.
4. Servir o frontend:

```bash
python -m http.server 5500 --directory frontend
```

5. Acessar `http://localhost:5500`.
6. Enviar primeiro `202401_NFs.zip`, por ser menor.
7. Confirmar o resumo: 2 CSVs, 100 notas e 565 itens.
8. Testar as perguntas:
   - Qual foi o valor total das notas?
   - Quais foram os cinco maiores fornecedores?
   - Qual produto apresentou o maior valor?
   - Qual UF concentrou o maior valor?
   - Quais foram os principais CFOPs?
9. Após validar a base pequena, testar `202505_NFe.zip`.

## Checklist final

- [ ] URL do backend configurada em `config.js`.
- [ ] `demoMode` alterado para `false`.
- [ ] Endpoint de upload disponível.
- [ ] Endpoint de consulta disponível.
- [ ] Respostas compatíveis com o contrato.
- [ ] CORS liberado para a origem do frontend.
- [ ] Limite de upload compatível com a base de 2025.
- [ ] Teste concluído com a base de 2024.
- [ ] Tratamento de erros validado.
- [ ] Chaves de API mantidas somente no backend.

---

Frontend: FiscalMind
Desafio 4 - Interface Inteligente para Consulta de Arquivos CSV
