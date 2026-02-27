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
from time import sleep
from os.path import exists
from pandas import read_csv, read_sql, DataFrame
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing_extensions import List, TypedDict
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
        
        class DictFiscal(TypedDict):
            significado: str
            valor : str            
            
        class DocFiscal1(BaseModel):
            tipo: str = Field(description="Responda apenas com a sigla do tipo")
            campos: list = Field(description='campos. **SOMENTE** os campos de CONTEUDO, com correção ortográfica, tendo como referência REFERENCIA, **NUNCA** os valores.')
            #sigcampos: list = Field(description="significado. Em poucas palavras, com a utilzação de siglas se existirem (Ex: CNPJ, UF, CPF) e **NUNCA REPETIR** os significados")
            #valores: list = Field(description="**SOMENTE** os valores associados a elemento de sigcampos. **NUNCA** os campos")
            registros : List[DictFiscal] = Field(description="Lista de significados. Correção ortográfica para significado. Se algum valor for nulo ou vazio, inserir N/A")
            versao: str = Field(description="versão. Se nulo, verificar se não se aplica, se sim, responder com N/A, se não, continuar buscando a versão até encontrar")
            modelo: str = Field(description="modelo. Se nulo, verificar se não se aplica, se sim, responder com N/A, se não, continuar buscando a versão até encontrar")            
                    
        parseador = JsonOutputParser(pydantic_object=DocFiscal1) 
            
        template = """Aja como um analista de contabilidade, aonde o seu objetivo é obter as informações de PASSOS, utlizando como referência de consulta
        REFERENCIA, a respeito do CONTEUDO do documento fiscal.
        
        CONTEUDO:
        É o texto {texto} com correção ortográfica para as palavras.
        
        REFERENCIA:
        a) Nota Técnica  
        b) Manual de Orientação do Contribuinte (MOC) 
        c) Schemas XSD referentes ao documento fiscal. Para impostos, identifique quais estão no documento fiscal por meio das tags.
        d) Sobre impostos, consultar os itens b) e c).         
                
        PASSOS: 
        ##########################################
        1 - Sigla do tipo do documento fiscal.
        2 - Significado para cada um dos campos de CONTEUDO, **SEMPRE** de acordo com a sigla do item 1 e de acordo com as orientações informadas em 
        PASSOS2 a), b), c) ou d) abaixo para o documento fiscal.       
        
        2.1 - Para esses significados, considerar que **NUNCA** deverão ser utilizados os campos do CONTEUDO
        2.2 - Para cada significado **SEMPRE** perguntar. Esse significado já existe ? **CASO SIM, ELIMINAR ESSE SIGNIFICADO**.
        
        3 - Para cada significado do item 2, **SEMPRE** identificar o valor associado em CONTEUDO, e executar os passos 3.1 e 3.2
        3.1 - O valor **NUNCA** deve ser igual ao nome do campo, se for, retornar para o passo 3.
        3.2 - Utilzando como referência REFERENCIA. O valor é adequado para o significado ? Caso não, retornar para o item 3. 
                              
        4 - Baseados nos campos do item 2 e na sigla do item 1. Qual é a versão desse documento fiscal ? Caso não encontre, procurar na legislação. 
        Responda somente com o número da versão. 
        5 - Baseados nos campos do item 2 e na sigla do item 1. Qual é o número do modelo desse documento fiscal ? Caso não encontre, procurar na legislação. 
        Responda somente com o número do modelo.
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
        
    
    elif tipo in ['text/plain','text/csv']: # DEVIDO A LLM NÃO ENTENDER BEM O CSV, TEVE QUE SE CRIAR UM PROMPT ESPECÍFICO.
                                            # NÃO HAVERÁ ESTOURO DE CONTEXTO, PELO FATO DE TRABALHAR SOMENTE COM AS COLUNAS
                                            # E NÃO COM OS DADOS.
                
        class DocFiscal2(BaseModel):
            tipo: str = Field(description="Responda apenas com a sigla do tipo")
            versao: str = Field(description="versão. Se nulo, verificar se não se aplica, se sim, responder com N/A, se não, continuar buscando a versão até encontrar")
            modelo: str = Field(description="modelo. Se nulo, verificar se não se aplica, se sim, responder com N/A, se não, continuar buscando a versão até encontrar")
            sigcampos: list = Field(description="[{{campo:<campo>,significado:<significado>}}]")           
                
        parseador = JsonOutputParser(pydantic_object=DocFiscal2) 
        
        template = """Aja como um analista de contabilidade, e utilize REFERENCIA para executar os ITENS 1, 2, 3 e 4 no contexto dos documentos 
        fiscais brasileiros 
        
        REFERENCIA:
        a) Nota Técnica  
        b) Manual de Orientação do Contribuinte (MOC) 
        c) Schemas XSD referente ao documento fiscal
        d) Sobre impostos, consultar o item b) e c)
        
                            
        ##########################################
        ITENS:
        1 - Baseado no significado para cada um dos campos {colunas_df}. Qual é a sigla do tipo do documento fiscal.
        2 - Baseado no significado para cada um dos campos {colunas_df} e na sigla do item 1. Qual é a versão desse documento fiscal ? Caso não encontre, procurar na legislação. Responda somente com o número da versão.
        3 - Baseado no significado para cada um dos campos {colunas_df} e na sigla do item 1. Qual é o número do modelo desse documento fiscal ? Caso não encontre, procurar na legislação. Responda somente com o número do modelo.
        4 - Significado para cada um dos nomes dos campos {colunas_df} em poucas palavras, sem repetição e, quando possível, 
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
        df = texto
        
        resposta = chain.invoke(input={"colunas_df":list(df.columns.values)}) 
          
        
    return resposta

