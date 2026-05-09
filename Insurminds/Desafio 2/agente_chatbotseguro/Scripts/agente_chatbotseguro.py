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
from os import getenv, path
from langchain_core.globals import set_debug, set_llm_cache
from langchain_core.caches import InMemoryCache
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEndpointEmbeddings, HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA

#set_debug(True)

load_dotenv() # CARREGANDO O ARQUIVO COM A API_KEY_OPENROUTER

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
 
    def __init__(self, documents: list, embeddings, db_path: str):
        self.documents = documents
        self.embeddings = embeddings

        self.db_path = db_path # O CAMINHO ONDE O ÍNDICE DE BUSCA VAI SER ARMAZENADO. 
                               # O OBJETIVO DE ARMAZENAR O ÍNDICE EM UM ARQUIVO É PERMITIR QUE ELE SEJA REUTILIZADO 
                               # EM VEZ DE SER RECRIADO TODA VEZ QUE O PROGRAMA FOR EXECUTADO AUMENTANDO ASSIM A PERFORMANCE.

    def db(self) -> FAISS:

        if path.exists(self.db_path):
            return FAISS.load_local(self.db_path, self.embeddings, allow_dangerous_deserialization=True) # O MÉTODO LOAD_LOCAL VAI CARREGAR O ÍNDICE DE BUSCA A PARTIR DO ARQUIVO SALVO. 
                                                                                                         # O PARÂMETRO ALLOW_DANGEROUS_DESERIALIZATION É NECESSÁRIO PARA PERMITIR 
                                                                                                         # QUE O FAISS CARREGUE O ÍNDICE DE BUSCA A PARTIR DO ARQUIVO        
        
        # Se não existir, cria e salva
        db_instance = FAISS.from_documents(self.documents, self.embeddings)
        
        db_instance.save_local(self.db_path)

        return db_instance


class AgenteChatbotSeguro:

  def __init__(self):

    llm = ChatOpenAI(
                        model="openrouter/free",                    
                        api_key=getenv("API_KEY_OPENROUTER"),
                        base_url="https://openrouter.ai/api/v1",
                        temperature=0 # POR CAUSA DE PERGUNTAS COMO "QUEM DESCOBRIU O BRASIL ?", É IMPORTANTE DEFINIR A TEMPERATURA COMO 0 
                                      # PARA GARANTIR QUE A RESPOSTA SEJA SEMPRE A MESMA E NÃO VARIE ENTRE EXECUÇÕES DIFERENTES.                   
                    )
    
    documents = Loader().load() # PASSO 1 - DIVIDIR OS DOCUMENTOS EM CHUNKS (FRAGMENTOS) PARA FACILITAR O PROCESSAMENTO PELA LLM. O CHUNK_SIZE VAI DETERMINAR O TAMANHO DE CADA FRAGMENTO.
    searchindex = SearchIndex(chunk_size=1000, documents=documents) # PASSO 2 - CRIAR UM ÍNDICE DE BUSCA PARA OS CHUNKS GERADOS. ESSE ÍNDICE VAI PERMITIR REALIZAR BUSCAS EFICIENTES NOS DOCUMENTOS FRAGMENTADOS.
    
    self.db_path = "faiss_index"

    if path.exists(self.db_path): 
        print("Apagando Índice de busca existente para carga de novos documentos...")
        path.remove(self.db_path) # APAGANDO O ÍNDICE DE BUSCA EXISTENTE PARA GARANTIR QUE O NOVO ÍNDICE SEJA CRIADO COM OS NOVOS DOCUMENTOS CARREGADOS. 

    db = VectorDB(documents=searchindex.splitter(), embeddings=searchindex.indexer(), db_path=self.db_path).db() # PASSO 3 - BANCO DE VETORES - UTILIZAR O ÍNDICE DE BUSCA PARA ARMAZENAR OS CHUNKS E SEUS RESPECTIVOS VETORES DE EMBEDDING.

    # create the RetrievalQA chain using the existing llm and the retriever (Quem busca no banco de dados)
    # qa_chain -> Nossa ferramenta de Perguntas e Respostas (Questions and Answers Chain)
    self.qa_chain = RetrievalQA.from_chain_type(
                                                  llm=llm, 
                                                  retriever=db.as_retriever(),
                                                  return_source_documents=True # ESSA OPÇÃO VAI PERMITIR QUE A CHAINE DEVOLVA OS DOCUMENTOS DE ORIGEM QUE FORAM UTILIZADOS PARA GERAR A RESPOSTA.
                                                                                                                                                                             
                                                )
    
  def query(self, question: str) -> str:
      
      self.output = self.qa_chain.invoke({"query": question})
      self.result = self.output['result']

      print('\nPergunta: ', question)

      return self.result


if __name__ == "__main__":

    agente = AgenteChatbotSeguro()

    print(agente.query("Não encontrei um seguro que eu contratei. O que fazer?"))
    print(agente.query("Como devo proceder caso tenha um item pessoal roubado ?"))
    print(agente.query("Quem descobriu o Brasil ?"))

#pergunta="Como devo proceder caso tenha um item pessoal roubado ?"