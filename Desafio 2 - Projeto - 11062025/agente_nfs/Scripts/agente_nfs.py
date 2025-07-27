# [markdown]
# ### INSTALAÇÕES

# [markdown]
# BINÁRIOS

# [markdown]
# <ul><li><a href="https://tesseract--ocr-github-io.translate.goog/tessdoc/Installation.html?_x_tr_sl=en&_x_tr_tl=pt&_x_tr_hl=pt&_x_tr_pto=tc">FAZER DOWNLOAD E INSTALAR O TESSERACT DE ACORDO COM O SEU SISTEMA OPERACIONAL</a></ul></li>
# <ul><li>FAZER DOWNLOAD DO POPPLER E DESCOMPACTAR NO DIRETÓRIO DE SCRIPTS</li></ul>
# <ul><ul><li><a href="https://github.com/oschwartz10612/poppler-windows?tab=readme-ov-file">PARA WINDOWS</a></li></ul></ul>
# <ul><ul><li><a href="https://poppler.freedesktop.org/">OUTROS SISTEMAS OPERACIONAIS</a></li></ul></ul>

# [markdown]
# PACOTES

#%pip install -qqqr requirements.txt

# [markdown]
# ### IMPORTS

from os import getenv,remove
from os.path import exists
from pandas import read_csv, read_sql, DataFrame
import sqlalchemy as sqlalc
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.globals import set_debug
from motor_ocr_otimizado import NotaFiscalOCR
import streamlit as st
from magic import from_buffer

set_debug(True)

class SemResposta(Exception):
    pass

def consultallmdocfiscal(texto,llm,tipo):
    
    # CRIANDO O PROMPT PARA A LLM COM A SAIDA FORMATADA
     
    if tipo not in ['text/plain','text/csv']: 
        
        class DocFiscal1(BaseModel):
            tipo: str = Field(description="Responda apenas com a sigla do tipo")
            nomecampos: list = Field(description="Nomes dos campos em poucas palavras")
            valores: list = Field(description="Somente os Valores")
            versao: str = Field(description="versão")
            modelo: str = Field(description="modelo")
            #nomescamposopc: list = Field(description="6 - Nomes dos campos opcionais") 
    
        parseador = JsonOutputParser(pydantic_object=DocFiscal1) 
            
        template = """Aja como um analista de contabilidade e forneça as seguintes informações sobre o documento fiscal referente a esse conteúdo "{texto}":
        ##########################################
        1 - Sigla do tipo do documento fiscal.
        2 - Significado dos nomes dos campos de acordo com a sigla do item 1 e as referências abaixo:
        a) Nota Técnica  
        b) Manual de Orientação do Contribuinte (MOC) 
        c) Schemas XSD
        
        3 - Os valores para cada um dos campos do item 2.
        4 - Baseados nos campos do item 2 e na sigla do item 1. Qual é a versão desse documento fiscal ? Caso não encontre, procurar na legislação. Responda somente com o número da versão. 
        5 - Baseados nos campos do item 2 e na sigla do item 1. Qual é o número do modelo desse documento fiscal ? Caso não encontre, procurar na legislação. Responda somente com o número do modelo.
        ###########################################
        
        {formatador_saida_ia}
        """
        prompt_template = PromptTemplate(
                                            template=template,
                                            input_variables=["texto"],
                                            partial_variables={"formatador_saida_ia" : parseador.get_format_instructions()}
                                        )
        
        # CRIANDO A CADEIA DE EXECUÇÃO PARA A LLM
        chain = prompt_template | llm | parseador
    
        # INVOCANDO A LLM
        resposta = chain.invoke(input={"texto":texto})
        
        
    elif tipo in ['text/plain','text/csv']:
        
        df = texto
        
        class DocFiscal2(BaseModel):
            tipo: str = Field(description="Responda apenas com a sigla do tipo")
            versao: str = Field(description="versão")
            modelo: str = Field(description="modelo")
            nomecampos: list = Field(description="Nomes dos campos em poucas palavras")
            #nomescamposopc: list = Field(description="6 - Nomes dos campos opcionais") 
    
        parseador = JsonOutputParser(pydantic_object=DocFiscal2) 
        
        template = """Aja como um analista de contabilidade e utilize como referência os itens abaixo para responder as perguntas 1,2 e 3:
        a) Nota Técnica  
        b) Manual de Orientação do Contribuinte (MOC) 
        c) Schemas XSD
        
        ##########################################
        PERGUNTAS:
        1 - Baseado no significado para cada um dos campos {colunas_df}. Qual é a sigla do tipo do documento fiscal.
        2 - Baseado no significado para cada um dos campos {colunas_df} e na sigla do item 1. Qual é a versão desse documento fiscal ? Caso não encontre, procurar na legislação. Responda somente com o número da versão.
        3 - Baseado no significado para cada um dos campos {colunas_df} e na sigla do item 1. Qual é o número do modelo desse documento fiscal ? Caso não encontre, procurar na legislação. Responda somente com o número do modelo.
        4 - Significado dos nomes dos campos {colunas_df} de acordo com a sigla do item 1 e as referências abaixo:
        a) Nota Técnica  
        b) Manual de Orientação do Contribuinte (MOC) 
        c) Schemas XSD     
        ###########################################
        
        {formatador_saida_ia}
        """   
        
        prompt_template = PromptTemplate(
                                            template=template,
                                            input_variables=["texto", "colunas_df"],
                                            partial_variables={"formatador_saida_ia" : parseador.get_format_instructions()}
                                        )
        
        # CRIANDO A CADEIA DE EXECUÇÃO PARA A LLM
        chain = prompt_template | llm | parseador
    
        # INVOCANDO A LLM
        resposta = chain.invoke(input={"colunas_df":list(df.columns.values)})
          
        
    return resposta

