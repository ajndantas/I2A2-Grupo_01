# UPGRADE DO PIP PARA VERSÃO 25.1.1 - PASSO 1

#!python -m pip install --upgrade pip

#%pip install -qqqr requirements.txt

# [markdown]
# ### IMPORTS

from os import getenv, mkdir, listdir
from io import BytesIO
from shutil import rmtree
from os.path import basename,exists
from pathlib import Path
from zipfile import ZipFile
from re import search
from pandas import read_csv, read_sql
import sqlalchemy as sqlalc
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI

class SemArquivoCabecalho(Exception):
    pass

class SemArquivoItens(Exception):
    pass

class SemArquivoZip(Exception):
    pass

class SemResposta(Exception):
    pass

# [markdown]
# ### FUNÇÃO QUE DESCOMPACTA ARQUIVOS<br/>
# <ul><li>VERIFICA SE EXISTE OS ARQUIVOS DE CABEÇALHO E ITENS</li></ul>
# <ul><li>CASO ALGUM DELES NÃO EXISTA, É LANÇADA UMA EXCEÇÃO (Raise)</li></ul>
# <ul><li>É OBRIGATÓRIO QUE OS ARQUIVOS SEJAM CSVs E TENHAM "CABECALHO" E "ITENS" NO NOME</li></ul>

def unzip(arquivo,diretorio):


    diretorio_destino = Path(f'{diretorio}') #\\arquivos_descompactados'
    subpasta = 'arquivos descompactados'
    diretorio_destino = diretorio_destino / subpasta

    #print('Arquivos em: ',listdir(f'{diretorio}\\'))

    if basename(diretorio_destino) in listdir(f'{diretorio}'):
        rmtree(diretorio_destino)

    mkdir(f'{diretorio_destino}')

    #print(f'Diretório {diretorio_destino} criado com sucesso!')


    #for f in arquivos_zipados:
    with ZipFile(arquivo, 'r') as zip_ref:
        
        #zip_ref.extractall(f'{diretorio_destino}')
         
        arquivos = zip_ref.namelist()
        #arquivos = [f'{Path(diretorio_destino) / x}' for x in listdir(f'{diretorio_destino}')]

        print(f'Arquivos descompactados: {arquivos}')
           
        # Check if any pattern matches
        arquivocabecalhoencontrado = any(search(r'.*[Cc]abecalho.csv$', arquivo) for arquivo in arquivos)
        arquivoitensencontrado = any(search(r'.*[Ii]tens.csv$', arquivo) for arquivo in arquivos)

        if arquivocabecalhoencontrado == False:
            return "SemArquivoCabecalho"

        elif arquivoitensencontrado == False:
            return "SemArquivoItens"
        
        lista_arquivos = []
        
        for arquivo in arquivos:
            if (search(r'.*[Cc]abecalho.csv$', arquivo) is not None):
                with zip_ref.open(arquivo) as myfile:
                    # The resulting BytesIO object can be used anywhere a file-like object is expected, 
                    # but it operates entirely in memory, making it useful for temporary processing of 
                    # binary data (such as images, PDFs, or ZIP files) without writing to disk. 
                    # A common use case is when you need to manipulate or pass file data to 
                    # APIs or libraries that expect a file-like object(Método read_csv do pandas), but you want to avoid 
                    # filesystem I/O.
                    lista_arquivos.append({'cabecalho': BytesIO(myfile.read()),'nome_arquivo': arquivo})
                    
            elif (search(r'.*[Ii]tens.csv$', arquivo) is not None):
                with zip_ref.open(arquivo) as myfile:
                    lista_arquivos.append({'itens': BytesIO(myfile.read()),'nome_arquivo': arquivo})
                             
        arquivos = lista_arquivos
        
    return arquivos


# [markdown]
# ### <b>AGENTE 1: Aquisição de Documentos</b>
# <b>Responsabilidade:</b> Obter e pré-processar documentos fiscais<br/><br/>
# <b>Funcionalidades:</b>
# <ul><li>Interface para upload manual de arquivos (PDF, imagens)</li></ul>
# <ul><li>Integração com APIs de órgãos governamentais (SEFAZ)</li></ul>
# <ul><li>Validação inicial de formato e integridade dos documentos</li></ul>
# <ul><li>Organização e catalogação dos arquivos recebidos</li></ul>

