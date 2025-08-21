# [markdown]
# PACOTES

#%pip install -r requirements.txt

# [markdown]
# ### IMPORTS

from os import getenv, remove
from os.path import exists
from pandas import read_csv, read_sql, DataFrame, read_excel, isnull
from sqlalchemy import create_engine, text, Table, MetaData, Integer, String, Date, Numeric, Column, CheckConstraint, ForeignKey, inspect
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.globals import set_debug
from datetime import date
import streamlit as st

set_debug(True)

class SemResposta(Exception):
    pass

def cria_tabelas(engine):
    
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
            Column('desc_situacao', String, nullable=False), # ESTA NA PLANILHA ATIVOS E NAS OUTRAS
            Column('qtd_dias', Integer), # NOVA COLUNA
            Column('data_inicio_apuracao',Date,nullable=False), # NOVA COLUNA
            Column('data_pgto',Date,nullable=False), # NOVA COLUNA
            Column('qtd_dias_uteis', Integer,nullable=False), # NOVA COLUNA
            Column('dia_demissao', Date), # NOVA COLUNA
            Column('comunicado_desligamento', String),  # NOVA COLUNA # Coluna para o comunicado de desligamento          
            CheckConstraint("desc_situacao IN ('Trabalhando', 'Férias', 'Licença Maternidade','Auxílio Doença','Exterior','Desligado')", name="ck_desc_situacao"), 
            CheckConstraint("NOT (desc_situacao = 'Férias' AND qtd_dias IS NULL)", name="ck_ferias_qtd_dias_obrigatorio"),
            CheckConstraint("NOT (desc_situacao = 'Desligado' AND (dia_demissao IS NULL OR dia_retorno IS NOT NULL))", name="ck_desligado_dia_demissao_obrigatorio"),
            CheckConstraint("NOT (desc_situacao = 'Férias' AND (dia_demissao IS NOT NULL OR comunicado_desligamento IS NOT NULL))", name="ck_ferias"),
            CheckConstraint("NOT (desc_situacao = 'Trabalhando' AND qtd_dias IS NOT NULL)", name="ck_nao_ferias_qtd_dias"),
            CheckConstraint("NOT (desc_situacao IN ('Licença Maternidade','Auxílio Doença','Exterior') AND qtd_dias IS NULL)", name="ck_afastamento_qtd_dias_obrigatorio")                                   
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


