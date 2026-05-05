# [markdown]
# # <a href="https://cursos.alura.com.br/course/langchain-python-ferramentas-llm-openai/task/156170?b2cUser=true"><b>Langchain Retrieval Texto</b></a><br/>

# [markdown]
# Utilizando para fazer pesquisas em documentos para responder perguntas 

# [markdown]
# <b>PASSOS:</b><br/>
# <b>PASSO 1 - CARGA NO CARREGADOR</b><br/>
# <b>PASSO 2 - CRIAÇÃO DO ÍNDICE DE BUSCA</b><br/>
# <ul><li><b>2.1 - QUEBRA DO TEXTO</b></li></ul>
# <ul><li><b>2.2 - INDEXANDO AS QUEBRAS DO TEXTO</b></li></ul>
# <ul><li><b>2.3 - ARMAZENANDO OS ÍNDICES EM UM BANCO VETORIAL NA MEMÓRIA</b></li></ul>
# <b>PASSO 3 - EXECUTANDO A PESQUISA</b>

#%pip install -r requirements.txt

# [markdown]
# ### <b>EXEMPLO 1</b><br/>
# O objetivo será realizar a pesquisa em um arquivo txt, sobre os benefícios do cartão Gold contra roubo.

from langchain_openai import ChatOpenAI
from os import getenv
from dotenv import load_dotenv # CARREGA A VARIÁVEL DE AMBIENTE OPENAI_KEY LIDA DO ARQUIVO .env
from langchain_core.globals import set_debug

set_debug(True)

load_dotenv() # CARREGANDO O ARQUIVO COM A OPENAI_KEY

llm = ChatOpenAI( # INSTANCIANDO A LLM
                    model="openrouter/free",                    
                    # 1 - OBTENDO A API KEY POR MEIO DA VARIÁVEL DE AMBIENTE OPENAI_KEY. QUE VAI FICAR ARMAZENADA NO ARQUIVO .env.
                    # 2 - AINDA É NECESSÁRIO CARREGAR ESSE ARQUIVO. VER NA PRIMEIRA CÉLULA DO NOTEBOOK
                    api_key=getenv("API_KEY_OPENROUTER")                    
                )

# [markdown]
# ### <b>PASSO 1 - CARGA NO CARREGADOR</b>

# [markdown]
# Carregando

from langchain_community.document_loaders import TextLoader

# CRIAÇÃO - ARQUIVOS NO FORMATO CSV
carregador = TextLoader("../rag_docs/*.csv", glob=True, encoding="utf-8") # PARA CARREGAR VÁRIOS ARQUIVOS DE UMA SÓ VEZ. O GLOBO É UM CURINGA PARA SELECIONAR VÁRIOS ARQUIVOS COM O MESMO PADRÃO. NESSE CASO, TODOS OS ARQUIVOS COM EXTENSÃO .CSV DENTRO DA PASTA ../rag_docs/

# CARGA NO CARREGADOR
documentos = carregador.load() # UM CARREGADOR DEVOLVE UM ARRAY DE DOCUMENTOS. NESSE CASO, EM PARTICULAR, SERÁ UM ARRAY COM UM ÚNICO ELEMENTO.

print('Documentos\n',documentos)

# [markdown]
# ### <b>PASSO 2 - CRIAÇÃO DO ÍNDICE DE BUSCA</b>

# [markdown]
# <li>Para isso, será necessário, primeiramente, realizar a quebra (splitter) em trechos, para que a IA possa indexá-los.

# [markdown]
# <b>2.1 - QUEBRA DO TEXTO</b>

from langchain_text_splitters import CharacterTextSplitter

# DEFINIÇÃO DO QUEBRADOR
quebrador = CharacterTextSplitter(chunk_size=1000) # QUEBRANDO EM CARACTERES. DE 1000 EM 1000 CARACTERES.

# QUEBRA DO TEXTO EM VÁRIOS TEXTOS
textos = quebrador.split_documents(documentos) # AQUI, DOCUMENTOS NÃO PODE SER UM ARRAY DE ARRAYS. TEM QUE SER APENAS UM ARRAY DE DOCUMENTOS.

print('\nTextos\n',textos)

# [markdown]
# <b>2.2 - INDEXANDO AS QUEBRAS DE TEXTO</b>

# [markdown]
# <ol>
#     <li>Sequências de palavras que possuem sentido semelhante, terão números semelhantes no espaço</li>
#     <li>Esse números são chamados de índices, e esses <b>índices</b> recebem o nome de <b>embeddings</b></li>
# </ol>

from langchain_huggingface import HuggingFaceEmbeddings

# CRIANDO OS EMBEDDINGS
#embeddings = OpenAIEmbeddings(api_key=getenv("OPENAI_KEY"))

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'}
)

print('Embeddings\n',embeddings)

# [markdown]
# <b>2.3 - ARMAZENANDO OS ÍNDICES EM UM BANCO VETORIAL NA MEMÓRIA</b>

from langchain.vectorstores import FAISS

# LUGAR PARA ARMAZENAR OS EMBEDDINGS -> BANCO VETORIAL. ARMAZENA O NÚMERO E A FRASE.
# SERÁ USADO O BANCO VETORIAL FAISS DO Facebook
db = FAISS.from_documents(textos,embeddings)   # CRIADO O BD A PARTIR DOS DOCUMENTOS

print(db)

# [markdown]
# ### <b>PASSO 3 - EXECUTANDO A PESQUISA</b>

from langchain.chains import RetrievalQA

# create the RetrievalQA chain using the existing llm and the retriever (Quem busca no banco de dados)
# qa_chain -> Nossa ferramenta de Perguntas e Respostas (Questions and Answers Chain)
qa_chain = RetrievalQA.from_chain_type(
                                        llm=llm, 
                                        retriever=db.as_retriever(),
                                        return_source_documents=True                       
                                      )

# exemplo de uso
pergunta = "Como devo proceder caso tenha um item pessoal roubado ?. Não faça qualquer tipo de comentário ou pergunta, apenas responda a pergunta."

resposta = qa_chain.invoke({"query": pergunta})
print('\nPergunta: ',pergunta,'\nResposta\n', resposta['result'])

print('\nDocumentos de origem da resposta:\n',resposta['source_documents'])



