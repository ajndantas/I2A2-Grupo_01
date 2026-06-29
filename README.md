# 🚀 Portfólio de Inteligência Artificial

Bem-vindo(a)! Sou Antonio Dantas, Analista de Sistemas Sênior focado no desenvolvimento de **aplicações práticas de IA, Engenharia de Dados e Automação de Workflows**. Aqui você encontrará soluções prontas para produção que unem **LLMs, Sistemas de Agentes e Visão Computacional** para resolver desafios reais de negócios.

Querendo entrar em contato, fique à vontade para se conectar comigo no Linkedin.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Conectar-blue?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/antoniodantasia/)

---

## 🛠️ Projetos em Destaque

| Projeto                                        | Solução Prática                                                                       | Stack Principal                        | Links                                                                                                                                                                                                        |
| :--------------------------------------------- | :--------------------------------------------------------------------------------------- | :------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **🤖 Agente Inteligente Chatbot Seguro** | FAQ automatizado para segurados via RAG com documentos técnicos de apólices e manuais. | Python, LangChain, OpenAI, Docker, GCP | [Demonstração](https://agente-chatbotseguro-574973424283.us-central1.run.app) \| [Código](https://github.com/ajndantas/I2A2-Grupo_01/tree/master/Insurminds/Desafio%202#-agente-inteligente-chatbot-seguro) |
| **🧾 Agente de Documentos Fiscais**      | OCR e LLM para extração e consulta de NF-e via linguagem natural.                      | Python, LangChain, OpenAI, Docker, GCP | [Demonstração](https://agente-nfs-574973424283.us-central1.run.app) \| [Código](https://github.com/ajndantas/I2A2-Grupo_01/tree/master/Desafio%202%20-%20Projeto%20-%2011062025#readme)                     |
| **🤖 Agente EDA AI**                     | Análise exploratória de dados automatizada com geração de insights.                  | Python, LangChain, OpenAI, Docker, GCP | [Demonstração](https://agente-eda-574973424283.us-central1.run.app) \| [Código](https://github.com/ajndantas/I2A2-Grupo_01/tree/master/Desafio%20Extra%20Fraude%20Cartao%20de%20Credito#readme)             |

---

## 🤖 Agente Inteligente Chatbot Seguro

Aplicação de FAQ inteligente voltada para segurados, que responde perguntas frequentes de forma instantânea utilizando **Inteligência Contextual (RAG)**. O sistema consulta documentos técnicos locais — como manuais e termos de apólices — para garantir que a IA forneça informações baseadas em dados reais.

* **🎯 Impacto:** Automação do atendimento a segurados com respostas contextualizadas e precisas, reduzindo a carga operacional de suporte e aumentando a qualidade das respostas através de base documental verificada.
* **🏗️ Arquitetura:** Ingestão de documentos (PDF/manuais) -> Embeddings locais (HuggingFace `all-MiniLM-L6-v2`) -> Orquestração RAG (LangChain + FAISS) -> Interface Streamlit -> Deploy containerizado na Cloud Run.
* **🧠 Tecnologias:** ![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) ![LangChain](https://img.shields.io/badge/LangChain-1C3C3A?style=flat-square&logo=langchain&logoColor=white) ![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat-square&logo=openai&logoColor=white) ![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white) ![Google Cloud](https://img.shields.io/badge/Google_Cloud-4285F4?style=flat-square&logo=google-cloud&logoColor=white) ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white) , `RAG, FAISS, HuggingFace`.

🌐 **[Acesse a Demonstração Ativa](https://agente-chatbotseguro-574973424283.us-central1.run.app)** | 📂 **[Repositório do Código](https://github.com/ajndantas/I2A2-Grupo_01/tree/master/Insurminds/Desafio%202/agente_chatbotseguro)**

---

## 🧾 Agente de Documentos Fiscais (NF-e)

Aplicação inteligente que combina **OCR e Modelos de Linguagem (LLMs)** para interpretar e estruturar dados de notas fiscais complexas disponibilizadas em formato PDF, imagem ou CSV. O sistema permite auditorias rápidas através de perguntas em linguagem natural diretamente sobre os dados extraídos.

* **🎯 Impacto:** Redução do tempo de conferência manual de notas fiscais através de extração automatizada de dados com alta tolerância a falhas de formatação.
* **🏗️ Arquitetura:** Pipeline de ingestão -> Extração de texto (Tesseract/OpenCV) -> Orquestração de contexto RAG (LangChain) -> Deploy em container gerenciado.
* **🧠 Tecnologias:** ![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) ![LangChain](https://img.shields.io/badge/LangChain-1C3C3A?style=flat-square&logo=langchain&logoColor=white) ![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat-square&logo=openai&logoColor=white) ![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white) ![Google Cloud](https://img.shields.io/badge/Google_Cloud-4285F4?style=flat-square&logo=google-cloud&logoColor=white) ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white) ,`Tesseract OCR`, `SQLAlchemy`, `Pandas`.

🌐 **[Acesse a Demonstração Ativa](https://agente-nfs-574973424283.us-central1.run.app)** | 📂 **[Repositório do Código](https://github.com/ajndantas/I2A2-Grupo_01/tree/master/Desafio%202%20-%20Projeto%20-%2011062025#readme)**

---

## 🤖 Agente EDA AI — Análise Exploratória Inteligente de Dados

Interface analítica que abstrai a complexidade do tratamento inicial de dados. Ao fazer o upload de qualquer dataset padronizado (CSV), um agente autônomo baseado em IA analisa o comportamento das variáveis, gerando gráficos iterativos e relatórios preditivos de forma imediata.

* **🎯 Impacto:** Automação de pipelines de Analytics para tomada de decisão ágil, identificando anomalias e padrões de fraude sem a necessidade de codificação manual de scripts de visualização.
* **🧠 Tecnologias:** ![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) ![LangChain](https://img.shields.io/badge/LangChain-1C3C3A?style=flat-square&logo=langchain&logoColor=white) ![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat-square&logo=openai&logoColor=white) ![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white) ![Google Cloud](https://img.shields.io/badge/Google_Cloud-4285F4?style=flat-square&logo=google-cloud&logoColor=white) ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white) , `Plotly`, `Pandas`.

🌐 **[Acesse a Demonstração Ativa](https://agente-eda-574973424283.us-central1.run.app)** | 📂 **[Repositório do Código](https://github.com/ajndantas/I2A2-Grupo_01/tree/master/Desafio%20Extra%20Fraude%20Cartao%20de%20Credito#readme)**

---

## 🧠 Diretrizes do Portfólio

O desenvolvimento destes projetos é focado em engenharia rigorosa para resolver gargalos corporativos de dados:

- **Produção e Escalabilidade:** Infraestrutura moderna em nuvem com isolamento em containers e deploys resilientes.
- **Autonomia de Agentes:** Implementação de ferramentas onde a IA atua ativamente na tomada de decisão sobre os fluxos de dados.
- **Raciocínio Avançado:** Integração de modelos de fronteira focados em extração estruturada (JSON Output) e lógica analítica complexa.

---

*Construído com Python, Inteligência Artificial e foco em automação avançada. ☕*