def cria_dataframe(resposta,arquivo):
    
    listaresultados = []
    
    listacampos = ['TIPO'] + [x for x in resposta['nomecampos']] + ['VERSÃO','MODELO','ARQUIVO']
    listavalores = [x for x in resposta['valores']]  # Convertendo para lista de listas
    
    listaresultados.append([resposta['tipo']] + listavalores + [resposta['versao'],resposta['modelo'],arquivo.name])
     
    df = DataFrame(listaresultados, columns=listacampos)     
       
    #print(df)
    
    return df

def obtem_sim_nao(pergunta,df,llm):
    
    #print(df)
    
    #    Utilizando a LLM para identificar se os campos e registros da base de documentos, são capazes de responder a pergunta
    #    do usuário.
    #
    #    Se sim, os arquivos são persistidos no banco de dados, caso contrário, o arquivo é descartado.
    
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
        
    #print(resposta)
    
    return resposta

def llm_gera_query(llm,engine,arquivo,pergunta):
    
        """
          Seu código cria um assistente inteligente que:

            1) Recebe uma pergunta em português.
            2) Consulta o banco de dados para saber quais colunas existem em uma tabela.
            3) Monta uma instrução detalhada (prompt) para um LLM, pedindo para ele criar uma query SQL com base na pergunta e nas colunas disponíveis, e exigindo que a resposta venha em um formato JSON específico.
            4) Envia essa instrução para o LLM.
            5) Recebe a resposta, a valida, extrai a query SQL e a exibe.  
        """
        
        # CRIANDO O PROMPT PARA A LLM COM A SAIDA FORMATADA
        #template_query = """Qual query deve ser executada na tabela {nome_arquivo} com as colunas {colunas} para responder
        #a pergunta {pergunta}? Se a query envolver mais de uma tabela, deve ser feito um JOIN entre elas utlizando a coluna "CHAVE DE ACESSO" como chave. {formatacao_saida}"""
        
        # PROBLEMA PARA GERAR QUERY QUANDO O ARQUIVO É IMAGEM
        template_query = """Qual query deve ser executada para responder
        a pergunta "{pergunta}"? Considere os seguintes passos:
        ##############################################################
        1 - As colunas "{colunas}" 
        2 - O nome da tabela é "{nome_arquivo}".
        ##############################################################
                    
        {formatacao_saida}"""

        # FORMATANDO A SAÍDA DA LLM COM JsonOutputParser
        class Query(BaseModel):
            query: str = Field(description='Esta é a query com DISTINCT, sem UNION, com todas as colunas necessárias, aonde o nome de cada coluna e o da tabela {nome_arquivo} devem ficar entre "')

        parseador = JsonOutputParser(pydantic_object=Query)
        
        prompt_template_query = PromptTemplate(
                                                template=template_query,
                                                input_variables=["pergunta","nome_arquivo","colunas"],
                                                partial_variables={"formatacao_saida" : parseador.get_format_instructions()}
                                              )

        # CRIANDO A CADEIA DE EXECUÇÃO PARA A LLM
        chain = prompt_template_query | llm | parseador

        with engine.connect() as con:
            # A TABELA TEM O NOME DO ARQUIVO
            query = sqlalc.text(f'PRAGMA table_info("{arquivo.name}")') # OBTENDO AS COLUNAS DO BD
            rs = con.execute(query)
            rows = rs.fetchall()
            colunas_query = sorted([col[1] for col in rows])
        
        query = chain.invoke(input={"pergunta":pergunta, "nome_arquivo":arquivo.name, "colunas":colunas_query})['query']

        print('\nQuery: ',query)
        
        return query


