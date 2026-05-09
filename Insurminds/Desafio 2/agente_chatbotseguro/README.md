# 🤖 Agente Inteligente Chatbot Seguro

Este projeto utiliza **Inteligência Artificial (LLMs)** e **RAG (Retrieval-Augmented Generation)** para automatizar o atendimento a segurados, processando manuais, apólices e bases de conhecimento para fornecer respostas precisas e naturais. [cite: 8]

## 🚀 O que este projeto faz

* **Automação de FAQ:** Responde a perguntas frequentes de segurados de forma instantânea. [cite: 8]
* **Inteligência Contextual (RAG):** Utiliza documentos técnicos localizados em `/rag_docs` (como manuais e termos de apólices) para garantir que a IA forneça informações baseadas em dados reais. [cite: 3, 8]
* **Processamento de Intenções:** Diferencia tipos de consultas e direciona fluxos conversacionais específicos. [cite: 8]

---

## 📜 Código Fonte Principal

O núcleo lógico do chatbot, incluindo a orquestração do LangChain e a interface Streamlit, pode ser acessado diretamente aqui:
* 🔗 **[agente_chatbotseguro.py](https://github.com/ajndantas/I2A2-Grupo_01/blob/master/Insurminds/Desafio%202/agente_chatbotseguro/Scripts/agente_chatbotseguro.py)** [cite: 8]

---

## ☁️ Infraestrutura e Deploy (GCP)

O projeto foi desenhado para rodar de forma escalável na **Google Cloud Platform (GCP)**, utilizando uma arquitetura de containers orquestrada via GitHub Actions. [cite: 8]

* **Hospedagem:** Implementado em uma **VM (Virtual Machine) na GCP**. [cite: 8]
* **Rede e Segurança:**
    * Utiliza **Nginx** como Proxy Reverso para gerenciar o tráfego nas portas 80 e 443. [cite: 8, nginx.conf]
    * Suporte a SSL via **Certbot**. [cite: nginx.conf]
* **CI/CD:** Pipeline automatizado (GitHub Actions) que realiza o build da imagem, envia para o GitHub Container Registry (GHCR) e executa o deploy via SSH na VM da GCP. [cite: 8, docker-image-agente_chatbotseguro.yml]

---

## 🔐 Gestão de Variáveis de Ambiente

As variáveis de ambiente são geridas de forma segura e persistente através de diferentes camadas:

### 1. GitHub Secrets (CI/CD)
As chaves sensíveis (`API_KEY_OPENROUTER`, `API_KEY`, `HUGGINGFACE_KEY`) são armazenadas nos **GitHub Secrets**. Durante o build, são passadas como `--build-arg`. [cite: docker-image-agente_chatbotseguro.yml]

### 2. Dockerfile (Persistência)
As variáveis são capturadas via `ARG` e fixadas na imagem via `ENV`, tornando-as disponíveis permanentemente para a aplicação Python via `os.getenv()`. [cite: 6, 7]

### 3. Docker Compose (Runtime)
No `docker-compose.yml`, as variáveis são injetadas no container para uso em tempo de execução. [cite: docker-compose.yml]

---

## 🐳 Execução com Docker

### 1️⃣ Configuração
* **Imagem Base:** Python 3.13-slim. [cite: Dockerfile]
* **Modelos:** Embeddings baixados localmente via `huggingface_models_download.py` para otimizar performance. [cite: 4]

### 2️⃣ Variáveis Necessárias
* `API_KEY_OPENROUTER`: Comunicação com LLMs. [cite: docker-compose.yml]
* `API_KEY`: Autenticação adicional. [cite: docker-compose.yml]
* `HUGGINGFACE_KEY`: Acesso a modelos e tokens. [cite: docker-compose.yml]

---

## ⚙️ Tecnologias Utilizadas

* 🧩 **LangChain** – Orquestração de RAG e memória conversacional. [cite: 8]
* 🤖 **OpenRouter** – Acesso aos modelos de linguagem (LLMs). [cite: 8]
* 🧱 **Streamlit** – Interface web interativa para o usuário. [cite: 8]
* 🐳 **Docker & Docker Compose** – Containerização e orquestração de serviços. [cite: 8]
* 🛡️ **Nginx** – Gateway de segurança e gerenciamento de subdomínios. [cite: 8]
* 🐙 **GitHub** – Hospedagem do código-fonte, gestão de versões e automação de CI/CD via GitHub Actions e armazenamento de imagens no GHCR. [cite: 8, docker-image-agente_chatbotseguro.yml]

---

## 📃 Licença

Código aberto sob **licença MIT**. [cite: 8]
