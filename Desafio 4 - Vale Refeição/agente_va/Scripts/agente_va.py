# [markdown]
# PACOTES

#%pip install -r requirements.txt

# [markdown]
# ### IMPORTS

from os import getenv
from re import findall
from os.path import exists
from pydantic import BaseModel, Field
from datetime import date, datetime, timedelta
from time import sleep
from typing import Dict, List, TypedDict, Any
from pandas import DataFrame, read_excel, read_sql
from sqlalchemy import create_engine, text, Table, MetaData, Integer, String, Date, Numeric, Column, CheckConstraint, UniqueConstraint ,ForeignKey, inspect, select, delete
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from langchain_community.cache import InMemoryCache
from langchain.globals import set_debug, set_llm_cache
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
   
    # Define a tabela com chave primária e restrição CHECK
    funcionarios = Table( # RECEBERÁ A CARGA DE TODAS AS OUTRAS PLANILHAS
            'funcionarios', metadata,
            Column('matricula', Integer,primary_key=True),  
            Column('titulo_cargo', String, nullable=False),
            Column('sindicato', String, ForeignKey('sindicato.sindicato')), 
            Column('desc_situacao', String, CheckConstraint("desc_situacao IN ('Trabalhando', 'Férias', 'Licença Maternidade','Auxílio Doença','Exterior','Desligado','Atestado')"), server_default="Trabalhando",primary_key=True), 
            Column('qtd_dias', Integer), 
            Column('data_inicio_mes_competencia',Date, server_default=data_inicio_mes_competencia,primary_key=True),
            Column('data_fim_mes_competencia',Date, server_default=data_fim_mes_competencia,primary_key=True),
            Column('data_demissao', Date),
            Column('data_retorno',Date),
            Column('data_admissao',Date),  
            Column('qtd_dias_uteis', Integer,ForeignKey('sindicato.qtd_dias_uteis'), nullable=False), 
            Column('valor_va',Numeric(7,2), ForeignKey('valor.valor_va')),            
            Column('comunicado_desligamento', String, CheckConstraint("comunicado_desligamento IN ('OK', 'Ok') OR comunicado_desligamento IS NULL"))                        
    ) 
    
    sindicato = Table( # DADOS DA PLANILHA Base dias uteis
            'sindicato', metadata,
            Column('id',Integer, primary_key=True), # ISSO É O SUFICIENTE PARA O AUTOINCREMENTO NO SQLITE. MAS TEM QUE TER APENAS UMA CHAVE PRIMÁRIA NA TABELA
            Column('sindicato', String, nullable=False),    
            Column('estado', String, nullable=False), 
            Column('data_inicio_mes_competencia',Date, server_default=data_inicio_mes_competencia),
            Column('data_fim_mes_competencia',Date, server_default=data_fim_mes_competencia),
            Column('qtd_dias_uteis', Integer, nullable=False),
            UniqueConstraint('estado','data_inicio_mes_competencia','data_fim_mes_competencia',name="uniq_sindicato")                                                                     
    )
    
    dias_nao_uteis = Table(
            'dias_nao_uteis',metadata,
            Column('id',Integer, primary_key=True),
            Column('estado',String), # PARA FERIADO NACIONAL
            Column('data',Date, nullable=False),
            Column('nome',String, nullable=False),
            Column('dia_semana',String, nullable=False),
            UniqueConstraint('estado','data','nome',name="uniq_dias_nao_uteis")                       
    )
    
    valor = Table( # DADOS DA PLANILHA Base valor
            'valor', metadata,           
            Column('estado', String, ForeignKey('sindicato.estado'),primary_key=True), 
            Column('data_inicio_mes_competencia',Date, ForeignKey('sindicato.data_inicio_mes_competencia'), server_default=data_inicio_mes_competencia, primary_key=True),
            Column('data_fim_mes_competencia',Date, ForeignKey('sindicato.data_fim_mes_competencia'), server_default=data_fim_mes_competencia, primary_key=True),            
            Column('valor_va',Numeric(7,2),nullable=False),
            UniqueConstraint('estado','data_inicio_mes_competencia','data_fim_mes_competencia',name="uniq_valor")                                      
    )
          
    if not inspect(engine).get_table_names(): # SE AS TABELAS NÃO EXISTIREM, CRIA
                                    
        # Cria a tabela no banco
        metadata.create_all(engine)


def recria_dataframe(df,resposta) -> DataFrame:
    
    data = {}
    for k in resposta.keys(): # COLUNAS DA PLANILHA
        valor = resposta[k] # COLUNAS DO BD
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
        tabela = 'funcionarios'
        columns = inspector.get_columns(tabela)
            
        colunas_tabela = [col['name'] for col in columns]
        
        class colunas(BaseModel):
            mapeamento: Dict[str,str] = Field(description="mapeamento")
                             
        parseador = JsonOutputParser(pydantic_object=colunas) 
            
        template = """
                            Você é um assistente que ajuda a mapear colunas de um DataFrame para as colunas de uma tabela de banco de dados.
                            Dada a lista de colunas do DataFrame e a lista de colunas da tabela, você deve sugerir um mapeamento entre elas com base no significado das colunas.
                            Colunas do DataFrame: {colunas_df}
                            Colunas da Tabela: {colunas_tabela}
                            
                            Caso não encontre uma correspondência, ignore essa coluna.
                            
                            ###################################################
                            Este mapeamento deve ser feito da seguinte forma:
                            1 - Lado esquerdo, para cada coluna {colunas_df}
                            2 - Lado direito, para cada coluna {colunas_tabela}
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
        colunas_df = list(df.columns.values)
        resposta = chain.invoke(input={"colunas_df":colunas_df, "colunas_tabela":colunas_tabela})
        
        resposta = resposta['mapeamento']
        
        print('Resposta: ', resposta)
        sleep(5)        
        
        # RECRIANDO DATAFRAME COM OS MESMOS NOMES DE COLUNA DO BD   
        df = recria_dataframe(df, resposta) 
        print('DataFrame mapeado...')
        print(df)                          
        sleep(10)
        
    return df

def obtem_finaisdesemana(data_inicio_mes_competencia: date, data_fim_mes_competencia: date) -> Dict:
    
    data = data_inicio_mes_competencia
    finaisdesemana = {}
    sabado = []
    domingo = []
    
    while data <= data_fim_mes_competencia:
        if data.weekday() == 5:            
            sabado.append(data.strftime('%Y-%m-%d')) # TRANSFORMA EM STRING NOVAMENTE PARA INSERIR NA LISTA
        elif data.weekday() == 6:
            domingo.append(data.strftime('%Y-%m-%d')) # TRANSFORMA EM STRING NOVAMENTE PARA INSERIR NA LISTA

        data = data + timedelta(days=1)
        
    finaisdesemana = {'sabado': sabado, 'domingo': domingo, 'total_dias':len(sabado) + len(domingo)}
    
    return finaisdesemana

def obtem_qtd_dias_corridos(data_inicio_mes_competencia: date, data_fim_mes_competencia: date) -> int:
    
    data = data_inicio_mes_competencia
    dias = []
    while data <= data_fim_mes_competencia:
        dias.append(data.strftime('%Y-%m-%d')) # CONVERTENDO EM STRING PARA ADICIONAR NA LISTA
        data = data + timedelta(days=1)
        
    print(f'Dias corridos entre {data_inicio_mes_competencia.strftime('%Y-%m-%d')} e {data_fim_mes_competencia.strftime('%Y-%m-%d')}: ',dias)
    
    qtd_dias_corridos = len(dias)
    
    return qtd_dias_corridos

# [markdown]
# ### <b>AGENTE 2: INTERVALO COMPETÊNCIA</b>

def agente_intervalo_competencia(uploaded_file_base_dias, llm): # UTILIZADO NO FRONTEND
    
    print('Obtendo intervalo de competencia...')
    
    class base_dias(BaseModel):
        data_inicio_mes_competencia: date = Field(description="data de inicio do mês de competência no formato YYYY-MM-DD")
        data_fim_mes_competencia: date = Field(description="data fim do mês de competência no formato YYYY-MM-DD")
            
    
    parseador = JsonOutputParser(pydantic_object=base_dias)

    template = """
                   Aja como um assistente que ajuda encontrar datas em um DataFrame {df}.
                   Para isso, você deve seguir os passos abaixo:
             
                   ###################################################
                    1 - Considere o ano de {ano}.
                    2 - As datas estão no formato DD/MM, aonde DD -> dia e MM -> mês 
                    3 - A data de inicio do mês de competência, será a menor data encontrada. Caso não encontre essa data, retorne null.
                    4 - A data fim do mês de competência, será a maior data encontrada. Caso não encontre essa data, retorne null. 
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
    resposta = chain.invoke(input={"df": dfbase_dias.to_string(index=False),"ano": ano})
    
    print('Tipo data mes competencia: ', type(resposta['data_inicio_mes_competencia'])) # A LLM SEMPRE RETORNA STRING NO JSON

    if resposta['data_inicio_mes_competencia'] and resposta['data_fim_mes_competencia']:
        print('Intervalo de competência: entre',resposta['data_inicio_mes_competencia'],'e',resposta['data_fim_mes_competencia'])
    else:
        resposta = None
    
    return resposta

