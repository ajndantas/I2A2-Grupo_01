# Utilizando para fazer pesquisas em documentos para responder perguntas 

# PASSOS:
# PASSO 1 - CARGA NO CARREGADOR
# PASSO 2 - CRIAÇÃO DO ÍNDICE DE BUSCA
# 2.1 - QUEBRA DO TEXTO
# 2.2 - INDEXANDO AS QUEBRAS DO TEXTO
# 2.3 - ARMAZENANDO OS ÍNDICES EM UM BANCO VETORIAL NA MEMÓRIA
# 3 - EXECUTANDO A PESQUISA

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from os import getenv, environ
from langchain_core.globals import set_debug, set_llm_cache
from langchain_core.caches import InMemoryCache
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEndpointEmbeddings, HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA

# set_debug(True)

load_dotenv() # CARREGANDO O ARQUIVO COM A OPENAI_KEY

# -------------------------------------------------------
# Cache nativo do LangChain (InMemoryCache)
# -------------------------------------------------------
set_llm_cache(InMemoryCache())

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
        self.documents = documents
    
    # PASSO 1 - DIVIDIR OS DOCUMENTOS EM CHUNKS (FRAGMENTOS) DE TEXTO PARA FACILITAR O PROCESSAMENTO PELA LLM. O CHUNK_SIZE VAI DETERMINAR O TAMANHO DE CADA FRAGMENTO.
    def splitter(self) -> list:
        
        splitter = CharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=200) # O CHUNK_OVERLAP VAI DETERMINAR O NÍVEL DE SOBREPOSIÇÃO ENTRE OS CHUNKS. SE FOR 0, NÃO HAVERÁ SOBREPOSIÇÃO. 
                                                                                      # SE FOR MAIOR QUE 0, OS CHUNKS VÃO SE SOBREPOR EM UMA QUANTIDADE DE CARACTERES DETERMINADA 
                                                                                      # PELO VALOR DO CHUNK_OVERLAP.
        self.texts_chunks = splitter.split_documents(self.documents)  

        return self.texts_chunks
    
    # PASSO 2 - CRIAR UM ÍNDICE DE BUSCA PARA OS CHUNKS GERADOS. ESSE ÍNDICE VAI PERMITIR REALIZAR BUSCAS EFICIENTES NOS DOCUMENTOS FRAGMENTADOS.
    def indexer(self):

        self.embeddings = HuggingFaceEmbeddings(
                    model_name="./cache/all-MiniLM-L6-v2",
                    model_kwargs={'device': 'cpu'}, # Força o uso do seu processador
                    encode_kwargs={'normalize_embeddings': True} # Normaliza os vetores de embedding para melhorar a precisão da busca.                                            
        )

        """ self.embeddings = OpenAIEmbeddings(
                                                model="nvidia/llama-nemotron-embed-vl-1b-v2:free",
                                                api_key=getenv("API_KEY_OPENROUTER"),
                                                base_url="https://openrouter.ai/api/v1"
                                                )  """

        """ self.embeddings = OpenAIEmbeddings(
                                                model="text-embedding-3-small", # MAIS RÁPIDO E BARATO, MAS MENOS PRECISO. IDEAL PARA TESTES E PROJETOS PEQUENOS.
                                                api_key=getenv("API_KEY")                                                
                                          ) """
        
        return self.embeddings

# PASSO 3 - BANCO DE VETORES - UTILIZAR O ÍNDICE DE BUSCA PARA ARMAZENAR OS CHUNKS E SEUS RESPECTIVOS VETORES DE EMBEDDING.
class VectorDB:
 
    def __init__(self, documents: list, embeddings):
        self.documents = documents
        self.embeddings = embeddings

    def db(self) -> FAISS:        
        db_instance = FAISS.from_documents(self.documents, self.embeddings)
                    
        return db_instance


class AgenteChatbotSeguro:

  def __init__(self):

    llm = ChatOpenAI(
                        model="openrouter/free",                    
                        api_key=getenv("API_KEY_OPENROUTER"),
                        base_url="https://openrouter.ai/api/v1"                    
                    )
    
    documents = Loader().load() # PASSO 1 - DIVIDIR OS DOCUMENTOS EM CHUNKS (FRAGMENTOS) PARA FACILITAR O PROCESSAMENTO PELA LLM. O CHUNK_SIZE VAI DETERMINAR O TAMANHO DE CADA FRAGMENTO.
    searchindex = SearchIndex(chunk_size=1000, documents=documents) # PASSO 2 - CRIAR UM ÍNDICE DE BUSCA PARA OS CHUNKS GERADOS. ESSE ÍNDICE VAI PERMITIR REALIZAR BUSCAS EFICIENTES NOS DOCUMENTOS FRAGMENTADOS.
    db = VectorDB(documents=searchindex.splitter(), embeddings=searchindex.indexer()).db() # PASSO 3 - BANCO DE VETORES - UTILIZAR O ÍNDICE DE BUSCA PARA ARMAZENAR OS CHUNKS E SEUS RESPECTIVOS VETORES DE EMBEDDING.

    # create the RetrievalQA chain using the existing llm and the retriever (Quem busca no banco de dados)
    # qa_chain -> Nossa ferramenta de Perguntas e Respostas (Questions and Answers Chain)
    self.qa_chain = RetrievalQA.from_chain_type(
                                                  llm=llm, 
                                                  retriever=db.as_retriever(),
                                                  return_source_documents=True                       
                                                )
    
  def query(self, question: str) -> str:
      
      self.output = self.qa_chain.invoke({"query": question})
      self.result = self.output['result']

      print('\nPergunta: ', question)
      print('Documentos de origem da resposta:\n', [doc.metadata for doc in self.output['source_documents']])

      return self.result


if __name__ == "__main__":

    agente = AgenteChatbotSeguro()

    print(agente.query("Aonde consultar as licitações das unidades da Susep ?"))
    print(agente.query("Como devo proceder caso tenha um item pessoal roubado ?"))
    print(agente.query("Quem descobriu o Brasil ?"))

#pergunta="Como devo proceder caso tenha um item pessoal roubado ?"