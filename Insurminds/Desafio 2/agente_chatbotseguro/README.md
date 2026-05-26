# 🤖 Agente Inteligente Chatbot Seguro

Este projeto utiliza **Inteligência Artificial (LLMs)** e **RAG (Retrieval-Augmented Generation)** para automatizar o atendimento a segurados, processando manuais, apólices e bases de conhecimento para fornecer respostas precisas e naturais.

---

## 🚀 Demonstração ao Vivo

O projeto está implantado e disponível para testes em tempo real na infraestrutura da **Google Cloud Platform (GCP)**:

🔗 **[Acessar Demo do Agente Chatbot Seguro](https://agente-chatbotseguro-574973424283.us-central1.run.app)**

---

## 🛠️ O que este projeto faz

* **Automação de FAQ:** Responde a perguntas frequentes de segurados de forma instantânea.
* **Inteligência Contextual (RAG):** Utiliza documentos técnicos localizados em [/rag_docs](https://github.com/ajndantas/I2A2-Grupo_01/tree/master/Insurminds/Desafio%202/agente_chatbotseguro/Scripts/rag_docs) (como manuais e termos de apólices) para garantir que a IA forneça informações baseadas em dados reais.
* **Processamento de Intenções:** Diferencia tipos de consultas e direciona fluxos conversacionais específicos.

---

## 📜 Código Fonte Principal

O núcleo lógico do chatbot, incluindo a orquestração do LangChain e a interface Streamlit, pode ser acessado diretamente aqui:

* 🔗 **[agente_chatbotseguro.py](https://github.com/ajndantas/I2A2-Grupo_01/blob/master/Insurminds/Desafio%202/agente_chatbotseguro/Scripts/agente_chatbotseguro.py)**
* 🔗 **[Frontend Streamlit app.py](https://github.com/ajndantas/I2A2-Grupo_01/blob/master/Insurminds/Desafio%202/agente_chatbotseguro/Scripts/app.py)**

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

A chave sensível (`API_KEY_OPENROUTER`) é armazenada nos **GitHub Secrets**. Durante o build, é passada como `--build-arg`.

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
* 🐙 **GitHub** – Hospedagem do código-fonte e automação de CI/CD.
* ☁️ **GCP (Google Cloud Platform)** – Infraestrutura de nuvem e hospedagem em VM.

---

# 💻 Implantação Local

Caso deseje executar o projeto localmente para fins de desenvolvimento, testes ou estudos, siga os passos abaixo.

## 📋 Pré-requisitos

Antes de iniciar, certifique-se de possuir instalado:

- Python 3.13
- Conta com acesso à API utilizada pelo OpenRouter

## 📦 Instalação das Dependências (Execução Local sem Docker)

Crie e ative um ambiente virtual:

### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

---

## 🔐 Configuração das Variáveis de Ambiente

Crie um arquivo `.env` dentro do diretório Scripts do ambiente virtual, contendo as variáveis necessárias:

```
cd .venv\Scripts
```

```env
API_KEY_OPENROUTER=SEU_TOKEN
```

## 📥 Instalando os códigos

Faça o download dos códigos abaixo, para dentro do diretório Scripts no ambiente virtual:

```bash
cd .venv\Scripts
```

🔗 **[agente_chatbotseguro.py](https://github.com/ajndantas/I2A2-Grupo_01/blob/master/Insurminds/Desafio%202/agente_chatbotseguro/Scripts/agente_chatbotseguro.py)**

🔗 **[app.py](https://github.com/ajndantas/I2A2-Grupo_01/blob/master/Insurminds/Desafio%202/agente_chatbotseguro/Scripts/app.py)**

---

## 🤖 Download do Modelo de Embedding

O projeto utiliza um modelo local ([all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)) do Hugging Face para embeddings.

- Faça o download do código [huggingface_models_download.py](https://github.com/ajndantas/I2A2-Grupo_01/blob/master/Insurminds/Desafio%202/agente_chatbotseguro/Scripts/huggingface_models_download.py) para dentro do diretório Scripts no ambiente virtual:
- De dentro desse diretório, execute o script responsável pelo download:

```bash
cd .venv\Scripts
python huggingface_models_download.py
```

Os modelos serão armazenados localmente para melhorar a performance e reduzir chamadas externas.

## 📁 Documentos da base de consulta

O diretório [/rag_docs](https://github.com/ajndantas/I2A2-Grupo_01/tree/master/Insurminds/Desafio%202/agente_chatbotseguro/Scripts/rag_docs), dentro de Scripts, deve conter os documentos utilizados pelo mecanismo RAG, como:

- Apólices
- FAQs
- Manuais técnicos
- Documentação de seguros

Esses arquivos são utilizados como base contextual para respostas da IA.

## ▶️ Execução Local com Streamlit

Após instalar as dependências, configurar as variáveis e baixar o modelo de embedding, execute o comando a seguir:

```bash
streamlit run app.py
```

O sistema ficará disponível em:

```text
http://localhost:8501
```

---

## 🛠️ Observações Importantes

- Certifique-se de que as portas `8501`, `80` e `443` estejam disponíveis.
- O primeiro carregamento dos modelos pode demorar alguns minutos.

## 📃 Licença

Código aberto sob **licença MIT**.
