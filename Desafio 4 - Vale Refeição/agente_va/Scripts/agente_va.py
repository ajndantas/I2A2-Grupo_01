# [markdown]
# PACOTES

#%pip install -r requirements.txt

# [markdown]
# ### IMPORTS

from os import getenv
from os.path import exists
from pandas import read_csv, read_sql, DataFrame
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.globals import set_debug
import streamlit as st

set_debug(True)

class SemResposta(Exception):
    pass

def obtem_sim_nao(pergunta,df,llm):
    
    # CRIANDO O PROMPT PARA A LLM COM A SAIDA FORMATADA
    template = """É possível responder a pergunta "{pergunta}" do usuário considerando os itens a seguir ? 
    1 - As colunas {colunas_df} do dataframe.
    2 - Os dados {df} 
    {resposta}"""
    
    # FORMATANDO A SAÍDA DA LLM COM JsonOutputParser
    class Resposta(BaseModel):
        resposta: str = Field(description="Responda Sim ou Não")

    parseador = JsonOutputParser(pydantic_object=Resposta)
   
    prompt_template = PromptTemplate(
                                        template=template,
                                        input_variables=["pergunta","df","colunas_df"],
                                        partial_variables={"resposta" : parseador.get_format_instructions()}
                                    )

    # CRIANDO A CADEIA DE EXECUÇÃO PARA A LLM
    chain = prompt_template | llm | parseador
    
    # INVOCANDO A LLM
    resposta = chain.invoke(input={"pergunta":pergunta, "df": df, "colunas_df": list(df.columns.values)})['resposta']
        
    return resposta

def llm_gera_query(llm,engine,pergunta):

        template_query = """Qual query deve ser executada para responder
        a pergunta "{pergunta}"? Considere os seguintes passos:
        ##############################################################
        1 - As colunas "{colunas}" 
        2 - O nome da tabela é "arquivo".
        ##############################################################
                    
        {formatacao_saida}"""

        # FORMATANDO A SAÍDA DA LLM COM JsonOutputParser
        class Query(BaseModel):
            query: str = Field(description='Esta é a query com DISTINCT, sem UNION, com todas as colunas necessárias, aonde o nome de cada coluna e o da tabela {nome_arquivo} devem ficar entre "')

        parseador = JsonOutputParser(pydantic_object=Query)
        
        prompt_template_query = PromptTemplate(
                                                template=template_query,
                                                input_variables=["pergunta","colunas"],
                                                partial_variables={"formatacao_saida" : parseador.get_format_instructions()}
                                              )

        # CRIANDO A CADEIA DE EXECUÇÃO PARA A LLM
        chain = prompt_template_query | llm | parseador

        with engine.connect() as con:
            query = text(f'PRAGMA table_info("arquivo")') # OBTENDO AS COLUNAS DO BD
            rs = con.execute(query)
            rows = rs.fetchall()
            colunas_query = sorted([col[1] for col in rows])
        
        query = chain.invoke(input={"pergunta":pergunta, "colunas":colunas_query})['query']

        print('\nQuery: ',query)
        
        return query


# [markdown]
# ### <b>AGENTE 3: Resposta e Interação</b>
# <b>Responsabilidade:</b> Interface inteligente com usuários<br/><br/>
# <b>Funcionalidades:</b>
# <ul><li>Integração com LLMs para consultas em linguagem natural.</li></ul>

def agente3(pergunta,arquivo,engine):

    try:
            print('\nExecutando agente 3...')

            print('\nPergunta: ',pergunta)

            resposta = agente2(pergunta,arquivo,engine) # A ENGINE NÃO É FECHADA AUTOMATICAMENTE, APENAS AS CONEXÕES QUANDO USADAS COM WITH

            if (not isinstance(resposta,str)) and resposta is not None: # VERIFICA SE A LLM RESPONDEU SIM PARA ALGUM ARQUIVO (DEVOLVEU UM DATAFRAME), OU SEJA, SE É CAPAZ DE RESPONDER A PERGUNTA DO USUÁRIO COM O
                                                                        # ARQUIVO FORNECIDO
               
               return resposta

            elif resposta == "Não":
                raise SemResposta

    except SemResposta:
            resposta = "SemResposta"
            return resposta # RETORNANDO A EXCEÇÃO PARA O FRONTEND, AGENTE 1

