import json
import os
import re
import requests
from .default_prompt import DefaultPrompt
from .monolithic_prompt import MonolithicPrompt
from autogpt.logs import logger
from colorama import Fore, Style


class Client:
    """API support for Text Gen WebUI's vanilla API plugin"""

    def __init__(self, base_url, prompt_profile):
        """Constructor"""

        # Initialize the prompt manager
        self.base_url = base_url
        self.prompt_profile = prompt_profile

        # Constants
        self.API_ENDPOINT_GENERATE = '/api/v1/generate'

        # Which prompt manager to use
        if self.prompt_profile is not None and 'template_type' in self.prompt_profile and self.prompt_profile['template_type'] == "monolithic":
            self.prompt_manager = MonolithicPrompt(self.prompt_profile)
        else:
            self.prompt_manager = DefaultPrompt(self.prompt_profile)

        logger.debug(f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Using prompt manager {self.prompt_manager.__class__.__name__}\n")
        logger.debug(f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Using base url {self.base_url}")
        # self.headers = {
        #     "api_key": self.api_key 
        # }
        

    def create_chat_completion(self, messages, temperature, max_tokens):
        """
        Create a chat completion API call to Text Gen WebUI

        Args:
            messages (list): The messages to be used as context.
            temperature (float): The temperature to use for the completion.
            max_tokens (int): The maximum number of tokens to generate.

        Returns:
            str: The resulting response.
        """

        # Preflight debug
        logger.debug(
            f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Creating chat completion with:\n{json.dumps(messages, indent=4)}\n"
            f"... and temperature {temperature}\n"
            f"... and max_tokens {max_tokens}\n\n"
        )

        # Token defaults
        if max_tokens is None:
            max_tokens=600
        if float(temperature)==0.0:
            temperature=0.01

        # Reshape the messages
        messages = self.prompt_manager.reshape_message(messages)
        logger.debug(
            f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Reshaped messages to:\n{messages}"
        )

        # API call
        request = {
            'prompt': messages, 
            'temperature': float(temperature), 
            'max_tokens': int(max_tokens)
        }
        response = requests.post(self.base_url + self.API_ENDPOINT_GENERATE, json=request)
        
        # Process the result
        if response.status_code == 200:

            # Make JSON
            try:
                response_json = response.json()
            except:
                response_json = {'results': [{'text': ''}]}

            # Debug
            logger.debug(
                f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Got API response:\n{response_json}\n\n"
            )

            # Return
            text_response = response_json['results'][0]['text']
            text_response = self.prompt_manager.reshape_response(text_response)
            logger.debug(
                f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Returning response:\n {text_response}\n"
                f"(as JSON: \n{response_json}\n\n"
            )
            return text_response
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