def escreve_bd(engine,resposta,nome_tabela):
    
    # ESCREVENDO NA TABELA
    print(f'Escrevendo na tabela {nome_tabela}...')
    
    with engine.connect() as conn:            
                               
            # DATAFRAME FÉRIAS            
            if nome_tabela == "Férias":
                dffuncionarios_ferias = resposta
                for r in dffuncionarios_ferias.values: # RESPOSTA AQUI É O DATAFRAME DE FUNCIONÁRIOS COM QTD_DIAS DE FÉRIAS
                    stmt = text(f"UPDATE funcionarios SET qtd_dias = {r[2]} WHERE matricula = {r[0]} AND desc_situacao = '{nome_tabela}'")                
                    conn.execute(stmt)
                conn.commit()
            
            elif nome_tabela == "afastamentos":
                dffuncionarios_afastados = resposta
                for r in dffuncionarios_afastados.values:
                    stmt = text(f"UPDATE funcionarios SET qtd_dias = :qtd_dias, data_retorno = :data_retorno WHERE matricula = :matricula AND desc_situacao = :desc_situacao")                
                    conn.execute(stmt,{"qtd_dias":r[2] , "matricula": r[0], "desc_situacao":r[1], "data_retorno" : r[5]})
                conn.commit()
                
            elif nome_tabela == "Desligado":
                dffuncionarios_desligados = resposta
                for r in dffuncionarios_desligados.values:
                    stmt = text(f"UPDATE funcionarios SET qtd_dias = :qtd_dias, data_demissao = :data_demissao WHERE matricula = :matricula AND desc_situacao = :desc_situacao'")                
                    conn.execute(stmt,{"qtd_dias":r[6] , "matricula": r[0], "desc_situacao":r[1], "data_demissao" : r[2]})                                            
                conn.commit()                
            
            elif nome_tabela == 'dias_nao_uteis':
                df = DataFrame(resposta) # TRANSFORMAR UMA LISTA DE DICIONÁRIOS EM DATAFRAME
                df.to_sql(name=f'{nome_tabela}', con=engine, if_exists='append',index=False)
                
            elif nome_tabela == 'admissao':
                dffuncionarios_admissao = resposta
                for r in dffuncionarios_admissao.values:
                    stmt = text(f"UPDATE funcionarios SET qtd_dias = :qtd_dias, data_admissao = :data_admissao WHERE matricula = :matricula AND desc_situacao = :desc_situacao'")                
                    conn.execute(stmt,{"qtd_dias":r[5] , "matricula": r[0], "desc_situacao":r[1], "data_admissao" : r[4]})                                            
                conn.commit()                     
                                            
            else: # TABELA FUNCIONÁRIO, SINDICATO, VALOR, ESTAGIARIO, APRENDIZES. INSERTs
                tabela = Table(nome_tabela,MetaData(),autoload_with=engine)
                stmt = delete(tabela) # POR CAUSA DO COMPORTAMENTO DO STREAMLIT EM RECARREGAR OS UPLOADED FILES
                conn.execute(stmt)
                conn.commit()
                
                df = DataFrame(resposta) # TRANSFORMAR UMA LISTA DE DICIONÁRIOS EM DATAFRAME
                df.to_sql(name=f'{nome_tabela}', con=engine, if_exists='append',index=False)

# [markdown]
# ### <b>AGENTE 3: DIAS ÚTEIS</b>

def agente_dias_uteis(uploaded_file_base_dias, llm, dictintervalo_competencia,engine): # UTILIZADO NO FRONTEND
    
    print('Obtendo dias úteis para cada sindicato e seu estado, dentro do mês de competência...')    
   
    df = read_excel(uploaded_file_base_dias)
    
    class Feriados(TypedDict):
        data: date
        nome: str
        dia_semana: str
    
    data_inicio_mes_competencia = datetime.strptime(dictintervalo_competencia['data_inicio_mes_competencia'],'%Y-%m-%d') # CONVERTENDO DE STRING PARA DATE PARA FUNÇÃO finaisdesemana
    data_fim_mes_competencia = datetime.strptime(dictintervalo_competencia['data_fim_mes_competencia'],'%Y-%m-%d') # # CONVERTENDO DE STRING PARA DATE PARA FUNÇÃO finaisdesemana
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
        total_feriados : int = Field(description="Para cada sindicato e estado, fornecer o somatório da quantidade de feriados_nacionais, feriados_estaduais e feriados_sindicais. Exclua da contagem os feriados_nacionais que coincidirem com o sabado ou que coincidirem com o domingo. Exclua da contagem os feriados_estaduais que coincidirem com o sabado, que coincidirem com o domingo ou que coincidirem com os feriados_nacionais. Exclua da contagem também, os feriados_sindicais que coincidirem com o sabado, que coincidirem com o domingo, que coincidirem com os feriados_nacionais ou que coincidirem com os feriados_estaduais.")
        
        qtd_dias_uteis: int = Field(description=f"Faça o cálculo: {qtd_dias_corridos} - {total_finaisdesemana} - total_feriados para cada sindicato e estado") # NUNCA SERÁ NULO       
        
    parseador = JsonOutputParser(pydantic_object=feriados)

    template = """
                   Você é um agente especializado em legislação brasileira, que ajuda a encontrar os feriados nacionais, estaduais obrigatórios e sindicais obrigatórios, 
                   no ano de {ano}, para sindicatos e seus estados associados.
                   **SEMPRE** gerar **JSONs VÁLIDOS**
                   
                   ####################################################
                    Para isso, você deve seguir os passos abaixo.
                        
                    1. Identificar sindicatos:
                    - Extraia os sindicatos do dataframe {df}.
                    - Elimine duplicatas.

                    2. Identificar estados:
                    - Para cada sindicato, recupere a sigla do estado associado.
                    - Caso não esteja explícito, tente inferir pelo nome do sindicato.
                    - Se não for possível, atribua `null`.
                    - Elimine duplicatas.

                    3. Obter feriados:
                    - **Feriados nacionais**: consulte a Lei nº 662/1949, Lei nº 6.802/1980, Dia da Consciência Negra, Carnaval no ano de {ano}, Corpus Christi 
                    no ano de {ano} e Sexta-Feira Santa = Domingo de Páscoa no ano de {ano} - 2 dias.
                    - **Feriados estaduais**: para cada estado associado, verifique a legislação oficial, Diário Oficial do Estado ou, em último caso, sites de grande audiência.
                    Para o estado RJ, 23 de Abril é Dia de São Jorge
                    - **Feriados sindicais**: para cada sindicato, verifique convenções coletivas recentes; se não encontrar, utilize fontes alternativas confiáveis. Se não houver dados, retorne `null`.

                    4. Filtrar feriados:
                    Para cada feriado encontrado, aplique:
                    a) Está entre {data_inicio_mes_competencia} e {data_fim_mes_competencia}? ("Sim"/"Não")  
                    b) É obrigatório segundo legislação/convênio aplicável? ("Sim"/"Não")  
                    Se "Sim" para ambos, inclua no resultado.                   
                    
                   ###################################################           

                   {formatador_saida_ia}
                """
                
    prompt_template = PromptTemplate(
                                        template=template,
                                        input_variables=['df','data_inicio_mes_competencia','data_fim_mes_competencia','ano'],
                                        partial_variables={"formatador_saida_ia": parseador.get_format_instructions()}
                                    )   
    
    
    # CRIANDO A CADEIA DE EXECUÇÃO PARA A LLM
    chain = prompt_template | llm | parseador
        
    # INVOCANDO A LLM       
    data_inicio_mes_competencia = dictintervalo_competencia['data_inicio_mes_competencia']
    data_fim_mes_competencia = dictintervalo_competencia['data_fim_mes_competencia'] 
    ano = date.today().year    
    
        
    qtd_dias_uteis = []
    
    resposta = chain.invoke(input={
                                        "df": df.to_string(index=False),
                                        "data_inicio_mes_competencia": data_inicio_mes_competencia,
                                        "data_fim_mes_competencia": data_fim_mes_competencia,
                                        "ano" : ano
                                        }
                                    )
    
    with engine.connect() as conn:
        tabela = Table('dias_nao_uteis',MetaData(),autoload_with=engine)
        stmt = delete(tabela) # POR CAUSA DO COMPORTAMENTO DO STREAMLIT EM RECARREGAR OS UPLOADED FILES
        conn.execute(stmt)
        conn.commit()
    
    i=0 # PARA PEGAR OS FERIADOS NACIONAIS APENAS UMA VEZ
    j=0 # PARA PEGAR OS FERIADOS SINDICAIS APENAS UMA VEZ 
    
    for q in resposta:
        if q['sindicato'] and q['estado']:
            d = {'sindicato' : q['sindicato'], 'estado' : q['estado'], 'qtd_dias_uteis' : q['qtd_dias_uteis']} # NUNCA SERÁ NULO
            qtd_dias_uteis.append(d)            
            
            # FERIADOS NACIONAIS            
            if i == 0:
                if q['feriados_nacionais']:
                    i+=1
                    lista = []
                    for f in q['feriados_nacionais']:
                        if (f['dia_semana'].upper() not in findall(r'S[AÁ]BADO|DOMINGO',f['dia_semana'].upper())):
                            data = {
                                        'estado' : 'NA', # PARA IDENTIFICAR O FERIADO COMO NACIONAL
                                        'data':f['data'],
                                        'nome':f['nome'],
                                        'dia_semana':f['dia_semana']                                    
                                    }                            
                            lista.append(data)
                    
                    df = DataFrame(lista)
                    escreve_bd(engine,df,'dias_nao_uteis')
            
            # FERIADOS ESTADUAIS           
            elif q['feriados_estaduais']:
                lista = []
                for f in q['feriados_estaduais']:
                    if (f['dia_semana'].upper() not in findall(r'S[AÁ]BADO|DOMINGO',f['dia_semana'].upper())):
                        data = {
                                        'estado' : q['estado'],
                                        'data':f['data'],
                                        'nome':f['nome'],
                                        'dia_semana':f['dia_semana']                                    
                                }                        
                        lista.append(data)
                    
                df = DataFrame(lista)
                escreve_bd(engine,df,'dias_nao_uteis')     
            
            # FERIADOS SINDICAIS    
            elif q['feriados_sindicais']:
                lista = []
                j+=1
                for f in q['feriados_sindicais']:                    
                    if (f['dia_semana'].upper() not in findall(r'S[AÁ]BADO|DOMINGO',f['dia_semana'].upper())):
                        data = {
                                        'estado' : 'SD', # PARA IDENTIFICAR O FERIADO COMO SINDICAL
                                        'data':f['data'],
                                        'nome':f['nome'],
                                        'dia_semana':f['dia_semana']                                    
                                }
                        lista.append(data)
                    
                df = DataFrame(lista)
                escreve_bd(engine,df,'dias_nao_uteis')                       
            
        else:
            qtd_dias_uteis = None
            break
    
    # SABADOS
    datas = finaisdesemana['sabado']
    estado = ['FD' for d in datas] # PARA IDENTIFICAR COMO FIM DE SEMANA
    nome = ['sabado' for d in datas]
    dia_semana = ['sabado' for d in datas]
    data = {
            'estado' : estado,
            'data' : datas,
            'nome' : nome,
            'dia_semana':dia_semana
            }
    df = DataFrame(data)
    escreve_bd(engine,df,'dias_nao_uteis')
    
    # DOMINGOS
    datas = finaisdesemana['domingo']
    estado = ['FD' for d in datas] # PARA IDENTIFICAR COMO FIM DE SEMANA
    nome = ['domingo' for d in datas]
    dia_semana = ['domingo' for d in datas]
    data = {
            'estado' : estado,
            'data' : datas,
            'nome' : nome,
            'dia_semana':dia_semana
            }
    df = DataFrame(data)
    escreve_bd(engine,df,'dias_nao_uteis')    
        
    if qtd_dias_uteis != None:        
        
        print('FINAIS DE SEMANA: ', finaisdesemana) 
        print('QTD_DIAS_CORRIDOS', qtd_dias_corridos)
    
        print('QTD_DIAS_UTEIS: ', qtd_dias_uteis)    
             
            
    return qtd_dias_uteis

