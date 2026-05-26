# Utilizando para fazer pesquisas em documentos para responder perguntas 

# PASSOS:
# PASSO 1 - CARGA NO CARREGADOR
# PASSO 2 - CRIAÇÃO DO ÍNDICE DE BUSCA
# 2.1 - QUEBRA DO TEXTO
# 2.2 - INDEXANDO AS QUEBRAS DO TEXTO
# 2.3 - ARMAZENANDO OS ÍNDICES EM UM BANCO VETORIAL NA MEMÓRIA
# 3 - EXECUTANDO A PESQUISA

from dotenv import load_dotenv
from os import getenv, path
from langchain_core.globals import set_debug, set_llm_cache, set_verbose
from langchain_core.caches import InMemoryCache
from time import time
import re

#set_debug(True)
set_verbose(True)

load_dotenv() # CARREGANDO O ARQUIVO COM A API_KEY_OPENROUTER


# PASSO 1 - CARGA NO CARREGADOR
class Loader:

    def __init__(self):        
        
        # Importação local para acelerar a inicialização do script. LAZY IMPORTING
        from langchain_community.document_loaders import TextLoader, DirectoryLoader, BSHTMLLoader

        # CRIAÇÃO - ARQUIVOS TEXTO (CSV, HTML, JSON, ETC) - CARREGADORES 
        loader_cls_map = {
            ".html": BSHTMLLoader,
            ".csv": TextLoader,
            ".txt": TextLoader
        }
        
        self.loader = DirectoryLoader(
                                        "rag_docs", # O DIRETÓRIO ONDE ESTÃO OS ARQUIVOS QUE QUERO CARREGAR
                                        #glob="*.html", # O PADRÃO DE NOME DOS ARQUIVOS
                                        glob=["*.html","*.csv","*.txt"],
                                        loader_kwargs={"encoding": "utf-8","language": "pt"}                        
                                     ) # PARA CARREGAR VÁRIOS ARQUIVOS DE UMA SÓ VEZ. O GLOB 
                                       # É UM CURINGA PARA SELECIONAR VÁRIOS ARQUIVOS COM O MESMO PADRÃO. NESSE CASO, 
                                       # TODOS OS ARQUIVOS COM EXTENSÃO .CSV DENTRO DA PASTA ../rag_docs/

        self.loader.loader_cls_map = loader_cls_map # PARA USAR NO MÉTODO LOAD  
        
    # O MÉTODO LOAD VAI SER RESPONSÁVEL POR CHAMAR O MÉTODO LOAD DO CARREGADOR PARA LER OS ARQUIVOS E DEVOLVER UM ARRAY DE DOCUMENTOS.
    def load(self) -> list:
        
        return self.loader.load() # UM CARREGADOR DEVOLVE UM ARRAY DE DOCUMENTOS.

