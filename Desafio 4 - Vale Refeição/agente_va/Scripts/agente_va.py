# [markdown]
# PACOTES

#%pip install -r requirements.txt

# [markdown]
# ### IMPORTS

from os import getenv, remove
from os.path import exists
from pydantic import BaseModel, Field
from datetime import date
from typing import Dict
from pandas import DataFrame, read_excel
from sqlalchemy import create_engine, text, Table, MetaData, Integer, String, Date, Numeric, Column, CheckConstraint, ForeignKey, inspect
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from langchain.globals import set_debug
import streamlit as st

set_debug(True)

class SemResposta(Exception):
    pass

def cria_tabelas(engine,data_inicio_mes_competencia, data_fim_mes_competencia):
    
    """
        Prompt para elaborar um diagrama de classes por meio do Deepseek.
    
        Gere o diagrama de classes, referente a função cria_tabelas, do script em anexo. 

        #########################
        Siga os seguintes passos:

        1 - Crie o script para ser executado no aplicativo de sua escolha para a geração do diagrama.
        2 - Execute o script no aplicativo.
        3 - Se não ocorrer erros, informe a imagem.
        4 - Caso ocorram erros, voltar para o passo 1
        5 - Adicione as cardinalidades e os relacionamentos entre as tabelas.
        6 - Gere a imagem final do diagrama de classes.
        7 - Explique o diagrama por meio de todos os exemplos possíveis, utilizando todas as classes.
        #########################
    
    """
    print('Criando as tabelas...')            
    
    # Objeto metadata para manter informações das tabelas
    metadata = MetaData()    
    
    print('Criando as tabelas...')
    

    # Objeto metadata para manter informações das tabelas
    metadata = MetaData()

    # Define a tabela com chave primária e restrição CHECK
    funcionarios = Table( # RECEBERÁ A CARGA DE TODAS AS OUTRAS PLANILHAS
            'funcionarios', metadata,
            Column('matricula', Integer, primary_key=True),  
            Column('titulo_cargo', String, primary_key=True),
            Column('sindicato', String, ForeignKey('sindicato.nome'), primary_key=True), # NOVA COLUNA. REFERENCIA PARA A MESMA COLUNA PARA A PLANILHA BASE SINDICATO X VALOR. RECEBERÁ A CARGA DA PLANILHA Base dias uteis
            Column('desc_situacao', String, server_default="Trabalhando",primary_key=True), # ESTA NA PLANILHA ATIVOS E NAS OUTRAS
            Column('qtd_dias', Integer), # NOVA COLUNA
            Column('data_inicio_mes_competencia',Date, server_default=data_inicio_mes_competencia, primary_key=True), # NOVA COLUNA
            Column('data_fim_mes_competencia',Date, server_default=data_fim_mes_competencia, primary_key=True), # NOVA COLUNA
            Column('qtd_dias_uteis', Integer,ForeignKey('sindicato.qtd_dias_uteis'), primary_key=True), # NOVA COLUNA
            Column('valor',Numeric(7,2), ForeignKey('valor.valor'), primary_key=True), # NOVA COLUNA. REFERENCIA PARA A MESMA COLUNA PARA A PLANILHA BASE SINDICATO X VALOR. RECEBERÁ A CARGA DA PLANILHA Base sindicato x valor
            Column('data_demissao', Date), # NOVA COLUNA
            Column('comunicado_desligamento', String),  # NOVA COLUNA # Coluna para o comunicado de desligamento          
            CheckConstraint("desc_situacao IN ('Trabalhando', 'Férias', 'Licença Maternidade','Auxílio Doença','Exterior','Desligado')", name="ck_desc_situacao"), 
            CheckConstraint("NOT (desc_situacao = 'Férias' AND (qtd_dias IS NULL OR data_demissao IS NOT NULL))", name="ck_ferias_qtd_dias_obrigatorio"),
            CheckConstraint("NOT (desc_situacao = 'Desligado' AND (data_demissao IS NULL OR qtd_dias IS NOT NULL))", name="ck_desligado_data_demissao_obrigatorio"),
            CheckConstraint("NOT (desc_situacao = 'Trabalhando' AND (data_demissao IS NOT NULL OR qtd_dias IS NOT NULL))", name="ck_trabalhando"),
            CheckConstraint("NOT (desc_situacao IN ('Licença Maternidade','Auxílio Doença','Exterior') AND data_demissao IS NOT NULL)", name="ck_afastamento"),
            CheckConstraint("NOT (qtd_dias > 30 OR qtd_dias_uteis > 22)", name="ck_qtd_dias_dias_uteis")                                               
    )
    
    sindicato = Table( # DADOS DA PLANILHA Base dias uteis
            'sindicato', metadata,
            Column('nome', String, primary_key=True),    
            Column('estado', String), # SENÃO FOR INFORMADO, OBTÉM DO NOME DO SINDICATO POR MEIO DE IA, POIS CADA SINDICATO TEM UM ESTADO.
            Column('qtd_dias_uteis', Integer, primary_key=True) # RECEBERÁ O VALOR POR IA, DE ACORDO COM O SINDICATO E/OU ESTADO                                      
    )
    
    valor = Table( # DADOS DA PLANILHA BASE SINDICATO X VALOR
            'valor', metadata,
            Column('sindicato', String, ForeignKey('sindicato.nome'),primary_key=True), 
            Column('estado', String, ForeignKey('sindicato.estado')),                                
            Column('valor', Numeric(7,2),primary_key=True), # RECEBERÁ A CARGA DA PLANILHA BASE SINDICATO X VALOR E SERÁ REFERÊNCIA PARA A MESMA COLUNA PARA A PLANILHA ATIVOS.                                                                                                 #                        
    )           
       
    if not inspect(engine).get_table_names(): 
                                    
        # Cria a tabela no banco
        metadata.create_all(engine)