# [markdown]
# ### <b>AGENTE 4: VALORES SINDICATO</b>

# OS VALORES SÃO REFERENTES A UM ÚNICO SINDICATO E POR ESTADO PARA ESSE SINDICATO
def agente_valores_sindicato(uploaded_file_sindvalor, engine, llm):
    
   df = read_excel(uploaded_file_sindvalor)
   
   print('DataFrame')
   print(df)
   
   class valores_estados(TypedDict):
      estado : str
      valor_va : float      
      
   class valores_sindicatos(BaseModel):
      valores_estados : List[Dict[str,Any]] = Field(description="estado e o valor associado a sigla. Ex: {'estado' : 'RJ', 'valor_va' : 35.0}")
      
   parseador = JsonOutputParser(pydantic_object=valores_sindicatos)
   
   template = """
                  Aja como um assistente especialista em extrair siglas de estados e valores de dataframes. 
                  Retornar **SEMPRE** um **JSON VÁLIDO** e nada mais 

                  ###########################################################################
                  A partir do dataframe {df}, você deverá executar os seguintes passos:
                  1 - Extrair a sigla do estado, caso não encontre, retorne null
                  2 - Extrair o valor associado ao estado, caso não encontre, retorne null                  
                  3 - Ignorar os registros que possuam tanto a sigla do estado igual a null quanto o valor igual a null ao mesmo tempo   
                                
                  {formatador_saida_ia}
                  ###########################################################################
                """
                
   prompt_template = PromptTemplate(
                                      template=template,
                                      input_variables=['df'],
                                      partial_variables={"formatador_saida_ia": parseador.get_format_instructions()}                        
                                   )
   
   chain = prompt_template | llm | parseador
   resposta = chain.invoke(input={'df':df.to_string(index=False)})
   
   resposta = resposta['valores_estados']
   print('Resposta: ', resposta)
   
   for r in resposta:
      if (r['estado'] == None) or (r['valor_va'] == None):
         return None
      else:
         continue              
   
   # SE NÃO HOUVER VALORES NULOS, VERIFICAR SE A QUANTIDADE DE ESTADOS É A MESMA ENTRE AS
   # PLANILHAS BASE DIAS ÚTEIS E BASE SINDICATO X VALORES
               
   # TEM QUE OBTER OS SINDICATOS VINCULADOS AOS ESTADOS, QUE SE ENCONTRAM NESSA PLANILHA
      
   # 1 - BUSCANDO OS SINDICATOS NA TABELA DE SINDICATOS
   metadata = MetaData()
   sindicato = Table("sindicato", metadata, autoload_with=engine)

   stmt = select(sindicato)
   
   listadict_sindicato_estado = []
   
   with engine.connect() as conn:
      results = conn.execute(stmt)
      #print('Results: ', results)
      for row in results:
         listadict_sindicato_estado.append({'sindicato':row.sindicato, 'estado':row.estado})

   dfsindicato_estado = DataFrame(listadict_sindicato_estado)      
   print('dfsindicato_estado')
   print(dfsindicato_estado)

   dfestado_valor = DataFrame(resposta)
   print('dfestado_valor')
   print(dfestado_valor)

   if not((dfestado_valor['estado'].isin(dfsindicato_estado['estado']).any()) and (dfsindicato_estado['estado'].isin(dfestado_valor['estado'])).any()):
      print('Valores diferentes de estado entre as planilhas base dias úteis e base sindicato x valor')
      return None            
      
   return dfestado_valor     