# PASSO 2 - CRIAÇÃO DO ÍNDICE DE BUSCA
#
# Para isso, será necessário, primeiramente, realizar a quebra (splitter) em trechos, para que a IA possa indexá-los.
class SearchIndex:
    
    # 1 - DIVIDIR OS DOCUMENTOS EM CHUNKS (FRAGMENTOS) DE TEXTO PARA FACILITAR O PROCESSAMENTO PELA LLM. O CHUNK_SIZE VAI DETERMINAR O TAMANHO DE CADA FRAGMENTO.
    def splitter(self, chunk_size: int, chunk_overlap: int, documents: list) -> list:
        
        # LAZY IMPORTING
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        splittered_docs = RecursiveCharacterTextSplitter(                                                    
                                                            chunk_size=chunk_size, 
                                                            chunk_overlap=chunk_overlap,                                                                                                                
                                                            separators=["<h1>","<h2>","<h3>","<h4>","<h5>","\n\n", "\n", " ", ""] # OS SEPARADORES VÃO DETERMINAR ONDE O 
                                                                                                                                        # SPLITTER VAI TENTAR QUEBRAR O TEXTO. 
                                                                                                                                        # ELE VAI TENTAR QUEBRAR PRIMEIRO 
                                                                                                                                        # PELO SEPARADOR MAIS PRIORITÁRIO, 
                                                                                                                                        # E SE NÃO CONSEGUIR, VAI TENTAR PELO PRÓXIMO 
                                                                                                                                        # SEPARADOR DA LISTA.

                                                                                                                                        # Somente se o texto entre as tags ainda for maior que o seu chunk_size 
                                                                                                                                        # é que o splitter utilizará os demais 
                                                                                                                                        # separadores (\n\n, \n, etc.)
                                                                                                                                        #
                                                                                                                                        # O ÚLTIMO SEPARADOR É UMA STRING VAZIA, 
                                                                                                                                        # O QUE SIGNIFICA QUE O SPLITTER VAI TENTAR 
                                                                                                                                        # QUEBRAR O TEXTO EM QUALQUER LUGAR SE NÃO 
                                                                                                                                        # CONSEGUIR PELO SEPARADOR ANTERIOR.
                                                    
                                                        ) # O CHUNK_OVERLAP VAI DETERMINAR O NÍVEL DE SOBREPOSIÇÃO ENTRE OS CHUNKS. SE FOR 0, NÃO HAVERÁ SOBREPOSIÇÃO. 
                                                    # SE FOR MAIOR QUE 0, OS CHUNKS VÃO SE SOBREPOR EM UMA QUANTIDADE DE CARACTERES DETERMINADA 
                                                    # PELO VALOR DO CHUNK_OVERLAP.

        self.chunked_docs = splittered_docs.split_documents(documents)  

        return self.chunked_docs 
    
    # 2 - CRIAR UM ÍNDICE DE BUSCA PARA OS CHUNKS GERADOS E SEUS RESPECTIVOS VETORES DE EMBEDDING. ESSE ÍNDICE VAI PERMITIR REALIZAR BUSCAS NOS DOCUMENTOS FRAGMENTADOS.
    def indexer(self):        

        # Mapeia o HuggingFaceEmbeddings apenas quando necessário
        #from langchain_community.embeddings import HuggingFaceEmbeddings
        from langchain_huggingface import HuggingFaceEmbeddings

        self.embeddings = HuggingFaceEmbeddings(
                    model_name="./cache/all-MiniLM-L6-v2",
                    model_kwargs={'device': 'cpu'}, # Força o uso do seu processador
                    encode_kwargs={'normalize_embeddings': True} # Normaliza os vetores de embedding para melhorar a precisão da busca.                                            
        )
        
        return self.embeddings

# PASSO 3 - CRIAÇÃO DO BANCO VETORIAL
class VectorDB:
 
    def __init__(self, db_path_name: str): 

        self.db_path = db_path_name # O CAMINHO ONDE O ÍNDICE DE BUSCA VAI SER ARMAZENADO. 
                                    # O OBJETIVO DE ARMAZENAR O ÍNDICE EM UM ARQUIVO É PERMITIR QUE ELE SEJA REUTILIZADO 
                                    # EM VEZ DE SER RECRIADO TODA VEZ QUE O PROGRAMA FOR EXECUTADO AUMENTANDO ASSIM A PERFORMANCE.
        
        self._embeddings = None  # Lazy loading do embedding

    @property # O DECORADOR @PROPERTY PERMITE QUE O MÉTODO SEJA ACESSADO COMO UM ATRIBUTO, O QUE PODE MELHORAR A LEGIBILIDADE DO CÓDIGO.
    def embeddings(self):        
        if self._embeddings == None: # Visibilidade de atributo privado, 
                                     # para garantir que os embeddings só sejam criados quando forem realmente necessários, 
                                     # evitando assim o consumo desnecessário de recursos.
           
           print("Criando os embeddings...\n")

           self._embeddings = SearchIndex().indexer()

        return self._embeddings

    def db(self):

        # LAZY IMPORTING
        from langchain_community.vectorstores import FAISS
        
        #---------------------------------------------------------
        #  MANEIRA RÁPIDA DE IMPLEMENTAR O RAG 
        #
        # 1 - LAZY LOADING
        # 2 - LAZY SPLITTING
        # 3 - CRIAÇÃO DO BANCO VETORIAL SÓ QUANDO FOR NECESSÁRIO.
        #---------------------------------------------------------

        # 3 - CRIAÇÃO DO BANCO VETORIAL SÓ QUANDO FOR NECESSÁRIO. SE O ÍNDICE DE BUSCA JÁ EXISTIR, ELE VAI SER CARREGADO A PARTIR DO ARQUIVO SALVO, 
        # O QUE É MAIS RÁPIDO DO QUE CRIAR UM NOVO ÍNDICE DE BUSCA A CADA EXECUÇÃO DO PROGRAMA.
        
        # ...se existir, carrega
        if path.exists(self.db_path):
            print("Índice de busca encontrado. Carregando o índice existente...\n")
            
            # O self.embeddings VAI SER CRIADO APENAS SE O MÉTODO EMBEDDINGS FOR CHAMADO, 
            # O QUE SÓ ACONTECE SE O ÍNDICE DE BUSCA EXISTIR, POIS O MÉTODO DB SÓ CHAMA O MÉTODO EMBEDDINGS SE O ÍNDICE EXISTIR.
            return FAISS.load_local(self.db_path, self.embeddings, allow_dangerous_deserialization=True) # O MÉTODO LOAD_LOCAL VAI CARREGAR O ÍNDICE DE BUSCA A PARTIR DO ARQUIVO SALVO. 
                                                                                                         # O PARÂMETRO ALLOW_DANGEROUS_DESERIALIZATION É NECESSÁRIO PARA PERMITIR 
                                                                                                         # QUE O FAISS CARREGUE O ÍNDICE DE BUSCA A PARTIR DO ARQUIVO        
        
        # ...se não existir, cria e salva
        print("Índice de busca não encontrado. Criando...\n")

        # LAZY LOADING
        documents = Loader().load() # PASSO 1 - CARGA NO CARREGADOR

        # LAZY SPLITTING
        chunked_documents = SearchIndex().splitter(chunk_size=800, chunk_overlap=500, documents=documents) # PASSO 2.1 - DIVISÃO DOS DOCUMENTOS

        db_instance = FAISS.from_documents(chunked_documents, self.embeddings) # PASSO 3 - CRIAÇÃO DO BD DE VETORES 
                                                                               # CRIANDO O BD DE VETORES A PARTIR DOS DOCUMENTOS E DOS VETORES DE EMBEDDING.        
        db_instance.save_local(self.db_path)

        return db_instance

