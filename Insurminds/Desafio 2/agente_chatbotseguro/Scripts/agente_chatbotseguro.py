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
from os import getenv
from langchain_core.globals import set_debug
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from sklearn import base

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
        
        #environ['CURL_CA_BUNDLE'] = '' # PARA EVITAR O ERRO DE CERTIFICADO SSL QUANDO O MODELO DE EMBEDDING TENTA SE CONECTAR À INTERNET PARA BAIXAR O MODELO.

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
                                                    model_name="BAAI/bge-small-2M", 
                                                    model_kwargs={"device": "cpu"},
                                                    base_url="https://api-inference.huggingface.co/models/BAAI/bge-small-2M",
                                                    api_key=getenv("HUGGINGFACE_KEY")
                                                    
                                                ) # PARA GERAR OS VETORES DE EMBEDDING DOS CHUNKS DE TEXTO. 
                                                  # O MODELO DE EMBEDDING VAI TRANSFORMAR CADA CHUNK DE TEXTO EM UM VETOR 
                                                  # NUMÉRICO QUE REPRESENTA O SIGNIFICADO DO TEXTO. 
                                                  # ESSE VETOR VAI SER USADO PARA REALIZAR BUSCAS EFICIENTES NO BANCO DE DADOS 
                                                  # VETORIAL.

        #self.embeddings = OpenAIEmbeddings(api_key=getenv("OPENAI_KEY"))
        
        return self.embeddings

# PASSO 3 - BANCO DE VETORES - UTILIZAR O ÍNDICE DE BUSCA PARA ARMAZENAR OS CHUNKS E SEUS RESPECTIVOS VETORES DE EMBEDDING.
# Somente a primeira instância da classe VectorDB vai criar o banco de dados vetorial. As próximas instâncias vão reutilizar o banco de dados já criado, 
# evitando a necessidade de recriá-lo a cada vez que uma nova instância da classe for criada. Isso é possível graças ao uso da variável de CLASSE _db_instance,
class VectorDBSingleton:
    _db_instance = None  # PARA GARANTIR QUE SEJA COMPARTILHADA ENTRE TODAS AS INSTÂNCIAS DA CLASSE.

    def __init__(self, documents: list, embeddings):
        self.documents = documents
        self.embeddings = embeddings

    def db(self) -> FAISS:
        # Verifica se a instância da CLASSE está vazia
        if VectorDBSingleton._db_instance is None:
            print("Criando banco vetorial pela primeira vez...")
            VectorDBSingleton._db_instance = FAISS.from_documents(self.documents, self.embeddings)
        else:
            print("Banco vetorial já existe, utilizando a instância existente...")
            
        return VectorDBSingleton._db_instance


class AgenteChatbotSeguro:

  def __init__(self, pergunta: str):

    self.pergunta = pergunta

    llm = ChatOpenAI(
                        model="openrouter/free",                    
                        api_key=getenv("API_KEY_OPENROUTER"),
                        base_url="https://openrouter.ai/api/v1"                    
                    )
    
    documents = Loader().load() # PASSO 1 - DIVIDIR OS DOCUMENTOS EM CHUNKS (FRAGMENTOS) PARA FACILITAR O PROCESSAMENTO PELA LLM. O CHUNK_SIZE VAI DETERMINAR O TAMANHO DE CADA FRAGMENTO.
    searchindex = SearchIndex(chunk_size=1000, documents=documents) # PASSO 2 - CRIAR UM ÍNDICE DE BUSCA PARA OS CHUNKS GERADOS. ESSE ÍNDICE VAI PERMITIR REALIZAR BUSCAS EFICIENTES NOS DOCUMENTOS FRAGMENTADOS.
    db = VectorDBSingleton(documents=searchindex.splitter(), embeddings=searchindex.indexer()).db() # PASSO 3 - BANCO DE VETORES - UTILIZAR O ÍNDICE DE BUSCA PARA ARMAZENAR OS CHUNKS E SEUS RESPECTIVOS VETORES DE EMBEDDING.

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

      print('\nPergunta: ',self.pergunta)
      print('Documentos de origem da resposta:\n', [doc.metadata for doc in self.resposta['source_documents']])

      return self.output


if __name__ == "__main__":

    print(AgenteChatbotSeguro(pergunta="Aonde consultar as licitações das unidades da Susep?").output())
    print(AgenteChatbotSeguro(pergunta="Como devo proceder caso tenha um item pessoal roubado ?").output())
    print(AgenteChatbotSeguro(pergunta="Quem descobriu o Brasil ?").output())
#pergunta="Como devo proceder caso tenha um item pessoal roubado ?"