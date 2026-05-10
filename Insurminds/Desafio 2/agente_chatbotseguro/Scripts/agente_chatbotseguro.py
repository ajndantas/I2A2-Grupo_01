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
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from time import time
from re import sub


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

    def __init__(self, chunk_size: int, chunk_overlap: int, documents: list):

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.documents = documents
    
    # PASSO 1 - DIVIDIR OS DOCUMENTOS EM CHUNKS (FRAGMENTOS) DE TEXTO PARA FACILITAR O PROCESSAMENTO PELA LLM. O CHUNK_SIZE VAI DETERMINAR O TAMANHO DE CADA FRAGMENTO.
    def splitter(self) -> list:
        
        splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap) # O CHUNK_OVERLAP VAI DETERMINAR O NÍVEL DE SOBREPOSIÇÃO ENTRE OS CHUNKS. SE FOR 0, NÃO HAVERÁ SOBREPOSIÇÃO. 
                                                                                      # SE FOR MAIOR QUE 0, OS CHUNKS VÃO SE SOBREPOR EM UMA QUANTIDADE DE CARACTERES DETERMINADA 
                                                                                      # PELO VALOR DO CHUNK_OVERLAP.
        self.texts_chunks = splitter.split_documents(self.documents)  

        return self.texts_chunks
    
    # PASSO 2 - CRIAR UM ÍNDICE DE BUSCA PARA OS CHUNKS GERADOS. ESSE ÍNDICE VAI PERMITIR REALIZAR BUSCAS EFICIENTES NOS DOCUMENTOS FRAGMENTADOS.
    def indexer(self) -> HuggingFaceEmbeddings:

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
            print("Índice de busca encontrado. Carregando o índice existente...\n")
            return FAISS.load_local(self.db_path, self.embeddings, allow_dangerous_deserialization=True) # O MÉTODO LOAD_LOCAL VAI CARREGAR O ÍNDICE DE BUSCA A PARTIR DO ARQUIVO SALVO. 
                                                                                                         # O PARÂMETRO ALLOW_DANGEROUS_DESERIALIZATION É NECESSÁRIO PARA PERMITIR 
                                                                                                         # QUE O FAISS CARREGUE O ÍNDICE DE BUSCA A PARTIR DO ARQUIVO        
        
        # Se não existir, cria e salva
        print("Índice de busca não encontrado. Criando...\n")
        db_instance = FAISS.from_documents(self.documents, self.embeddings)
        
        db_instance.save_local(self.db_path)

        return db_instance   