class AgenteChatbotSeguro:

  def __init__(self, newconversation: bool): 

    if newconversation:
        # -------------------------------------------------------
        # Apaga cache nativo do LangChain (InMemoryCache)
        # -------------------------------------------------------
        print("Nova conversa iniciada. Cache do LangChain desativado para iniciar uma nova conversa sem histórico.\n")
        set_llm_cache(None)  # DESATIVA O CACHE DO LANGCHAIN PARA INICIAR UMA NOVA CONVERSA SEM HISTÓRICO
              
    # -------------------------------------------------------
    # Cache nativo do LangChain (InMemoryCache)
    # -------------------------------------------------------
    print("Cache do LangChain ativado para acelerar as respostas.\n")
    set_llm_cache(InMemoryCache())

    # TÉCNICA DE LAZY IMPORTING PARA CARREGAR AS DEPENDÊNCIAS APENAS QUANDO FOR NECESSÁRIO, O QUE PODE MELHORAR A PERFORMANCE DO PROGRAMA.
    from langchain_openai import ChatOpenAI 
    from langchain_core.prompts import PromptTemplate
    from langchain.chains import RetrievalQA

    llm = ChatOpenAI(
                        model="openrouter/free",
                        #model="gpt-5-mini",                   
                        api_key=getenv("API_KEY_OPENROUTER"),
                        #api_key=getenv("API_KEY"),                        
                        base_url="https://openrouter.ai/api/v1",
                        #reasoning_effort="high", #, # PARA EVITAR ERROS NAS RESPOSTAS QUE NÃO CONTENHAM DOCUMENTOS
                        temperature=0 # PARA TORNAR AS RESPOSTAS MAIS PRECISAS E MENOS CRIATIVAS, O QUE É IMPORTANTE QUANDO SE TRATA DE RESPONDER PERGUNTAS COM BASE EM DOCUMENTOS.                  
                    )
    
    db_path_name = "faiss_index"

    db = VectorDB(db_path_name).db()
    print("Índice de busca carregado com sucesso!\n")

    template = """
                    Você é um assistente de perguntas e respostas especializado em seguros.
                    
                    Seus conhecimentos estão baseados em um conjunto de documentos relacionados a seguros, CONTEXTO,
                    que podem conter informações relevantes para responder às perguntas dos usuários. 

                    Reescreva a pergunta do usuário para incluir **TODOS** os sinônimos importantes do bem informado. Ex: Se a pergunta mencionar 'carro', certifique-se de incluir 
                    'veículo' na busca.                  

                    **NUNCA** utilizar outra fonte de informação para responder as perguntas dos usuários que não seja CONTEXTO.

                    PERGUNTA:                    
                    ------------------------------------------------------------------------------------------------------------------------------------------------------------------
                        {question}
                    ------------------------------------------------------------------------------------------------------------------------------------------------------------------

                    CONTEXTO:                    
                    ------------------------------------------------------------------------------------------------------------------------------------------------------------------
                        {context}
                    ------------------------------------------------------------------------------------------------------------------------------------------------------------------

                    DIRETRIZES:
                    ------------------------------------------------------------------------------------------------------------------------------------------------------------------
                        - Se os documentos não contiverem informações relevantes para responder à pergunta, **SEMPRE** responda "Desculpe, não tenho informações suficientes para
                        responder a essa pergunta. Entre em contato com um especialista por meio de email, informe no assunto um resumo do problema e também o protocolo gerado, para 
                        que ele possa lhe ajudar." e nada mais. 

                        - Se os documentos contiverem informações relevantes, responda com base nessas informações. Seja claro e conciso nas suas respostas. Realize todas as 
                        correções ortográficas e gramaticais, referentes a lingua portuguesa, em sua resposta.
                    ------------------------------------------------------------------------------------------------------------------------------------------------------------------ 
                    
                    **SEMPRE** utilizar o seguinte formato para a saída.

                    {{
                        "pergunta": "Pergunta do usuário",     
                        "resposta": "A resposta para a pergunta. Se for informar o bem, não é necessário informar seus sinonimos. Se a resposta contiver a expressão 'canais de atendimento', solicitar envio de email e número do protocolo.",
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
    # O RetrievalQA pega os chunks retornados pelo retriever, concatena seus textos e injeta o resultado dentro da variável {context} do PromptTemplate.
    self.qa_chain = RetrievalQA.from_chain_type(
                                                  llm=llm, 
                                                  retriever=db.as_retriever(),                                                                                                      
                                                  chain_type_kwargs={"prompt": prompt_template},
                                                  return_source_documents=True                                                                                                                                                                              
                                                )
    
  def query(self, question: str) -> str:
      
      import json

      output = self.qa_chain.invoke({"query": question}) 
      print("Saída: \n",output)
      
      try:          
            result = json.loads(output['result'])

      except json.JSONDecodeError as e:
            # TENTA EXTRAIR O JSON DE DENTRO DA RESPOSTA USANDO EXPRESSÃO REGULAR
            match = re.search(r"\{.*?\}", str(output['result']), re.DOTALL) # A FLAG re.DOTALL 
                                                                            # PERMITE QUE O PONTO (.) NA EXPRESSÃO REGULAR 
                                                                            # CORRESPONDA A QUALQUER CARACTERE, INCLUINDO 
                                                                            # QUEBRAS DE LINHA, O QUE É ÚTIL PARA EXTRAIR JSONS 
                                                                            # MULTILINHA.
            if match:
                  result = json.loads(match.group().strip())
            else:
                  # SE NÃO ENCONTRAR JSON, CRIA UMA ESTRUTURA PADRÃO
                  result = {
                        "pergunta": question,
                        "resposta": str(output['result'])
                  }

      
      # EXTRAÇÃO DAS FONTES DOS DOCUMENTOS RETORNADOS PELO RETRIEVER PARA INCLUIR NA RESPOSTA DO AGENTE. 
      source_documents = output['source_documents']
      fontes = list(set([path.basename(r.metadata["source"]) if r and len(source_documents) > 0 else "Nenhuma fonte encontrada" for r in source_documents]))      
      fontes = "Todas" if len(fontes) == len(source_documents) else fontes 
      result["fontes"] = fontes
      
      # Limpa tags HTML residuais que o LLM às vezes injeta na resposta
      self.json = json.dumps(result, indent=2, ensure_ascii=True)
      
      print("JSON\n",self.json)    

      return self.json 


# CÓDIGO PARA WARM UP PARA CRIAR O BANCO DE DADOS VETORIAL 
if __name__ == "__main__":

    inicio = time() # Marca o tempo inicial

    agente = AgenteChatbotSeguro(newconversation = False) # INICIA O AGENTE COM O CACHE ATIVO PARA APROVEITAR O BANCO DE DADOS VETORIAL JÁ CRIADO. SE O CACHE ESTIVER DESATIVADO, O BANCO DE DADOS VETORIAL VAI SER RECRIADO DO ZERO, O QUE PODE DEMORAR MUITO MAIS PARA RESPONDER A PRIMEIRA PERGUNTA.

    # PERGUNTAS PARA TESTAR O AGENTE
    """     print(agente.query("Não encontrei um seguro que eu contratei. O que fazer?"),"\n")
    fim = time() # Marca o tempo final
    #print(f"\nTempo total de execução: {fim - inicio:.2f} segundos\n")

    inicio = time() # Marca o tempo inicial
    print(agente.query("Como devo proceder caso tenha meu celular roubado ?"),"\n")
    fim = time() # Marca o tempo final
    #print(f"\nTempo total de execução: {fim - inicio:.2f} segundos\n") """

    # WARMUP PARA CRIAR O BANCO DE DADOS VETORIAL
    print(agente.query("Como posso acionar o seguro ?"))
    fim = time() # Marca o tempo final
    print(f"\nTempo total de execução: {fim - inicio:.2f} segundos\n")