from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from os import getenv
from langchain_core.globals import set_debug
from functools import lru_cache

set_debug(True)

load_dotenv()

class LLM:

    @classmethod   
    @lru_cache
    def getLLM(cls):               

        llm = ChatOpenAI(
                                model_name="openrouter/free",
                                base_url="https://openrouter.ai/api/v1",

                                #model_name="gpt-5.6-luna",
                                #model_name="gpt-5.4-mini", 
                                #api_key=getenv("API_KEY"),
                                api_key=getenv("API_KEY_OPENROUTER"),
                                cache=False,
                                temperature=0.5,
                                #reasoning_effort="high",                            
                        ) 

        
        return llm    


if __name__ == "__main__":
    
    LLM.getLLM()
    