from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from os import getenv
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.globals import set_debug, set_llm_cache
from langchain_core.exceptions import OutputParserException
from langchain_core.caches import InMemoryCache
from typing import List

set_debug(True)

load_dotenv()

class Tips(BaseModel):
    temp: List[str] = Field(description="lista de 5 dicas relacionadas a variação de temperatura")
    rain: List[str] = Field(description="lista de 5 dicas relacionadas a chuva")
    wind: List[str] = Field(description="lista de 5 dicas relacionadas a rajadas de vento")
    humidity: List[str] = Field(description="lista de 5 dicas relacionadas a umidade relativa")
    eye: List[str] = Field(description="lista de 5 dicas relacionadas a saúde ocular")
    
class Cities(BaseModel):
    brcities: List[str] = Field(description="lista das cidades brasileiras. Primeira palavra e a última em maiuscula")
    worldcities: List[str] = Field(description="lista das cidades do mundo. Primeira palavra e a última em maiuscula")


class TipsCities():
    def __init__(self):

        llm = ChatOpenAI(
                                #model_name="openrouter/free",
                                #base_url="https://openrouter.ai/api/v1",

                                model_name="gpt-5.6-luna", 
                                api_key=getenv("API_KEY"),
                                #api_key=getenv("API_KEY_OPENROUTER"),
                                temperature=0                            
                         )        

        set_llm_cache(InMemoryCache()) # Ativando memória personalizada

        template = """
                        Aja como um especialistas de meteorologia e clima. e siga PASSOS abaixo:

                        PASSOS:
                        ----------------------------------------------------------------------------
                        1. Forneça dicas relacionadas a variação de temperatura, 
                        2. Forneça dicas relacionadas a chuva, 
                        3. Forneça dicas relacionadas a rajadas de vento, 
                        4. Forneça dicas relacionadas a umidade relativa e 
                        5. Forneça dicas relacionadas a saude ocular.
                        6. Forneça 5 cidades, aonde o somatório das quantidades é 7, sendo que a 
                        maior quantidade deve ser das principais cidades brasileiras, e a menor, 
                        das principais cidades do mundo.
                        ----------------------------------------------------------------------------

                        SAÍDA
                        ----------------------------------------------------------------------------
                        {formatação de saída}
                        ----------------------------------------------------------------------------
                   """
        parser = JsonOutputParser(pydantic_object=TipsCitiesModel)        
                
        prompt_template = PromptTemplate(
            template=template,
            partial_variables={"formatação de saída": parser.get_format_instructions()},            
        )
        
        self.llm = llm
        self.prompt_template = prompt_template
        self.parser = parser    

    def getCities(self):

        try:
            qa_chain = self.prompt_template | self.llm | self.parser
            qa_chain = qa_chain.invoke()

        except OutputParserException: 
            qa_chain = self.prompt_template | self.llm | self.parser
            qa_chain = qa_chain.invoke()

        finally:
            return qa_chain['result']


# TESTE
if __name__ == "__main__":
    tipscities = TipsCities().getTips()
    