# [markdown]
# PACOTES

#%pip install -r requirements.txt

# [markdown]
# ### IMPORTS

from os import getenv
from os.path import splitext
from time import sleep
from pydantic import BaseModel, Field
from typing import Dict, List, Any
from pandas import DataFrame, read_csv, read_sql
from sqlalchemy import create_engine, text, Engine
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from langchain_community.cache import InMemoryCache
from langchain.globals import set_debug, set_llm_cache
import streamlit as st
import streamlit.components.v1 as components
from streamlit.runtime.uploaded_file_manager import UploadedFile
from transformers import AutoTokenizer
import requests
from re import findall,sub
import io, zipfile

set_debug(True)


class ErroProcessamento(Exception):
    pass

# [markdown]
# ### <b>AGENTE 3: Conclusão Geral</b>

def agente3(llm:ChatOpenAI, conclusoes:List[Dict[str,str]]) -> Dict:

    print('\nExecutando agente 3...')
    
    template_query = """
                        Aja como um analista de dados que analisou dados relativos a um dataset e que obteve as conclusões abaixo de análises anteriores.
                        
                        Seja sucinto. Deverá ser gerado um código HTML com a conclusão geral sobre os dados.                        
                                        
                        CONCLUSÕES ANTERIORES:
                        {conclusoes}
                        
                        A resposta deve ser no idioma português do Brasil.
                        
                        ** SEMPRE GERE UM JSON VÁLIDO **.
                        
                        **- Não faça perguntas nem adicione esclarecimentos.**
                        
                        Deverão ser seguidos os seguintes passos:
                        
                        PASSOS:
                        1 - Aplique formatação condicional (via CSS no <style>) para destacar valores relevantes (ex: valores altos em vermelho, baixos em verde).
                        2 - Inclua títulos e legendas para clareza.
                        3 - Incorpore gráficos, se necessário, para melhor visualização. (Ex: Histogramas, gráficos de barras, linhas, boxplots, heatmaps, etc). Para a criação
                        dos gráficos, siga os passos 3.1, 3.2, 3.3, 3.4 e 3.4.1
                        3.1 - ** SEMPRE ** utilize o script plotly.js de https://cdn.plot.ly/plotly-3.3.0.min.js para a geração dos gráficos interativos.
                        3.2 - ** SEMPRE ** use as informações de CONCLUSÕES ANTERIORES para criar os gráficos
                        3.3 - ** SEMPRE ** de nomes aos eixos dos gráficos.
                        3.4 - Os gráficos ** SEMPRE ** devem possuir dados, não somente seus títulos ou legendas                     
                        3.4.1 - ** SEMPRE ** simule o que aconteceria com a carga do código HTML e produza a saida no console, se os gráficos estiverem sem os dados, ou somente com seus 
                        títulos ou legendas, retorne para o passo 3
                        4 - Incorpore tabelas (com a formatação condicional do passo 1), se necessário, para melhor visualização.
                        5 - Adicione uma seção de conclusões no final, destacando os principais insights e aprendizados com as CONCLUSÕES ANTERIORES.                      
                        
                        {formatacao_saida}
                        
                        {{codigo : "HTML com a resposta da análise de dados"}}                        
                        
                     """
                     
    # FORMATANDO A SAÍDA DA LLM COM JsonOutputParser
    class ConclusaoGeral(BaseModel):
        codigo: str = Field(description='Codigo HTML')
        
    parseador = JsonOutputParser(pydantic_object=ConclusaoGeral)
    
    prompt_template_query = PromptTemplate(
                                            template=template_query,
                                            input_variables=["conclusoes"],
                                            partial_variables={"formatacao_saida" : parseador.get_format_instructions()}
                                          )
    
    
    chain = prompt_template_query | llm | parseador
    
            
    err = 0
    while err <= 4:
        if err == 3:
            raise ErroProcessamento()
        
        else:
            err += 1
            try:
                print("\n Agente 3 - Invocando a LLM...\n")
                resposta = chain.invoke({"conclusoes":conclusoes})   
                break
            
            except Exception as e:
                print("\nAguardando 10 segundos para tentar novamente...\n")
                
                sleep(10)
                
                continue
            
    print("\n Código HTML gerado:\n",resposta['codigo'])    
    
    with open('codigo.html', 'w', encoding='utf-8') as f:
        f.write(resposta['codigo'])
    
    return resposta