def padroniza_situacao(df,llm):
    
    print("Padronizando a descrição da situação para 'Trabalhando', 'Férias', 'Licença Maternidade','Auxílio Doença','Exterior','Desligado' ou 'Atestado'...")
    sleep(5)
    
    dfativos_situacao = df['desc_situacao'].drop_duplicates()
        
    print('Dataframe sem duplicatas')
    print(dfativos_situacao)
    
           
    class dictsituacao(TypedDict):
        situacao_antes : str
        situacao_depois : str
        
    class desc_situacao(BaseModel):
        situacao : List[dictsituacao] = Field(description="Lista de matricula, situacao antes e situacao depois associadas")
                
                
    parseador = JsonOutputParser(pydantic_object=desc_situacao)
    
    template = """
                    Aja como um assistente que é capaz de mapear valores, de acordo com os significados 
                    dos valores informados na coluna desc_situacao no Dataframe {context}.
                    **- Não faça perguntas nem adicione esclarecimentos.**
                                                       
                    Para isso, devem ser seguidos os seguintes passos:
                    ##########################################################################################################################################
                    1 - Se o valor do campo na coluna desc_situacao, tiver o significado de que se encontra trabalhando, 
                    informar **SEMPRE O VALOR DO CAMPO DA COLUNA DESC_SITUACAO** como situação antes, e para a situação depois, informar "Trabalhando",
                    2 - Se o valor do campo na coluna desc_situacao, tiver o significado de que se encontra em férias, 
                    informar **SEMPRE O VALOR DO CAMPO DA COLUNA DESC_SITUACAO** como situacao antes, e para a situação depois, informar "Férias".
                    3 - Se o valor do campo na coluna desc_situacao, tiver o significado de que se encontra em licença maternidade, 
                    informar **SEMPRE O VALOR DO CAMPO DA COLUNA DESC_SITUACAO** como situação antes, e para a situação depois, informar "Licença Maternidade". 
                    4 - Se o valor do campo na coluna desc_situacao, tiver o significado de que foi beneficiada por auxílio doença, 
                    informar **SEMPRE O VALOR DO CAMPO DA COLUNA DESC_SITUACAO** como situação antes, e para a situação depois, informar "Auxílio Doença". 
                    5 - Se o valor do campo na coluna desc_situacao, tiver o significado de que se encontra em viagem no exterior, 
                    informar **SEMPRE O VALOR DO CAMPO DA COLUNA DESC_SITUACAO** como situação antes, e para a situação depois, informar "Exterior".
                    6 - Se o valor do campo na coluna desc_situacao, tiver o significado de que foi desligado da empresa, 
                    informar **SEMPRE O VALOR DO CAMPO DA COLUNA DESC_SITUACAO** como situação antes, e para a situação depois, informar "Desligado".
                    7 - Se o valor do campo na coluna desc_situacao, tiver o significado de que se encontra ausente por apresentação de atestado, 
                    informar **SEMPRE O VALOR DO CAMPO DA COLUNA DESC_SITUACAO** como situação antes, e para a situação depois, informar "Atestado".
                    8 - Se o valor do campo na coluna desc_situacao, tiver o significado de que a matricula não se encontra trabalhando, ou não se encontra em 
                    férias, ou não se encontra em licença maternidade, ou não foi beneficiada por auxílio doença, ou não se encontra em viagem no exterior,
                    ou foi desligada da empresa, ou se encontra ausente por apresentação de atestado médico, informar **SEMPRE O VALOR DO CAMPO DA COLUNA DESC_SITUACAO** 
                    como situação antes, e para a situação depois, informar "erro situacao".
                    9 - **SEMPRE** informar um JSON **válido**
                    ##########################################################################################################################################
                    
                    {formatador_saida_ia}
            """
            
    prompt_template = PromptTemplate(
                                        template=template,
                                        input_variables=["context"],
                                        partial_variables={"formatador_saida_ia":parseador.get_format_instructions()}
                                    )   
    
       
    chain = prompt_template |llm | parseador
    
        
    # TRATANDO RESPOSTAS INDEVIDAS
    resposta = chain.invoke(input={"context" : dfativos_situacao.to_string(index=False)})['situacao']         
            
    # PADRONIZANDO O CAMPO SITUACAO
    for r in resposta:
        if r['situacao_antes'] in ['.','Outro']: # TRATANDO PROBLEMA
            continue
        
        elif r['situacao_depois'] != "erro situacao":
        
            df.loc[df['desc_situacao'] == r['situacao_antes'],'desc_situacao'] = r['situacao_depois']
            
        else:
            return "erro situacao"
          
    
    # df COM O CAMPO DESC SITUACAO PADRONIZADO
    print('DataFrame \n')
    print(df)
    
    return df 
    

def valor_sindicato(sindicato_id,engine,sindicato_table):
    
    stmtestadosindicato = select(sindicato_table.c.estado).where(sindicato_table.c.id == sindicato_id)
    estado = read_sql(stmtestadosindicato, con=engine)['estado'].values[0]
    
    valor_table = Table("valor", MetaData(), autoload_with=engine)
    stmtvalor = select(valor_table.c.valor_va).where(valor_table.c.estado == estado)
    valor_sindicato = read_sql(stmtvalor, con=engine)['valor_va'].values[0]
    
    return valor_sindicato

def padroniza_sindicato_valor(df, llm, engine, sindicato_table): 
    
    print('Padroniza o nome do sindicato com as outras planilhas previamente carregadas, e obtém qtd_dias_uteis...')
    sleep(5)
    
    print('Dataframe sem duplicatas de sindicatos do')
    dfsindicato = df['sindicato'].drop_duplicates()
    print(dfsindicato) 
    
    class dictsindicato(TypedDict):
        sindicato_df: str
        sindicato_id_tab: str
        
    class sindicato(BaseModel):
        sindicato : List[dictsindicato] = Field(description="Lista de ids e sindicatos associados")
        
    parseador = JsonOutputParser(pydantic_object=sindicato)
    
    template = """ 
                    Aja como um assistente que é capaz de mapear valores, de acordo com os significados 
                    dos valores informados na coluna sindicato do dataframe {df}.
                    **- Não faça perguntas nem adicione esclarecimentos.**
                                                       
                    Para isso, devem ser seguidos os seguintes passos:
                    ##########################################################################################################################################
                    1 - Buscar sindicato id tabela, na tabela de sindicatos {tab_sind}, aonde o sindicato do dataframe tenha o mesmo significado do 
                    sindicato da tabela de sindicatos, caso não encontre, retorne "erro sindicato" para sindicato id tabela.
                    
                    ##########################################################################################################################################    
                    
                    {formatador_saida_ia}
               """
        
    prompt_template = PromptTemplate(
                                        template=template,
                                        input_variables=["df","tab_sind"],
                                        partial_variables={"formatador_saida_ia":parseador.get_format_instructions()}
                                    )   
    
    chain = prompt_template |llm | parseador
    
    stmt = select(sindicato_table)   
    dfsindicatotab = read_sql(stmt,engine)
    
    resposta = chain.invoke(input={"df" : dfsindicato.to_string(index=False), "tab_sind":dfsindicatotab.to_string(index=False)})['sindicato']
                       
    for r in resposta:
               
        if r['sindicato_id_tab'] != 'erro sindicato':
            
            stmt = select(sindicato_table.c.sindicato,sindicato_table.c.qtd_dias_uteis).where(sindicato_table.c.id == r['sindicato_id_tab'])
            nome_sindicato = read_sql(stmt,engine)['sindicato'].values[0] # NOME DO SINDICATO PARA O ID
            qtd_dias_uteis = read_sql(stmt,engine)['qtd_dias_uteis'].values[0] # QTD_DIAS_UTEIS PARA O ID
            valor = valor_sindicato(r['sindicato_id_tab'],engine,sindicato_table) # VALOR PARA O ID. NÃO DÁ PARA CHAMAR A VARIÁVEL DE valor_sindicato, pois dá erro com a 
                                                                                  # função de mesmo nome 
            
            # INCLUINDO A QTD DIAS ÚTEIS PARA O SINDICATO DO DATAFRAME
            df.loc[df['sindicato'].str.contains(r['sindicato_df']),'qtd_dias_uteis'] = qtd_dias_uteis
                                    
            # INCLUINDO O VALOR PARA O SINDICATO DO DATAFRAME
            df.loc[df['sindicato'].str.contains(r['sindicato_df']),'valor_va'] = valor
                        
            # PREENCHENDO QTD_DIAS = qtd_dias_uteis, SE DESC.SITUACAO = Trabalhando
            df.loc[((df['sindicato'].str.contains(r['sindicato_df'])) & (df['desc_situacao'] == 'Trabalhando')), 'qtd_dias'] = qtd_dias_uteis
                                    
            # PADRONIZANDO O CAMPO SINDICATO   
            df.loc[df['sindicato'].str.contains(r['sindicato_df']),'sindicato'] = nome_sindicato
                                
        else:
            return "erro sindicato"
            
    # df COM O CAMPO SINDICATO PADRONIZADO, QTD_DIAS_UTEIS E VALOR DO SINDICATO
    print('DataFrame \n')
    print(df)
    
    return df 
    