# [markdown]
# ### <b>AGENTE 3: Resposta e Interação</b>
# <b>Responsabilidade:</b> Interface inteligente com usuários<br/><br/>
# <b>Funcionalidades:</b>
# <ul><li>Integração com LLMs para consultas em linguagem natural.</li></ul>

def agente3(pergunta,arquivo):

    try:
            print('\nExecutando agente 3...')

            print('\nPergunta: ',pergunta)

            resposta = agente2(pergunta,arquivo) # A ENGINE NÃO É FECHADA AUTOMATICAMENTE, APENAS AS CONEXÕES QUANDO USADAS COM WITH

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

def agente2(pergunta,arquivo):

    print('\nExecutando agente 2...')
    
    if exists('nfs_data.db'): # CRIAÇÃO DO BANCO DE DADOS PARA A PRIMEIRA EXECUÇÃO
        remove('nfs_data.db')        
    
    print('\nCriando o banco de dados nfs_data...')
    DATABASE_URL = "sqlite:///nfs_data.db" # Define o nome do arquivo do banco de dados
    engine = sqlalc.create_engine(DATABASE_URL)

    #else:
    #    engine = sqlalc.create_engine("sqlite:///nfs_data.db") # Conecta ao banco de dados existente

    # INTEGRAÇÃO COM A LLM
    load_dotenv() # CARREGANDO O ARQUIVO COM A API_KEY

    llm = ChatGoogleGenerativeAI( # ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",  # ou "gemini-2.5-pro" ou "gemini-2.5-flash", gpt-4.1-mini
        temperature=0.5, # Padrão é 0.5
        google_api_key=getenv("GOOGLE_API_KEY") # google_api_key
    )
    
    # CATALOGANDO OS ARQUIVOS NO BD
    inspector = sqlalc.inspect(engine) # INSPECTOR PARA LISTAR AS TABELAS DO BANCO DE DADOS

    ocr = NotaFiscalOCR() # INSTÂNCIA DO MOTOR OCR
    
    #tipo = from_file(arquivo,mime=True)
    tipo = from_buffer(arquivo.getvalue(),mime=True)
    arquivo.seek(0)
    
    print(f"\nArquivo: {arquivo.name}, Tipo MIME detectado: {tipo}")
    
    if tipo not in ['text/plain','text/csv']:        
        
        imagem_proc = ocr.preprocessar_imagem(ocr.carregar_arquivo(arquivo))
        texto = ocr.extrair_texto(imagem_proc)
        
        print("\nTexto\n",texto)                

        resposta = consultallmdocfiscal(texto,llm,tipo) # O NOME DAS COLUNAS ESTÁ AQUI 
        
        df = cria_dataframe(resposta,arquivo) # DATAFRAME COM AS COLUNAS E VALORES QUE SERÁ USADO PARA A PERGUNTA COM RESPOSTA "Sim", "Não" 
                                              # E PARA CRIAR A TABELAS NO BD                                                        
          
    elif tipo in ['text/plain','text/csv']: 
        
        df = read_csv(arquivo)
        
        resposta = consultallmdocfiscal(df,llm,tipo) # O NOME DAS COLUNAS ESTÁ AQUI
        
    df['TIPO'] = resposta['tipo']
    df['MODELO'] = resposta['modelo']        
    df['VERSÃO'] = resposta['versao']
    listacampos = [x.replace('"','') for x in resposta['nomecampos']]
    #print(listacampos)
    df['ARQUIVO'] = arquivo.name        
        
    tipo = df['TIPO'].loc[0]
    modelo = df['MODELO'].loc[0]
    versao = df['VERSÃO'].loc[0]
        
    dfdocfiscal = DataFrame({'TIPO':[tipo],'MODELO':[modelo],'VERSÃO':[versao]})
    dfcampos = DataFrame({'CAMPOS':[listacampos]}) # LISTA COM UMA LISTA DE CAMPOS
        
    #print(dfdocfiscal)        
                 
    resposta = obtem_sim_nao(pergunta,df,llm)             
    
    if resposta == "Sim":
        
        # PERSISTINDO OS DADOS NO BANCO DE DADOS
        print('Sim para o arquivo: ',arquivo.name)

        # PRECISA VERIFICAR SE A TABELA COM O NOME DO ARQUIVO JÁ EXISTE NO BANCO DE DADOS
        tabela = arquivo.name
        if tabela not in inspector.get_table_names():
                        
            df.to_sql(name=tabela, con=engine, if_exists='replace', index=False)               
                    
        query = llm_gera_query(llm,engine,arquivo,pergunta)
        
        # OBTENÇÃO DO RESULTADO DA QUERY
        with engine.connect() as con:
            dfsql = read_sql(query, con)                        
            dfresposta = dfsql      
                
        lista_df = []
        lista_df.append(dfdocfiscal)
        lista_df.append(dfresposta)
        lista_df.append(dfcampos)
                        
        resposta = lista_df
                                    
        return resposta
    
    elif resposta == "Não":
        print('Não é possível responder a essa pergunta com o arquivo carregado')
        return resposta

