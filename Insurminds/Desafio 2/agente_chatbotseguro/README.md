# 🤖 Agente Inteligente Chatbot Seguro

Este projeto utiliza **Inteligência Artificial (LLMs)** e **RAG (Retrieval-Augmented Generation)** para automatizar o atendimento a segurados, processando manuais, apólices e bases de conhecimento para fornecer respostas precisas e naturais.

## 🚀 O que este projeto faz

* **Automação de FAQ:** Responde a perguntas frequentes de segurados de forma instantânea^^.
* **Inteligência Contextual (RAG):** Utiliza documentos técnicos localizados em `/rag_docs` (como manuais e termos de apólices) para garantir que a IA não alucine e forneça informações baseadas em dados reais.
* **Processamento de Intenções:** Diferencia tipos de consultas e direciona fluxos conversacionais específicos.

---

## ☁️ Infraestrutura e Deploy (GCP)

O projeto foi desenhado para rodar de forma escalável na  **Google Cloud Platform (GCP)** , utilizando uma arquitetura de containers orquestrada via GitHub Actions.

* **Hospedagem:** Implementado em uma  **VM (Virtual Machine) na GCP** .
* **Rede e Segurança:**
  * Utiliza **Nginx** como Proxy Reverso.
* **CI/CD:** Pipeline automatizado que realiza o build da imagem e executa comandos via SSH diretamente na instância da GCP para atualização do serviço.

---

## 🐳 Execução com Docker

O serviço é distribuído como um container Docker, facilitando a portabilidade entre ambientes de desenvolvimento e produção na nuvem.

### 1️⃣ Requisitos

* Chave de API para a LLM do **OpenRouter** (configurada como segredo no GitHub ou variável de ambiente).

### 2️⃣ Variáveis de Ambiente

O container utiliza a variável `API_KEY_OPENROUTER` para comunicação com o cérebro da IA.

---

## ⚙️ Tecnologias Utilizadas

* 🧩 **LangChain** – Orquestração de RAG e memória conversacional.
* 🤖 **OpenRouter** – Acesso aos modelos de linguagem mais modernos.
* 🧱 **Streamlit** – Interface web para interação com o segurado.
* 🐳 **Docker** – Containerização da aplicação.
* 🛡️ **Nginx** – Gateway de segurança e gerenciamento de portas na GCP.
* 📓 **Jupyter** – O código principal reside em `agente_chatbotseguro.ipynb` e é convertido automaticamente para produção.

---


## 📃 Licença

Código aberto sob  **licença MIT** .