def recria_dataframe(df,resposta) -> DataFrame:
    
    data = {}
    for k in resposta.keys():
        valor = resposta[k]
        #print('Valor: ',valor)
        
        data[valor] = [v for v in df[k]] # ADICIONANDO OUTRO PAR CHAVE-VALOR
        #print('data: ', data,'\n')        
    
    df = DataFrame(data)    
    
    return df

# [markdown]
# DEPOIS VALIDAR O RETORNO NA TELA, QUANDO O ARQUIVO NÃO POSSUI DATAS

def obtem_dias_uteis(uploaded_file_base_dias, llm) -> Dict: # UTILIZADO NO FRONTEND
        
    dfbase_dias = read_excel(uploaded_file_base_dias)

    class base_dias(BaseModel):
        data_inicio_mes_competencia: date = Field(description="data de inicio do mes de competencia")
        data_fim_mes_competencia: date = Field(description="data fim do mês de competencia")
        qtd_dias_uteis: list[dict] = Field(description="quantidade de dias uteis por sindicato")

    parseador = JsonOutputParser(pydantic_object=base_dias)

    template = """
                   Você é um assistente que ajuda a encontrar datas e quantidade de dias úteis dentro de um DataFrame.
                   Dado o DataFrame {df}, Você deve seguir os seguintes passos:

                   ###################################################
                   1 - A data de inicio do mês de competencia, será a menor data encontrada. Caso não encontre, retorne null
                   2 - A data fim do mês de competencia, será a maior data encontrada. Caso não encontre, retorne null
                   3 - Caso não encontre o ano no DataFrame, retorne o ano atual no formato YYYY
                   4 - Retorne as datas no formato DD/MM/AAAA
                   5 - A quantidade de dias úteis, deve ser de acordo com a convenção mais recente para cada sindicato, e seu respectivo estado, estando o valor do estado não nulo ou nulo, 
                   informados no DataFrame. Caso não encontre a quantidade de dias úteis, retorne null
                   ###################################################

                   {formatador_saida_ia}
                """

    prompt_template = PromptTemplate(
        template=template,
        input_variables=["df"],
        partial_variables={"formatador_saida_ia": parseador.get_format_instructions()}
    )

    # CRIANDO A CADEIA DE EXECUÇÃO PARA A LLM
    chain = prompt_template | llm | parseador

    # INVOCANDO A LLM
    resposta = chain.invoke(input={"df": dfbase_dias.to_string()})

    return resposta

# [markdown]
# OK

