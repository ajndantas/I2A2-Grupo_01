from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from os import getenv
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.globals import set_debug, set_llm_cache
from langchain_core.exceptions import OutputParserException
from langchain_core.caches import InMemoryCache

set_debug(True)

load_dotenv()

class LatLongModel(BaseModel):
    cidade: str = Field(description="O nome da cidade")
    latitude: float = Field(description="Latitude da cidade")
    longitude: float = Field(description="Longitude da cidade")

class LatLong:
    def __init__(self):

        self.llm = ChatOpenAI(
                                #model_name="openrouter/free",
                                #base_url="https://openrouter.ai/api/v1",

                                model_name="gpt-5.6-luna", 
                                api_key=getenv("API_KEY"),
                                #api_key=getenv("API_KEY_OPENROUTER"),
                                temperature=0                            
                            )        

        set_llm_cache(InMemoryCache()) # Ativando memória personalizada

        template = """
                        Qual é a latitude e a longitude da cidade {cidade} ?

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