# [markdown]
# ### <b>AGENTE 5: ATIVOS</b>

def agente_ativos(uploaded_file_ativos,engine,llm):
    
    print('Executando agente ativos...')
            
    # PADRONIZA O NOME DAS COLUNAS CONFORME TABELA FUNCIONÁRIOS
    dfativos = checa_colunas(uploaded_file_ativos,engine,llm) # O ARQUIVO NÃO CONTÉM DESLIGADOS
    
    # REMOVE LINHAS NULAS
    dfativos = dfativos.dropna(how='all').drop_duplicates()
    dfativos = dfativos.dropna(subset=['matricula'])
    
    # PROBLEMA
    dfativos.drop(labels=dfativos.loc[dfativos['desc_situacao'] == "."].index,inplace=True)
    
    # INSERE COLUNAS, PARA PERSISTIR VALORES NA TABELA FUNCIONARIOS
    dfativos.insert(loc=len(list(dfativos.columns.values)), column='qtd_dias_uteis',value=0) 
    dfativos.insert(loc=len(list(dfativos.columns.values)), column='valor_va',value=0.0)
    
    sindicato_table = Table("sindicato", MetaData(), autoload_with=engine)

    dfsituacao_padronizada = padroniza_situacao(dfativos,llm)
    
    if isinstance(dfsituacao_padronizada,DataFrame) and not dfativos.empty:    
        dfsindicato_padronizado = padroniza_sindicato_valor(dfsituacao_padronizada,llm,engine,sindicato_table) # JOGA O RESULTADO DE padroniza_situacao AQUI
        
        if isinstance(dfsindicato_padronizado, str) and dfsindicato_padronizado == "erro sindicato":
            return "erro sindicato"
        
    elif isinstance(dfsituacao_padronizada,str) and dfsituacao_padronizada == "erro situacao":
        return "erro situacao" 

      
    return dfsindicato_padronizado

# [markdown]
# ### <b>AGENTE 6: FÉRIAS</b>

def agente_ferias(uploaded_file_ferias,engine,llm):
    
    print('Executando agente férias...')
        
    # PADRONIZA O NOME DAS COLUNAS CONFORME TABELA FUNCIONÁRIOS - VERIFICAR ISSO -> DIAS FÉRIAS para qtd_dias ? SIM
    #df = checa_colunas(uploaded_file_ferias,engine,llm)
    
    df = read_excel(uploaded_file_ferias)
    
    # ELIMINANDO NULOS E DUPLICATAS
    df = df.dropna(how='all').drop_duplicates()
    df = df.dropna(subset=['MATRICULA'])
    
    # VERIFICA SE TODAS AS MATRICULAS EXISTEM NA TABELA FUNCIONÁRIOS
    dffuncionarios_ferias = read_sql("SELECT matricula, desc_situacao, qtd_dias FROM funcionarios WHERE desc_situacao = 'Férias'",engine)
    
    # EXISTEM 4 MATRÍCULAS QUE ESTÃO NA PLANILHA FÉRIAS E NÃO ESTÃO NA PLANILHA ATIVOS. {30867,31237,31740 E 34447}
    # E SEM O SINDICATO, NÃO DÁ PARA SABER O VALOR DOS VAs
    if (~df['MATRICULA'].isin(dffuncionarios_ferias['matricula'])).any():
        
        dfsem_matricula = df.loc[df['MATRICULA'].isin(dffuncionarios_ferias['matricula']) == False]
        print('Matrículas de férias que não estão na planilha de ativos')
        print(dfsem_matricula)
        
        #return "erro matricula" # COMENTANDO PARA PROSSEGUIR A EXECUÇÃO
    
    elif (df['qtd_dias'].isna()).any():
        return "erro ferias"        
            
    # ATUALIZANDO QTD_DIAS (DE FÉRIAS) NA TABELA FUNCIONÁRIO
    #else: # COMENTANDO PARA PROSSEGUIR A EXECUÇÃO 
    for l in df.values:
        dffuncionarios_ferias.loc[((dffuncionarios_ferias['matricula'] == l[0])),'qtd_dias'] = l[2]                      
        
    return dffuncionarios_ferias  

# [markdown]
# ### <b>AGENTE 7 - AFASTAMENTOS</b>

def agente_afastamentos(uploaded_file_afastamentos, engine,llm):
    
    print('Executando agente afastamentos...')
        
    df = read_excel(uploaded_file_afastamentos)
    
    # ELIMINANDO NULOS E DUPLICATAS
    df = df.dropna(how='all').drop_duplicates()
    df = df.dropna(subset=['MATRICULA'])   
    
    print('DataFrame planilha')
    print(df)
        
    # VERIFICA SE TODAS AS MATRICULAS EXISTEM NA TABELA FUNCIONÁRIOS
    dffuncionarios_afastados = read_sql("SELECT matricula, desc_situacao, qtd_dias, data_inicio_mes_competencia, data_fim_mes_competencia, data_retorno FROM funcionarios WHERE desc_situacao IN ('Licença Maternidade','Auxílio Doença','Atestado')",engine)
    
    if (~df['MATRICULA'].isin(dffuncionarios_afastados['matricula'])).any():
        print("Erro: Existem matrículas na planilha de afastamento que não estão na planilha ativos que foram afastados") 
        print(df.loc[df['MATRICULA'].isin(dffuncionarios_afastados['matricula']) == False])
        
        return "erro matricula"        

    else:
                       
        # PADRONIZAÇÃO SITUAÇÃO
        dffuncionarios_afastados = padroniza_situacao(dffuncionarios_afastados,llm)
        
        # SITUACAO NÃO MAPEADA   
        if isinstance(dffuncionarios_afastados,str) and dffuncionarios_afastados == 'erro situacao':    
            return "erro situacao" 
        
        class afastamento(TypedDict):
            matricula : int 
            desc_situacao: str
            data_retorno : date
            
        class Afastamento(BaseModel):
            extracao_data : List[afastamento] = Field(description='Lista contendo matricula, desc_situacao e data de retorno associadas')                             
                     
        parseador = JsonOutputParser(pydantic_object=Afastamento)
        
        template = """
                        Aja como um assistente que é capaz de **EXTRAIR DATAS** de um dataframe {context}.
                        As datas podem estar no formato **DD/MM** ou **DD/MM/YYYY**. DD -> dias, MM -> mês, YYYY -> ano. Considere YYYY = {ano}
                        Ex: 11/06, 12/06, 04/06, 26/05, 05/06
                        **SEMPRE** gere **JSONs VÁLIDOS**
                                                                      
                        **- Não faça perguntas nem adicione esclarecimentos.**
                        
                        ########################################################################################################                                
                        Para isso, você deve seguir os passos abaixo:
                        
                        1 - Obter as matriculas, as desc_situacao e as datas associadas
                        a cada matricula.
                        2 - As datas estão no formato DD/MM
                        3 - Converta as datas para o formato YYYY-MM-DD
                        4 - Caso não encontre a data para a matricula, retornar null para a data de retorno
                        ########################################################################################################
                                             
                        {formatador_saida_ia}
                   """
                
        prompt_template = PromptTemplate(
                                            template=template,
                                            input_variables=["context","ano"],
                                            partial_variables={"formatador_saida_ia":parseador.get_format_instructions()}
                                        )       
        
        chain = prompt_template |llm | parseador
                
        # TRATANDO OS DADOS DA PLANILHA COM IA    
        ano = date.today().year
        resposta = chain.invoke(input={"context" : df.to_string(index=False), "ano" : ano})['extracao_data']     
        
        # CALCULO PARA A QUANTIDADE DE DIAS E VERIFICAÇÃO DE RETORNO NO INTERVALO DE COMPETÊNCIA
        data_inicio_mes_competencia = dffuncionarios_afastados['data_inicio_mes_competencia'].drop_duplicates().values[0]
        data_fim_mes_competencia = dffuncionarios_afastados['data_fim_mes_competencia'].drop_duplicates().values[0]
        
        intervalo_competencia = f'{data_inicio_mes_competencia} e {data_fim_mes_competencia}'
        
        data_inicio_mes_competencia = datetime.strptime(data_inicio_mes_competencia,'%Y-%m-%d').date() # PARA FAZER DIFERENÇA, TEM QUE TRANSFORMAR PARA O TIPO DATE
        data_fim_mes_competencia = datetime.strptime(data_fim_mes_competencia,'%Y-%m-%d').date() # PARA FAZER DIFERENÇA, TEM QUE TRANSFORMAR PARA O TIPO DATE                
        
        for r in resposta:
            
            print('Matricula: ',r['matricula'])
            print('Desc situacao: ', r['desc_situacao'])
            
            if r['data_retorno']: 
                data_retorno = datetime.strptime(r['data_retorno'],'%Y-%m-%d').date() # PARA FAZER DIFERENÇA, TEM QUE TRANSFORMAR PARA O TIPO DATE 
                dffuncionarios_afastados.loc[((dffuncionarios_afastados['matricula'] == r['matricula']) & (dffuncionarios_afastados['desc_situacao'] == r['desc_situacao'])),'data_retorno'] = data_retorno
                                               
                if not (data_inicio_mes_competencia <= data_retorno <= data_fim_mes_competencia):
                    
                    print(f'Data_retorno fora do intervalo de competência. Intervalo de competencia: {intervalo_competencia}. Setando qtd_dias para null')
                    qtd_dias = None                 
                                        
                else: # DATA RETORNO DENTRO DO INTERVALO DE COMPETÊNCIA                    
                    
                    qtd_dias_corridos = (data_fim_mes_competencia - data_retorno + timedelta(days=1)).days # QTD DIAS CORRIDOS DE VALE PARA PAGAR.
                    
                    tabela = Table('dias_nao_uteis',MetaData(),autoload_with=engine)
                    stmt = select(tabela)
                    dfdias_nao_uteis = read_sql(stmt,engine)
                    
                    listadias_nao_uteis_intervalo = []
                    
                    if not dfdias_nao_uteis.empty:
                        for d in dfdias_nao_uteis['data'].values:
                                                        
                            d = datetime.strptime(d,'%Y-%m-%d').date()
                            
                            if (data_retorno <= d <= data_fim_mes_competencia):
                                listadias_nao_uteis_intervalo.append(d)
                        
                        qtd_dias = qtd_dias_corridos - len(listadias_nao_uteis_intervalo)
                        
                    else:
                        qtd_dias = qtd_dias_corridos           
                    
                print('Data retorno: ',data_retorno)       
                                                            
            else:
                print('Data retorno nula')
                qtd_dias = None
            
            dffuncionarios_afastados.loc[((dffuncionarios_afastados['matricula'] == r['matricula']) & (dffuncionarios_afastados['desc_situacao'] == r['desc_situacao'])),'qtd_dias'] = qtd_dias
                
    print('DataFrame afastados\n',dffuncionarios_afastados)
              
    return dffuncionarios_afastados

