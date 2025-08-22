# [markdown]
# PACOTES

#%pip install -r requirements.txt

# [markdown]
# ### IMPORTS

from os import getenv, remove
from os.path import exists
from pandas import read_csv, read_sql, DataFrame, read_excel
from sqlalchemy import create_engine, text, Table, MetaData, Integer, String, Date, Numeric, Column, CheckConstraint, ForeignKey, inspect
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
#from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain.globals import set_debug
from datetime import date
import streamlit as st

set_debug(True)

class SemResposta(Exception):
    pass

def cria_tabelas(engine,data_inicio_mes_competencia, data_fim_mes_competencia):
    
    """
        Prompt para elaborar um diagrama de classes por meio do Deepseek.
    
        '1 - Gere uma figura de um diagrama de classes, baseado na função def cria_tabelas do script em anexo, para o SQLAlchemy.
         2 - Informe todos os possíveis registros, que não podem ser inseridos nessa estrutura de tabelas, sem repetição de cenários'
    
    """
    print('Criando as tabelas...')            
    
    # Objeto metadata para manter informações das tabelas
    metadata = MetaData()

    # Define a tabela com chave primária e restrição CHECK
    funcionarios = Table( # RECEBERÁ A CARGA DE TODAS AS OUTRAS PLANILHAS
            'funcionarios', metadata,
            Column('matricula', Integer, nullable=False),  
            Column('titulo_cargo', String, nullable=False),
            Column('sindicato', String, nullable=False),            
            Column('desc_situacao', String, server_default="Trabalhando"), # ESTA NA PLANILHA ATIVOS E NAS OUTRAS
            Column('qtd_dias', Integer), # NOVA COLUNA
            Column('data_inicio_mes_competencia',Date, server_default=data_inicio_mes_competencia), # NOVA COLUNA
            Column('data_fim_mes_competencia',Date, server_default=data_fim_mes_competencia), # NOVA COLUNA
            Column('qtd_dias_uteis', Integer,nullable=False), # NOVA COLUNA
            Column('data_demissao', Date), # NOVA COLUNA
            Column('comunicado_desligamento', String),  # NOVA COLUNA # Coluna para o comunicado de desligamento          
            CheckConstraint("desc_situacao IN ('Trabalhando', 'Férias', 'Licença Maternidade','Auxílio Doença','Exterior','Desligado')", name="ck_desc_situacao"), 
            CheckConstraint("NOT (desc_situacao = 'Férias' AND (qtd_dias IS NULL OR data_demissao IS NOT NULL))", name="ck_ferias_qtd_dias_obrigatorio"),
            CheckConstraint("NOT (desc_situacao = 'Desligado' AND (data_demissao IS NULL))", name="ck_desligado_data_demissao_obrigatorio"),
            CheckConstraint("NOT (desc_situacao = 'Trabalhando' AND (qtd_dias IS NOT NULL OR data_demissao IS NOT NULL))", name="ck_nao_ferias_qtd_dias"),
            CheckConstraint("NOT (desc_situacao IN ('Licença Maternidade','Auxílio Doença','Exterior') AND data_demissao IS NOT NULL)", name="ck_afastamento"),
            CheckConstraint("NOT (qtd_dias > 30 OR qtd_dias uteis > 22)", name="ck_qtd_dias_dias_uteis")                                               
    )
    
    sindicato = Table(
            'sindicato', metadata,
            Column('sindicato', String, ForeignKey('funcionarios.sindicato'), primary_key=True), # NOVA COLUNA 
            Column('estado', String, primary_key=True),
            Column('valor', Numeric(7,2),nullable=False)            
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

def checa_dias_uteis(uploaded_file_base_dias,llm):
    
    dfbase_dias = read_excel(uploaded_file_base_dias)
    
    class base_dias(BaseModel):
        data_inicio_mes_competencia : date = Field(description="data_inicio_mes_competencia")
        data_fim_mes_competencia : date = Field(description="data_fim_mes_competencia")                          
                    
    parseador = JsonOutputParser(pydantic_object=base_dias) 
    
    template = """
                   Você é um assistente que ajuda a encontrar datas dentro de um DataFrame.
                   Dado o DataFrame {df}, Você deve seguir os seguintes passos:
                                     
                   ###################################################                   
                   1 - A data de inicio do mês de competencia, será a menor data encontrada. Caso não encontre, retorne null
                   2 - A data fim do mês de competencia, será a maior data encontrada. Caso não encontre, retorne null
                   3 - Caso não encontre o ano no DataFrame {df}, retorne o ano atual no formato YYYY
                   4 - Retorne as datas no formato DD/MM/AAAA  
                   ###################################################
                                      
                   {formatador_saida_ia}
                """
    
    prompt_template = PromptTemplate(
                                        template=template,
                                        input_variables=["df"],
                                        partial_variables={"formatador_saida_ia" : parseador.get_format_instructions()}
                                    )
                                    
    # CRIANDO A CADEIA DE EXECUÇÃO PARA A LLM
    chain = prompt_template | llm | parseador
        
    # INVOCANDO A LLM
    resposta = chain.invoke(input={"df":dfbase_dias.to_string()})
       
    data_inicio_mes_competencia = resposta['data_inicio_mes_competencia']
    data_fim_mes_competencia = resposta['data_fim_mes_competencia']    
    
    
    return data_inicio_mes_competencia, data_fim_mes_competencia

# [markdown]
# ESTOU AQUI TAMBÉM

def checa_colunas(uploaded_files, engine, llm) -> DataFrame:
    
    print('Checando colunas...')
    
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
    
    # CHECANDO AS COLUNAS
    dfferias = read_excel(uploaded_files['ferias'][0])        
    #dfexterior = read_excel(uploaded_files['exterior'][0])
        
    
    df = dfferias
    
    """     if file.keys() in ['afastamentos','exterior']:
        df['qtd_dias'] = None
    elif file.keys() in ['ferias','afastamentos','exterior']:
        df['data_inicio_apuracao'] = None
        df['data_pgto'] = None
    elif file.keys() in ['sindicato']:
        df['estado'] = None
        df['valor'] = None """
        
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
    
    return df

# [markdown]
# ESTOU AQUI

def analise_dados(uploaded_files,engine,llm):
    
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
    
    df = checa_colunas(uploaded_files,engine,llm) # RETORNA O DATAFRAME COM AS COLUNAS VALIDADAS           
    
    print('Novo Dataframe')
    print(df)
    
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

def agente2(uploaded_files,engine,llm):

    print('\nExecutando agente 2...')   
        
    #analise_dados(uploaded_files['ferias'][0],engine,llm)
    analise_dados(uploaded_files,engine,llm)           
       
    #print('Uploaded_files: ', uploaded_files)
    
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
            data_inicio_mes_competencia, data_fim_mes_competencia = checa_dias_uteis(uploaded_file_base_dias,llm)
        
        if data_inicio_mes_competencia is None or data_fim_mes_competencia is None:
            st.error("Não foi possível determinar as datas de início e fim do mês de competência. Verifique a planilha Base dias uteis.")
        else:
                            
                st.text(f'Data início mês de competência: {data_inicio_mes_competencia} - Data fim mês de competência: {data_fim_mes_competencia}')  
                uploaded_file_ativos = st.file_uploader("📂 Adicione a planilha ATIVOS", type=["xls","xlsx"])
                uploaded_file_ferias = st.file_uploader("📂 Adicione a planilha FÉRIAS", type=["xls","xlsx"]) # VALIDANDO AS COLUNAS COM ESSE
                uploaded_file_desligados = st.file_uploader("📂 Adicione a planilha DESLIGADOS", type=["xls","xlsx"]) 
                st.text('Se estiver como OK o comunicado até dia 15, não considerar compra, se informado depois do dia 15, considerar compra proporcional')
                uploaded_file_afastamentos = st.file_uploader("📂 Adicione a planilha AFASTAMENTO", type=["xls","xlsx"])
                uploaded_file_exterior = st.file_uploader("📂 Adicione a planilha EXTERIOR", type=["xls","xlsx"])
                uploaded_file_admissao = st.file_uploader("📂 Adicione a planilha ADMISSAO", type=["xls","xlsx"])           
                uploaded_file_sindvalor = st.file_uploader("📂 Adicione a planilha Base sindicato x valor", type=["xls","xlsx"])    
                uploaded_file_estagaprendiz = st.file_uploader("📂 Adicione as planilhas ESTÁGIO e APRENDIZ", type=["xls","xlsx"],accept_multiple_files=True)
                                                
                if st.button("🔍 Consultar"):                
                    
                    cria_tabelas(engine, data_inicio_mes_competencia, data_fim_mes_competencia) # CRIANDO AS TABELAS NO BD
                    
                    # if not uploaded_file_ativos:
                    #     st.error("Você precisa fazer o upload da planilha ATIVOS")
                    if not uploaded_file_ferias:
                        st.error("Você precisa fazer o upload da planilha FÉRIAS")
                    # elif not uploaded_file_desligados:
                    #     st.error("Você precisa fazer o upload da planilha DESLIGADOS")
                    # elif not uploaded_file_afastamentos:
                    #     st.error("Você precisa fazer o upload da planilha AFASTAMENTOS")
                    # elif not uploaded_file_exterior:
                    #    st.error("Você precisa fazer o upload da planilha EXTERIOR")
                    # elif not uploaded_file_admissao:
                    #     st.error("Você precisa fazer o upload da planilha ADMISSAO")             
                    # elif not uploaded_file_sindvalor:
                    #     st.error("Você precisa fazer o upload da planilha Base sindicato x valor")
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
                                resultado_df = agente2(uploaded_files,engine,llm) 

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

