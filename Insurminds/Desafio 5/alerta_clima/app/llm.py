from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from os import getenv
from langchain_core.globals import set_debug, set_llm_cache
from langchain_core.caches import InMemoryCache

set_debug(True)

load_dotenv()

class LLM:

    cache = InMemoryCache()
    set_llm_cache(cache) # Ativando memória personalizada

    def getLLM(self):

        self.llm = ChatOpenAI(
                                model_name="openrouter/free",
                                base_url="https://openrouter.ai/api/v1",

                                #model_name="gpt-5.6-luna",
                                #model_name="gpt-5.4-mini", 
                                #api_key=getenv("API_KEY"),
                                api_key=getenv("API_KEY_OPENROUTER"),
                                #reasoning_effort="high",
                                temperature=0                            
                            )       

        return self.llm

if __name__ == "__main__":

    llm = LLM()
    llm.getLLM()