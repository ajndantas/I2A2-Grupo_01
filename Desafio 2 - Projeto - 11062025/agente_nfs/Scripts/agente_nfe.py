# [markdown]
# ### INSTALAÇÕES

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

from os import getenv
from os.path import exists
from pandas import read_csv, read_sql, read_xml, DataFrame
from io import StringIO
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.globals import set_debug, set_llm_cache
from langchain_community.cache import InMemoryCache
from motor_ocr_otimizado import NotaFiscalOCR
import streamlit as st
from magic import from_buffer
import xml.etree.ElementTree as ET

set_debug(True)

class SemResposta(Exception):
    pass

def consultallmdocfiscal(texto,llm,tipo):
    
    if tipo not in ['text/plain','text/csv']:
        
        # CRIANDO O PROMPT PARA A LLM COM A SAIDA FORMATADA     
        
        class DocFiscal1(BaseModel):
            tipo: str = Field(description="Responda apenas com a sigla do tipo")
            campos: list = Field(description="campos extraídos do documento fiscal")
            sigcampos: list = Field(description="significado. Em poucas palavras e com a utilzação de siglas se existirem (Ex: CNPJ, UF, CPF)")
            valores: list = Field(description="Somente os Valores")
            versao: str = Field(description="versão. Se nulo, verificar se não se aplica, se sim, responder com N/A, se não, continuar buscando a versão até encontrar")
            modelo: str = Field(description="modelo. Se nulo, verificar se não se aplica, se sim, responder com N/A, se não, continuar buscando a versão até encontrar")            
                    
        parseador = JsonOutputParser(pydantic_object=DocFiscal1) 
            
        template = """Aja como um analista de contabilidade e forneça as seguintes informações sobre o documento fiscal referente a esse conteúdo "{texto}":
        ##########################################
        1 - Sigla do tipo do documento fiscal.
        2 - Significado para os nomes dos campos, de acordo com a sigla do item 1 e com as referências abaixo:
        a) Nota Técnica  
        b) Manual de Orientação do Contribuinte (MOC) 
        c) Schemas XSD
        3 - Campos para cada um dos valores 
        4 - Os valores para cada um dos campos do item 2.
        5 - Baseados nos campos do item 2 e na sigla do item 1. Qual é a versão desse documento fiscal ? Caso não encontre, procurar na legislação. Responda somente com o número da versão. 
        6 - Baseados nos campos do item 2 e na sigla do item 1. Qual é o número do modelo desse documento fiscal ? Caso não encontre, procurar na legislação. Responda somente com o número do modelo.
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
    
    elif tipo in ['text/plain','text/csv']: # DEVIDO A LLM NÃO ENTENDER BEM O CSV, TEVE QUE SE CRIAR UM PROMPT ESPECÍFICO
                
        df = texto
        
        class DocFiscal2(BaseModel):
            tipo: str = Field(description="Responda apenas com a sigla do tipo")
            versao: str = Field(description="versão. Se nulo, verificar se não se aplica, se sim, responder com N/A, se não, continuar buscando a versão até encontrar")
            modelo: str = Field(description="modelo. Se nulo, verificar se não se aplica, se sim, responder com N/A, se não, continuar buscando a versão até encontrar")
            sigcampos: list = Field(description="significado")           
                
        parseador = JsonOutputParser(pydantic_object=DocFiscal2) 
        
        template = """Aja como um analista de contabilidade e utilize como referência os itens abaixo para responder as perguntas 1, 2, 3 e 4:
        a) Nota Técnica  
        b) Manual de Orientação do Contribuinte (MOC) 
        c) Schemas XSD
        
        ##########################################
        PERGUNTAS:
        1 - Baseado no significado para cada um dos campos {colunas_df}. Qual é a sigla do tipo do documento fiscal.
        2 - Baseado no significado para cada um dos campos {colunas_df} e na sigla do item 1. Qual é a versão desse documento fiscal ? Caso não encontre, procurar na legislação. Responda somente com o número da versão.
        3 - Baseado no significado para cada um dos campos {colunas_df} e na sigla do item 1. Qual é o número do modelo desse documento fiscal ? Caso não encontre, procurar na legislação. Responda somente com o número do modelo.
        4 - Significado para cada um dos nomes dos campos {colunas_df} em poucas palavras e, quando possível, 
        com a utilização de siglas (Ex: CNPJ, UF, CPF)              
        ###########################################
        
        {formatador_saida_ia}
        """   
        
        prompt_template = PromptTemplate(
                                            template=template,
                                            input_variables=["colunas_df"],
                                            partial_variables={"formatador_saida_ia" : parseador.get_format_instructions()}
                                        )
        
        # CRIANDO A CADEIA DE EXECUÇÃO PARA A LLM
        chain = prompt_template | llm | parseador
    
        # INVOCANDO A LLM
        resposta = chain.invoke(input={"colunas_df":list(df.columns.values)})
          
        
    return resposta

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
    resposta = chain.invoke(input={"pergunta":pergunta, "df": df.to_string(index=False), "colunas_df": list(df.columns.values)})['resposta']
        
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

# [markdown]
# <b>If you’re unsure about the structure</b>

def read_tags_values_xml_file(arquivo):
    
    # Carrega o XML
    tree = ET.parse(arquivo)
    print('Tree: ',tree)
    root = tree.getroot()
    print('root: ',root)

    dict_xml = {} # DICIONÁRIO TAG-VALOR
    
    for elem in root.iter():
        #print('elem.tag: ',elem.tag)
        tag_name = elem.tag.split('}')[-1]  # TAGS. Remove o namespace do nome pegando o último elemento [-1]
        tag_value = elem.text.strip() if elem.text else '' # VALUES
        
        dict_xml[tag_name] = tag_value

    colunas = list(dict_xml.keys())
    valores = list(dict_xml.values())
    print('dict_xml: ',dict_xml)
    
    df = DataFrame(data=[valores],columns=colunas)
    print('\nDataframe\n',df)
       
    return df    


def agente2(pergunta,arquivo,engine):

    print('\nExecutando agente 2...')
    
    # INTEGRAÇÃO COM A LLM
    load_dotenv() # CARREGANDO O ARQUIVO COM A API_KEY

    set_llm_cache(InMemoryCache())
    llm = ChatOpenAI( 
        #model="tngtech/deepseek-r1t2-chimera:free",
        model="microsoft/mai-ds-r1:free",
        base_url="https://openrouter.ai/api/v1",
        cache=True,
        temperature=0.3,        
        reasoning_effort="high",        
        api_key=getenv("API_KEY")        
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
                    
              
    elif tipo in ['text/plain','text/csv'] and not arquivo.name.endswith('.xml'): 
        
        df = read_csv(arquivo)
        campos = list(df.columns.values)
        
        resposta = consultallmdocfiscal(df,llm,tipo) # O NOME DAS COLUNAS ESTÁ AQUI

        listacampos = [x.split(':')[-1].strip() for x in resposta['sigcampos']] # LISTA COM OS NOMES DOS CAMPOS DO DOCUMENTO FISCAL
        
        #listacampos = [x['significado'] for x in resposta['sigcampos']] # LISTA COM OS NOMES DOS CAMPOS DO DOCUMENTO FISCAL]        
        
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
# <ul><li>Interface para upload manual de arquivos (PDF, imagens)</li></ul>
# <ul><li>Integração com APIs de órgãos governamentais (SEFAZ)</li></ul>
# <ul><li>Validação inicial de formato e integridade dos documentos</li></ul>
# <ul><li>Organização e catalogação dos arquivos recebidos</li></ul>

def css():
    st.markdown("""
        <style>
        /* Fundo geral */
        .stApp {
            background-color: #013440;
            background-image: linear-gradient(135deg, #013440 40%, #02545C 100%);
            color: #F2F2F2;
            font-family: 'Segoe UI', 'Roboto', sans-serif;
        }

        /* Título */
        h1 {
            color: #00C2CB;
            text-align: center;
            font-size: 2.3em;
            font-weight: 700;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
        }

        /* Textos e inputs */
        .stTextInput label, .stFileUploader label, .stTextArea label {
            color: #CDE7E8 !important;
            font-weight: bold;
        }

        /* Centralizar o botão */
        div.stButton {
            display: flex;
            justify-content: center;
            margin-top: 20px;
            margin-bottom: 20px;
        }

        /* Botão principal */
        div.stButton > button:first-child {
            background: linear-gradient(90deg, #028090, #00C2CB);
            color: white;
            font-weight: 600;
            border: none;
            border-radius: 10px;
            padding: 0.6em 1.4em;
            transition: all 0.3s ease-in-out;
            box-shadow: 0px 4px 8px rgba(0,0,0,0.3);
        }

        /* Hover do botão */
        div.stButton > button:hover {
            background: linear-gradient(90deg, #00C2CB, #028090);
            transform: scale(1.05);
        }

        /* Caixas de resultado */
        .stDataFrame, .stTable {
            background-color: #E0F7FA;
            border-radius: 12px;
            padding: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.4);
        }

        /* Mensagens */
        .stSuccess, .stWarning, .stError {
            border-radius: 10px;
            font-weight: bold;
        }

        /* Links */
        a {
            color: #00C2CB;
            text-decoration: none;
        }
        a:hover {
            color: #F2F2F2;
            text-decoration: underline;
        }
        </style>
    """, unsafe_allow_html=True)


def agente1(engine): # FRONTEND

    print("Executando o agente 1...")
    
    st.set_page_config(page_title="Agente NFe", layout="centered")
    st.title("🤖 Agente NFe")
    
    css()
    
    st.markdown('<a href="https://github.com/ajndantas/I2A2-Grupo_01/raw/refs/heads/master/Desafio%202%20-%20Projeto%20-%2011062025/agente_nfs/PDFs%20Docfiscais.zip" target="_blank">Ex: Arquivo PDF, </a>', unsafe_allow_html=True)
    st.markdown('<a href="https://github.com/ajndantas/I2A2-Grupo_01/raw/refs/heads/master/Desafio%202%20-%20Projeto%20-%2011062025/agente_nfs/Imagens%20Docfiscais.zip" target="_blank">Arquivo PNG, </a>', unsafe_allow_html=True)
    st.markdown('<a href="https://github.com/ajndantas/I2A2-Grupo_01/raw/refs/heads/master/Desafio%202%20-%20Projeto%20-%2011062025/agente_nfs/CSVs%20Docfiscais.zip" target="_blank">Arquivo CSV, </a>', unsafe_allow_html=True)
    st.markdown('<a href="https://github.com/ajndantas/I2A2-Grupo_01/raw/refs/heads/master/Desafio%202%20-%20Projeto%20-%2011062025/agente_nfs/Docs%20Fiscais%20XML.zip" target="_blank">Arquivo XML </a>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader("📂 Envie um documento fiscal no formato CSV, PDF, PNG ou XML", type=["csv","pdf","png","xml"])  
           
    pergunta = st.text_input("📝 Digite sua pergunta sobre os dados:")
    
    if st.button("🔍 Consultar"):
        if not uploaded_file:
            st.error("Você precisa fazer o upload de um arquivo CSV, PDF, imagem PNG ou XML.")
            
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

