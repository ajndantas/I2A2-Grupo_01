# 🤖 Agente Análise de Fraudes em Cartões de Crédito

Fala, dev! 👋
Esse projeto é um **sistema inteligente para análise de fraudes em cartões de crédito**.
A ideia é simples: você faz o upload dos seus dados (CSV), escolhe perguntas já pré-configuradas ou faz novas análises, e a IA devolve gráficos, tabelas e até uma conclusão geral sobre os padrões encontrados nos dados.

---

## 🎯 Objetivo

O sistema ajuda a:

- Entender melhor os dados de transações financeiras 🏦
- Descobrir padrões suspeitos 🔎
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
- LangChain + [TNG: DeepSeek R1T2 Chimera (free)](https://openrouter.ai/tngtech/deepseek-r1t2-chimera:free) LLM 🤯
- Pandas, SQLAlchemy e [Plotly](https://plotly.com/javascript/)📊

---

## 🚀 Como rodar o projeto

Faça o download do código e do arquivo requirements.txt:

[Script agente_fraude_cartao.py](https://github.com/ajndantas/I2A2-Grupo_01/blob/master/Desafio%20Extra%20Fraude%20Cartao%20de%20Credito/agente_fraude_cartao/Scripts/agente_fraudecredito.py)

[Arquivo requirements.txt](https://github.com/ajndantas/I2A2-Grupo_01/blob/master/Desafio%20Extra%20Fraude%20Cartao%20de%20Credito/agente_fraude_cartao/requirements.txt)

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

Arquivo com os dados para a análise -> [creditcard.zip](https://github.com/ajndantas/I2A2-Grupo_01/blob/master/Desafio%20Extra%20Fraude%20Cartao%20de%20Credito/agente_fraude_cartao/Scripts/creditcard.zip)

---

## 🖥️ Demo Online

Não quer instalar nada? A gente tem uma versão de testes hospedada aqui 👉
[🔗 Acesse a demo](https://agente-fraude-cartao-credito.streamlit.app/)

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