def checa_colunas(key, file, engine, llm) -> DataFrame:
    
    print('Checando colunas...')    
            
    df = read_excel(file)
    
    if key is not None:
        # file.keys() in ['afastamentos','exterior','férias']:
        
        df['qtd_dias'] = None
    
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
                   3 - Caso exista alguma coluna da tabela que não tenha sido mapeada para alguma coluna do dataframe, não considere no mapeamento
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
                                'ativos':list[uploaded_file_ativos],
                                'ferias':list[uploaded_file_ferias],
                                'desligados':list[uploaded_file_desligados],
                                'afastamentos':list[uploaded_file_afastamentos],
                                'exterior': list[uploaded_file_exterior],
                                'admissao': list[uploaded_file_admissao],''
                                'sindvalor': list[uploaded_file_sindvalor],
                                'estagaprendiz': uploaded_file_estagaprendiz
                        } 
    """
    for file in uploaded_files:
        if file.keys() in ['afastamentos','exterior','férias']:
            df = checa_colunas(file.keys(),file,engine,llm) # RETORNA O DATAFRAME COM AS COLUNAS VALIDADAS          
            
    
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

# [markdown]
# ### <b>AGENTE 3: Resposta e Interação</b>
# <b>Responsabilidade:</b> Interface inteligente com usuários<br/><br/>
# <b>Funcionalidades:</b>
# <ul><li>Integração com LLMs para consultas em linguagem natural.</li></ul>

def agente3(uploaded_files,engine):

    try:
            print('\nExecutando agente 3...')

            resposta = agente2(uploaded_files,engine) # A ENGINE NÃO É FECHADA AUTOMATICAMENTE, APENAS AS CONEXÕES QUANDO USADAS COM WITH

            if (not isinstance(resposta,str)) and resposta is not None: # VERIFICA SE A LLM RESPONDEU SIM PARA ALGUM ARQUIVO (DEVOLVEU UM DATAFRAME), OU SEJA, SE É CAPAZ DE RESPONDER A PERGUNTA DO USUÁRIO COM O
                                                                        # ARQUIVO FORNECIDO
               
               return resposta

            elif resposta == "Não":
                raise SemResposta

    except SemResposta:
            resposta = "SemResposta"
            return resposta # RETORNANDO A EXCEÇÃO PARA O FRONTEND, AGENTE 1

# [markdown]
# ### <b>AGENTE 2: Extração - Estou Aqui</b>
# <b>Responsabilidade:</b> Processar documentos e extrair dados relevantes<br/><br/>
# <b>Funcionalidades:</b>
# <ul><li>Identificação e extração de campos específicos</li></ul>
# <ul><li>Validação cruzada de dados extraídos</li></ul>

def agente2(uploaded_files,engine):

    print('\nExecutando agente 2...')
    
    cria_tabelas(engine)
    
    # INTEGRAÇÃO COM A LLM
    load_dotenv() # CARREGANDO O ARQUIVO COM A API_KEY

    llm = ChatGoogleGenerativeAI( 
        model="gemini-1.5-flash",  # ou "gemini-2.5-pro" ou "gemini-2.5-flash", gpt-4.1-mini, gemini-2.0-flash
        temperature=0.5, # Padrão é 0.5
        google_api_key=getenv("GOOGLE_API_KEY") # google_api_key
    )    
    
    """ uploaded_files = {
                                'ativos':list[uploaded_file_ativos],
                                'ferias':list[uploaded_file_ferias],
                                'desligados':list[uploaded_file_desligados],
                                'afastamentos':list[uploaded_file_afastamentos],
                                'exterior': list[uploaded_file_exterior],
                                'admissao': list[uploaded_file_admissao],''
                                'sindvalor': list[uploaded_file_sindvalor],
                                'estagaprendiz': uploaded_file_estagaprendiz
                        } 
    """
    
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

def agente1(engine): # FRONTEND

    #css()
    
    print("Executando o agente 1...")
    
    st.set_page_config(page_title="Agente VA", layout="centered")
    st.title("🤖 Agente VA")
    
    combo_atestado = st.selectbox('Considerar Atestado médico para desconto ?',['Sim','Não'])
    
    mes_competencia = st.selectbox('Selecione o mês de competência',[1,2,3,4,5,6,7,8,9,10,11,12],index=3) #index = date.today().month - 1   
    
    uploaded_file_ativos = st.file_uploader("📂 Adicione a planilha ATIVOS", type=["xls","xlsx"])
    uploaded_file_ferias = st.file_uploader("📂 Adicione a planilha FÉRIAS", type=["xls","xlsx"])
    st.text('Se estiver como OK o comunicado até dia 15, não considerar compra. Se informado depois do dia 15, considerar compra proporcional') 
    uploaded_file_desligados = st.file_uploader("📂 Adicione a planilha DESLIGADOS", type=["xls","xlsx"]) # VALIDANDO AS COLUNAS COM ESSE
    uploaded_file_afastamentos = st.file_uploader("📂 Adicione a planilha AFASTAMENTO", type=["xls","xlsx"])
    uploaded_file_exterior = st.file_uploader("📂 Adicione a planilha EXTERIOR", type=["xls","xlsx"])
    uploaded_file_admissao = st.file_uploader("📂 Adicione a planilha ADMISSAO", type=["xls","xlsx"])
           
    uploaded_file_sindvalor = st.file_uploader("📂 Adicione a planilha BASE SINDICATOS X VALOR", type=["xls","xlsx"])    
    uploaded_file_estagaprendiz = st.file_uploader("📂 Adicione as planilhas ESTÁGIO e APRENDIZ", type=["xls","xlsx"],accept_multiple_files=True)
                                              
    if st.button("🔍 Consultar"):
        # if not uploaded_file_ativos:
        #     st.error("Você precisa fazer o upload da planilha ATIVOS")
        # elif not uploaded_file_ferias:
        #     st.error("Você precisa fazer o upload da planilha FÉRIAS")
        # elif not uploaded_file_desligados:
        #     st.error("Você precisa fazer o upload da planilha DESLIGADOS")
        if not uploaded_file_afastamentos:
             st.error("Você precisa fazer o upload da planilha AFASTAMENTOS")
        # elif not uploaded_file_exterior:
        #     st.error("Você precisa fazer o upload da planilha EXTERIOR")
        # elif not uploaded_file_admissao:
        #     st.error("Você precisa fazer o upload da planilha ADMISSAO")             
        # elif not uploaded_file_sindvalor:
        #     st.error("Você precisa fazer o upload da planilha BASE SINDICATOS X VALOR")
        # elif not uploaded_file_estagaprendiz or len(uploaded_file_estagaprendiz) != 2:
        #     st.error("Você precisa fazer o upload somente das planilhas ESTÁGIO e APRENDIZ")            
                
        else:
            uploaded_files = {
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
                    resultado_df = agente3(uploaded_files,engine) # RESPOSTA E INTERAÇÃO COM O USUÁRIO

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

# [markdown]
# ### <b>TESTANDO</b>

if __name__ == "__main__":
    
    #if not exists('va_data.db'): # CRIAÇÃO DO BANCO DE DADOS PARA A PRIMEIRA EXECUÇÃO
    #    print('\nCriando o banco de dados va_data...')     
    
     # PARA TESTES
    if exists('va_data.db'):
        remove('va_data.db')
    
    DATABASE_URL = "sqlite:///va_data.db" 
    engine = create_engine(DATABASE_URL,echo=True)        
          
    # INICIALIZAÇÃO DO AGENTE
    agente1(engine)  # Executa a função que inicia o agente
     

# EXPORTAR ESSE NOTEBOOK PARA UM SCRIPT PYTHON ANTES
#!streamlit run agente_va.py --server.port 8100

