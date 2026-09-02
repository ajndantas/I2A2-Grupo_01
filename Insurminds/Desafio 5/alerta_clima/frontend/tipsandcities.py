from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.modelos.tipsandcities import TipsandCities as TipsandCitiesModel
from app.llm import LLM

class TipsandCities:
    def __init__(self):

        llm = LLM().getLLM() 
        
        template = """
                        Aja como um especialistas de meteorologia e clima. e siga PASSOS abaixo:

                        PASSOS:
                        ------------------------------------------------------------------------------
                        1. Forneça 3 dicas do tipo variação de temperatura,
                        2. Forneça 3 dicas do tipo tempestades, 
                        3. Forneça 3 dicas do tipo chuva, 
                        4. Forneça 3 dicas do tipo rajadas de vento, 
                        5. Forneça 3 dicas do tipo umidade relativa.
                        6. Forneça 3 dicas do tipo raios ultravioleta
                        7. Forneça 3 dicas do tipo saúde ocular
                        8. Forneça 3 dicas do tipo neblina
                        9. Forneça 3 dicas do tipo frio
                        10. Forneça 3 dicas do tipo inundação 
                        11. Forneça o nome de 14 cidades e as respectivas siglas de seus 
                        estados, sendo que a maior quantidade deve ser das principais cidades 
                        brasileiras, e a menor, das principais cidades do mundo, mas SEMPRE deve
                        haver pelo menos 1 principal cidade do mundo.

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

        return self.__qa_chain['cities_badges']
    

    def getTips(self):

       return self.__qa_chain['tips']


# TESTE
if __name__ == "__main__":
    tipsandcities = TipsandCities()
    
    cities = tipsandcities.getCities()
    tips = tipsandcities.getTips()

    print("Cities: \n", cities)
    print("Tips: \n", tips)

    