def llm_gera_query(llm,engine,pergunta):

        template_query = """Como agente especialista em documentos fiscais brasileiros e banco de dados, seu objetivo é gerar a query SQL para responder a pergunta {pergunta}.
        Para isso, você deve considerar os PASSOS e o CONTEXTO abaixo.
        
        - **NUNCA** fazer comentários
        - **NUNCA** fazer questionamentos 
        
        PASSOS:
        ########################################################################################################
        1 - Entender o significado das colunas "{colunas}" do documento, por meio do CONTEXTO informado abaixo 
        2 - O nome da tabela é "arquivo".
        3 - Se o documento não possuir uma coluna, aonde o significado seja capaz de responder a pergunta, responder com null 
        ########################################################################################################
        
        CONTEXTO:
        a) Nota Técnica  
        b) Manual de Orientação do Contribuinte (MOC) 
        c) Schemas XSD referentes ao documento fiscal. Para impostos, identifique quais estão no documentos fiscal por meio das tags.
        d) Para saber as colunas referentes aos impostos a serem considerados para o documento fiscal, consultar os itens b) e c). Se os impostos tiverem 
        valor nulo ou zero, exibir como zero.
        
        
        {formatacao_saida}"""

        # FORMATANDO A SAÍDA DA LLM COM JsonOutputParser
        class Query(BaseModel):
            query: str = Field(description='Esta é a query com DISTINCT, sem UNION, com todas as colunas necessárias, aonde o da tabela {nome_arquivo} deve ficar entre "')

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


def obtem_sim_nao(pergunta,df,llm,engine): # AQUI PODE ACONTECER O ESTOURO DE JANELA DE CONTEXT. VAI RESPONDER A PERGUNTA POR MEIO 
                                           # DO PROCEDIMENTO LLM_GERA_QUERY    
    
    print("MÉTODO OBTÉM SIM NÃO")
    
    df.to_sql("arquivo", con=engine, if_exists="replace", index=False)
    
    query = llm_gera_query(llm, engine, pergunta)
    
    dft = read_sql(query,con=engine)
    
    print('\nDataFrame dft\n',dft)       
    
    if dft.empty or dft.values.tolist()[0][0] == '' or dft.values.tolist()[0][0] is None:
        resposta = "Não"
    
    else:
        
        listavalues = dft.values.tolist()[0]
        listacolumns = [str(c).replace('"','') for c in dft.columns.tolist()]
        
        print('listavalues: ',listavalues)
        print('listacolumns: ',listacolumns)
        
        print(any(c in listavalues for c in listacolumns))
        
        if any(c in listavalues for c in listacolumns): 
            resposta = "Não"
    
        else:
            resposta = "Sim"   
    
    return resposta

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

