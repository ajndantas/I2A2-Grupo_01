from datetime import date
from datetime import datetime,timedelta
from pandas import read_excel
from pydantic import BaseModel, Field
from typing import List, Dict, TypedDict
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from langchain_community.cache import InMemoryCache
from langchain.globals import set_debug, set_llm_cache
from os import getenv
from dotenv import load_dotenv

set_debug(True)

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


def agente_dias_uteis(uploaded_file_base_dias, llm, dictintervalo_competencia): # UTILIZADO NO FRONTEND
    
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
    

    for q in resposta:
        if q['sindicato'] and q['estado']:
            d = {'sindicato' : q['sindicato'], 'estado' : q['estado'], 'qtd_dias_uteis' : q['qtd_dias_uteis']} # NUNCA SERÁ NULO
            qtd_dias_uteis.append(d)    
            
        else:
            qtd_dias_uteis = None
            break            
        
    if qtd_dias_uteis != None:        
        
        print('FINAIS DE SEMANA: ', finaisdesemana) 
        print('QTD_DIAS_CORRIDOS', qtd_dias_corridos)
    
        print('QTD_DIAS_UTEIS: ', qtd_dias_uteis)            
            
    return qtd_dias_uteis


def main(uploaded_file_base_dias, dictintervalo_competencia):
    
    load_dotenv() # CARREGANDO O ARQUIVO COM A API_KEY

    set_llm_cache(InMemoryCache())
        
    llm = ChatOpenAI(                    
            model="microsoft/mai-ds-r1:free",
            base_url="https://openrouter.ai/api/v1",
            temperature=0,
            cache=True,
            reasoning_effort="high",
            api_key=getenv("API_KEY")                                  
    )
    
    return agente_dias_uteis(uploaded_file_base_dias, llm, dictintervalo_competencia)