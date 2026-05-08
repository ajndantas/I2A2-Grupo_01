# "https://cursos.alura.com.br/course/langchain-python-ferramentas-llm-openai/task/156170?b2cUser=true"
#
# Utilizando para fazer pesquisas em documentos para responder perguntas 

# PASSOS:
# PASSO 1 - CARGA NO CARREGADOR
# PASSO 2 - CRIAÇÃO DO ÍNDICE DE BUSCA
# 2.1 - QUEBRA DO TEXTO
# 2.2 - INDEXANDO AS QUEBRAS DO TEXTO
# 2.3 - ARMAZENANDO OS ÍNDICES EM UM BANCO VETORIAL NA MEMÓRIA
# 3 - EXECUTANDO A PESQUISA


from langchain_openai import ChatOpenAI
from os import getenv
from dotenv import load_dotenv
from langchain_core.globals import set_debug
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA

# set_debug(True)

load_dotenv() # CARREGANDO O ARQUIVO COM A OPENAI_KEY

# PASSO 1 - CARGA NO CARREGADOR
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

# PASSO 2 - CRIAÇÃO DO ÍNDICE DE BUSCA
#
# Para isso, será necessário, primeiramente, realizar a quebra (splitter) em trechos, para que a IA possa indexá-los.

class SearchIndex:

    def __init__(self, chunk_size: int, documents: list):
        self.chunk_size = chunk_size
        self.documents = Loader().load() # CARREGANDO OS DOCUMENTOS PARA O MÉTODO SPLITTER
    
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


class Main:

  def __init__(self,pergunta: str):

    self.pergunta = pergunta

    llm = ChatOpenAI(
                        model="openrouter/free",                    
                        api_key=getenv("API_KEY_OPENROUTER")                    
                    )

    # PASSO 1 - DIVIDIR OS DOCUMENTOS EM CHUNKS (FRAGMENTOS) PARA FACILITAR O PROCESSAMENTO PELA LLM. O CHUNK_SIZE VAI DETERMINAR O TAMANHO DE CADA FRAGMENTO.
    documents = Loader().load() # CARREGANDO OS DOCUMENTOS PARA O MÉTODO SPLITTER

    # PASSO 2 - CRIAR UM ÍNDICE DE BUSCA PARA OS CHUNKS GERADOS. ESSE ÍNDICE VAI PERMITIR REALIZAR BUSCAS EFICIENTES NOS DOCUMENTOS FRAGMENTADOS.
    searchindex = SearchIndex(chunk_size=1000, documents=documents)
    # PASSO 3 - BANCO DE VETORES - UTILIZAR O ÍNDICE DE BUSCA PARA ARMAZENAR OS CHUNKS E SEUS RESPECTIVOS VETORES DE EMBEDDING.
    db = VectorDB(documents=searchindex.splitter(), embeddings=searchindex.indexer()).db()

    # create the RetrievalQA chain using the existing llm and the retriever (Quem busca no banco de dados)
    # qa_chain -> Nossa ferramenta de Perguntas e Respostas (Questions and Answers Chain)
    self.qa_chain = RetrievalQA.from_chain_type(
                                                  llm=llm, 
                                                  retriever=db.as_retriever(),
                                                  return_source_documents=True                       
                                                )
    
  def output(self) -> str:
      
      self.resposta = self.qa_chain.invoke({"query": self.pergunta})
      self.output = self.resposta['result']

      print('\nPergunta: ',self.pergunta,'\n')
      #print('\nDocumentos de origem da resposta:\n',self.resposta['source_documents'])

      return self.output

print(Main(pergunta="Aonde consultar as licitações das unidades da Susep?").output())
print(Main(pergunta="Como devo proceder caso tenha um item pessoal roubado ?").output())
print(Main(pergunta="Quem descobriu o Brasil ?").output())
#pergunta="Como devo proceder caso tenha um item pessoal roubado ?"

