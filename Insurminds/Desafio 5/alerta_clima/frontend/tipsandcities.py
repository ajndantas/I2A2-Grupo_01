from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from os import getenv
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.globals import set_debug, set_llm_cache
from langchain_core.caches import InMemoryCache
from app.modelos.tipsandcities import TipsandCities as TipsandCitiesModel

set_debug(True)

load_dotenv()

class TipsandCities:
    def __init__(self):

        llm = ChatOpenAI(
                                model_name="openrouter/free",
                                base_url="https://openrouter.ai/api/v1",

                                #model_name="gpt-5.6-luna", 
                                #api_key=getenv("API_KEY"),
                                api_key=getenv("API_KEY_OPENROUTER"),
                                reasoning_effort="high",
                                temperature=0                            
                         )        

        set_llm_cache(InMemoryCache()) # Ativando memória personalizada

        template = """
                        Aja como um especialistas de meteorologia e clima. e siga PASSOS abaixo:

                        PASSOS:
                        ------------------------------------------------------------------------------
                        1. Forneça dicas relacionadas a variação de temperatura,
                        2. Forneça dicas relacionadas a tempestades, 
                        2. Forneça dicas relacionadas a chuva, 
                        3. Forneça dicas relacionadas a rajadas de vento, 
                        4. Forneça dicas relacionadas a umidade relativa.
                        4. Forneça dicas relacionadas a raios ultravioleta
                        5. Forneça dicas relacionadas a saúde ocular
                        6. Forneça dicas relacionadas a neblina
                        7. Forneça dicas relacionadas a frio
                        8. Forneça dicas relacionadas a inundação 
                        9. Forneça o nome de 14 cidades e suas respectivas siglas, sendo que a maior 
                        quantidade deve ser das principais cidades brasileiras, e a menor, das 
                        principais cidades do mundo.

                        NUNCA repetir TODAS as dicas e nem TODAS as cidades.
                        -----------------------------------------------------------------------------

                        SAÍDA
                        -----------------------------------------------------------------------------
                        {formatação de saída}
                        -----------------------------------------------------------------------------
                   """
        parser = JsonOutputParser(pydantic_object=TipsandCitiesModel)       
                
        prompt_template = PromptTemplate(
            template=template,
            partial_variables={"formatação de saída": parser.get_format_instructions()},            
        )        

        qa_chain = prompt_template | llm | parser

        try:
            qa_chain = qa_chain.invoke({})

        except Exception:
            qa_chain = qa_chain.invoke({})        
        
        finally:
            self.__qa_chain = qa_chain
        
    def getCities(self):

        return self.__qa_chain['cities']

    def getTips(self):

       return self.__qa_chain['tips']


# TESTE
if __name__ == "__main__":
    tipsandcities = TipsandCities()
    
    cities = tipsandcities.getCities()
    tips = tipsandcities.getTips()

    print("Cities: \n", cities)
    print("Tips: \n", tips)

    