def read_tags_values_xml_file(arquivo, llm):
    
    print("READ TAGS XML...")
    
    conteudo_bytes = arquivo.read()  # ARQUIVO É UM UPLOADEDFILE DO STREAMLIT  
    conteudo = conteudo_bytes.decode('utf-8')
        
    template = """Aja como um analista de contabilidade, e para CONTEUDO, utilize REFERENCIA para executar ITENS no contexto dos documentos 
    fiscais brasileiros   
    
    CONTEUDO:
    {conteudo}
    
    REFERENCIA:
    a) Nota Técnica  
    b) Manual de Orientação do Contribuinte (MOC) 
    c) Schemas XSD referente ao documento fiscal
    d) Sobre impostos, consultar o item b) e c)    
                            
    ##########################################
    ITENS:
    
    Os valores das tags **NUNCA** devem ser alterados, **APENAS** os nomes das tags.
    
    1 - Crie NOVOCONTEUDO, **SEMPRE** substituindo cada nome de tag em CONTEUDO pelo seu significado, utilizando poucas palavras, sem repetição, e quando possível, com a utilização 
    de siglas (Ex: CNPJ, UF, CPF).
    2 - Em NOVOCONTEUDO, **SEMPRE** acrescente ao final de cada nome de tag, o nome de tag da hierarquia superior separado por "_", e assim por diante, para cada nível hierárquico.    
    ###########################################    
        
    """       
    prompt_template = PromptTemplate(
                                        template=template,
                                        input_variables=["conteudo"]#,
                                        #partial_variables={"formatador_saida_ia" : parseador.get_format_instructions()}
                                    )
    
    # CRIANDO A CADEIA DE EXECUÇÃO PARA A LLM
    chain = prompt_template | llm
    
    # INVOCANDO A LLM
        
    resposta1 = chain.invoke(input={"conteudo":conteudo}) 
    resposta = resposta1.content.split('```xml')[1].split('```')[0].strip()
    
    print('\nSaída\n',resposta)
    
    # TRANSFORMANDO O XML EM DATAFRAME
    
    # Carrega o XML
    #tree = ET.parse(arquivo)
    tree = ET.ElementTree(ET.fromstring(resposta))
    print('Tree: ',tree)
    root = tree.getroot()
    print('root: ',root)

    dict_xml = {} # DICIONÁRIO TAG-VALOR
    
    for elem in root.iter():
        #print('elem.tag: ',elem.tag)
        tag_name = elem.tag.split('}')[-1]  # TAGS. Remove o namespace do nome pegando o último elemento [-1]
        tag_value = elem.text.strip() if elem.text else None # VALUES #if elem.text else '' # VALUES
        
        #print('Tag name: ',tag_name, ' Tag value: ', tag_value)
                
        if tag_value: # SE O VALOR NÃO FOR NULO    
            dict_xml[tag_name] = tag_value

    colunas = list(dict_xml.keys())
    valores = list(dict_xml.values())
    print('dict_xml: ',dict_xml)
    sleep(20)
    
    df = DataFrame(data=[valores],columns=colunas)
           
    return df    


