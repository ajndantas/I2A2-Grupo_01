# 🤖 Agente EDA AI

Fala, dev! 👋
Esse projeto é um **sistema inteligente para realizar análise exploratória de dados, a partir de um dataset disponibilizado**.
A ideia é simples: você faz o upload dos seus dados (CSV), escolhe perguntas já pré-configuradas ou faz novas análises, e a IA devolve gráficos, tabelas e até uma conclusão geral sobre os padrões encontrados nos dados.

---

## 🎯 Objetivo

O sistema ajuda a:

- Entender melhor os dados fornecidos 🏦
- Descobrir padrões 🔎
- Identificar outliers e anomalias 🚨
- Visualizar relações entre variáveis com gráficos maneiros 📊
- Ter uma conclusão geral da análise sem dor de cabeça 😎

---

## ⚙️ Como funciona?

O projeto roda em **Streamlit** e usa **LangChain + LLMs (Large Language Models)** para processar os dados.

Ele é dividido em **3 agentes** principais:

- **Agente 1 (Aquisição de Documentos)** → faz o upload e organiza as perguntas
- **Agente 2 (Análise de Dados)** → roda queries SQL e devolve respostas formatadas em HTML (com gráficos e tabelas)
- **Agente 3 (Conclusão Geral)** → gera um relatório consolidado com os insights finais

---

## 🛠️ Tecnologias que usamos

- Python 🐍
- Streamlit 💻
- LangChain + [Deepseek-R1t2-chimera](https://huggingface.co/tngtech/DeepSeek-TNG-R1T2-Chimera) LLM 🤯
- Pandas, SQLAlchemy e [Plotly](https://plotly.com/javascript/)📊

---

## 🚀 Como rodar o projeto

Faça o download do código, do arquivo requirements.txt, do script plotly.js para geração de gráficos e dos arquivos do tokenizers para contagem de tokens:

[Script agente_eda.py](https://github.com/ajndantas/I2A2-Grupo_01/blob/master/Desafio%20Extra%20Fraude%20Cartao%20de%20Credito/agente_fraude_cartao/Scripts/agente_eda.py)

[Arquivo requirements.txt](https://github.com/ajndantas/I2A2-Grupo_01/blob/master/Desafio%20Extra%20Fraude%20Cartao%20de%20Credito/agente_fraude_cartao/requirements.txt)

[tokenizer.json](https://github.com/ajndantas/I2A2-Grupo_01/blob/master/Desafio%20Extra%20Fraude%20Cartao%20de%20Credito/agente_fraude_cartao/Scripts/tokenizer.json)

[tokenizer_config.json](https://github.com/ajndantas/I2A2-Grupo_01/blob/master/Desafio%20Extra%20Fraude%20Cartao%20de%20Credito/agente_fraude_cartao/Scripts/tokenizer_config.json)

Crie um ambiente virtual e ative:

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Crie o arquivo `.env` com sua chave de API gerada no provedor **[Openrouter](https://openrouter.ai/)**:

```ini
API_KEY="sua_chave_aqui"
```

Rode a aplicação:

```bash
streamlit run agente_fraudecredito.py
```

Arquivo exemplo com os dados para a análise -> [creditcard.zip](https://github.com/ajndantas/I2A2-Grupo_01/blob/master/Desafio%20Extra%20Fraude%20Cartao%20de%20Credito/agente_fraude_cartao/Scripts/creditcard.zip)

---

## 🖥️ Demo Online

Não quer instalar nada? A gente tem uma versão de testes hospedada aqui 👉
[🔗 Acesse a demo](https://agente-eda-ai.streamlit.app/)

---

## 📑 Perguntas prontas para usar

Você já pode mandar perguntas pré-cadastradas, como:

- "Quais são os tipos de dados (numéricos, categóricos)?"
- "Existem padrões ou tendências temporais?"
- "Existem valores atípicos nos dados?"
- "Como as variáveis estão relacionadas umas com as outras?"

E muitas outras!

---

## 💾 Memória do sistema

O app guarda o **histórico das perguntas e respostas** durante a sessão, então você consegue ir montando suas conclusões até decidir gerar o **relatório final**.

---

## 📜 Licença

Este projeto é open-source e está sob a licença MIT.

---

Feito com ❤️ e algumas madrugadas de café ☕
