from app.llm import LLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.globals import set_debug
from functools import lru_cache
from typing import List, overload
import json

@lru_cache
def getLLM():
    return LLM().getLLM()

set_debug(True)

class Advice:

    @overload
    def __init__(self, description: List[str]): ...        
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
                partial_variables={"formatação de saída": '{conselho: "Conselho"}'}            
            )

        qa_chain = self.prompt_template | self.llm | self.parser
        self.__qa_chain = json.loads(qa_chain.invoke({"description": description}))['conselho']


    def getAdvice(self) -> str:
        return self.__qa_chain

## TESTE
if __name__ == "__main__":

    advice = Advice("Chuva com granizo")

    print(advice.getAdvice())