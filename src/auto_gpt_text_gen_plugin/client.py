import requests
import os
from colorama import Fore, Style
from autogpt.logs import logger

    
class Client:
    def __init__(self):
        self.base_url = os.environ.get('LOCAL_LLM_BASE_URL', "http://127.0.0.1:5000/")
        logger.debug(
            f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Using base url {self.base_url}"
        )
        # self.headers = {
        #     "api_key": self.api_key 
        # }

    def create_chat_completion(self, messages, temperature, max_tokens):
        logger.debug(
            f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Creating chat completion with messages {messages}\n"
            f" and temperature {temperature}\n"
            f" and max_tokens {max_tokens}"
        )
        if max_tokens is None:
            max_tokens=400
        if float(temperature)==0.0:
            temperature=0.01
        request = {'prompt': str(messages),'temperature': float(temperature), 'max_tokens': int(max_tokens)}

        response = requests.post(self.base_url+'/api/v1/generate', json=request)
        
        if response.status_code == 200:
            logger.debug(
                f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Got response {response.json()}"
            )
            resp=response.json()
            return resp['results'][0]['text']
        else:
            logger.debug(
                f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET}\n"
                f"{Fore.RED}Error: Response status code {response.status_code}{Fore.RESET}"
            )
            return "Error: " + response.text


    def get_embedding(self,text):
        logger.debug(
            f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Getting embedding for text {text}"
        )
        request = {'text':str(text)}

        response = requests.post(self.base_url+'/api/v1/get-embeddings', json=request)
        
        if response.status_code == 200:
            logger.debug(
                f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Got response {response.json()}"
            )
            return response.json()['results'][0]['embeddings']
        else:
            logger.debug(
                f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET}\n"
                f"{Fore.RED}Error: Response status code {response.status_code}{Fore.RESET}"
            )
            return ["Error"]

