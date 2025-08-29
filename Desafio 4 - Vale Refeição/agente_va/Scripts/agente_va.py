# [markdown]
# PACOTES

#%pip install -r requirements.txt

# [markdown]
# ### IMPORTS

from os import getenv, remove
from os.path import exists
from pydantic import BaseModel, Field
from datetime import date, datetime, timedelta
from typing import Dict, List, TypedDict, Any
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
            Column('valor',Numeric(7,2), ForeignKey('sindicato.valor'), primary_key=True), # NOVA COLUNA. REFERENCIA PARA A MESMA COLUNA PARA A PLANILHA BASE SINDICATO X VALOR. RECEBERÁ A CARGA DA PLANILHA Base sindicato x valor
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
            Column('estado', String), 
            Column('data_inicio_mes_competencia',Date,primary_key=True),
            Column('data_fim_mes_competencia',Date,primary_key=True),
            Column('qtd_dias_uteis', Integer, primary_key=True), 
            Column('valor',Numeric(7,2),primary_key=True)                                      
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

def checa_colunas(uploaded_file, engine, llm) -> DataFrame:
    
    print(f'Mapeando colunas do arquivo {uploaded_file.name}')            
    
    df = read_excel(uploaded_file)
    
    # MAPEANDO AS COLUNAS DOS DATAFRAMES PARA AS COLUNAS DO BANCO DE DADOS
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
        
        print('Resposta: ', resposta)        
        
        # RECRIANDO DATAFRAME COM OS MESMOS NOMES DE COLUNA DO BD   
        df = recria_dataframe(df, resposta)                           
        
    return df

# [markdown]
# ### <b>AGENTE 4 - VALORES SINDICATO</b> - ESTOU AQUI

# OS VALORES SÃO REFERENTES A UM ÚNICO SINDICATO E POR ESTADO PARA ESSE SINDICATO
def agente_valores_sindicato(uploaded_file_sindvalor, qtd_dias_uteis, llm) -> List[Dict[str,Any]]:
    
   df = read_excel(uploaded_file_sindvalor)
  
   class valores_sindicatos(BaseModel):
      
      estado : str = Field(description="estado")
      valor: float = Field(description="valor")
       
   parseador = JsonOutputParser(pydantic_object=valores_sindicatos)
   
   template = """
                  Aja como um assistente especialista em extrair informações de dataframes. 

                  Apartir do dataframe {df}, você deverá executar os seguintes passos:
                  1 - Extrair a sigla do estado
                  2 - Extrair o valor                          
                  
                  {formatador_saida_ia}
                """
                
   prompt_template = PromptTemplate(
                                      template=template,
                                      input_variables=['df','qtd_dias_uteis'],
                                      partial_variables={"formatador_saida_ia": parseador.get_format_instructions()}                        
                                   )
   
   chain = prompt_template | llm | parseador
   resposta = chain.invoke(input={'df':df, 'qtd_dias_uteis':qtd_dias_uteis})
     
   
   return resposta
                

