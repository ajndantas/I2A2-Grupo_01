#%pip install -qqqr requirements.txt

# [markdown]
# ### IMPORTS

from os import getenv
from os.path import exists
from pandas import read_csv, read_sql, DataFrame
import sqlalchemy as sqlalc
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from magic import from_file
import motor_ocr_otimizado as ocr
import streamlit as st

class SemResposta(Exception):
    pass

# [markdown]
# ### <b>AGENTE 1: Aquisição de Documentos</b>
# <b>Responsabilidade:</b> Obter e pré-processar documentos fiscais<br/><br/>
# <b>Funcionalidades:</b>
# <ul><li>Interface para upload manual de arquivos (PDF, imagens)</li></ul>
# <ul><li>Integração com APIs de órgãos governamentais (SEFAZ)</li></ul>
# <ul><li>Validação inicial de formato e integridade dos documentos</li></ul>
# <ul><li>Organização e catalogação dos arquivos recebidos</li></ul>

def agente1():

    print("Executando o agente 1...")
    
    st.set_page_config(page_title="Agente NFe", layout="centered")
    st.title("🤖 Agente Inteligente para Notas Fiscais")

    pergunta = st.text_input("📝 Digite sua pergunta sobre os dados:")

    uploaded_file = st.file_uploader("📂 Envie um arquivo CSV, PDF ou PNG da NFe", type=["csv","pdf","png"])

    if st.button("🔍 Consultar"):
        if not uploaded_file:
            st.error("Você precisa fazer o upload de um arquivo CSV, PDF ou de uma imagem PNG.")
            
        elif not pergunta.strip():
            st.error("Digite uma pergunta válida.")
            
        else:
            with st.spinner("Analisando os dados com IA..."):
                try:
                    resultado_df = agente3(pergunta, uploaded_file)

                    if (isinstance(resultado_df,str) and resultado_df == "SemResposta") or (isinstance(resultado_df, DataFrame) and resultado_df.empty):
                        st.warning("Consulta realizada, mas nenhum dado foi encontrado.")                  
                        
                    elif isinstance(resultado_df, DataFrame) and not resultado_df.empty:
                        st.success("✅ Resultado encontrado:")
                        st.dataframe(resultado_df)                                        
                        
                except Exception as e:
                    st.error(f"Erro ao processar: {e}")

# [markdown]
# ### <b>AGENTE 2: Extração e Aprendizado</b>
# <b>Responsabilidade:</b> Processar documentos e extrair dados relevantes<br/><br/>
# <b>Funcionalidades:</b>
# <ul><li>OCR avançado para digitalização de documentos</li></ul>
# <ul><li>NLP para identificação e extração de campos específicos</li></ul>
# <ul><li>IA para adaptação a novos layouts</li></ul>
# <ul><li>Validação cruzada de dados extraídos</li></ul>

def agente2(pergunta,llm,engine,arquivo):

    print('\nExecutando agente 2...')
    
    # CATALOGANDO OS ARQUIVOS NO BD
    j=0

    inspector = sqlalc.inspect(engine) # INSPECTOR PARA LISTAR AS TABELAS DO BANCO DE DADOS

    tipo = from_file(arquivo, mime=True)
        
    """
        CSV -> text/plain
        PDF -> application/pdf
        PNG -> image/png
    """
    print(f"\nArquivo: {arquivo}, Tipo MIME detectado: {tipo}")
    
    # ESTOU AQUI
    if tipo != 'text/plain':
        imagem_proc = ocr.preprocessar_imagem(ocr.carregar_imagem(arquivo))
        texto = ocr.extrair_texto(imagem_proc)
        print("Texto extraído:\n")
        print(texto)       
        
    else:
        # SERÁ CRIADO UM DATAFRAME PARA CADA ARQUIVO
        df = read_csv(arquivo)

        # INSERINDO COLUNA COM O NOME DO ARQUIVO NO DATAFRAME
        df['ARQUIVO'] = arquivo
    
    """
        Utilizando a LLM para identificar se os campos e registros da base de documentos, são capazes de responder a pergunta
        do usuário.

        Se sim, os arquivos são persistidos no banco de dados, caso contrário, o arquivo é descartado.
    """
    # FORMATANDO A SAÍDA DA LLM COM JsonOutputParser
    class Resposta(BaseModel):
        resposta: str = Field(description="Responda Sim ou Não")

    parseador = JsonOutputParser(pydantic_object=Resposta)

    # CRIANDO O PROMPT PARA A LLM COM A SAIDA FORMATADA
    template = """É possível responder a pergunta {pergunta} do usuário baseado no dataframe {df} ? {resposta}"""

    prompt_template = PromptTemplate(
                                        template=template,
                                        input_variables=["pergunta","df"],
                                        partial_variables={"resposta" : parseador.get_format_instructions()}
                                    )

    # CRIANDO A CADEIA DE EXECUÇÃO PARA A LLM
    chain = prompt_template | llm | parseador
    
    # INVOCANDO A LLM
    resposta = chain.invoke(input={"pergunta":pergunta, "df": df})['resposta']
        
    if resposta == "Sim":
        
        # PERSISTINDO OS DADOS NO BANCO DE DADOS
        print('Sim para o arquivo: ',arquivo)

        # PRECISA VERIFICAR SE A TABELA COM O NOME DO ARQUIVO JÁ EXISTE NO BANCO DE DADOS
        if arquivo in inspector.get_table_names():
            dftable = read_sql(arquivo, con=engine)

            #print('dftable NFCABECALHO\n',dftable)

            # CUIDANDO DE DUPLICIDADE
            df = df[~df['CHAVE DE ACESSO'].isin(dftable['CHAVE DE ACESSO'])]

            # INSERINDO NO BANCO DE DADOS
            df.to_sql(name=arquivo, con=engine, if_exists='append', index=False)
                    
        
        # FORMATANDO A SAÍDA DA LLM COM JsonOutputParser
        class Query(BaseModel):
            query: str = Field(description='Esta é a query com DISTINCT aonde o nome de cada coluna e das tabelas devem ficar entre "')

        parseador = JsonOutputParser(pydantic_object=Query)

        # CRIANDO O PROMPT PARA A LLM COM A SAIDA FORMATADA
        template_query = """Qual query deve ser executada na tabela {nome_arquivo} com as colunas {colunas} para responder
        a pergunta {pergunta}? Se a query envolver as tabelas, deve ser feito um JOIN entre elas utlizando a coluna "CHAVE DE ACESSO" como chave. {formatacao_saida}"""

        prompt_template_query = PromptTemplate(
                                                template=template_query,
                                                input_variables=["pergunta","nome_arquivo","colunas"],
                                                partial_variables={"formatacao_saida" : parseador.get_format_instructions()}
                                              )

        # CRIANDO A CADEIA DE EXECUÇÃO PARA A LLM
        chain = prompt_template_query | llm | parseador

        with engine.connect() as con:
            query1 = sqlalc.text(f'PRAGMA table_info("{arquivo}")')
            rs = con.execute(query1)
            rows = rs.fetchall()
            colunas_query = sorted([col[1] for col in rows])
            
        query = chain.invoke(input={"pergunta":pergunta, "nome_arquivo":arquivo, "colunas":colunas_query})['query']

        print('\nQuery: ',query)

        # # OBTENÇÃO DO RESULTADO DA QUERY
        with engine.connect() as con:
            df = read_sql(query, con)
            resposta = df

        return resposta
    
    else:
        raise SemResposta

