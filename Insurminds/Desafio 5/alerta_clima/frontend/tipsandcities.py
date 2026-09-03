from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.modelos.tipsandcities import Tips, TipsandCities as TipsandCitiesModel, City
from app.llm import LLM
from typing import List

class TipsandCities:
    def __init__(self):

        llm = LLM().getLLM() 
        
        template = """
                        Aja como um especialista de meteorologia e clima. e siga PASSOS abaixo:

                        ## PASSOS:
                        1. Forneça 3 dicas do tipo variação de temperatura no contexto de clima,
                        2. Forneça 3 dicas do tipo tempestades, 
                        3. Forneça 3 dicas do tipo chuva, 
                        4. Forneça 3 dicas do tipo rajadas de vento, 
                        5. Forneça 3 dicas do tipo umidade relativa.
                        6. Forneça 3 dicas do tipo raios ultravioleta
                        7. Forneça 3 dicas do tipo saúde ocular no contexto de clima
                        8. Forneça 3 dicas do tipo neblina
                        9. Forneça 3 dicas do tipo frio no contexto de clima
                        10. Forneça 3 dicas do tipo inundação 
                        11. Forneça o nome de 14 cidades, as respectivas siglas de seus 
                        estados e seus tipos, se brasileira ou global (não brasileira). Caso não tenha estado, que seja do seu país.
                        12. 4 cidades brasileiras e 3 globais.

                        NUNCA repetir TODAS as dicas e nem TODAS as cidades.
                        
                        ## SAÍDA
                        NUNCA fornecer um JSON incorreto

                        {formatação de saída}
                        
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
        
    def getCities(self) -> List[City]:
        
        return self.__qa_chain['cities']
    

    def getTips(self) -> Tips:

       return self.__qa_chain['tips']


# TESTE
if __name__ == "__main__":
    tipsandcities = TipsandCities()
    
    cities = tipsandcities.getCities()
    tips = tipsandcities.getTips()

    print("Cities: \n", cities)
    print("Tips: \n", tips)

    