# [markdown]
# ### <b>AGENTE 2: Análise de Dados</b>
# <b>Responsabilidade:</b> Processar documentos e extrair dados relevantes<br/><br/>

def num_tokens_from_string(df:DataFrame) -> int:
    
    # pip3 install transformers
    # python3 deepseek_tokenizer.py
    
    print('Verificando a quantidade de tokens...')
    
    chat_tokenizer_dir = "./"

    tokenizer = AutoTokenizer.from_pretrained( 
            chat_tokenizer_dir, trust_remote_code=True
            )   
    
    result = len(tokenizer.encode(df.to_string(index=False)))
    
    print("Quantidade de tokens: ", result,"\n")
     
    return result


def obter_context_window_size(llm):
    
    headers = {
        "Authorization": f"Bearer {getenv('API_KEY')}"
    }

    response = requests.get(
        "https://openrouter.ai/api/v1/models",
        headers=headers
    )

    models = response.json()

    for model in models["data"]:
        if model["id"] == llm.model_name:    
            print(model["id"], model.get("context_length"))
            return model.get("context_length")
    
    


def llm_gera_query(llm,engine,pergunta,nome_arquivo, conclusoes, df, qtd_tokens, taxa_reducao):

        template_query = """
                            Qual query deve ser executada, ** SOMENTE PARA COLETAR OS DADOS, SEM REALIZAR QUALQUER OPERAÇÃO SOBRE ELES **, a fim de que se possa responder
                            a pergunta "{pergunta}"? Para isso, considere os passos a seguir
                                                             
                            IMPORTANTE: Use apenas SQL compatível com SQLite. Não utilize INFORMATION_SCHEMA nem outras tabelas/metadados que não existam no SQLite. 
                            Para metadados use PRAGMA table_info("{arquivo}").
                            
                            **Não faça perguntas nem adicione esclarecimentos.**
                            
                            #######################################################################################
                            Considere os seguintes passos:
                            1 - Informações sobre os dados {describe}
                            2 - Uma amostra dos dados {amostra}
                            3 - As conclusões de análise anteriores foram {conclusoes}
                            4 - A tabela possui {linhas} linhas
                            5 - A query deve **SEMPRE FILTRAR AS COLUNAS RELEVANTES**. As colunas são "{colunas}" 
                            6 - Usar apenas parte dos dados, usando WHERE ou outras cláusulas SQL.
                            7 - ** SEMPRE ** adicionar a cláusula LIMIT que deve ser menor que {linhas}                           
                            8 - O nome da tabela é {arquivo}.   
                            9 - ** NÃO UTILIZE UNION **    
                                                        
                            ########################################################################################
                            
                            ** SEMPRE ** forneça um ** JSON VÁLIDO **                    
                                      
                            {formatacao_saida}
                            
                         """

        # FORMATANDO A SAÍDA DA LLM COM JsonOutputParser
        class Query(BaseModel):
            query: str = Field(description='Esta é a query com todas as colunas necessárias, aonde o nome de cada coluna e o da tabela {nome_arquivo} devem ficar entre ""')

        parseador = JsonOutputParser(pydantic_object=Query)
        
        prompt_template_query = PromptTemplate(
                                                template=template_query,
                                                input_variables=["pergunta","colunas","linhas","arquivo","conclusoes","describe","qtd_tokens","amostra"],
                                                partial_variables={"formatacao_saida" : parseador.get_format_instructions()}
                                              )

        # CRIANDO A CADEIA DE EXECUÇÃO PARA A LLM
        chain = prompt_template_query | llm | parseador

                        
        with engine.connect() as con:
            query = text(f'PRAGMA table_info("{nome_arquivo}")') # OBTENDO AS COLUNAS DO BD
            rs = con.execute(query)
            rows = rs.fetchall()
            colunas_query = sorted([col[1] for col in rows])
            
            # OBTENDO NÚMERO DE LINHAS            
            query = text(f'SELECT COUNT(*) FROM "{nome_arquivo}"') # OBTENDO AS COLUNAS DO BD
            rs = con.execute(query)
            rows = rs.fetchone()
            linhas = rows[0]            
        
        describe = df.describe().to_string()       
        
        print('Invocando a LLM para obter query...')
        
        amostra = df.head().to_string(index=False)        
        query = chain.invoke(input={"pergunta":pergunta, "colunas":colunas_query, "linhas" : linhas, "arquivo" : nome_arquivo, "conclusoes":conclusoes, "describe":describe, "qtd_tokens":qtd_tokens, "amostra":amostra})['query']
        
        print('Query inicial: ', query)
        
        stmt = text(query)
        dfcontext = read_sql(stmt, con=engine)
        
        print('Quantidade inicial de tokens')
        tokens = num_tokens_from_string(dfcontext) # OBTÉM A QTD DE TOKENS EQUIVALENTE AO DATAFRAME
                
        limit = int(findall(r'LIMIT (\d+)', query)[0]) # EXTRAI A PARTE NUMÉRICA DE LIMIT XYZ DA QUERY
        
        t = 0
        
        print()
        
        qtd_max_tokens = qtd_tokens*0.4
        
                
        while tokens > qtd_max_tokens and limit > 0:
                
                print('Quantidade máxima de tokens de entrada deve ser: ', qtd_max_tokens)
                
                print('DIMINUÍNDO O NÚMERO DE LINHAS...')
                
                t+=1
                print('t: ',t)
                limit = int(limit*(1 - taxa_reducao*t))                        
                print(f'NOVO VALOR DE LIMIT: {limit}') # NOVO LIMIT                                  
                
                result = sub(r'LIMIT (\d+)',f'LIMIT {limit}', query) # SUBSTITUI O "LIMIT XYZ" NA query E ATRIBUI a result
                query = result # ATRIBUI result A query                
                print('Nova Query: ', query)
                
                stmt = text(query)
                dfcontext = read_sql(stmt, con=engine) # NOVO DATAFRAME COM OBTIDO COM O NOVO VALOR DE LIMIT
                
                tokens = num_tokens_from_string(dfcontext) # OBTÉM A QTD DE TOKENS EQUIVALENTE AO NOVO DATAFRAME                
                
                sleep(10)
                
        else: 
            if limit <= 0:
                print("Valor negativo ou 0 para LIMIT...")
                
                result = sub(r'LIMIT .*',f'LIMIT 80',query)
                #result = sub(r'LIMIT .*',f'LIMIT 1000',query)
                query = result
                
                stmt = text(query)
                dfcontext = read_sql(stmt,con=engine)
                
                num_tokens_from_string(dfcontext)                      
                
        print('Query final: ', query) 
        sleep(20)
                           
        return query

