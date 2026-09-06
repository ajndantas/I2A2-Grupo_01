from app.llm import LLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.globals import set_debug
from functools import lru_cache
from typing import overload
import json
from re import findall, DOTALL
from pydantic import BaseModel, Field

@lru_cache
def getLLM():
    return LLM().getLLM()

set_debug(True)

class AdviceModel(BaseModel):
   conselho: str = Field(description="O conselho")

   
class Advice:

    @overload
    def __init__(self, description: list): ...        
    @overload
    def __init__(self, description: str): ...    
    def __init__(self, description):

        self.llm = LLM().getLLM()        

        if isinstance(description, str):

            self.parser = JsonOutputParser(pydantic_object=AdviceModel)

            template = """
                            Aja como um especialista de meteorologia e dê um conselho para o clima descrito como {description}
    
                            ## SAÍDA
                            {formatação de saída}

                            SEMPRE forneça um JSON de acordo com {formatação de saída}                        
                    """ 

            self.prompt_template = PromptTemplate(
                template=template,
                input_variables=["description"],
                partial_variables={"formatação de saída": self.parser.get_format_instructions()}            
            ) 

            qa_chain = self.prompt_template | self.llm | self.parser

            try:
                json_conselho = qa_chain.invoke({"description": description})
                conselho = json_conselho

            except Exception:
                json_conselho = qa_chain.invoke({"description": description})
                conselho = json_conselho

            self.__conselho = conselho['conselho']
        
                          
        elif isinstance(description, list):

            self.parser = StrOutputParser()

            template = """
                            Aja como um especialista de meteorologia e dê um conselho para cada um dos climas descritos na lista {descriptionlist}
    
                            ## SAÍDA
                            NUNCA fornecer um JSON incorreto

                            {formatação de saída}                        
                    """
             
            dictionary = {desc: "Qual é o conselho ?" for desc in description}

            self.prompt_template = PromptTemplate(
                template=template,
                input_variables=["descriptionlist"],
                partial_variables={"formatação de saída": f'{{"conselhos": {json.dumps(dictionary, ensure_ascii=False)}}}'}                                             
            )        

            qa_chain = self.prompt_template | self.llm | self.parser

            try:
                json_conselho = findall(r"\{.*\}", qa_chain.invoke({"descriptionlist": description}), DOTALL)[0]
                
                conselho = json.loads(json_conselho)
                
            except Exception:
                json_conselho = findall(r"\{.*\}", qa_chain.invoke({"descriptionlist": description}), DOTALL)[0]
                               
                conselho = json.loads(json_conselho)
                
            self.__conselho = conselho['conselhos']


    def getAdvice(self) -> str:
        return self.__conselho

## TESTE
if __name__ == "__main__":

    description = ["Chuva com granizo","Chuva com neve","Chuva com neve e granizo"]
    #description = "Chuva com neve e granizo"

    advice = Advice(description)

    print(advice.getAdvice())