def checa_colunas(uploaded_files, engine, llm) -> Dict:
    
    print('Mapeando colunas...')
            
    
    # MAPEANDO AS COLUNAS DOS DATAFRAMES PARA AS COLUNAS DO BANCO DE DADOS
    dictdf = {} # DICIONÁRIO PARA ARMAZENAR OS DATAFRAMES COM AS COLUNAS CORRIGIDAS. CHAVE = NOME DO ARQUIVO, VALOR = DATAFRAME
    for item in uploaded_files.items():
        
            print('Mapeando colunas do arquivo de chave: ', item[0])
        
            file = item[1]
            key = item[0]
            
            df = read_excel(file)           
                
            colunas_df = df.columns.tolist()
            
            with engine.connect() as conn:
                inspector = inspect(conn)
                tabela = inspector.get_table_names()[0]
                columns = inspector.get_columns(tabela)
            
            colunas_tabela = [col['name'] for col in columns]
            
            class colunas(BaseModel):
                mapeamento: dict = Field(description="mapeamento")
                                
                            
            parseador = JsonOutputParser(pydantic_object=colunas) 
            
            template = """
                            Você é um assistente que ajuda a mapear colunas de um DataFrame para as colunas de uma tabela de banco de dados.
                            Dada a lista de colunas do DataFrame e a lista de colunas da tabela, você deve sugerir um mapeamento entre elas com base no significado das colunas.
                            Colunas do DataFrame: {colunas_df}
                            Colunas da Tabela: {colunas_tabela}
                            
                            ###################################################
                            Este mapeamento deve ser feito da seguinte forma:
                            1 - Lado esquerdo, {colunas_df}
                            2 - Lado direito, {colunas_tabela}
                            3 - Não mapear qualquer coluna do dataframe com o significado de valor, para qualquer outra coluna da tabela, com o significado de titulo                   
                            ###################################################
                                                
                            {formatador_saida_ia}
                        """
            
            prompt_template = PromptTemplate(
                                                template=template,
                                                input_variables=["colunas_df", "colunas_tabela"],
                                                partial_variables={"formatador_saida_ia" : parseador.get_format_instructions()}
                                            )
                                            
            # CRIANDO A CADEIA DE EXECUÇÃO PARA A LLM
            chain = prompt_template | llm | parseador
                
            # INVOCANDO A LLM
            resposta = chain.invoke(input={"colunas_df":colunas_df, "colunas_tabela":colunas_tabela})
            
            resposta = resposta['mapeamento']        
            
            # RECRIANDO DATAFRAME COM OS MESMOS NOMES DE COLUNA DO BD   
            df = recria_dataframe(df, resposta)
            
            dictdf[key] = df
                            
        
    return dictdf

# [markdown]
# ESTOU AQUI

def analise_dados(uploaded_files,engine,llm,dictdias_uteis):
    
    print('Analisando os dados...')    
    
    """ uploaded_files = {
                                'base_dias':[uploaded_file_base_dias],
                                'ativos':[uploaded_file_ativos],
                                'ferias':[uploaded_file_ferias],
                                'desligados':[uploaded_file_desligados],
                                'afastamentos':[uploaded_file_afastamentos],
                                'exterior': [uploaded_file_exterior],
                                'admissao': [uploaded_file_admissao],
                                'sindvalor': [uploaded_file_sindvalor],
                                'estagaprendiz': uploaded_file_estagaprendiz
                         }
    """
    
    dictdf = checa_colunas(uploaded_files,engine,llm) # RETORNA O DATAFRAME COM AS COLUNAS VALIDADAS           
    
    for item in dictdf.items():
        print(f'Novo Dataframe {item[0]}')
        print(item[1])
        
    for item in dictdias_uteis.items():
        print(f'Chave: {item[0]}')
        print(f'Valor: {item[1]}')
    
    # NADA ABAIXO EXECUTADO
    
    # INSERE NO BD
    df = read_excel(file)
    
    # Verificando se as colunas necessárias estão presentes
    """ colunas_necessarias = ['matricula', 'titulo_cargo', 'sindicato', 'desc_situacao', 'dias_ferias', 'dia_retorno', 'dia_demissao', 'comunicado_desligamento']
    for coluna in colunas_necessarias:
        if coluna not in df.columns:
            raise ValueError(f'Coluna necessária ausente: {coluna}')
    
    # Validando os dados
    situacoes_validas = ['Trabalhando', 'Férias', 'Licença Maternidade', 'Auxílio Doença', 'Exterior', 'Desligado']
    for index, row in df.iterrows():
        if row['desc_situacao'] not in situacoes_validas:
            raise ValueError(f'Situação inválida na linha {index + 2}: {row["desc_situacao"]}')  # +2 para considerar o cabeçalho e índice 0
        
        if row['desc_situacao'] == 'Férias' and isnull(row['dias_ferias']):
            raise ValueError(f'Dias de férias obrigatórios para situação "Férias" na linha {index + 2}')
        
        if row['desc_situacao'] == 'Desligado' and (isnull(row['dia_demissao']) or not isnull(row['dia_retorno'])):
            raise ValueError(f'Data de demissão obrigatória e data de retorno deve ser nula para situação "Desligado" na linha {index + 2}')
        
        #if row['desc_situacao'] == 'Férias' and (not isnull(row['dia_retorno']) or     """

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
# ### <b>AGENTE 2: Extração</b>
# <b>Responsabilidade:</b> Processar documentos e extrair dados relevantes<br/><br/>
# <b>Funcionalidades:</b>
# <ul><li>Identificação e extração de campos específicos</li></ul>
# <ul><li>Validação cruzada de dados extraídos</li></ul>