def rag(arquivo:UploadedFile, pergunta:str, llm:ChatOpenAI, engine:Engine, conclusoes:List[Dict[str,str]], qtd_tokens:int, taxa_reducao:float) -> str:
    
    # OBJETIVO DE OBTER A QUERY A PARTIR DO DATAFRAME
    
    if arquivo.type == "text/csv":
        
        df = read_csv(arquivo)
        
        nome_tabela = splitext(arquivo.name)[0]
        df.to_sql(nome_tabela, con=engine, if_exists="replace", index=False)
                        
        query = llm_gera_query(llm, engine, pergunta, nome_tabela, conclusoes, df, qtd_tokens, taxa_reducao)   
                        
    else:
        # Read the file data into a BytesIO buffer
        
        with io.BytesIO(arquivo.getvalue()) as buffer:
            # Open the zip file from the buffer
            with zipfile.ZipFile(buffer, "r") as z:
                #st.write("Zip file uploaded and opened successfully!")
                print("Zip file uploaded and opened successfully!")
                
                # Display contents (optional)
                #st.write("Files in the zip:", z.namelist())
                print("Files in the zip:", z.namelist())
                
                # Example: extract all files to a temporary directory for processing
                # You would need to manage temporary directories if saving to disk
                # z.extractall("path/to/temp/directory")
                                
                # You can process files in memory without extracting to disk
                for filename in z.namelist():
                    with z.open(filename) as arquivo:
                        # Process the file data (e.g., read a CSV or JSON)
                        #st.write(f"Processing {filename}...")
                        print(f"Processing {filename}...")

                        df = read_csv(arquivo)
                        
                        nome_tabela = splitext(arquivo.name)[0]
                        df.to_sql(nome_tabela, con=engine, if_exists="replace", index=False)
                        
                        query = llm_gera_query(llm, engine, pergunta, nome_tabela, conclusoes, df, qtd_tokens, taxa_reducao)   
            
    return query

