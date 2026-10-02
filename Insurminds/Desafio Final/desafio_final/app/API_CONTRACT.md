# Contrato de integração do FiscalMind

O frontend pode operar em modo demonstrativo ou conectado a uma API. Para conectar o FastAPI, altere `demoMode` para `false` e informe `apiBaseUrl` em `frontend/js/config.js`.

## Upload

`POST /api/datasets/upload` com `multipart/form-data`, campo `file`.

Resposta esperada:

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
    "quality_message": "Estrutura consistente.",
    "detected_files": ["cabecalho.csv", "itens.csv"]
  }
}
```

## Consulta

`POST /api/datasets/{dataset_id}/query`

```json
{ "question": "Quais foram os cinco maiores fornecedores?" }
```

A API poderá responder com `type` igual a `text`, `table`, `chart` ou `mixed`. Os campos ausentes não são renderizados.

```json
{
  "answer": "Os cinco maiores fornecedores representam 42% do valor total.",
  "type": "mixed",
  "table": {
    "columns": ["Fornecedor", "Valor total"],
    "rows": [["Fornecedor A", "R$ 1.250.000,00"]]
  },
  "chart": {
    "type": "bar",
    "labels": ["Fornecedor A"],
    "datasets": [{ "label": "Valor total", "data": [1250000] }]
  }
}
```

## CORS

O backend deverá liberar a origem em que o frontend for publicado. Durante desenvolvimento, normalmente `http://localhost:5500` ou `http://127.0.0.1:5500`.