# [markdown]
# ### <b>AGENTE 2: Extração e Aprendizado</b>
# <b>Responsabilidade:</b> Processar documentos e extrair dados relevantes<br/><br/>
# <b>Funcionalidades:</b>
# <ul><li>OCR avançado para digitalização de documentos</li></ul>
# <ul><li>NLP para identificação e extração de campos específicos</li></ul>
# <ul><li>IA para adaptação a novos layouts</li></ul>
# <ul><li>Validação cruzada de dados extraídos</li></ul>

def agente2(pergunta,arquivo,engine):

    print('\nExecutando agente 2...')
    
    # INTEGRAÇÃO COM A LLM
    load_dotenv() # CARREGANDO O ARQUIVO COM A API_KEY

    llm = ChatGoogleGenerativeAI( # ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",  # ou "gemini-2.5-pro" ou "gemini-2.5-flash", gpt-4.1-mini
        temperature=0.5, # Padrão é 0.5
        google_api_key=getenv("GOOGLE_API_KEY") # google_api_key
    )
    
    ocr = NotaFiscalOCR() # INSTÂNCIA DO MOTOR OCR
    
    tipo = from_buffer(arquivo.getvalue(),mime=True)
    arquivo.seek(0)
    
    print(f"\nArquivo: {arquivo.name}, Tipo MIME detectado: {tipo}")
    
    if tipo not in ['text/plain','text/csv']:        
        
        imagem_proc = ocr.preprocessar_imagem(ocr.carregar_arquivo(arquivo))
        texto = ocr.extrair_texto(imagem_proc)
        
        print("\nTexto\n",texto)
        resposta = consultallmdocfiscal(texto,llm,tipo) # O NOME DAS COLUNAS ESTÁ AQUI 
        
        campos = resposta['campos'] # CAMPOS DO PRÓPRIO DOCUMENTO
        
        listacampos = resposta['sigcampos'] # AQUI ESTÁ A LISTA DE CAMPOS DO ARQUIVO
               
        df = DataFrame([resposta['valores']], columns=listacampos)                                       
                    
              
    elif tipo in ['text/plain','text/csv']: 
        
        df = read_csv(arquivo)
        campos = list(df.columns.values)
        
        resposta = consultallmdocfiscal(df,llm,tipo) # O NOME DAS COLUNAS ESTÁ AQUI
    
        listacampos = [x['significado'] for x in resposta['sigcampos']] # LISTA COM OS NOMES DOS CAMPOS DO DOCUMENTO FISCAL]        
        
        df = DataFrame(df.values, columns=listacampos)    
    
            
    df['TIPO'] = resposta['tipo']
    df['MODELO_DOC'] = resposta['modelo']        
    df['VERSÃO_DOC'] = resposta['versao']    
    df['ARQUIVO'] = arquivo.name        
            
    dfdocfiscal = DataFrame({'TIPO':[df['TIPO'].loc[0]],'MODELO':[df['MODELO_DOC'].loc[0]],'VERSÃO':[df['VERSÃO_DOC'].loc[0]]})
    
    dfcampos = DataFrame({'CAMPOS':[campos]}) # LISTA COM UMA LISTA DE CAMPOS
    
    resposta = obtem_sim_nao(pergunta,df,llm)                 
    
    if resposta == "Sim":
        
        # PERSISTINDO OS DADOS NO BANCO DE DADOS
        print('Sim para o arquivo: ',arquivo.name)

        df.to_sql(name='arquivo', con=engine, if_exists='replace', index=False)               
                    
        query = llm_gera_query(llm,engine,pergunta)
        
        # OBTENÇÃO DO RESULTADO DA QUERY
        with engine.connect() as con:
            dfsql = read_sql(query, con)                        
            dfresposta = dfsql      
                
        lista_df = []
        lista_df.append(dfdocfiscal)
        lista_df.append(dfresposta)
        lista_df.append(dfcampos)
                        
        resposta = lista_df
                                    
        return resposta # RESPOSTA PARA O FRONTEND, AGENTE 1
    
    elif resposta == "Não":
        print('Não é possível responder a essa pergunta com o arquivo carregado')
        return resposta

