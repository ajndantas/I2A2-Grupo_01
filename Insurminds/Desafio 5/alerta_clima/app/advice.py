from app.llm import LLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.globals import set_debug
from typing import overload
import json
from pydantic import BaseModel, Field

set_debug(True)

class AdviceModel(BaseModel):
   conselho: str = Field(description="O conselho")

class AdviceListModel(BaseModel):
   conselhos: list = Field(description="O dicionario de conselhos. Cada chave corresponde a descrição do clima e o valor corresponde ao respectivo conselho")

   
class Advice:

    @overload
    def __init__(self, description: list): ...        
    @overload
    def __init__(self, description: str): ...    
    def __init__(self, description):

        if isinstance(description, str):

            parser = JsonOutputParser(pydantic_object=AdviceModel)

            template = """
                            Aja como um especialista de meteorologia e dê um conselho para o clima descrito como {description}
    
                            ## SAÍDA
                            {formatação de saída}

                            SEMPRE forneça um JSON de acordo com {formatação de saída}                        
                        """ 

            prompt_template = PromptTemplate(
                template=template,
                input_variables=["description"],
                partial_variables={"formatação de saída": parser.get_format_instructions()}            
            ) 

            qa_chain = prompt_template | LLM.getLLM() | parser

            try:
                json_conselho = qa_chain.invoke({"description": description})
                conselho = json_conselho

            except Exception:
                json_conselho = qa_chain.invoke({"description": description})
                conselho = json_conselho

            self.__conselho = conselho['conselho']
        
                          
        elif isinstance(description, list):

            parser = JsonOutputParser(pydantic_object=AdviceListModel)

            template = """
                            Aja como um especialista de meteorologia e dê um conselho para cada um dos climas descritos na lista {descriptionlist}
    
                            ## SAÍDA
                            NUNCA fornecer um JSON incorreto

                            {formatação de saída}                        
                    """            

            prompt_template = PromptTemplate(
                template=template,
                input_variables=["descriptionlist"],
                partial_variables={"formatação de saída": parser.get_format_instructions()}
            )        

            qa_chain = prompt_template | LLM.getLLM() | parser

            try:
                json_conselhos = qa_chain.invoke({"descriptionlist": description})
                
                conselhos = json.loads(json.dumps(json_conselhos, ensure_ascii=False))
                
            except Exception:                

                json_conselhos = qa_chain.invoke({"descriptionlist": description})
                               
                conselhos = json.loads(json.dumps(json_conselhos, ensure_ascii=False))
                
            self.__conselho = conselhos['conselhos']


    def getAdvice(self) -> str:
        return self.__conselho

## TESTE
if __name__ == "__main__":

    description = ["Chuva com granizo","Chuva com neve","Chuva com neve e granizo"]
    #description = "Chuva com neve e granizo"

    advice = Advice(description)

    print(advice.getAdvice())