class AgenteChatbotSeguro:

  def __init__(self):

    llm = ChatOpenAI(
                        model="openrouter/free",                    
                        api_key=getenv("API_KEY_OPENROUTER"),
                        base_url="https://openrouter.ai/api/v1",
                        reasoning_effort="high"                  
                    )
    
    documents = Loader().load() # PASSO 1 - DIVIDIR OS DOCUMENTOS EM CHUNKS (FRAGMENTOS) PARA FACILITAR O PROCESSAMENTO PELA LLM. O CHUNK_SIZE VAI DETERMINAR O TAMANHO DE CADA FRAGMENTO.
    searchindex = SearchIndex(chunk_size=800, chunk_overlap=500, documents=documents) # PASSO 2 - CRIAR UM ÍNDICE DE BUSCA PARA OS CHUNKS GERADOS. ESSE ÍNDICE VAI PERMITIR REALIZAR BUSCAS EFICIENTES NOS DOCUMENTOS FRAGMENTADOS.
    
    self.db_path = "faiss_index"

    #if path.exists(self.db_path): 
    #   print("Apagando Índice de busca existente para carga de novos documentos...\n")
    #   shutil.rmtree(self.db_path) # O MÉTODO RMTREE VAI APAGAR O DIRETÓRIO ONDE O ÍNDICE DE BUSCA ESTÁ SALVO, INCLUINDO TODOS OS ARQUIVOS E SUBDIRETÓRIOS CONTIDOS NELE.
                                    # rmdir só pode ser usado para remover diretórios vazios.       
         

    db = VectorDB(documents=searchindex.splitter(), embeddings=searchindex.indexer(), db_path=self.db_path).db() # PASSO 3 - BANCO DE VETORES - UTILIZAR O ÍNDICE DE BUSCA PARA ARMAZENAR OS CHUNKS E SEUS RESPECTIVOS VETORES DE EMBEDDING.
    
    template = """
                    Você é um assistente de perguntas e respostas especializado em seguros.
                    
                    CONTEXTO: Você tem acesso a um conjunto de documentos relacionados a seguros, que podem conter informações relevantes para responder às perguntas dos usuários. 
                    Esses documentos podem incluir políticas de seguro, termos e condições, FAQs, entre outros. 
                    --------------------------------------------------------------------------------
                        {context}
                    --------------------------------------------------------------------------------

                    DIRETRIZES:
                    ----------------------------------------------------------------------------------------------------------------------------------------------------------
                        - Se os documentos não contiverem informações relevantes para responder à pergunta, responda "Desculpe, não tenho informações suficientes para 
                        responder a essa pergunta.".
                        - Se os documentos contiverem informações relevantes, responda com base nessas informações, citando os nomes das fontes utilizadas. Seja claro e conciso em 
                        suas respostas.
                        - Se as fontes não forem citadas, responda "Desculpe, não existem fontes que possam responder a essa pergunta.". NUNCA deixar em branco ou omitir as fontes.
                        - SEMPRE responda no formato JSON, seguindo a estrutura definida abaixo.
                    ---------------------------------------------------------------------------------------------------------------------------------------------------------- 
                    
                    Pergunta: {question}
                    
                    Resposta:
                    {{
                        "pergunta": "{question}",     
                        "resposta": "A resposta para a pergunta. Seja claro e conciso em sua resposta.",
                        "fontes": "As fontes utilizadas para responder à pergunta do usuário"
                    }}
                """    

    prompt_template = PromptTemplate(
                                        template=template,
                                        input_variables=["context", "question"]                                  
                                    )

    # create the RetrievalQA chain using the existing llm and the retriever (Quem busca no banco de dados)
    # 
    # Quando o usuário faz uma pergunta, o as_retriever() converte a pergunta em vetor e faz uma busca por similaridade no FAISS, 
    # retornando os K chunks cujos vetores são matematicamente mais próximos ao vetor da pergunta. Por padrão, LangChain retorna os 4 mais relevantes.
    #
    # OS CHUNKS ENCONTRADOS SÃO INJETADOS NO {context}
    # chain_type_kwargs={"prompt": prompt_template}
    #
    # O RetrievalQA pega os chunks retornados pelo retriever, concatena seus textos e injeta o resultado dentro da variável {context} do PromptTemplate. O prompt final enviado ao LLM fica assim:
    self.qa_chain = RetrievalQA.from_chain_type(
                                                  llm=llm, 
                                                  retriever=db.as_retriever(),                                                                                                      
                                                  chain_type_kwargs={"prompt": prompt_template}                                                                                                                                                                              
                                                )
    
  def query(self, question: str) -> str:
      
      self.output = self.qa_chain.invoke({"query": question}) 
      self.result = sub(r"```json|```","",str(self.output['result'])).strip() # O RESULTADO VAI VIR COM QUEBRAS DE LINHA, ENTÃO SUBSTITUÍMOS AS QUEBRAS DE LINHA POR ESPAÇOS EM BRANCO PARA DEIXAR O JSON EM UMA ÚNICA LINHA.

      return self.result


if __name__ == "__main__":

    inicio = time() # Marca o tempo inicial

    agente = AgenteChatbotSeguro()

    # PERGUNTAS PARA TESTAR O AGENTE
    print(agente.query("Não encontrei um seguro que eu contratei. O que fazer?"))
    fim = time() # Marca o tempo final
    #print(f"\nTempo total de execução: {fim - inicio:.2f} segundos\n")

    inicio = time() # Marca o tempo inicial
    print(agente.query("Como devo proceder caso tenha meu celular roubado ?"))
    fim = time() # Marca o tempo final
    #print(f"\nTempo total de execução: {fim - inicio:.2f} segundos\n")

    inicio = time() # Marca o tempo inicial
    print(agente.query("Quem descobriu o Brasil ?"))
    fim = time() # Marca o tempo final
    #print(f"\nTempo total de execução: {fim - inicio:.2f} segundos\n")