# [markdown]
# ### <b>AGENTE 1: Aquisição de Documentos</b>
# <b>Responsabilidade:</b> Obter e pré-processar documentos fiscais<br/><br/>
# <b>Funcionalidades:</b>
# <ul><li>Interface para upload manual de arquivos</li></ul>
# <ul><li>Validação inicial de formato e integridade dos documentos</li></ul>
# <ul><li>Organização e catalogação dos arquivos recebidos</li></ul>

def agente1(engine): # FRONTEND

    print("Executando o agente 1...")
    
    st.set_page_config(page_title="Agente VA", layout="centered")
    st.title("🤖 Agente VA")
        
    uploaded_file_ferias = st.file_uploader("📂 Adicione a planilha FÉRIAS", type=["xls","xlsx"])         
    uploaded_file_ativos = st.file_uploader("📂 Adicione a planilha ATIVOS", type=["xls","xlsx"])
    uploaded_file_sindvalor = st.file_uploader("📂 Adicione a planilha BASE SINDICATOS X VALOR", type=["xls","xlsx"])
    uploaded_file_admissao = st.file_uploader("📂 Adicione a planilha ADMISSAO", type=["xls","xlsx"])
                                         
    if st.button("🔍 Consultar"):
        if not uploaded_file_ferias:
            st.error("Você precisa fazer o upload da planilha FÉRIAS")
        elif not uploaded_file_ativos:
            st.error("Você precisa fazer o upload da planilha ATIVOS")
        elif not uploaded_file_sindvalor:
            st.error("Você precisa fazer o upload da planilha BASE SINDICATOS X VALOR")
        elif not uploaded_file_admissao:
            st.error("Você precisa fazer o upload da planilha ADMISSAO")                
            
        elif not pergunta.strip():
            st.error("Digite uma pergunta válida.")
            
        else:
            with st.spinner("Analisando os dados com IA..."):
                try:
                    resultado_df = agente3(pergunta, uploaded_file,engine) # RESPOSTA E INTERAÇÃO COM O USUÁRIO

                    if (isinstance(resultado_df,str) and resultado_df == "SemResposta") or (resultado_df is None):
                        st.warning("Consulta realizada, mas nenhum dado foi encontrado.")                  
                    
                    elif resultado_df is not None:
                        st.success("Dados sobre o documento fiscal")
                        st.table(resultado_df[0])
                        st.table(resultado_df[2])
                        st.success("✅ Resultado encontrado:")                        
                        st.dataframe(resultado_df[1])                                       
                                                
                except Exception as e:
                    st.error(f"Erro ao processar: {e}")

# [markdown]
# ### <b>TESTANDO</b>

if __name__ == "__main__":
    
    if not exists('nfs_data.db'): # CRIAÇÃO DO BANCO DE DADOS PARA A PRIMEIRA EXECUÇÃO
        print('\nCriando o banco de dados nfs_data...')     
    
    DATABASE_URL = "sqlite:///nfs_data.db" 
    engine = create_engine(DATABASE_URL,echo=True)        
          
    # INICIALIZAÇÃO DO AGENTE
    agente1(engine)  # Executa a função que inicia o agente
     

# EXPORTAR ESSE NOTEBOOK PARA UM SCRIPT PYTHON ANTES
#!streamlit run agente_nfs.py --server.port 8000