def agente2(pergunta,arquivo,engine):

    print('\nExecutando agente 2...')
    
    # INTEGRAÇÃO COM A LLM
    load_dotenv() # CARREGANDO O ARQUIVO COM A API_KEY

    set_llm_cache(InMemoryCache())
    llm = ChatOpenAI( 
        #model="mistralai/mistral-small-3.2-24b-instruct:free",
        #model="mistralai/mistral-small-3.1-24b-instruct:free",
        model="gpt-5-nano",
        #base_url="https://openrouter.ai/api/v1",
        temperature=0,
        cache=True,      
        reasoning_effort="high",        
        api_key=getenv("API_KEY")        
    )
    
    
    ocr = NotaFiscalOCR() # INSTÂNCIA DO MOTOR OCR
    
    tipo = from_buffer(arquivo.getvalue(),mime=True)
    arquivo.seek(0)
    
    print(f"\nArquivo: {arquivo.name}, Tipo MIME detectado: {tipo}")
    
    if tipo not in ['text/plain','text/csv']:        
        
        imagem_proc = ocr.preprocessar_imagem(ocr.carregar_arquivo(arquivo)) # PREPROCESSANDO A IMAGEM, PARA MELHORAR A SUA QUALIDADE.
        texto = ocr.extrair_texto(imagem_proc)
        
        print("\nTexto\n",texto)
        sleep(20)
        
        if texto: # SE NÃO FOR DOCUMENTO FISCAL VAZIO
            
            print('Existe texto')
            
            resposta = consultallmdocfiscal(texto,llm,tipo) # O NOME DAS COLUNAS ESTÁ AQUI 
            
            campos = resposta['campos'] 
            
            lista_dictregistros = resposta['registros']        
            listacampos = [dict['significado'] for dict in lista_dictregistros] # AQUI ESTÁ A LISTA DE CAMPOS APÓS ANÁLISE
            
            listavalores = [dict['valor'] for dict in lista_dictregistros]
                        
            df = DataFrame([listavalores], columns=listacampos)                                       
        
        else: # CRIA UM DATAFRAME VAZIO
            df = DataFrame()
                        
              
    elif tipo in ['text/plain','text/csv']: 
                
        if arquivo.name.endswith('.xml'):
            df = read_tags_values_xml_file(arquivo,llm)
        
        else:
            df = read_csv(arquivo)
        
        if not df.empty: # SE NÃO FOR DOCUMENTO FISCAL VAZIO
            
            campos = df.columns.tolist() # CAMPOS DO PRÓPRIO DOCUMENTO FISCAL 
            
            resposta = consultallmdocfiscal(df,llm,tipo) # O NOME DAS COLUNAS ESTÁ AQUI 
            
            lista_dictsigcampos = resposta['sigcampos']        
            listacampos = [dict['significado'] for dict in lista_dictsigcampos] # AQUI ESTÁ A LISTA DE CAMPOS APÓS ANÁLISE
                
            listavalores = df.values.tolist()
                                        
            df = DataFrame(listavalores, columns=listacampos) # NOVO DATAFRAME COM OS SIGNIFICADOS DAS COLUNAS
            
                            
    if not df.empty:               
               
        df['TIPO'] = resposta['tipo']
        df['MODELO_DOC'] = resposta['modelo']        
        df['VERSÃO_DOC'] = resposta['versao']    
        df['ARQUIVO'] = arquivo.name        
                
        dfdocfiscal = DataFrame({'TIPO':[df['TIPO'].loc[0]],'MODELO':[df['MODELO_DOC'].loc[0]],'VERSÃO':[df['VERSÃO_DOC'].loc[0]]})
        
        dfcampos = DataFrame({'CAMPOS DO DOC FISCAL':[campos]}) # LISTA COM UMA LISTA DE CAMPOS    
        
        resposta = obtem_sim_nao(pergunta,df,llm,engine) # AQUI PODE ACONTECER O ESTOURO DE JANELA DE CONTEXTO   
        
    else:        
        resposta = "Não"
                            
        
    if resposta == "Sim":  # PERSISTINDO OS DADOS NO BANCO DE DADOS        
       
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
    st.markdown('<a href="https://drive.google.com/open?id=1SR3gJB0NWX_JGMb_QOQmagRtbUeOWVRi&usp=drive_fs" target="_blank">Arquivo XML </a>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader("📂 Envie um documento fiscal no formato CSV, PDF, PNG ou XML", type=["csv","pdf","png","xml"])  
           
    pergunta = st.text_input("📝 Digite sua pergunta sobre os dados:")
    
    if st.button("🔍 Consultar"):
        if not uploaded_file:
            st.error("Você precisa fazer o upload de um arquivo CSV, PDF, imagem PNG ou XML.")
            
        elif not pergunta.strip():
            st.error("Digite uma pergunta válida.")
            
        else:
            with st.spinner("Analisando os dados com IA..."):
                #try:
                    resultado_df = agente3(pergunta, uploaded_file,engine) # RESPOSTA E INTERAÇÃO COM O USUÁRIO

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
    
    if not exists('nfs_data.db'): # CRIAÇÃO DO BANCO DE DADOS PARA A PRIMEIRA EXECUÇÃO
        print('\nCriando o banco de dados nfs_data...')     
    
    DATABASE_URL = "sqlite:///nfs_data.db" 
    engine = create_engine(DATABASE_URL,echo=True)        
          
    # INICIALIZAÇÃO DO AGENTE
    agente1(engine)  # Executa a função que inicia o agente
     

# EXPORTAR ESSE NOTEBOOK PARA UM SCRIPT PYTHON ANTES
#!streamlit run agente_nfs.py --server.port 8000