# [markdown]
# ### <b>AGENTE 8 - DESLIGADOS - ESTOU AQUI</b>

def agente_desligados(uploaded_file_desligados, engine,llm):
    
    print('Executando agente desligados...')
        
    df = checa_colunas(uploaded_file_desligados,engine,llm)
        
    # ELIMINANDO NULOS E DUPLICATAS
    df = df.dropna(how='all').drop_duplicates()
    df = df.dropna(subset=['matricula'])
    
    # VERIFICA SE TODAS AS MATRICULAS EXISTEM NA TABELA FUNCIONÁRIOS (PLANILHA ATIVOS)
    dffuncionarios_desligados = read_sql("SELECT matricula, desc_situacao, data_demissao, data_inicio_mes_competencia, data_fim_mes_competencia, comunicado_desligamento, qtd_dias FROM funcionarios WHERE desc_situacao = 'Desligado'",engine)
    
    if (~df['matricula'].isin(dffuncionarios_desligados['matricula']).any()): # NÃO EXISTE NENHUMA MATRICULA DA PLANILHA DESLIGADOS, NA PLANILHA ATIVOS
        dfsem_matricula = df.loc[(df['matricula'].isin(dffuncionarios_desligados['matricula']) == False)]
        print('Matrículas desligadas que não estão na planilha de ativos') # COMO A PLANILHA NÃO POSSUI OS SINDICATOS, NÃO TEM COMO CALCULAR O VALOR DO VA PARA
                                                                           # ESSAS MATRICULAS
        print(dfsem_matricula) 
        #return "erro matricula"
    
    for l in df.values:
        matricula = l[0]
        
        if (df.loc[df['matricula'] == matricula,'comunicado_desligamento'].str.upper() == 'OK') and df.loc[df['matricula'] == matricula,'data_demissao'].isna():
            return "erro data_demissao"

        else: # MATRICULA PRESENTE NA TABELA FUNCIONÁRIOS (PLANILHA ATIVOS)        
            
            # OBTENDO OS DADOS DO BD 
            data_inicio_mes_competencia = dffuncionarios_desligados['data_inicio_mes_competencia'].drop_duplicates().values[0]
            data_fim_mes_competencia = dffuncionarios_desligados['data_fim_mes_competencia'].drop_duplicates().values[0]
                            
            print('Tipo da data_fim_mes_competencia: ', type(data_fim_mes_competencia)) # TIPO DA DATA NO BD.       
                    
            data_inicio_mes_competencia = datetime.strptime(data_inicio_mes_competencia,'%Y-%m-%d').date() # PARA FAZER DIFERENÇA OU COMPARAÇÕES, TEM QUE TRANSFORMAR PARA O TIPO DATE 
            data_fim_mes_competencia = datetime.strptime(data_fim_mes_competencia,'%Y-%m-%d').date() # PARA FAZER DIFERENÇA OU COMPARAÇÕES, TEM QUE TRANSFORMAR PARA O TIPO DATE        
                    
            for l in df.values:
                matricula = l[0]
                data_demissao = datetime.strptime(l[1],'%Y-%m-$d').date()
                comunicado_desligamento = l[2]
                
                dffuncionarios_desligados.loc[((dffuncionarios_desligados['matricula'] == matricula) & (dffuncionarios_desligados['desc_situacao'] == 'Desligado'),'data_demissao')] = data_demissao
                
                print('Matrícula: ',matricula)
                print('data_demissao: ',data_demissao)
                print('Comunicado desligamento: ',comunicado_desligamento)                
                        
                if data_demissao <= data_inicio_mes_competencia:
                    qtd_dias = None
                    
                    dffuncionarios_desligados.loc[((dffuncionarios_desligados['matricula'] == matricula) & (dffuncionarios_desligados['desc_situacao'] == 'Desligado'),'qtd_dias')] = qtd_dias                    
                    
                elif data_inicio_mes_competencia < data_demissao <= data_fim_mes_competencia:
                    qtd_dias_corridos = (data_demissao - data_inicio_mes_competencia + timedelta(days=1)).days
                    
                    tabela = Table('dias_nao_uteis',MetaData(),autoload_with=engine)
                    stmt = select(tabela)
                    dfdias_nao_uteis = read_sql(stmt,engine)
                    
                    listadias_nao_uteis_intervalo = []
                    
                    if not dfdias_nao_uteis.empty:
                        for d in dfdias_nao_uteis['data'].values:
                                                        
                            d = datetime.strptime(d,'%Y-%m-%d').date()
                            
                            if (data_inicio_mes_competencia <= d <= data_demissao):
                                listadias_nao_uteis_intervalo.append(d)
                        
                        qtd_dias = qtd_dias_corridos - len(listadias_nao_uteis_intervalo)
                        
                        dffuncionarios_desligados.loc[((dffuncionarios_desligados['matricula'] == matricula) & (dffuncionarios_desligados['desc_situacao'] == 'Desligado'),'qtd_dias')] = qtd_dias
                                                    
                    else:
                        qtd_dias = qtd_dias_corridos 
                        
                        dffuncionarios_desligados.loc[((dffuncionarios_desligados['matricula'] == matricula) & (dffuncionarios_desligados['desc_situacao'] == 'Desligado'),'qtd_dias')] = qtd_dias                        
                              
                else:
                    qtd_dias = None                
                
                print('Qtd dias: ', qtd_dias) 
                
                
    print('DataFrame\n',dffuncionarios_desligados)
              
    return dffuncionarios_desligados

# [markdown]
# ### <b>AGENTE 9: ADMISSÃO</b>