# [markdown]
# ### <b>AGENTE 1: Aquisição de Documentos</b>
# <b>Responsabilidade:</b> Obter e pré-processar documentos fiscais<br/><br/>
# <b>Funcionalidades:</b>
# <ul><li>Interface para upload manual de arquivos (PDF, imagens)</li></ul>
# <ul><li>Integração com APIs de órgãos governamentais (SEFAZ)</li></ul>
# <ul><li>Validação inicial de formato e integridade dos documentos</li></ul>
# <ul><li>Organização e catalogação dos arquivos recebidos</li></ul>

def agente1(): # FRONTEND

    print("Executando o agente 1...")
    
    st.set_page_config(page_title="Agente NFe", layout="centered")
    st.title("🤖 Agente Inteligente para Notas Fiscais")

    uploaded_file = st.file_uploader("📂 Envie um documento fiscal no formato CSV, PDF ou PNG da NFe", type=["csv","pdf","png"])
        
    #print('Tipo Uploaded File: ',type(uploaded_file))
    
    pergunta = st.text_input("📝 Digite sua pergunta sobre os dados:")
    
    if st.button("🔍 Consultar"):
        if not uploaded_file:
            st.error("Você precisa fazer o upload de um arquivo CSV, PDF ou de uma imagem PNG.")
            
        elif not pergunta.strip():
            st.error("Digite uma pergunta válida.")
            
        else:
            with st.spinner("Analisando os dados com IA..."):
                try:
                    resultado_df = agente3(pergunta, uploaded_file) # RESPOSTA E INTERAÇÃO COM O USUÁRIO

                    if (isinstance(resultado_df,str) and resultado_df == "SemResposta") or (resultado_df is None):
                        st.warning("Consulta realizada, mas nenhum dado foi encontrado.")                  
                    
                    elif resultado_df is not None:
                        st.success("Dados sobre o documento fiscal")
                        st.table(resultado_df[0]) # Para remover os índices do Dataframe
                        st.table(resultado_df[2])
                        st.success("✅ Resultado encontrado:")                        
                        st.table(resultado_df[1])                                        
                                                
                except Exception as e:
                    st.error(f"Erro ao processar: {e}")

# [markdown]
# ### <b>TESTANDO</b>

if __name__ == "__main__":
    
     agente1()  # Executa a função que inicia o agente
     

# EXPORTAR ESSE NOTEBOOK PARA UM SCRIPT PYTHON ANTES
#!streamlit run agente_nfs.py --server.port 8000