# [markdown]
# ### <b>AGENTE 3: Resposta e Interação</b>
# <b>Responsabilidade:</b> Interface inteligente com usuários<br/><br/>
# <b>Funcionalidades:</b>
# <ul><li>Integração com LLMs para consultas em linguagem natural.</li></ul>

def agente3(pergunta,arquivo):

    if not exists('nfs_data.db'): # CRIAÇÃO DO BANCO DE DADOS PARA A PRIMEIRA EXECUÇÃO
        print('\nCriando o banco de dados nfs_data...')
        DATABASE_URL = "sqlite:///nfs_data.db" # Define o nome do arquivo do banco de dados
        engine = sqlalc.create_engine(DATABASE_URL)

    else:
        engine = sqlalc.create_engine("sqlite:///nfs_data.db") # Conecta ao banco de dados existente


    # INTEGRAÇÃO COM A LLM
    load_dotenv() # CARREGANDO O ARQUIVO COM A API_KEY

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",  # ou "gemini-2.5-pro"
        temperature=0.5,
        google_api_key=getenv("GOOGLE_API_KEY")
    )


    try:
            print('\nExecutando agente 3...')

            print('\nPergunta: ',pergunta)

            resposta = agente1(pergunta,engine,arquivo,llm) # A ENGINE NÃO É FECHADA AUTOMATICAMENTE, APENAS AS CONEXÕES QUANDO USADAS COM WITH

            if resposta == "Sim": # VERIFICA SE A LLM RESPONDEU SIM PARA ALGUM ARQUIVO, OU SEJA, SE É CAPAZ DE RESPONDER A PERGUNTA DO USUÁRIO COM OS
                                  # ARQUIVOS FORNECIDOS
                                  
                query = agente2(pergunta,llm,engine,arquivo)

                # # OBTENÇÃO DO RESULTADO DA QUERY
                with engine.connect() as con:
                        df = read_sql(query, con)
                        resposta = df

            elif resposta == "Não":
                raise SemResposta

    except SemResposta:
            resposta = "SemResposta"

    print('\nResposta\n',f'{resposta}')
    
    return resposta

# [markdown]
# ### <b>TESTANDO</b>

if __name__ == "__main__":

     # TESTANDO OS TIPOS DE ARQUIVO
     #arquivo = "202401_NFs_Cabecalho.csv"
     #arquivo = "Grupo_01_Proposta_de_Projeto.pdf"
     arquivo = "nota_fiscal_exemplo.png"
     
     #print('Diretório atual: ',getcwd())
     
#    # EXEMPLOS DE PERGUNTA PARA TESTE. ELAS DEVEM SER OBTIDAS DO FRONTEND
     pergunta = "Qual é a chave de acesso da nota 3510129 ?"
     #pergunta = "Quem descobriu o Brasil ?"
     #pergunta = "Qual é a descrição dos serviços de nf com número 2525 ?"
     #pergunta = "Qual é a descrição dos serviços e a natureza da operação da nf com número 2525 ?"

     #resposta = agente3(pergunta, arquivo)  # Chama a função principal com a pergunta e o diretório
     #print('\nResposta: \n',resposta)
     
     agente1()  # Executa a função que inicia o agente