def agente_admissao(uploaded_file_admissao, engine):
    
    print('Executando agente admissao...')
        
    df = read_excel(uploaded_file_admissao)
        
    # ELIMINANDO NULOS E DUPLICATAS
    df = df.dropna(how='all').drop_duplicates()
    df = df.dropna(subset=['MATRICULA'])
    
    print('DataFrame \n',df)
    
    # VERIFICA SE TODAS AS MATRICULAS EXISTEM NA TABELA FUNCIONÁRIOS (PLANILHA ATIVOS)
        
    dffuncionarios_admissao = read_sql("SELECT matricula, desc_situacao, data_inicio_mes_competencia, data_fim_mes_competencia, data_admissao, qtd_dias FROM funcionarios WHERE matricula IN :listamatriculas AND desc_situacao = 'Trabalhando'",engine,params=tuple(listamatriculas))
    
    if (~df[df.columns.values.tolist()[-1]].isna().any()): # MATRICULAS DA PLANILHA ADMISSAO ABRIL, QUE NÃO NA PLANILHA ATIVOS
                                                           # 35699, 35708, 35715, 35716, 35719, 35725, 35737, 35742, 35755, 35767
                                                                            
        print('Planilha faltando valor') 
        return "erro valor"
    
    elif df.iloc[:,1].isna().any():
        return "erro data_admissao"

    else: # MATRICULA PRESENTE NA TABELA FUNCIONÁRIOS (PLANILHA ATIVOS)        
        
        # OBTENDO OS DADOS DO BD 
        data_inicio_mes_competencia = dffuncionarios_admissao['data_inicio_mes_competencia'].drop_duplicates().values[0]
        data_fim_mes_competencia = dffuncionarios_admissao['data_fim_mes_competencia'].drop_duplicates().values[0]
                        
        data_inicio_mes_competencia = datetime.strptime(data_inicio_mes_competencia,'%Y-%m-%d').date() # PARA FAZER DIFERENÇA OU COMPARAÇÕES, TEM QUE TRANSFORMAR PARA O TIPO DATE 
        data_fim_mes_competencia = datetime.strptime(data_fim_mes_competencia,'%Y-%m-%d').date() # PARA FAZER DIFERENÇA OU COMPARAÇÕES, TEM QUE TRANSFORMAR PARA O TIPO DATE     
                        
        for l in df.values:
            matricula = l[0]
            data_admissao = datetime.strptime(l[1],'%Y-%m-$d').date()
                        
            print('Matrícula: ',matricula)
            print('data_admissao: ',data_admissao)
            
            if (data_inicio_mes_competencia <= data_admissao <= data_fim_mes_competencia):
               qtd_dias_corridos = (data_fim_mes_competencia - data_admissao + timedelta(days=1)).days
               
               print('Qtd dias corridos: ', qtd_dias)
               
               tabela = Table('dias_nao_uteis',MetaData(),autoload_with=engine)
               stmt = select(tabela)
               dfdias_nao_uteis = read_sql(stmt,engine)
               
               listadias_nao_uteis_intervalo = []
               
               if not dfdias_nao_uteis.empty:
                   for d in dfdias_nao_uteis['data'].values:
                                                   
                       d = datetime.strptime(d,'%Y-%m-%d').date()
                       
                       if (data_admissao <= d <= data_fim_mes_competencia):
                           listadias_nao_uteis_intervalo.append(d)
                   
                   qtd_dias = qtd_dias_corridos - len(listadias_nao_uteis_intervalo)
                   
               else:
                   qtd_dias = qtd_dias_corridos   
               
               print('Qtd dias: ', qtd_dias)
               
            else:
                qtd_dias = None
            
            dffuncionarios_admissao.loc[((dffuncionarios_admissao['matricula'] == matricula) & (dffuncionarios_admissao['desc_situacao'] == 'Trabalhando'),'qtd_dias')] = qtd_dias
            dffuncionarios_admissao.loc[((dffuncionarios_admissao['matricula'] == matricula) & (dffuncionarios_admissao['desc_situacao'] == 'Trabalhando'),'data_admissao')] = data_admissao
           
    
    print('DataFrame\n',dffuncionarios_admissao)
              
    return dffuncionarios_admissao
    

# [markdown]
# ### <b>AGENTE 10: EXTERIOR</b>

def agente_exterior(uploaded_file_exterior, engine):
    
    print('Executando agente exterior...')
        
    df = read_excel(uploaded_file_exterior)
        
    # ELIMINANDO NULOS E DUPLICATAS
    df = df.dropna(how='all').drop_duplicates()
    df = df.dropna(subset=['MATRICULA'])
        
    print('DataFrame \n',df)
    
    # VERIFICA SE TODAS AS MATRICULAS EXISTEM NA TABELA FUNCIONÁRIOS (PLANILHA ATIVOS)
    listamatriculas = tuple(df['MATRICULA'].values)
    
    dffuncionarios_exterior = read_sql("SELECT matricula FROM funcionarios WHERE matricula IN :listamatriculas AND desc_situacao = 'Trabalhando'",engine,params=tuple(listamatriculas))
    
    if (~df['MATRICULA'].isin(dffuncionarios_exterior['matricula']).any()): # MATRICULAS DA PLANILHA ADMISSAO ABRIL, QUE NÃO NA PLANILHA ATIVOS
                                                                            # 35699, 35708, 35715, 35716, 35719, 35725, 35737, 35742, 35755, 35767
                                                                            
        dfsem_matricula = df.loc[(df['MATRICULA'].isin(dffuncionarios_exterior['matricula']) == False)]
        print("Matrículas de colaboradores no exterior que não estão na planilha de ativos. Essas matrículas devem estar como 'Trabalhando'") 
        print(dfsem_matricula) 
        return "erro matricula"
    
    elif df.iloc[:,1].isna().any():
        return "erro valor"

    else: # MATRICULA PRESENTE NA TABELA FUNCIONÁRIOS (PLANILHA ATIVOS)        
        
        # OBTENDO OS DADOS DO BD 
        data_inicio_mes_competencia = dffuncionarios_exterior['data_inicio_mes_competencia'].drop_duplicates().values[0]
        data_fim_mes_competencia = dffuncionarios_exterior['data_fim_mes_competencia'].drop_duplicates().values[0]
                        
        data_inicio_mes_competencia = datetime.strptime(data_inicio_mes_competencia,'%Y-%m-%d').date() # PARA FAZER DIFERENÇA OU COMPARAÇÕES, TEM QUE TRANSFORMAR PARA O TIPO DATE 
        data_fim_mes_competencia = datetime.strptime(data_fim_mes_competencia,'%Y-%m-%d').date() # PARA FAZER DIFERENÇA OU COMPARAÇÕES, TEM QUE TRANSFORMAR PARA O TIPO DATE     
                        
        for l in df.values:
            matricula = l[0]
            data_admissao = datetime.strptime(l[1],'%Y-%m-$d').date()
                        
            print('Matrícula: ',matricula)
            print('data_admissao: ',data_admissao)
            
            if (data_inicio_mes_competencia <= data_admissao <= data_fim_mes_competencia):
               qtd_dias_corridos = (data_fim_mes_competencia - data_admissao + timedelta(days=1)).days
               
               print('Qtd dias corridos: ', qtd_dias)
               
               tabela = Table('dias_nao_uteis',MetaData(),autoload_with=engine)
               stmt = select(tabela)
               dfdias_nao_uteis = read_sql(stmt,engine)
               
               listadias_nao_uteis_intervalo = []
               
               if not dfdias_nao_uteis.empty:
                   for d in dfdias_nao_uteis['data'].values:
                                                   
                       d = datetime.strptime(d,'%Y-%m-%d').date()
                       
                       if (data_admissao <= d <= data_fim_mes_competencia):
                           listadias_nao_uteis_intervalo.append(d)
                   
                   qtd_dias = qtd_dias_corridos - len(listadias_nao_uteis_intervalo)
                   
               else:
                   qtd_dias = qtd_dias_corridos   
               
               print('Qtd dias: ', qtd_dias)
               
            else:
                qtd_dias = None
            
            dffuncionarios_admissao.loc[((dffuncionarios_admissao['matricula'] == matricula) & (dffuncionarios_admissao['desc_situacao'] == 'Trabalhando'),'qtd_dias')] = qtd_dias
            dffuncionarios_admissao.loc[((dffuncionarios_admissao['matricula'] == matricula) & (dffuncionarios_admissao['desc_situacao'] == 'Trabalhando'),'data_admissao')] = data_admissao
           
    
    print('DataFrame\n',dffuncionarios_admissao)
              
    return dffuncionarios_exterior
    

# [markdown]
# ### <b>AGENTE 1: AQUISIÇÃO DE DOCUMENTOS</b>
# <b>Responsabilidade:</b> Obter e pré-processar documentos fiscais<br/><br/>
# <b>Funcionalidades:</b>
# <ul><li>Interface para upload manual de arquivos</li></ul>
# <ul><li>Validação inicial de formato e integridade dos documentos</li></ul>
# <ul><li>Organização e catalogação dos arquivos recebidos</li></ul>

