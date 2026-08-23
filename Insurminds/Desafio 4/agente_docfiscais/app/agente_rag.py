from dotenv import load_dotenv
from os import getenv
from langchain_core.globals import set_debug, set_llm_cache, set_verbose
from langchain_core.caches import InMemoryCache
from time import time
import re
from pathlib import Path

set_debug(True)
#set_verbose(True)

ENV_PATH = (
                Path(__file__) # O CAMINHO DO ARQUIVO ATUAL
                .resolve() # RESOLVE O CAMINHO ABSOLUTO
                .parent # RETORNA O CAMINHO DA PASTA PAI DO ARQUIVO ATUAL
            )
            

load_dotenv(dotenv_path=f"{ENV_PATH}/.env")  # CARREGANDO O ARQUIVO .env DA PASTA DO APP, pois antes só funcionaria se 
                                             # o processo fosse iniciado na pasta correta, ou quando o arquivo .env está no diretório de trabalho atual. 
                                             # No seu projeto, a aplicação é iniciada em um diretório diferente do que contém o arquivo da aplicação, 
                                             # então o Python não encontrava o arquivo app/.env.

class AgenteRag:
  
  def __init__(self):
                  
    # -------------------------------------------------------
    # Cache nativo do LangChain (InMemoryCache)
    # -------------------------------------------------------
    self.__set_memory() # ATIVA O CACHE DO LANGCHAIN

    # TÉCNICA DE LAZY IMPORTING PARA CARREGAR AS DEPENDÊNCIAS APENAS QUANDO FOR NECESSÁRIO, O QUE PODE MELHORAR A PERFORMANCE DO PROGRAMA.
    from langchain_openai import ChatOpenAI 
    from langchain_core.prompts import PromptTemplate
    from langchain_core.output_parsers import JsonOutputParser
    from pydantic import BaseModel, Field

    llm = ChatOpenAI(
                        model="gpt-5.4-mini", # MAIS RÁPIDO
                        #model="gpt-5.6-luna",                   
                        api_key=getenv("API_KEY"),                        
                        #reasoning_effort="high", #, # PARA EVITAR ERROS NAS RESPOSTAS QUE NÃO CONTENHAM DOCUMENTOS
                        temperature=0 # PARA TORNAR AS RESPOSTAS MAIS PRECISAS E MENOS CRIATIVAS, O QUE É IMPORTANTE QUANDO SE TRATA DE RESPONDER PERGUNTAS COM BASE EM DOCUMENTOS.                  
                    )    


    class OutputSchema(BaseModel):
        pergunta: str = Field(description="A pergunta do usuário")
        resposta: str = Field(description="A resposta para a pergunta.")
        tipo: str = Field(description="O tipo da resposta. Se for somente texto, responder como text, se for texto e tabela, responder como table, se for texto com gráfico, responder como chart, se for texto, tabela e grafico, responder como mixed.")
        

    parseador = JsonOutputParser(pydantic_object=OutputSchema)

    template = """
                    Você é um assistente de perguntas e respostas, especializado em documentos fiscais e que 
                    
                    Seus conhecimentos estão baseados em um conjunto de documentos relacionados a documentos fiscais, CONTEXTO,
                    que podem conter informações relevantes para responder às perguntas dos usuários. 

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
                        responder a essa pergunta. 

                        - Se os documentos contiverem informações relevantes, responda com base nessas informações. Seja claro e conciso nas suas respostas. Realize todas as 
                        correções ortográficas e gramaticais, referentes a lingua portuguesa, em sua resposta.

                        - **NUNCA** responda em branco, em vez disso responda: "Desculpe, não tenho informações suficientes para responder a essa pergunta."
                    ------------------------------------------------------------------------------------------------------------------------------------------------------------------ 
                    
                    **SEMPRE** utilizar o seguinte formato para a saída.

                    {formatador da saida}
                    
                """    

    prompt_template = PromptTemplate(
                                        template=template,
                                        input_variables=["context", "question"],
                                        partial_variables={"formatador da saida":  parseador.get_format_instructions()} # O PARSEADOR VAI SER INJETADO NO PROMPT TEMPLATE PARA SER USADO DENTRO DO TEMPLATE DE PROMPT, O QUE PERMITE QUE O LLM FORMATE A RESPOSTA DE ACORDO COM O ESQUEMA DEFINIDO PELO PARSEADOR.                                                                          
                                    )
    

    self.__qa_chain = prompt_template | llm | parseador

    
  def query(self, question: str) -> str:      
      
      import json

      with open(f"{ENV_PATH}/rag_docs/extracted_text.txt", "r", encoding="utf-8") as f:
          context = f.read()
      
      output = self.__qa_chain.invoke({"question": question, "context": context}) 
      print("Saída: \n",output)

      result = ""

      try:          
            result = json.dumps(output, indent=2, ensure_ascii=True)

      except json.JSONDecodeError as e:
            # TENTA EXTRAIR O JSON DE DENTRO DA RESPOSTA USANDO EXPRESSÃO REGULAR
            match = re.search(r"\{.*?\}", str(output), re.DOTALL) # A FLAG re.DOTALL 
                                                                  # PERMITE QUE O PONTO (.) NA EXPRESSÃO REGULAR 
                                                                  # CORRESPONDA A QUALQUER CARACTERE, INCLUINDO 
                                                                  # QUEBRAS DE LINHA, O QUE É ÚTIL PARA EXTRAIR JSONS 
                                                                  # MULTILINHA.
            if match:
                  result = json.dumps(match.group().strip())
            else:
                  # SE NÃO ENCONTRAR JSON, CRIA UMA ESTRUTURA PADRÃO
                  result = {
                        "pergunta": question,
                        "resposta": str(output['resposta']),
                        "tipo": "text"
                  }      

      
      # Limpa tags HTML residuais que o LLM às vezes injeta na resposta
      self.json = result
      
      print("JSON\n",self.json)    

      return self.json

  
  def __set_memory(self):
      
      set_llm_cache(InMemoryCache()) 
      print("Memória personalizada ativada para iniciar uma nova conversa com um histórico específico.\n")


# CÓDIGO PARA WARM UP PARA CRIAR O BANCO DE DADOS VETORIAL 
if __name__ == "__main__":

    inicio = time() # Marca o tempo inicial

    agente = AgenteRag() # INICIA O AGENTE COM O CACHE ATIVO PARA APROVEITAR O BANCO DE DADOS VETORIAL JÁ CRIADO. SE O CACHE ESTIVER DESATIVADO, O BANCO DE DADOS VETORIAL VAI SER RECRIADO DO ZERO, O QUE PODE DEMORAR MUITO MAIS PARA RESPONDER A PRIMEIRA PERGUNTA.

    # PERGUNTAS PARA TESTAR O AGENTE
    """     print(agente.query("Não encontrei um seguro que eu contratei. O que fazer?"),"\n")
    fim = time() # Marca o tempo final
    #print(f"\nTempo total de execução: {fim - inicio:.2f} segundos\n")

    inicio = time() # Marca o tempo inicial
    print(agente.query("Como devo proceder caso tenha meu celular roubado ?"),"\n")
    fim = time() # Marca o tempo final
    #print(f"\nTempo total de execução: {fim - inicio:.2f} segundos\n") """

    # WARMUP PARA CRIAR O BANCO DE DADOS VETORIAL
    print(agente.query("Qual é a razão social ?"))
    fim = time() # Marca o tempo final
    print(f"\nTempo total de execução: {fim - inicio:.2f} segundos\n")