def agente1(pergunta,engine, arquivo,llm):

    print('\nExecutando agente 1...')

    # VALIDAÇÃO DE INTEGRIDADE -> UMA FORMA DE GARANTIR QUE OS ARQUIVOS ESTÃO NO FORMATO ZIP
    #arquivos_zipados = lista_arquivos_zipados(diretorio)

    #if arquivos_zipados == "SemArquivoZip":
    #    return "SemArquivoZip"

    # VALIDAÇÃO DE INTEGRIDADE -> UMA FORMA DE GARANTIR QUE O ARQUIVO DE CABECALHO E O DE ITENS EXISTEM
    diretorio = '.'
    arquivos = unzip(arquivo,diretorio)

    if arquivos == "SemArquivoCabecalho":
        return "SemArquivoCabecalho"
    elif arquivos == "SemArquivoItens":
        return "SemArquivoItens"

    # VALIDAÇÃO DE INTEGRIDADE -> IMPLEMENTAR PARA DETERMINAR SE O ARQUIVO REALMENTE É UM TIPO ZIP. NÃO FAZER PELA EXTENSÃO
    # FAZER

    """
        Utilizando a LLM para identificar se os campos e resigstros da base de documentos, é capaz de responder a pergunta
        do usuário.

        Se sim, o arquivo é persistido no banco de dados, caso contrário, o arquivo é descartado.
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

    # CATALOGANDO OS ARQUIVOS ZIPADOS NO BD
    j=0

    inspector = sqlalc.inspect(engine)

    #print('valor de j: ',j)
    for f in arquivos:

        # SERÁ CRIADO UM DATAFRAME PARA CADA ARQUIVO
        if f.get('cabecalho') is not None:
            dfcabecalho = read_csv(f.get('cabecalho'))

            # INSERINDO COLUNA COM O NOME DO ARQUIVO NO DATAFRAME
            dfcabecalho['ARQUIVO'] = f.get('nome_arquivo')
            df = dfcabecalho

            #print('Dataframe de cabeçalho: ',df)

            # INVOCANDO A LLM
            resposta = chain.invoke(input={"pergunta":pergunta, "df": df})['resposta']

            if resposta == 'Sim':
                j+=1

                print('Sim para o arquivo: ',f.get('nome_arquivo'))

                # PRECISA VERIFICAR SE A TABELA JÁ EXISTE NO BANCO DE DADOS ANTES DE LER
                if 'NFCABECALHO' in inspector.get_table_names():
                    dftable = read_sql('NFCABECALHO', con=engine)

                    #print('dftable NFCABECALHO\n',dftable)

                    # CUIDANDO DE DUPLICIDADE
                    df = df[~df['CHAVE DE ACESSO'].isin(dftable['CHAVE DE ACESSO'])]

                # INSERINDO NO BANCO DE DADOS
                df.to_sql(name='NFCABECALHO', con=engine, if_exists='append', index=False)

                continue

            else:
                continue

        if f.get('itens') is not None:
            dfitens = read_csv(f.get('itens'))

            # INSERINDO COLUNA COM O NOME DO ARQUIVO NO DATAFRAME
            dfitens['ARQUIVO'] = f.get('nome_arquivo')
            df = dfitens

            #print('Dataframe de itens: ',df)

            # INVOCANDO A LLM
            resposta = chain.invoke(input={"pergunta":pergunta, "df": df})['resposta']

            if resposta == 'Sim':
                j+=1

                print('Sim para o arquivo: ',f.get('nome_arquivo'))

                 # PRECISA VERIFICAR SE A TABELA JÁ EXISTE NO BANCO DE DADOS ANTES DE LER
                if 'NFITENS' in inspector.get_table_names():
                    dftable = read_sql('NFITENS', con=engine)

                    #print('dftable NFINTENS\n',dftable)

                    # CUIDANDO DE DUPLICIDADE
                    df = df[~df['CHAVE DE ACESSO'].isin(dftable['CHAVE DE ACESSO'])]

                # INSERINDO NO BANCO DE DADOS
                df.to_sql(name='NFITENS', con=engine, if_exists='append', index=False)

                continue

            else:
                continue

    if j == 0:
        return "Não"

    else:
        return "Sim"

# [markdown]
# ### <b>AGENTE 2: Extração e Aprendizado</b>
# <b>Responsabilidade:</b> Processar documentos e extrair dados relevantes<br/><br/>
# <b>Funcionalidades:</b>
# <ul><li>OCR avançado para digitalização de documentos</li></ul>
# <ul><li>NLP para identificação e extração de campos específicos</li></ul>
# <ul><li>IA para adaptação a novos layouts</li></ul>
# <ul><li>Validação cruzada de dados extraídos</li></ul>

def agente2(pergunta,llm,engine):

    print('\nExecutando agente 2...')

    # FORMATANDO A SAÍDA DA LLM COM JsonOutputParser
    class Query(BaseModel):
        query: str = Field(description='Esta é a query com DISTINCT e o nome de cada colunas entre "')

    parseador = JsonOutputParser(pydantic_object=Query)

    # CRIANDO O PROMPT PARA A LLM COM A SAIDA FORMATADA
    template = """Qual query deve ser executada na tabela NFCABECALHO com as colunas {colunas_tab_cabecalho} ou tabela NFITENS com as colunas {colunas_tab_itens} para responder
    a pergunta {pergunta}? {formatacao_saida}"""

    prompt_template = PromptTemplate(
                                        template=template,
                                        input_variables=["pergunta","colunas_tab_cabecalho","colunas_tab_itens"],
                                        partial_variables={"formatacao_saida" : parseador.get_format_instructions()}
                                    )

    # CRIANDO A CADEIA DE EXECUÇÃO PARA A LLM
    chain = prompt_template | llm | parseador

    with engine.connect() as con:
        query1 = sqlalc.text('PRAGMA table_info(NFCABECALHO)')
        rs = con.execute(query1)
        rows = rs.fetchall()
        colunas_query1 = sorted([col[1] for col in rows])
        #print('Colunas query1: ', colunas_query1)

        query2 = sqlalc.text('PRAGMA table_info(NFITENS)')
        rs = con.execute(query2)
        rows = rs.fetchall()
        colunas_query2 = sorted([col[1] for col in rows])
        #print('Colunas query2: ', colunas_query2)


    query = chain.invoke(input={"pergunta":pergunta, "colunas_tab_cabecalho":colunas_query1,"colunas_tab_itens":colunas_query2})['query']

    print('\nQuery: ',query)

    resposta = query

    return resposta

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
        model="gemini-2.0-flash",  # ou "gemini-2.0-pro"
        temperature=0.5,
        google_api_key=getenv("GOOGLE_API_KEY")
    )


    try:
            print('\nExecutando agente 3...')

            print('\nPergunta: ',pergunta)

            resposta = agente1(pergunta,engine,arquivo,llm) # A ENGINE NÃO É FECHADA AUTOMATICAMENTE, APENAS AS CONEXÕES QUANDO USADAS COM WITH

            if resposta == "Sim":
                query = agente2(pergunta,llm,engine)

                # # OBTENÇÃO DO RESULTADO DA QUERY
                with engine.connect() as con:
                        df = read_sql(query, con)
                        resposta = df
                        print(f'\nResposta\n,{resposta}')


            elif resposta == "Não":
                    raise SemResposta

            # elif resposta == "SemArquivoZip":
            #     raise SemArquivoZip

            elif resposta == "SemArquivoCabecalho":
                    raise SemArquivoCabecalho

            elif resposta == "SemArquivoItens":
                    raise SemArquivoItens


    # EXECUÇÃO DAS EXCEÇÕES
    except SemArquivoCabecalho:
            resposta = "SemArquivoCabecalho"

    except SemArquivoItens:
            resposta = "SemArquivoItens"

    # except SemArquivoZip:
    #     caminho_absoluto = abspath(diretorio)
    #     print(f'\nNão há arquivos zipados no diretório {caminho_absoluto}!\n')

    except SemResposta:
            resposta = "SemResposta"


    return resposta

# [markdown]
# ### <b>TESTANDO</b>

if __name__ == "__main__":

     #arquivo = ".\\202401_NFS - new.zip"  # Diretório onde os arquivos zipados estão localizados
     
     arquivo = ".\\202401_NFS.zip"  # Diretório onde os arquivos zipados estão localizados
     
#     # EXEMPLOS DE PERGUNTA PARA TESTE. ELAS DEVEM SER OBTIDAS DO FRONTEND
     pergunta = "Qual é a chave de acesso da nota 3510129 ?"
     pergunta = "Quem descobriu o Brasil ?"
     pergunta = "Qual é a descrição dos serviços de nf com número 2525 ?"
     pergunta = "Qual é a descrição dos serviços e a natureza da operação da nf com número 2525 ?"

     resposta = agente3(pergunta, arquivo)  # Chama a função principal com a pergunta e o diretório
     print('\nResposta: \n',resposta)


