import json
import os
import re
import requests
from monolithic_prompt import MonolithicPrompt
from colorama import Fore, Style
from autogpt.logs import logger

    
class Client:
    def __init__(self):

        # Load environment variables
        self.base_url = os.environ.get('LOCAL_LLM_BASE_URL', "http://127.0.0.1:5000/")
        self.prompt_profile = os.environ.get('LOCAL_LLM_PROMPT_PROFILE', '')
        self.prompt_type = self.load_prompt_type()
        self.prompt_manager = MonolithicPrompt(self.prompt_profile)

        logger.debug(
            f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Using base url {self.base_url}"
        )
        # self.headers = {
        #     "api_key": self.api_key 
        # }


    def load_prompt_type(self) -> str:
        """Load the prompt type from the defined file."""

        try:
            with open(self.prompt_profile, 'r') as f:
                prompt_profile_json = json.load(f)
                return prompt_profile_json['template_type']
        except:
            return "monolithic"
        

    def extract_commands(self, message = '') -> str:
        """
        Extract commands from the system prompt
        
        Args:
            message (str): The message to extract commands from. Defaults to ''.
        
        Returns:
            str: The extracted commands as a string.
        """

        try:
            match = re.search(r"(Commands:.*?Resources:)", message, re.DOTALL)
            match = match.group(1).strip()
            return match
        except:
            return ''
        

    def create_chat_completion(self, messages, temperature, max_tokens):
        commands = self.extract_commands(messages[0]['content'])
        messages[0]['content'] = self.prompt_manager.build_prompt_payload(commands)
        logger.debug(
            f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Creating chat completion with messages {messages}\n"
            f" and temperature {temperature}\n"
            f" and max_tokens {max_tokens}"
        )
        if max_tokens is None:
            max_tokens=400
        if float(temperature)==0.0:
            temperature=0.01
        reshaped_messages = self.prompt_manager.reshape_message(messages)
        logger.debug(
            f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Reshaped messages to:\n{reshaped_messages}"
        )
        request = {'prompt': reshaped_messages, 'temperature': float(temperature), 'max_tokens': int(max_tokens)}

        response = requests.post(self.base_url+'/api/v1/generate', json=request)
        
        if response.status_code == 200:
            logger.debug(
                f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Got response {response.json()}"
            )
            response = response.json()
            resp = response['results'][0]['text']
            resp = self.remove_whitespace(resp)
            logger.debug(
                f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Returning response:\n {resp}\n"
                f"(with formatted JSON: \n{resp}\n\n"
            )
            return resp
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

