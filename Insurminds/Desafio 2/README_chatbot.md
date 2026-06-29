# 🤖 Agente Inteligente Chatbot Seguro

## 🛠️ O que este projeto faz

* **Automação de FAQ:** Responde a perguntas frequentes de segurados de forma instantânea, por meio de **Inteligência Contextual (RAG) :** fazendo uso de documentos técnicos localizados em [/rag_docs](https://github.com/ajndantas/I2A2-Grupo_01/tree/master/Insurminds/Desafio%202/agente_chatbotseguro/Scripts/rag_docs) (como manuais e termos de apólices) para garantir que a IA forneça informações baseadas em dados reais.

---

## Tecnologias Utilizadas

* 🧩 **LangChain** – Orquestração de RAG e memória conversacional.
* 🤖 **OpenAI/ChatGPT** – Acesso ao modelo de linguagem (LLMs).
* 🧱 **Streamlit** – Interface web interativa para o usuário.
* 🐳 **Docker** – Containerização e orquestração de serviços.
* 🐙 **GitHub** **(CI/CD)**– Hospedagem do código-fonte, automação de CI/CD para GHCR (GitHub Container Registry -> Repositório de Imagens Docker) e deploy na Cloud Run na GCP
* ☁️ **GCP (Google Cloud Platform)** -> **CloudRun** – Deploy das Imagens Docker em Infraestrutura de nuvem.

---

## 🚀 Demonstração ao Vivo

O projeto está implantado e disponível para testes em tempo real na infraestrutura da **Google Cloud Platform (GCP)**:

🔗 **[Acessar Demo do Agente Chatbot Seguro](https://agente-chatbotseguro-574973424283.us-central1.run.app)**

---

## 📜 Código Fonte Principal

O núcleo lógico do chatbot, incluindo a orquestração do LangChain e a interface Streamlit, pode ser acessado diretamente aqui:

* 🔗 **[agente_chatbotseguro.py](https://github.com/ajndantas/I2A2-Grupo_01/blob/master/Insurminds/Desafio%202/agente_chatbotseguro/Scripts/agente_chatbotseguro.py)**
* 🔗 **[Frontend Streamlit app.py](https://github.com/ajndantas/I2A2-Grupo_01/blob/master/Insurminds/Desafio%202/agente_chatbotseguro/Scripts/app.py)**

---

## ☁️ Infraestrutura e Deploy (GCP)

O projeto foi desenhado para rodar de forma escalável na **Google Cloud Platform (GCP)**, utilizando uma arquitetura de containers orquestrada via GitHub Actions.

* **Hospedagem:** Implementado em uma **CloudRun na GCP**
* **Rede e Segurança:**
  * Suporte a SSL.
* **CI/CD:** Pipeline automatizado (GitHub Actions) que realiza o build da imagem para a GHCR e executa o deploy na CloudRun.

---

## 🔐 Gestão de Variáveis de Ambiente

As variáveis de ambiente são geridas de forma segura e persistente através de diferentes camadas:

### GitHub Secrets (CI/CD)

A chave sensível (`API_KEY`) é armazenada nos **GitHub Secrets**. Durante o build, é passada como `--build-arg`.

---

## 🐳 Execução com Docker

### 1️⃣ Configuração

* **Imagem Base:** Python 3.13-slim.
* **Modelos:** Embeddings baixados localmente via `huggingface_models_download.py` para otimizar performance.

### 2️⃣ Variáveis Necessárias

* `API_KEY`: Comunicação com LLMs.

---

# 💻 Implantação Local

Caso deseje executar o projeto localmente para fins de desenvolvimento, testes ou estudos, siga os passos abaixo.

## 📋 Pré-requisitos

Antes de iniciar, certifique-se de possuir instalado:

- Python 3.13
- Chave API da OpenAI do ChatGPT

## 📦 1 - Instalação das Dependências

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

### Linux / macOS

[requirements.txt](https://github.com/ajndantas/I2A2-Grupo_01/blob/master/Insurminds/Desafio%202/agente_chatbotseguro/Scripts/requirements.txt "https://github.com/ajndantas/I2A2-Grupo_01/blob/master/Insurminds/Desafio%202/agente_chatbotseguro/Scripts/requirements.txt")

```bash
pip install -r requirements.txt
```

### Windows

[requirements_windows.txt](https://github.com/ajndantas/I2A2-Grupo_01/blob/master/Insurminds/Desafio%202/agente_chatbotseguro/Scripts/requirements_windows.txt "https://github.com/ajndantas/I2A2-Grupo_01/blob/master/Insurminds/Desafio%202/agente_chatbotseguro/Scripts/requirements_windows.txt")

```
1     pip install -r requirements_windows.txt
```

---

## 🔐 2 - Configuração das Variáveis de Ambiente

Crie um arquivo `.env` dentro do diretório Scripts do ambiente virtual, contendo as variáveis necessárias:

```
cd .venv\Scripts
```

```env
API_KEY=CHAVE_OPENAI_CHATGPT
```

## 📥 3 - Instalando os códigos

Faça o download dos códigos abaixo, para dentro do diretório Scripts no ambiente virtual:

```bash
cd .venv\Scripts
```

🔗 **[agente_chatbotseguro.py](https://github.com/ajndantas/I2A2-Grupo_01/blob/master/Insurminds/Desafio%202/agente_chatbotseguro/Scripts/agente_chatbotseguro.py)**

🔗 **[app.py](https://github.com/ajndantas/I2A2-Grupo_01/blob/master/Insurminds/Desafio%202/agente_chatbotseguro/Scripts/app.py)**

---

## 🤖 4 - Download do Modelo de Embedding

O projeto utiliza um modelo local ([all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)) do Hugging Face para embeddings.

- Faça o download do código [huggingface_models_download.py](https://github.com/ajndantas/I2A2-Grupo_01/blob/master/Insurminds/Desafio%202/agente_chatbotseguro/Scripts/huggingface_models_download.py) para dentro do diretório Scripts no ambiente virtual:
- De dentro desse diretório, execute o script responsável pelo download:

```bash
cd .venv\Scripts
python huggingface_models_download.py
```

Os modelos serão armazenados localmente para melhorar a performance e reduzir chamadas externas.

## 📁 5 - Documentos da base de consulta

O diretório [/rag_docs](https://github.com/ajndantas/I2A2-Grupo_01/tree/master/Insurminds/Desafio%202/agente_chatbotseguro/Scripts/rag_docs), dentro de Scripts, deve conter os documentos utilizados pelo mecanismo RAG, como:

- Apólices
- FAQs
- Manuais técnicos
- Documentação de seguros

Esses arquivos são utilizados como base contextual para respostas da IA.

## ▶️ 6 - Execução Local com Streamlit

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

- O primeiro carregamento dos modelos pode demorar alguns minutos.

## 📃 Licença

Código aberto sob **licença MIT**.