def agente2(uploaded_files,engine,llm,dictdias_uteis):

    print('\nExecutando agente 2...')   
        
    analise_dados(uploaded_files,engine,llm,dictdias_uteis)           
       
    #print('Uploaded_files: ', uploaded_files) 
   


# [markdown]
# ### <b>AGENTE 1: Aquisição de Documentos</b>
# <b>Responsabilidade:</b> Obter e pré-processar documentos fiscais<br/><br/>
# <b>Funcionalidades:</b>
# <ul><li>Interface para upload manual de arquivos</li></ul>
# <ul><li>Validação inicial de formato e integridade dos documentos</li></ul>
# <ul><li>Organização e catalogação dos arquivos recebidos</li></ul>

def agente1(engine,llm): # FRONTEND

    #css()
    
    print("Executando o agente 1...")    
    
    st.set_page_config(page_title="Agente VA", layout="centered")
    st.title("🤖 Agente VA")
    
    combo_atestado = st.selectbox('Considerar Atestado médico para desconto ?',['Não','Sim'])
    
    uploaded_file_base_dias = st.file_uploader("📂 Adicione a planilha Base dias uteis", type=["xls","xlsx"])    
    
    data_inicio_mes_competencia = ""
    data_fim_mes_competencia = ""
        
    if uploaded_file_base_dias:
        
        with st.spinner("Analisando os dados com IA..."):
           dictdias_uteis = obtem_dias_uteis(uploaded_file_base_dias,llm)
           
           data_inicio_mes_competencia = dictdias_uteis['data_inicio_mes_competencia']
           data_fim_mes_competencia = dictdias_uteis['data_fim_mes_competencia']
        
        if data_inicio_mes_competencia is None or data_fim_mes_competencia is None:
            st.error("Não foi possível determinar as datas de início e fim do mês de competência. Verifique a planilha Base dias uteis.")
        else:
                            
                st.text(f'Data início mês de competência: {data_inicio_mes_competencia} - Data fim mês de competência: {data_fim_mes_competencia}') 
                uploaded_file_sindvalor = st.file_uploader("📂 Adicione a planilha Base sindicato x valor. Obrigatória", type=["xls","xlsx"])  
                uploaded_file_ativos = st.file_uploader("📂 Adicione a planilha ATIVOS", type=["xls","xlsx"])
                uploaded_file_ferias = st.file_uploader("📂 Adicione a planilha FÉRIAS", type=["xls","xlsx"]) # VALIDANDO AS COLUNAS COM ESSE
                uploaded_file_desligados = st.file_uploader("📂 Adicione a planilha DESLIGADOS", type=["xls","xlsx"]) 
                st.text('Se estiver como OK o comunicado até dia 15, não considerar compra, se informado depois do dia 15, considerar compra proporcional')
                uploaded_file_afastamentos = st.file_uploader("📂 Adicione a planilha AFASTAMENTO", type=["xls","xlsx"])
                uploaded_file_exterior = st.file_uploader("📂 Adicione a planilha EXTERIOR", type=["xls","xlsx"])
                uploaded_file_admissao = st.file_uploader("📂 Adicione a planilha ADMISSAO", type=["xls","xlsx"])                  
                uploaded_file_estagaprendiz = st.file_uploader("📂 Adicione as planilhas ESTÁGIO e APRENDIZ", type=["xls","xlsx"],accept_multiple_files=True)
                                                
                if st.button("🔍 Consultar"):                
                    
                    cria_tabelas(engine, data_inicio_mes_competencia, data_fim_mes_competencia) # CRIANDO AS TABELAS NO BD
                    
                    # if not uploaded_file_ativos:
                    #     st.error("Você precisa fazer o upload da planilha ATIVOS")
                    # elif not uploaded_file_ferias:
                    #    st.error("Você precisa fazer o upload da planilha FÉRIAS")
                    # elif not uploaded_file_desligados:
                    #     st.error("Você precisa fazer o upload da planilha DESLIGADOS")
                    # elif not uploaded_file_afastamentos:
                    #     st.error("Você precisa fazer o upload da planilha AFASTAMENTOS")
                    # elif not uploaded_file_exterior:
                    #    st.error("Você precisa fazer o upload da planilha EXTERIOR")
                    # elif not uploaded_file_admissao:
                    #     st.error("Você precisa fazer o upload da planilha ADMISSAO")             
                    if not uploaded_file_sindvalor:
                         st.error("Você precisa fazer o upload da planilha Base sindicato x valor")
                    # elif not uploaded_file_estagaprendiz or len(uploaded_file_estagaprendiz) != 2:
                    #     st.error("Você precisa fazer o upload somente das planilhas ESTÁGIO e APRENDIZ")            
                            
                    else:
                        uploaded_files = {
                                            'base_dias':[uploaded_file_base_dias],
                                            'ativos':[uploaded_file_ativos],
                                            'ferias':[uploaded_file_ferias],
                                            'desligados':[uploaded_file_desligados],
                                            'afastamentos':[uploaded_file_afastamentos],
                                            'exterior': [uploaded_file_exterior],
                                            'admissao': [uploaded_file_admissao],
                                            'sindvalor': [uploaded_file_sindvalor],
                                            'estagaprendiz': uploaded_file_estagaprendiz
                                        }
                        
                        with st.spinner("Analisando os dados com IA..."):
                            #try:
                                resultado_df = agente2(uploaded_files,engine,llm,dictdias_uteis) 

                                if (isinstance(resultado_df,str) and resultado_df == "SemResposta") or (resultado_df is None):
                                    st.warning("Consulta realizada, mas nenhum dado foi encontrado.")                  
                                
                                elif resultado_df is not None:
                                    st.success("Dados sobre o documento fiscal")
                                    st.table(resultado_df[0])
                                    st.table(resultado_df[2])
                                    st.success("✅ Resultado encontrado:")                        
                                    st.dataframe(resultado_df[1])                                       
                                                            
                            #except Exception as e:
                            #    st.error(f"Erro ao processar: {e}")             

                    

