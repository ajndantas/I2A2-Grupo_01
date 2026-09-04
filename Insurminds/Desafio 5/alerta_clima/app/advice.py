from app.llm import LLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.globals import set_debug
from functools import lru_cache
from typing import overload
import json

@lru_cache
def getLLM():
    return LLM().getLLM()

set_debug(True)

class Advice:

    @overload
    def __init__(self, description: list): ...        
    @overload
    def __init__(self, description: str): ...    
    def __init__(self, description):

        self.llm = LLM().getLLM()
        self.parser = StrOutputParser()

        if isinstance(description, str):

            template = """
                            Aja como um especialista de meteorologia e dê um conselho para o clima descrito como {description}
    
                            ## SAÍDA
                            NUNCA fornecer um JSON incorreto

                            {formatação de saída}                        
                    """ 

            self.prompt_template = PromptTemplate(
                template=template,
                input_variables=["description"],
                partial_variables={"formatação de saída": "{'conselho': 'Conselho'}"}                
            ) 

            qa_chain = self.prompt_template | self.llm | self.parser
            self.__qa_chain = json.loads(qa_chain.invoke({"description": description}))['conselho']
                          
        elif isinstance(description, list):

            template = """
                            Aja como um especialista de meteorologia e dê um conselho para cada um dos climas descritos na lista {descriptionlist}
    
                            ## SAÍDA
                            NUNCA fornecer um JSON incorreto

                            {formatação de saída}                        
                    """
            dictionary = {}
            
            for desc in description:
                dictionary[desc] = 'conselho'                       

            self.prompt_template = PromptTemplate(
                template=template,
                input_variables=["description"],
                partial_variables={"formatação de saída": f"{{'conselhos': {dictionary}}}" }                
            )        

            qa_chain = self.prompt_template | self.llm | self.parser
            self.__qa_chain = json.loads(qa_chain.invoke({"descriptionlist": description}))['conselhos']


    def getAdvice(self) -> str:
        return self.__qa_chain

## TESTE
if __name__ == "__main__":

    descriptionlist = ["Chuva com granizo","Chuva com neve","Chuva com neve e granizo"]

    advice = Advice(descriptionlist)

    print(advice.getAdvice())