def agente1(engine,llm): # FRONTEND.
                         # CADASTRO NO BD OCORRE AQUI 

    #css()
    
    print("Executando o agente 1...")    
    
    st.set_page_config(page_title="Agente VA", layout="centered")
    st.title("🤖 Agente VA")
    
       
    uploaded_file_base_dias = st.file_uploader("📂 Adicione a planilha Base dias uteis", type=["xls","xlsx"])    
                    
    if uploaded_file_base_dias is not None:       
                
        with st.spinner("Analisando os dados com IA..."):
           dictintervalo_competencia = agente_intervalo_competencia(uploaded_file_base_dias,llm)
           
        if dictintervalo_competencia is not None:
                       
            data_inicio_mes_competencia = dictintervalo_competencia['data_inicio_mes_competencia']
            data_fim_mes_competencia = dictintervalo_competencia['data_fim_mes_competencia']
                                                
            st.text(f'Data início mês de competência: {datetime.strptime(data_inicio_mes_competencia,'%Y-%m-%d').strftime('%d/%m/%Y')} - Data fim mês de competência: {datetime.strptime(data_fim_mes_competencia,'%Y-%m-%d').strftime('%d/%m/%Y')}') 
                    
            # CRIANDO AS TABELAS PARA COMEÇAR A REALIZAR O MAPEAMENTO DAS COLUNAS DAS PLANILHAS COM AS COLUNAS DO BD
            cria_tabelas(engine, data_inicio_mes_competencia, data_fim_mes_competencia)
            
            with st.spinner("Analisando os dados com IA..."):       
                resposta_qtd_dias_uteis = agente_dias_uteis(uploaded_file_base_dias, llm, dictintervalo_competencia, engine)                
            
            if resposta_qtd_dias_uteis:
                escreve_bd(engine,resposta_qtd_dias_uteis,'sindicato') 
                
                uploaded_file_sindvalor = st.file_uploader("📂 Adicione a planilha Base sindicato x valor.", type=["xls","xlsx"])                                                
                                                
                if uploaded_file_sindvalor: 
                                                               
                    print('Arquivo com os valores...')
                                
                    with st.spinner("Analisando os dados com IA..."):                                            
                        resposta = agente_valores_sindicato(uploaded_file_sindvalor, engine, llm) # ESTADO E VALOR
                    
                    if resposta is not None:
                            
                        escreve_bd(engine, resposta, 'valor')
                        
                        uploaded_file_ativos = st.file_uploader("📂 Adicione a planilha ATIVOS", type=["xls","xlsx"])                         
                        
                        if uploaded_file_ativos:
                            with st.spinner("Analisando os dados com IA..."):
                                resposta = agente_ativos(uploaded_file_ativos,engine, llm)
                                
                            if isinstance(resposta,DataFrame) and not resposta.empty:                                
                                escreve_bd(engine,resposta,'funcionarios')                               
                                
                                uploaded_file_ferias = st.file_uploader("📂 Adicione a planilha FÉRIAS", type=["xls","xlsx"])
                                
                                if uploaded_file_ferias:
                                    with st.spinner("Analisando os dados com IA..."):
                                        resposta = agente_ferias(uploaded_file_ferias, engine,llm)
                                    
                                    if isinstance(resposta,DataFrame) and not resposta.empty:
                                        escreve_bd(engine,resposta,'Férias')                                   
                                                           
                                        uploaded_file_afastamentos = st.file_uploader("📂 Adicione a planilha AFASTAMENTO", type=["xls","xlsx"])
                                        
                                        if uploaded_file_afastamentos:
                                            with st.spinner("Analisando os dados com IA..."):
                                                resposta = agente_afastamentos(uploaded_file_afastamentos, engine,llm) 
                                                
                                            if isinstance(resposta,DataFrame) and not resposta.empty:
                                                escreve_bd(engine,resposta,'afastamentos') 
                                                                                                        
                                                uploaded_file_desligados = st.file_uploader("📂 Adicione a planilha DESLIGADOS", type=["xls","xlsx"])
                                                st.text('Se estiver como OK o comunicado até dia 15, não considerar compra, se informado depois do dia 15, considerar compra proporcional') 
                                                
                                                if uploaded_file_desligados:
                                                    with st.spinner("Analisando os dados com IA..."):
                                                        resposta = agente_desligados(uploaded_file_desligados, engine, llm)
                                                        
                                                    if isinstance(resposta, DataFrame) and not resposta.empty:
                                                        escreve_bd(engine,resposta,'Desligado')                                      
                                                    
                                                        uploaded_file_admissao = st.file_uploader("📂 Adicione a planilha ADMISSAO", type=["xls","xlsx"])
                                                        
                                                        if uploaded_file_admissao:
                                                            with st.spinner("Analisando os dados com IA..."):
                                                                resposta = agente_desligados(uploaded_file_desligados, engine, llm)
                                                        
                                                        if isinstance(resposta,DataFrame) and not resposta.empty:
                                                            escreve_bd(engine,resposta,'admissao')
                                                                                                                
                                                            uploaded_file_exterior = st.file_uploader("📂 Adicione a planilha EXTERIOR", type=["xls","xlsx"])                  
                                                            
                                                            uploaded_file_estagaprendiz = st.file_uploader("📂 Adicione as planilhas ESTÁGIO e APRENDIZ", type=["xls","xlsx"],accept_multiple_files=True)
                                                                                                    
                                                            if st.button("🔍 Consultar"):                
                                                                                                            
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
                                                                    
                                                    elif isinstance(resposta,str):
                                                        # NENHUMA MATRICULA DA PLANILHA DESLIGAMENTOS SE ENCONTRA NA PLANILHA ATIVOS
                                                        # if resposta == "erro matricula": 
                                                        #     st.error(""" Verifique se todas as matriculas da planilha desligados estão na planilha ativos.""")
                                                            
                                                        if resposta == "erro data_demissao":
                                                            st.error(""" Verifique se todas as datas de demissão foram preenchidas """)                                                                    
                                                
                                                    
                                            elif isinstance(resposta,str): 
                                                if resposta == "erro matricula":
                                                    st.error(""" Verifique se todas as matriculas da planilha afastamentos estão na planilha ativos.""")
                                                        
                                                elif resposta == "erro situacao":
                                                    st.error(""" Verifique se todas as desc_situacao cadastradas na planilha de afastamentos estão na planilha de ativos """)                                            
                                            
                                    elif isinstance(resposta,str): 
                                        if resposta == "erro matricula":
                                            st.error(""" Verifique se todas as matriculas da planilha Férias estão na planilha ativos.""")
                                                
                                        elif resposta == "erro ferias":
                                            st.error(""" Verifique se a planilha está completamente preenchida """)                                                             
                                            
                            elif isinstance(resposta,str): 
                                if resposta == "erro sindicato":
                                    st.error(""" Verifique se planilha de ativos possui os mesmos sindicatos que as outras.""")
                                        
                                elif resposta == "erro situacao":
                                    st.error(""" Verifique se planilha de ativos possui uma descrição de situação diferente de 
                                                 'Trabalhando', 'Férias', 'Licença Maternidade','Auxílio Doença','Exterior','Desligado' ou 'Atestado'      
                                             """)                                                             
                                   
                    else:
                        st.error(""" Verifique se planilha sindicato x valor está completamente preenchida, 
                                    ou se os estados entre essa planilha e a sindicato x dias úteis são os mesmos.""")           
            else:
                st.error(""" Verifique se planilha de base de dias úteis, possui os nomes dos sindicatos e seus estados.""")                                                   
        else:            
            st.error(""" Não foi possível determinar as datas de início ou de fim do mês de competência. 
                        Verifique se planilha informa o intervalo de dias úteis.""")
                        
                

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

    set_llm_cache(InMemoryCache())
    
    llm = ChatOpenAI(                    
        model="gpt-5-mini",
        #model="microsoft/mai-ds-r1:free",
        #base_url="https://openrouter.ai/api/v1",
        #model="gpt-5",
        temperature=0,
        cache=True,
        reasoning_effort="high",        
        api_key=getenv("API_KEY")                                  
    )
    
    DATABASE_URL = "sqlite:///va_data.db"
    engine = create_engine(DATABASE_URL,echo=True) 
    
    if not exists('va_data.bd'):
        print('Criando BD...')
                    
            
    # INICIALIZAÇÃO DO AGENTE
    agente1(engine,llm)  # Executa a função que inicia o agente   

# EXPORTAR ESSE NOTEBOOK PARA UM SCRIPT PYTHON ANTES
#!streamlit run agente_va.py --server.port 8100