def css():
    
    st.markdown("""
    <style>
        :root {
            --bg1:#0f172a; --bg2:#1f2937; --card:#111827; --text:#e5e7eb; --muted:#9ca3af;
            --primary:#22c55e; --border:rgba(255,255,255,.08);
            --fileupload-bg: #d3d3d3; /* light gray */
        }
        body, .main, .stApp {
            background: linear-gradient(135deg,var(--bg1) 0%, var(--bg2) 100%) !important;
            color: var(--text) !important;
        }
        h1, h2, h3, h4, h5, h6, p, label, span, div {
            color: var(--text) !important;
        }
        
        div[data-testid="stForm"] {
            background: var(--card);
            padding: 22px;
            border-radius: 18px;
            border: 1px solid var(--border);
            box-shadow: 0 14px 40px rgba(0,0,0,.35);
        }
        
        .stButton > button {
            background: var(--primary);
            color: #0b111d;
            border: none;
            padding: 10px 16px;
            border-radius: 10px;
            font-weight: 700;
        }

        /* Light gray background for file uploader areas */
        div[data-testid="stFileUploader"] {
            background-color: var(--fileupload-bg) !important;
            border-radius: 12px;
            padding: 10px;
        }

        /* Black text for uploader labels containing "Adicione ..." */
        div[data-testid="stFileUploader"] label {
            color: black !important;
            font-weight: 600;
        }

        /* Black text for tables and dataframes */
        div[data-testid="stTable"] table, 
        div[data-testid="stDataFrame"] table {
            color: black !important;
        }

    </style>
    """, unsafe_allow_html=True)

# [markdown]
# ### <b>TESTANDO</b>

if __name__ == "__main__":
    
    # INTEGRAÇÃO COM A LLM
    load_dotenv() # CARREGANDO O ARQUIVO COM A API_KEY

    llm = ChatOpenAI ( #ChatGoogleGenerativeAI( 
        model="openai/gpt-oss-20b:free",  # ou "gemini-2.5-pro" ou "gemini-2.5-flash", gpt-4.1-mini, gemini-2.0-flash
        temperature=0.5, # Padrão é 0.5
        base_url="https://openrouter.ai/api/v1",
        api_key=getenv("OPENROUTER_GPT_OSS") # google_api_key        
    )
    
    #if not exists('va_data.db'): # CRIAÇÃO DO BANCO DE DADOS PARA A PRIMEIRA EXECUÇÃO
    #    print('\nCriando o banco de dados va_data...')     
    
    # PARA TESTES
    if exists('va_data.db'):
        remove('va_data.db')
    
    DATABASE_URL = "sqlite:///va_data.db" 
    engine = create_engine(DATABASE_URL,echo=True)        
          
    # INICIALIZAÇÃO DO AGENTE
    agente1(engine,llm)  # Executa a função que inicia o agente
     

# EXPORTAR ESSE NOTEBOOK PARA UM SCRIPT PYTHON ANTES
#!streamlit run agente_va.py --server.port 8100

