# 🤖 Agente Inteligente Chatbot Seguro

Este projeto utiliza **Inteligência Artificial (LLMs)** e **RAG (Retrieval-Augmented Generation)** para automatizar o atendimento a segurados, processando manuais, apólices e bases de conhecimento para fornecer respostas precisas e naturais.

## 🚀 O que este projeto faz

* **Automação de FAQ:** Responde a perguntas frequentes de segurados de forma instantânea.
* **Inteligência Contextual (RAG):** Utiliza documentos técnicos localizados em `/rag_docs` (como manuais e termos de apólices) para garantir que a IA forneça informações baseadas em dados reais.
* **Processamento de Intenções:** Diferencia tipos de consultas e direciona fluxos conversacionais específicos.

---

## 📜 Código Fonte Principal

O núcleo lógico do chatbot, incluindo a orquestração do LangChain e a interface Streamlit, pode ser acessado diretamente aqui:

* 🔗 **[agente_chatbotseguro.py](https://github.com/ajndantas/I2A2-Grupo_01/blob/master/Insurminds/Desafio%202/agente_chatbotseguro/Scripts/agente_chatbotseguro.py)**

---

## ☁️ Infraestrutura e Deploy (GCP)

O projeto foi desenhado para rodar de forma escalável na **Google Cloud Platform (GCP)**, utilizando uma arquitetura de containers orquestrada via GitHub Actions.

* **Hospedagem:** Implementado em uma **VM (Virtual Machine) na GCP**.
* **Rede e Segurança:**
  * Utiliza **Nginx** como Proxy Reverso para gerenciar o tráfego nas portas 80 e 443.
  * Suporte a SSL via **Certbot**.
* **CI/CD:** Pipeline automatizado (GitHub Actions) que realiza o build da imagem, envia para o GitHub Container Registry (GHCR) e executa o deploy via SSH na VM da GCP.

---

## 🔐 Gestão de Variáveis de Ambiente

As variáveis de ambiente são geridas de forma segura e persistente através de diferentes camadas:

### GitHub Secrets (CI/CD)

As chaves sensíveis (`API_KEY_OPENROUTER`, `API_KEY`, `HUGGINGFACE_KEY`) são armazenadas nos **GitHub Secrets**. Durante o build, são passadas como `--build-arg`

---

## 🐳 Execução com Docker

### 1️⃣ Configuração

* **Imagem Base:** Python 3.13-slim.
* **Modelos:** Embeddings baixados localmente via `huggingface_models_download.py` para otimizar performance.

### 2️⃣ Variáveis Necessárias

* `API_KEY_OPENROUTER`: Comunicação com LLMs.

---

## ⚙️ Tecnologias Utilizadas

* 🧩 **LangChain** – Orquestração de RAG e memória conversacional.
* 🤖 **OpenRouter** – Acesso aos modelos de linguagem (LLMs).
* 🧱 **Streamlit** – Interface web interativa para o usuário.
* 🐳 **Docker & Docker Compose** – Containerização e orquestração de serviços.
* 🛡️ **Nginx** – Gateway de segurança e gerenciamento de subdomínios.
* 🐙 **GitHub** – Hospedagem do código-fonte, gestão de versões e automação de CI/CD via GitHub Actions.
* ☁️ **GCP (Google Cloud Platform)** – Infraestrutura de nuvem e hospedagem em Máquina Virtual (VM).

---

## 📃 Licença

Código aberto sob **licença MIT**.