def agente2(pergunta:str, arquivo:UploadedFile, llm:ChatOpenAI, engine:Engine, conclusoes, qtd_tokens:int, taxa_reducao:float) -> Any:

    print('\nExecutando agente 2...')
    
    template_query = """
                        Aja como um analista de dados e responda a seguinte PERGUNTA {pergunta} a respeito de um dataset fornecido.
                        
                        Use as informações de CONTEXTO e CONCLUSÕES ANTERIORES abaixo.
                        
                        Seja sucinto, informe os **NOMES DAS COLUNAS** na resposta. 
                        Informe os dados que foram utilizados.
                        Ao final, deverá ser gerado um código HTML com o resumo das análises.
                        
                        CONTEXTO:
                        {context}

                        CONCLUSÕES ANTERIORES:
                        {conclusoes}
                        
                        A resposta deve ser no idioma português do Brasil.
                        
                        **- Não faça perguntas nem adicione esclarecimentos.**
                        
                                                                 
                        Deverão ser seguidos os seguintes passos:
                        
                        PASSOS:
                        1 - Aplique formatação condicional (via CSS ou <style>) para destacar valores relevantes (ex: valores altos em vermelho, baixos em verde).
                        2 - Inclua títulos e legendas para clareza.
                        3 - Informe os dados utilizados e a quantidade de registros analisados
                        4 - Incorpore gráficos, se necessário, para melhor visualização. (Ex: Histogramas, gráficos de barras, linhas, boxplots, heatmaps, etc). Para a criação
                        dos gráficos, siga os passos 4.1, 4.2, 4.3, 4.4 e 4.4.1
                        4.1 - ** SEMPRE ** utilize o script plotly.js de https://cdn.plot.ly/plotly-3.3.0.min.js para a geração dos gráficos interativos.
                        4.2 - ** SEMPRE ** use as informações de CONTEXTO e CONCLUSÕES ANTERIORES para criar os gráficos
                        4.3 - ** SEMPRE ** dê nomes aos eixos dos gráficos.
                        4.4 - Os gráficos ** SEMPRE DEVEM POSSUIR DADOS, NÃO SOMENTE SEUS TÍTULOS OU LEGENDAS **
                        4.4.1 - ** SEMPRE ** simule o que aconteceria com a carga do código HTML e produza a saida no console, se os gráficos estiverem sem os dados, ou somente com seus 
                        títulos ou legendas, retorne para o passo 4
                        5 - Incorpore tabelas (com a formatação condicional do passo 1), se necessário, para melhor visualização.
                        6 - ** SEMPRE ** adicione uma seção de conclusões no final incluíndo a resposta a PERGUNTA 
                        7 - ** SEMPRE ** simule o que aconteceria com a leitura do JSON, e produza a saída no console, se o JSON não for válido, retorne para o passo 1                      
                        
                        {formatacao_saida}                                      
                        
                     """
                     
    # FORMATANDO A SAÍDA DA LLM COM JsonOutputParser
    class AnaliseDados(BaseModel):
        codigo: str = Field(description='Codigo HTML')
        texto: str = Field(description='Texto da análise de dados')

    parseador = JsonOutputParser(pydantic_object=AnaliseDados)
    
    prompt_template_query = PromptTemplate(
                                            template=template_query,
                                            input_variables=["pergunta","context","conclusoes"],
                                            partial_variables={"formatacao_saida" : parseador.get_format_instructions()}
                                          )
    
    
    chain = prompt_template_query | llm | parseador
    
    print('Executando o RAG...')   
           
    query = rag(arquivo, pergunta, llm, engine, conclusoes, qtd_tokens, taxa_reducao)

    err=0    
           
    while err <= 4:
        if err == 3:
            raise ErroProcessamento()
        
        else:
            err += 1            
            try:
                
                print('Executando agente 2 para obtenção de HTML e texto de conclusão...')
                stmt = text(query)
                        
                dfcontext = read_sql(stmt, con=engine)
                                                                            
                print('\nPrimeiras linhas do dataframe de contexto:\n',dfcontext.head())                    
                print("\nAgente 2. Invocando a LLM...\n")
                        
                resposta = chain.invoke({"pergunta" : pergunta, "context" : dfcontext.to_string(index=False), "conclusoes":conclusoes})
                
                print("\n Código HTML gerado:\n",resposta['codigo'])
                print("\n Texto da análise de dados:\n",resposta['texto'])
                
                break
                
            except ValueError as e: # EXCEÇÃO DE ESTOURO DE JANELA DE CONTEXTO NA GERAÇÃO DO HTML
                
                print('\nEstouro da Janela de Contexto...')
                print("\nTentando executar novamente...\n")
                
                result = sub(r'LIMIT (\d+)',f'LIMIT 80',query)
                #result = sub(r'LIMIT (\d+)',f'LIMIT 1000',query)
                stmt = text(result)
                dfcontext = read_sql(stmt, con=engine)
                
                num_tokens_from_string(dfcontext)
                
                resposta = chain.invoke({"pergunta" : pergunta, "context" : dfcontext.to_string(index=False), "conclusoes":conclusoes})

                sleep(10)
                
                break
            
            except KeyError as e: # EXCEÇÃO DE JSON INVÁLIDO NA GERAÇÃO DO HTML
                
                print('\nJSON Inválido...')
                print("\nAguardando 10 segundos para tentar novamente...\n")                
                
                continue                  
    
        
    with open('codigo.html', 'w', encoding='utf-8') as f:
        f.write(resposta['codigo'])
    
    return resposta

