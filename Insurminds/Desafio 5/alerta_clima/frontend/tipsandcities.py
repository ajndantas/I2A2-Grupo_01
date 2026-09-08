from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.modelos.tipsandcities import Tips as TipsModel, TipsandCities, City
from app.llm import LLM
from typing import List
import json
from fastapi import HTTPException

class Tips:

    def __init__(self):             

        template = """
                        Aja como um especialista de meteorologia e clima que fala Português do Brasil, e siga PASSOS abaixo:

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
                                                
                        ## SAÍDA
                        {formatação de saída}                     
                        
                   """
        parser = JsonOutputParser(pydantic_object=TipsandCities)

        prompt_template = PromptTemplate(
            template=template,
            partial_variables={"formatação de saída": parser.get_format_instructions()},
        )
        
        qa_chain = prompt_template | LLM.getLLM() | parser        
        
        try:
            json_qa_chain = json.dumps(qa_chain.invoke({}), ensure_ascii=False)            

        except Exception:
            raise HTTPException(status_code=500, detail="Nao foi possivel obter as dicas. Reinicie a aplicação")
        
            
        self.__qa_chain = json.loads(json_qa_chain)
        
    def getTips(self) -> TipsModel:
       self.__tips = self.__qa_chain['tips']
       return self.__tips

class Cities:

    def __init__(self):             

        template = """
                        Aja como um especialista de meteorologia e clima que fala Português do Brasil, e siga PASSOS abaixo:

                        ## PASSOS:
                        1. Forneça o nome de 18 cidades, as respectivas siglas de seus 
                        estados, caso não tenha estado, que seja do seu país, e seus tipos, se brasileira ou global (não brasileira). 
                        2. 10 cidades brasileiras e 8 globais.
                                                
                        ## SAÍDA
                        {formatação de saída}                     
                        
                   """
        parser = JsonOutputParser(pydantic_object=TipsandCities)

        prompt_template = PromptTemplate(
            template=template,
            partial_variables={"formatação de saída": parser.get_format_instructions()},
        )
        
        qa_chain = prompt_template | LLM.getLLM() | parser        
        
        try:
            json_qa_chain = json.dumps(qa_chain.invoke({}), ensure_ascii=False)            

        except Exception:
            raise HTTPException(status_code=500, detail="Nao foi possivel obter as cidades. Reinicie a aplicação")
        
            
        self.__qa_chain = json.loads(json_qa_chain)
        
    def getCities(self) -> List[City]:
        self.__cities = self.__qa_chain['cities']
        return self.__cities
    


# TESTE
if __name__ == "__main__":
    tips = Tips()
    cities = Cities()
    
    cities = cities.getCities()
    tips = tips.getTips()

    print("Cities: \n", cities)
    print("Tips: \n", tips)

    