def obtem_intervalo_competencia(uploaded_file_base_dias, llm) -> Dict[str,date]: # UTILIZADO NO FRONTEND
    
    print('Obtendo intervalo de competencia...')
    
    class base_dias(BaseModel):
        data_inicio_mes_competencia: date = Field(description="data de inicio do mês de competência")
        data_fim_mes_competencia: date = Field(description="data fim do mês de competência")
            
    
    parseador = JsonOutputParser(pydantic_object=base_dias)

    template = """
                   Aja como um assistente que ajuda encontrar datas em um DataFrame {df}.
                   Para isso, você deve seguir os passos abaixo:
             
                   ###################################################
                    1 - Considere o ano como o ano atual. 
                    2 - A data de inicio do mês de competência, será a menor data encontrada. Caso não encontre essa data, retorne null.
                    3 - A data fim do mês de competência, será a maior data encontrada. Caso não encontre essa data, retorne null. 
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
    dfbase_dias = read_excel(uploaded_file_base_dias)
    ano = date.today().year
    resposta = chain.invoke(input={"df": dfbase_dias.to_string(),"ano": ano})

    print('Intervalo de competência: entre',resposta['data_inicio_mes_competencia'],'e',resposta['data_fim_mes_competencia'])
    
    return resposta

def obtem_finaisdesemana(data_inicio_mes_competencia: date, data_fim_mes_competencia: date) -> Dict:
    
    data = data_inicio_mes_competencia
    finaisdesemana = {}
    sabado = []
    domingo = []
    
    while data <= data_fim_mes_competencia:
        if data.weekday() == 5:            
            sabado.append(data.strftime('%Y-%m-%d'))
        elif data.weekday() == 6:
            domingo.append(data.strftime('%Y-%m-%d'))

        data = data + timedelta(days=1)
        
    finaisdesemana = {'sabado': sabado, 'domingo': domingo, 'total_dias':len(sabado) + len(domingo)}
    
    return finaisdesemana

def obtem_qtd_dias_corridos(data_inicio_mes_competencia: date, data_fim_mes_competencia: date) -> int:
    
    data = data_inicio_mes_competencia
    dias = []
    while data <= data_fim_mes_competencia:
        dias.append(data.strftime('%Y-%m-%d'))
        data = data + timedelta(days=1)
        
    print(f'Dias corridos entre {data_inicio_mes_competencia.strftime('%Y-%m-%d')} e {data_fim_mes_competencia.strftime('%Y-%m-%d')}: ',dias)
    
    qtd_dias_corridos = len(dias)
    
    return qtd_dias_corridos

# [markdown]
# ### <b>AGENTE 3 - DIAS ÚTEIS</b>

def agente_dias_uteis(uploaded_file_base_dias, llm, dictintervalo_competencia) -> List[Dict]: # UTILIZADO NO FRONTEND
    
    print('Obtendo dias úteis para cada sindicato e seu estado, dentro do mês de competência...')
    
    data_inicio_mes_competencia = datetime.strptime(dictintervalo_competencia['data_inicio_mes_competencia'],'%Y-%m-%d')    
    data_fim_mes_competencia = datetime.strptime(dictintervalo_competencia['data_fim_mes_competencia'],'%Y-%m-%d')
    
    #print('Tipo: ', type(data_inicio_mes_competencia),'Data: ', data_inicio_mes_competencia)        
    
    df = read_excel(uploaded_file_base_dias)
    
    class Feriados(TypedDict):
        data: date
        nome: str
        dia_semana: str
    
    finaisdesemana = obtem_finaisdesemana(data_inicio_mes_competencia, data_fim_mes_competencia)
    total_finaisdesemana = len(finaisdesemana['sabado']) + len(finaisdesemana['domingo'])
    qtd_dias_corridos = obtem_qtd_dias_corridos(data_inicio_mes_competencia, data_fim_mes_competencia)
    
    class feriados(BaseModel):
        
        sindicato: str = Field(description="sindicato")
        estado: str = Field(description="estado") # EXCLUIR DUPLICATAS PORQUE VEM DE PLANILHA
        feriados_nacionais : List[Feriados] = Field(description="Feriados nacionais. dia_semana em português")
        feriados_estaduais : List[Feriados] = Field(description="Feriados estaduais. dia_semana em português")
        feriados_sindicais : List[Feriados] = Field(description="Feriados sindicais. dia_semana em português")  
                     
        # EXCLUI DA CONTAGEM OS FERIADOS QUE CAIREM NO SÁBADO OU DOMINGO OU QUE POSSUEM DATAS COINCIDENTES
        total_feriados : int = Field(description="Somatório da quantidade de feriados_nacionais, feriados_estaduais e feriados_sindicais. Exclua da contagem os feriados_nacionais que coincidirem com o sabado ou que coincidirem com o domingo. Exclua da contagem os feriados_estaduais que coincidirem com o sabado, que coincidirem com o domingo ou que coincidirem com os feriados_nacionais. Exclua da contagem também, os feriados_sindicais que coincidirem com o sabado, que coincidirem com o domingo, que coincidirem com os feriados_nacionais ou que coincidirem com os feriados_estaduais.")
        
        qtd_dias_uteis: int = Field(description=f"Faça o cálculo: {qtd_dias_corridos} - {total_finaisdesemana} - total_feriados + 1")        
        
    parseador = JsonOutputParser(pydantic_object=feriados)

    template = """
                   Aja como um advogado, que ajuda a encontrar a quantidade de feriados obrigatórios para sindicatos e seus estados associados.
                   Para isso, você deve seguir os passos abaixo:
                    
                   ###################################################
                    1 - data_inicio_mes_competencia: {data_inicio_mes_competencia} e data_fim_mes_competencia: {data_fim_mes_competencia}, estão no formato YYYY-MM-DD, 
                    aonde YYYY -> ano, MM -> mês e DD -> dia
                    2 - Encontre os sindicatos informados no dataframe {df}. Excluir as duplicatas.
                    3 - Quais são as siglas dos estados associados a cada sindicato no dataframe {df} ? Caso não encontre, tente inferir a sigla do estado 
                    a partir do sindicato associado, caso não consiga encontrar o estado, retorne null. Excluir as duplicatas
                    3 - Obtenha os feriados. Para isso, execute os passos a seguir:
                    
                    3.1 - Encontre as datas de Feriados nacionais. Utilize como referência a Lei nº 662/1949, a Lei nº 6.802/1980, Dia da Consciência Negra, Carnaval, Corpus Christi
                    e Sexta-Feira da Paixão.
                     
                    Para cada data encontrada, perguntar se a data está entre a data {data_inicio_mes_competencia} e a data {data_fim_mes_competencia} inclusive, 
                    se a resposta for "Sim", considerar. 
                    
                    Havendo algum null para cada estado do item 2 acima, nâo execute os passos abaixo e retorne null para a quantidade de
                    dias úteis.
                                                        
                    3.2 - Encontre as datas de Feriados estaduais obrigatórios, para cada sigla de estado associado a cada sindicato. Utilize como referência o Diário Oficial do estado 
                    associado a cada sindicato. Caso não encontre nada, utilize sites da internet que possuam bastante audiência sobre o assunto Feriados estaduais obrigatórios, 
                    relativos ao estado associado, mesmo assim, caso não encontre, retorne null 
                    
                    Para cada data encontrada, fazer as seguintes perguntas:
                    a) A data está entre a data {data_inicio_mes_competencia} e a data {data_fim_mes_competencia} inclusive ? Responda Sim ou Não
                    b) A data é um feriado obrigatório no estado ? Responda Sim ou Não
                    Se a resposta for "Sim" para as perguntas a) e b), considerar esse Feriado estadual.  
                                       
                    3.3 - Encontre as datas de Feriados sindicais obrigatórios, para cada sigla de estado associado a cada sindicato. Para saber quais são os feriados sindicais, pesquisar as 
                    convenções sindicais recentes para cada sigla de estado associado ao sindicato. Caso não encontre nada, utilize sites da internet que possuam bastante audiência sobre 
                    o assunto Feriados sindicais obrigatórios correspondente a cada sigla do estado associado ao sindicato.
                    
                    Para cada data encontrada, fazer as seguintes perguntas:
                    a) A data está entre a data {data_inicio_mes_competencia} e a data {data_fim_mes_competencia} inclusive ? Responda Sim ou Não
                    b) A data é um feriado obrigatório no estado ? Responda Sim ou Não
                    Se a resposta for "Sim" para as perguntas a) e b), considerar esse Feriado sindical.  
                                                           
                    3.4 - Você deve retornar uma lista de JSONs válida.             
                    
                    ##################################################           

                   {formatador_saida_ia}
                """
                
    prompt_template = PromptTemplate(
                                        template=template,
                                        input_variables=['df','data_inicio_mes_competencia','data_fim_mes_competencia'],
                                        partial_variables={"formatador_saida_ia": parseador.get_format_instructions()}
                                    )   
    
    
    # CRIANDO A CADEIA DE EXECUÇÃO PARA A LLM
    chain = prompt_template | llm | parseador    
    
    # INVOCANDO A LLM       
    data_inicio_mes_competencia = dictintervalo_competencia['data_inicio_mes_competencia']
    data_fim_mes_competencia = dictintervalo_competencia['data_fim_mes_competencia'] 
    
    print('Tipo data_inicio_mes_competencia: ',type(data_inicio_mes_competencia))    
    print('data_inicio_mes_competencia: ',data_inicio_mes_competencia)
    print('data_fim_mes_competencia: ',data_fim_mes_competencia)
    
    resposta = chain.invoke(input={"df": df.to_string(),
                                  "data_inicio_mes_competencia": data_inicio_mes_competencia,
                                  "data_fim_mes_competencia": data_fim_mes_competencia}
                            ) 
    
    
    print('Resposta: ',resposta)
    
    qtd_dias_uteis = []
    for q in resposta:
        #print('q: ',q)
        d = {'sindicato' : q['sindicato'], 'estado' : q['estado'], 'qtd_dias_uteis' : q['qtd_dias_uteis']}
        qtd_dias_uteis.append(d)
    
    print('FINAIS DE SEMANA: ', finaisdesemana)
    print('QTD_DIAS_CORRIDOS', qtd_dias_corridos)
    
    print('QTD_DIAS_UTEIS: ', qtd_dias_uteis)       
            
    return qtd_dias_uteis

def analise_dados(uploaded_files,engine,llm,dictintervalo_competencia,resposta_dias_uteis,combo_atestado): # UTILIZADO NO FRONTEND. EXECUTADO APÓS CLICAR EM Consultar.
    
    print('Analisando os dados...')    
    
    """ uploaded_files = {
                                'base_dias':uploaded_file_base_dias,
                                'ativos':uploaded_file_ativos,
                                'ferias':uploaded_file_ferias,
                                'desligados':uploaded_file_desligados,
                                'afastamentos':uploaded_file_afastamentos,
                                'exterior': uploaded_file_exterior,
                                'admissao': uploaded_file_admissao,
                                'sindvalor': uploaded_file_sindvalor,
                                'estagaprendiz': uploaded_file_estagaprendiz
                         }
    """
    
    dictdf = checa_colunas(uploaded_files,engine,llm) # RETORNA O DATAFRAME COM AS COLUNAS VALIDADAS           
    
    for item in dictdf.items():
        print(f'Novo Dataframe {item[0]}')
        print(item[1])
        
    for item in dictintervalo_competencia.items():
        print(f'Chave: {item[0]}')
        print(f'Valor: {item[1]}')
        
    resposta = obtem_dias_uteis(uploaded_files['base_dias'], llm, dictintervalo_competencia)
    
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
# ### <b>AGENTE 2: Extração</b>
# <b>Responsabilidade:</b> Processar documentos e extrair dados relevantes<br/><br/>
# <b>Funcionalidades:</b>
# <ul><li>Identificação e extração de campos específicos</li></ul>
# <ul><li>Validação cruzada de dados extraídos</li></ul>

def agente2(uploaded_files,engine,llm,dictintervalo_competencia,resposta_dias_uteis,combo_atestado): # UTILIZADO NO FRONTEND

    print('\nExecutando agente 2...')   
        
    analise_dados(uploaded_files,engine,llm,dictintervalo_competencia,resposta_dias_uteis,combo_atestado)           
       
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
    resposta_dias_uteis = ""
    uploaded_file_sindvalor = None
            
    if uploaded_file_base_dias and (data_inicio_mes_competencia == "" and data_fim_mes_competencia == "" and resposta_dias_uteis == ""):
        
        with st.spinner("Analisando os dados com IA..."):
           dictintervalo_competencia = obtem_intervalo_competencia(uploaded_file_base_dias,llm)
                     
           if dictintervalo_competencia['data_inicio_mes_competencia'] == None or dictintervalo_competencia["data_fim_mes_competencia"] == None:
                
                st.error(""" Não foi possível determinar as datas de início ou de fim do mês de competência. 
                            Verifique se todos os campos da planilha Base dias uteis estão preenchidos corretamente.""")
                
           else:            
                            
                data_inicio_mes_competencia = dictintervalo_competencia['data_inicio_mes_competencia']
                data_fim_mes_competencia = dictintervalo_competencia['data_fim_mes_competencia']
                                            
                st.text(f'Data início mês de competência: {datetime.strptime(data_inicio_mes_competencia,'%Y-%m-%d').strftime('%d/%m/%Y')} - Data fim mês de competência: {datetime.strptime(data_fim_mes_competencia,'%Y-%m-%d').strftime('%d/%m/%Y')}') 
                
                # CRIANDO AS TABELAS PARA COMEÇAR A REALIZAR O MAPEAMENTO DAS COLUNAS DAS PLANILHAS COM AS COLUNAS DO BD
                cria_tabelas(engine, data_inicio_mes_competencia, data_fim_mes_competencia)
                
                resposta_dias_uteis = agente_dias_uteis(uploaded_file_base_dias, llm, dictintervalo_competencia)          

                if not resposta_dias_uteis: # VALIDAR ESSA CONDIÇÃO
                    st.error(""" Verifique se planilha de base de dias úteis, possui os nomes dos sindicatos e seus estados.""")

                else:
                    uploaded_file_sindvalor = st.file_uploader("📂 Adicione a planilha Base sindicato x valor.", type=["xls","xlsx"])                   

                    
    if uploaded_file_sindvalor is not None: # AQUI
                                        
        with st.spinner("Analisando os dados com IA..."):
                                
            isnull,resposta = obtem_valores(uploaded_file_sindvalor, llm, resposta_dias_uteis)

            if not isnull:
                pass
            else: 
                pass
            
            if resposta:                     
                
                uploaded_file_ativos = st.file_uploader("📂 Adicione a planilha ATIVOS", type=["xls","xlsx"])                            
                uploaded_file_ferias = st.file_uploader("📂 Adicione a planilha FÉRIAS", type=["xls","xlsx"]) # VALIDANDO AS COLUNAS COM ESSE
                uploaded_file_desligados = st.file_uploader("📂 Adicione a planilha DESLIGADOS", type=["xls","xlsx"]) 
                st.text('Se estiver como OK o comunicado até dia 15, não considerar compra, se informado depois do dia 15, considerar compra proporcional')
                uploaded_file_afastamentos = st.file_uploader("📂 Adicione a planilha AFASTAMENTO", type=["xls","xlsx"])
                uploaded_file_exterior = st.file_uploader("📂 Adicione a planilha EXTERIOR", type=["xls","xlsx"])
                uploaded_file_admissao = st.file_uploader("📂 Adicione a planilha ADMISSAO", type=["xls","xlsx"])                  
                uploaded_file_estagaprendiz = st.file_uploader("📂 Adicione as planilhas ESTÁGIO e APRENDIZ", type=["xls","xlsx"],accept_multiple_files=True)
                                                        
                if st.button("🔍 Consultar"):                
                            
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
                    #elif not uploaded_file_estagaprendiz or len(uploaded_file_estagaprendiz) != 2:
                    #    st.error("Você precisa fazer o upload somente das planilhas ESTÁGIO e APRENDIZ")            
                                    
                    else:
                        uploaded_files = {
                                            'base_dias':uploaded_file_base_dias,
                                            'ativos':uploaded_file_ativos,
                                            'ferias':uploaded_file_ferias,
                                            'desligados':uploaded_file_desligados,
                                            'afastamentos':uploaded_file_afastamentos,
                                            'exterior': uploaded_file_exterior,
                                            'admissao': uploaded_file_admissao,
                                            'sindvalor': uploaded_file_sindvalor,
                                            'estagaprendiz': uploaded_file_estagaprendiz
                                        }
                        
                        with st.spinner("Analisando os dados com IA..."):
                            #try:
                                resultado_df = agente2(uploaded_files,engine,llm,dictintervalo_competencia,resposta_dias_uteis,combo_atestado) # RETORNA UM DATAFRAME COM O RESULTADO DA CONSULTA

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

    llm = ChatOpenAI(                    
        model="openai/gpt-oss-120b",  # ou "gemini-2.5-pro" ou "gemini-2.5-flash", "gpt-4.1-mini", "openai/gpt-oss-120b"
        base_url="https://openrouter.ai/api/v1",
        temperature=0,
        api_key=getenv("API_KEY"),
        max_tokens=20000                      
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

