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
# ### <b>IMPORTS</b><br/>

from langchain_openai import ChatOpenAI
from os import getenv
from dotenv import load_dotenv
from langchain_core.globals import set_debug
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
#from langchain.vectorstores import FAISS
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA

set_debug(True)

load_dotenv() # CARREGANDO O ARQUIVO COM A OPENAI_KEY

# [markdown]
# ### <b>PASSO 1 - CARGA NO CARREGADOR</b>

# [markdown]
# Carregando

class Loader:

    def __init__(self):        

        # CRIAÇÃO - ARQUIVOS TEXTO (CSV, HTML, JSON, ETC) - CARREGADORES 
        self.loader = DirectoryLoader(
                                        "rag_docs", # O DIRETÓRIO ONDE ESTÃO OS ARQUIVOS QUE QUERO CARREGAR
                                        #glob="*.html", # O PADRÃO DE NOME DOS ARQUIVOS
                                        loader_cls=TextLoader,
                                        loader_kwargs={"encoding": "utf-8"}
                                     ) # PARA CARREGAR VÁRIOS ARQUIVOS DE UMA SÓ VEZ. O GLOB 
                                       # É UM CURINGA PARA SELECIONAR VÁRIOS ARQUIVOS COM O MESMO PADRÃO. NESSE CASO, 
                                       # TODOS OS ARQUIVOS COM EXTENSÃO .CSV DENTRO DA PASTA ../rag_docs/

        
    # O MÉTODO LOAD VAI SER RESPONSÁVEL POR CHAMAR O MÉTODO LOAD DO CARREGADOR PARA LER OS ARQUIVOS E DEVOLVER UM ARRAY DE DOCUMENTOS.
    def load(self) -> list:
        
        return self.loader.load() # UM CARREGADOR DEVOLVE UM ARRAY DE DOCUMENTOS.

# [markdown]
# ### <b>PASSO 2 - CRIAÇÃO DO ÍNDICE DE BUSCA</b>

# [markdown]
# <li>Para isso, será necessário, primeiramente, realizar a quebra (splitter) em trechos, para que a IA possa indexá-los.

class SearchIndex:

    def __init__(self, chunk_size: int, documents: list):
        self.chunk_size = chunk_size
        self.documents = documents
    
    # PASSO 1 - DIVIDIR OS DOCUMENTOS EM CHUNKS (FRAGMENTOS) PARA FACILITAR O PROCESSAMENTO PELA LLM. O CHUNK_SIZE VAI DETERMINAR O TAMANHO DE CADA FRAGMENTO.
    def splitter(self) -> list:
        
        splitter = CharacterTextSplitter(chunk_size=self.chunk_size)
        self.texts = splitter.split_documents(self.documents)  

        return self.texts
    
    # PASSO 2 - CRIAR UM ÍNDICE DE BUSCA PARA OS CHUNKS GERADOS. ESSE ÍNDICE VAI PERMITIR REALIZAR BUSCAS EFICIENTES NOS DOCUMENTOS FRAGMENTADOS.
    def indexer(self):

        """self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}            
        ) """

        self.embeddings = OpenAIEmbeddings(api_key=getenv("OPENAI_KEY"))

        return self.embeddings

# PASSO 3 - BANCO DE VETORES - UTILIZAR O ÍNDICE DE BUSCA PARA ARMAZENAR OS CHUNKS E SEUS RESPECTIVOS VETORES DE EMBEDDING.
class VectorDB:

    def __init__(self, documents: list, embeddings):
        self.documents = documents
        self.embeddings = embeddings
    
    def db(self) -> FAISS:
        self.db = FAISS.from_documents(self.documents, self.embeddings)

        return self.db

# [markdown]
# ### <b>PASSO 3 - EXECUTANDO A PESQUISA</b>

# [markdown]
# ### <b>LLM</b><br/>

llm = ChatOpenAI( # INSTANCIANDO A LLM
                    model="gpt-5.4-mini",                    
                    # 1 - OBTENDO A API KEY POR MEIO DA VARIÁVEL DE AMBIENTE OPENAI_KEY. QUE VAI FICAR ARMAZENADA NO ARQUIVO .env.
                    # 2 - AINDA É NECESSÁRIO CARREGAR ESSE ARQUIVO. VER NA PRIMEIRA CÉLULA DO NOTEBOOK
                    api_key=getenv("OPENAI_KEY")                    
                )

searchindex = SearchIndex(chunk_size=1000, documents=Loader().load())
db = VectorDB(documents=searchindex.splitter(), embeddings=searchindex.indexer()).db()

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

