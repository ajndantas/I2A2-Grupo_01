from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from app.llm import LLM


class LatLongModel(BaseModel):
    cidade: str = Field(description="O nome da cidade")
    latitude: float = Field(description="Latitude da cidade")
    longitude: float = Field(description="Longitude da cidade")

class LatLong:
    def __init__(self):

        self.llm = LLM().getLLM()
        
        template = """
                        Qual é a latitude e a longitude da cidade {cidade} ?

                        ## SAÍDA
                        - NUNCA fornecer um JSON incorreto

                        {formatação de saída}
                        
                   """
        self.parser = JsonOutputParser(pydantic_object=LatLongModel)        
                
        self.prompt_template = PromptTemplate(
            template=template,
            input_variables=["cidade"],
            partial_variables={"formatação de saída": self.parser.get_format_instructions()},            
        )
        

    def getLatLong(self,city):

        try:
            qa_chain = self.prompt_template | self.llm | self.parser
            qa_chain = qa_chain.invoke({"cidade": city})

        except OutputParserException: 
            qa_chain = self.prompt_template | self.llm | self.parser
            qa_chain = qa_chain.invoke({"cidade": city})

        finally:
            return qa_chain


# TESTE
if __name__ == "__main__":
    latlong = LatLong()
    print(latlong.getLatLong("Rio de Janeiro"))