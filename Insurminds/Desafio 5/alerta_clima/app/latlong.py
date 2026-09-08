from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.globals import set_llm_cache, set_debug
from langchain_core.caches import InMemoryCache
from langchain_core.exceptions import OutputParserException
from os import getenv
from dotenv import load_dotenv


load_dotenv()
set_debug(True)

class LatLongModel(BaseModel):
    cidade: str = Field(description="O nome da cidade")
    latitude: float = Field(description="Latitude da cidade")
    longitude: float = Field(description="Longitude da cidade")


class LatLong:
    def __init__(self):

        set_llm_cache(InMemoryCache())

        self.llm = ChatOpenAI(
                                model_name="openrouter/free",
                                base_url="https://openrouter.ai/api/v1",
                                api_key=getenv("API_KEY_OPENROUTER"), 
                                temperature=0
                              )

        
        template = """
                        Qual é a latitude e a longitude da cidade {cidade} ?

                        ## SAÍDA
                        {formatação de saída}           
                   """
        self.parser = JsonOutputParser(pydantic_object=LatLongModel)        
                
        self.prompt_template = PromptTemplate(
            template=template,
            input_variables=["cidade"],
            partial_variables={"formatação de saída": self.parser.get_format_instructions()},            
        )
        

    def getLatLong(self,city):
        
        qa_chain = self.prompt_template | self.llm | self.parser

        try:
            qa_chain = qa_chain.invoke({"cidade": city})
        except OutputParserException:
            qa_chain = qa_chain.invoke({"cidade": city})        

        return qa_chain


# TESTE
if __name__ == "__main__":
    latlong = LatLong()
    print(latlong.getLatLong("Rio de Janeiro"))