# [markdown]
# ### <b>AGENTE 1: Aquisição de Documentos</b>
# <b>Responsabilidade:</b> Obter e pré-processar o arquivo<br/><br/>
# <b>Funcionalidades:</b>
# <ul><li>Interface para upload manual do arquivo</li></ul>
# <ul><li>Organização e catalogação dos arquivos recebidos</li></ul>

def agente1(llm:ChatOpenAI, engine:Engine, conclusoes:List[Dict[str,str]],qtd_tokens,taxa_reducao:float): # FRONTEND

    print("Executando o agente 1...")
    
    st.set_page_config(page_title="Agente EDA AI", layout="centered")
    st.title("Agente EDA AI")
        
    # Inicializa session_state para os combos
    # SE NÃO FIZER ESSE TRATAMENTO DE SESSÃO, O STREAMLIT VAI COLAPSAR TODOS OS WIDGETS,  A CADA INTERAÇÃO COM A INTERFACE
    if 'distribuicao_done' not in st.session_state: # if chave not in session_state. A chave não pode se chamar base_dias, porque esse já é nome escolhido pelo streamlit
        st.session_state['distribuicao_done'] = {}
                    
    if 'padroes_done' not in st.session_state:
        st.session_state['padroes_done'] = {}
            
    if 'anomalias_done' not in st.session_state:
        st.session_state['anomalias_done'] = {}
            
    if 'relacao_done' not in st.session_state:
        st.session_state['relacao_done'] = {}
    
    if 'conclusoes_done' not in st.session_state:
        st.session_state['conclusoes_done'] = conclusoes
               
    st.markdown('<a href="https://github.com/ajndantas/I2A2-Grupo_01/raw/refs/heads/master/Desafio%20Extra%20Fraude%20Cartao%20de%20Credito/agente_fraude_cartao/Scripts/creditcard.zip" target="_blank">Ex: Arquivo de dados</a>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("📂 Carregue o arquivo csv de dados ou zip", type=["csv","zip"])        
    default_index = 0
    
    if uploaded_file: 
              
        try:
            
            # COMBO BOX DISTRIBUIÇÃO
            options_distribuicao = [
                                        "Quais são os tipos de dados (numéricos, categóricos)?",
                                        "Qual a distribuição de cada variável ? (histogramas,distribuições)",
                                        "Qual o intervalo de cada variável (mínimo, máximo)?",
                                        "Quais são as medidas de tendência central (média, mediana)?",
                                        "Qual a variabilidade dos dados (desvio padrão, variância)?"
                                   ]
            # tenta preservar a pergunta previamente selecionada, se existir no session_state
            if st.session_state['distribuicao_done'] and 'pergunta' in st.session_state['distribuicao_done']:
                default_index = options_distribuicao.index(st.session_state['distribuicao_done']['pergunta'])
            else:
                default_index = 0

            pergunta_distribuicao = st.selectbox(
                                                    "Descrição dos dados. Escolha uma opção",  # Pergunta
                                                    options_distribuicao,  # Opções
                                                    index=default_index
                                                )  # Exibir histogramas
            
            if st.button("🔍 Consultar", key="distribuicao"):
                with st.spinner("Analisando com IA..."):
                    
                    resposta = agente2(pergunta_distribuicao, uploaded_file, llm, engine, st.session_state['conclusoes_done'],qtd_tokens,taxa_reducao)
                    #print('Conclusôes Antes: ', conclusoes)
                    conclusao = {"pergunta":pergunta_distribuicao, "resposta":resposta['texto']}
                    conclusoes = st.session_state['conclusoes_done']
                    conclusoes.append(conclusao)
                    print("Conclusões: ", conclusoes)            
                                    
                # Render raw HTML using Streamlit Components.
                # components.html accepts the HTML string, optional height and scrolling.
                components.html(resposta['codigo'], height=600, scrolling=True)
                st.session_state['distribuicao_done'] = {"codigo":resposta['codigo'], "pergunta":pergunta_distribuicao}
                st.session_state['conclusoes_done'] = conclusoes
                        
            elif st.session_state['distribuicao_done']:                 
                components.html(st.session_state['distribuicao_done']['codigo'], height=600, scrolling=True)
            
            # COMBO BOX PADRÕES                       
            options_padroes = [
                                "Existem padrões ou tendências temporais?",
                                "Quais os valores mais frequentes ou menos frequentes?",
                                "Existem agrupamentos (clusters) nos dados?"
                              ]
            
            if st.session_state['padroes_done']:
                default_index = options_padroes.index(st.session_state['padroes_done']['pergunta'])
            else:
                default_index = 0
                
            pergunta_padroes = st.selectbox(
                                                "identificação de padrões e tendências",
                                                options_padroes,
                                                index=default_index     
                                            )
                
            if st.button("🔍 Consultar",key="padroes"):
                with st.spinner("Analisando com IA..."):
                    
                    resposta = agente2(pergunta_padroes, uploaded_file, llm, engine,st.session_state['conclusoes_done'],qtd_tokens, taxa_reducao)
                    #print('Conclusôes Antes: ', conclusoes)
                    conclusao = {"pergunta":pergunta_padroes, "resposta":resposta['texto']}
                    conclusoes = st.session_state['conclusoes_done']
                    conclusoes.append(conclusao)
                    print("Conclusões: ", conclusoes) 
                    
                # Render raw HTML using Streamlit Components.
                # components.html accepts the HTML string, optional height and scrolling.
                components.html(resposta['codigo'], height=600, scrolling=True)
                st.session_state['padroes_done'] = {"codigo":resposta['codigo'], "pergunta":pergunta_padroes}
                st.session_state['conclusoes_done'] = conclusoes
                        
            elif st.session_state['padroes_done']:
                components.html(st.session_state['padroes_done']['codigo'], height=600, scrolling=True)
            
            # COMBO BOX ANOMALIAS
            options_anomalias = [
                                    "Existem valores atípicos nos dados?",
                                    "Como esses outliers afetam a análise?",
                                    "Podem ser removidos, transformados ou investigados?"
                                ]
            
            if st.session_state['anomalias_done']:
                default_index = options_anomalias.index(st.session_state['anomalias_done']['pergunta'])
            else:
                default_index = 0
            
            pergunta_anomalias = st.selectbox(
                                                "Detecção de Anomalias (Outliers):",
                                                options_anomalias,
                                                index=default_index
                                                
                                                # Exibir Boxplots
                                            )
                    
            if st.button("🔍 Consultar",key="anomalias"):
                with st.spinner("Analisando com IA..."):
                    
                    resposta = agente2(pergunta_anomalias, uploaded_file, llm, engine, st.session_state['conclusoes_done'],qtd_tokens, taxa_reducao)
                    conclusao = {"pergunta":pergunta_anomalias, "resposta":resposta['texto']}
                    conclusoes = st.session_state['conclusoes_done']
                    conclusoes.append(conclusao)
                    print("Conclusões: ", conclusoes) 
                                    
                # Render raw HTML using Streamlit Components.
                # components.html accepts the HTML string, optional height and scrolling.
                components.html(resposta['codigo'], height=600, scrolling=True)
                st.session_state['anomalias_done'] = {"codigo":resposta['codigo'], "pergunta":pergunta_anomalias}
                st.session_state['conclusoes_done'] = conclusoes
                        
            elif st.session_state['anomalias_done']:
                components.html(st.session_state['anomalias_done']['codigo'], height=600, scrolling=True)
            
            # COMBO BOX RELAÇÃO
            options_relacao = [
                                    "Como as variáveis estão relacionadas umas com as outras? (Gráficos de dispersão, tabelas cruzadas)",
                                    "Existe correlação entre as variáveis?",
                                    "Quais variáveis parecem ter maior ou menor influência sobre outras?"
                              ]
            
            if st.session_state['relacao_done']:
                default_index = options_relacao.index(st.session_state['relacao_done']['pergunta'])
            else:
                default_index = 0
                
            pergunta_relacao = st.selectbox(
                                                "Relação entre variáveis:",
                                                options_relacao,
                                                index=default_index
                                            ) # Plottar heatmaps
            
            if st.button("🔍 Consultar",key="relacao"):
                with st.spinner("Analisando com IA..."):
                    
                    resposta = agente2(pergunta_relacao, uploaded_file, llm, engine, st.session_state['conclusoes_done'],qtd_tokens, taxa_reducao)
                    conclusao = {"pergunta":pergunta_relacao, "resposta":resposta['texto']}
                    conclusoes = st.session_state['conclusoes_done']
                    conclusoes.append(conclusao)
                    print("Conclusões: ", conclusoes) 
                    
                # Render raw HTML using Streamlit Components.
                # components.html accepts the HTML string, optional height and scrolling.
                components.html(resposta['codigo'], height=600, scrolling=True)
                st.session_state['relacao_done'] = {"codigo":resposta['codigo'], "pergunta":pergunta_relacao}
                st.session_state['conclusoes_done'] = conclusoes
                        
            elif st.session_state['relacao_done']:
                components.html(st.session_state['relacao_done']['codigo'], height=600, scrolling=True)
            
            # CONCLUSÃO GERAL
            if st.button("🔍 Conclusão Geral",key="conclusao_geral"):
                with st.spinner("Analisando com IA..."):
                    resposta = agente3(llm, st.session_state['conclusoes_done'])
                
                if resposta:
                    print("Conclusão Geral: ", resposta)
                    components.html(resposta['codigo'], height=600, scrolling=True)
                    
                    # DEPOIS DE EXECUTAR A CONCLUSÃO GERAL, TODAS AS CONCLUSÕES ANTERIORES SÃO REMOVIDAS
                    pergunta = ""
                    resposta = ""
                    conclusoes = [{"pergunta":pergunta,"resposta":resposta}]
                    st.session_state['conclusoes_done'] = conclusoes
                    
                    st.session_state['distribuicao_done'] = {}                    
                    st.session_state['padroes_done'] = {}
                    st.session_state['anomalias_done'] = {}
                    st.session_state['relacao_done'] = {}
                    
        except ErroProcessamento as e:
            st.error("Erro de processamento ou limite de tokens alcançado. Favor tentar novamente ou executar a conclusão geral.")
                

# [markdown]
# ### <b>TESTANDO</b>


if __name__ == "__main__":    
    
    # INICIALIZAÇÃO DO BANCO DE DADOS
    engine = create_engine('sqlite:///./dados.db', echo=False)
    
    # INTEGRAÇÃO COM A LLM
    load_dotenv() # CARREGANDO O ARQUIVO COM A API_KEY
    
    set_llm_cache(InMemoryCache())
    
    llm = ChatOpenAI(
        #model="tngtech/deepseek-r1t2-chimera:free",
        model="gpt-5-mini",
        #base_url="https://openrouter.ai/api/v1",
        temperature=0,
        reasoning_effort="high",
        cache=True, 
        api_key=getenv("API_KEY")        
    )   
    
    qtd_tokens = obter_context_window_size(llm)    
    print("Quantidade de tokens da janela de contexto do modelo:", qtd_tokens)
    
    pergunta = ""
    resposta = ""
    conclusoes = [{"pergunta":pergunta,"resposta":resposta}]
    taxa_reducao = 0.1 # TAXA DE REDUÇÃO DA QUANTIDADE DE LINHAS DO DATASET
    
    # INICIALIZAÇÃO DO AGENTE
    agente1(llm,engine,conclusoes,qtd_tokens,taxa_reducao)  # Executa a função que inicia o agente
     

# EXPORTAR ESSE NOTEBOOK PARA UM SCRIPT PYTHON ANTES
#!streamlit run agente_nfs.py --server.port 8000

