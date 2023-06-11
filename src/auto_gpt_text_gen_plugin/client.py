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

    def __init__(self, base_url, prompt_profile, model = None):
        """Constructor"""

        # Initialize the prompt manager
        self.base_url = base_url
        self.prompt_profile = prompt_profile

        # Constants
        self.MAX_RESPONSE_TOKENS = 300
        self.API_ENDPOINT_GENERATE = '/api/v1/generate'
        self.API_ENDPOINT_MODELS = '/api/v1/model'
        self.API_ENDPOINT_TOKENCOUNT = '/api/v1/token-count'

        # Which prompt manager to use
        if self.prompt_profile is not None and 'template_type' in self.prompt_profile and self.prompt_profile['template_type'] == "monolithic":
            self.prompt_manager = MonolithicPrompt(self.prompt_profile)
        else:
            self.prompt_manager = DefaultPrompt(self.prompt_profile)

        if model is not None:
            self.model = model
        else:
            self.model = self.select_model()
        
        self.context_size = self.get_context_size(self.model)


        logger.debug(f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Using prompt manager {self.prompt_manager.__class__.__name__}\n")
        logger.debug(f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Using base url {self.base_url}")
        # self.headers = {
        #     "api_key": self.api_key 
        # }
        

    def create_chat_completion(self, messages:list, temperature:float, max_tokens:int = 300, model_properties:dict = None):
        """
        Create a chat completion API call to Text Gen WebUI

        Args:
            messages (list): The messages to be used as context.
            temperature (float): The temperature to use for the completion.
            max_tokens (int): The maximum number of tokens to generate.
            model_properties (dict): The properties of the model to use on submission.

        Returns:
            str: The resulting response.
        """

        # Preflight debug
        logger.debug(
            f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Creating chat completion with:\n{json.dumps(messages, indent=4)}\n"
            f"... and temperature {temperature}\n\n"
        )

        # Reshape the messages
        messages = self.prompt_manager.reshape_message(messages)
        logger.debug(
            f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Reshaped messages to:\n{messages}"
        )

        # Calculate tokens
        logger.debug(f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Requested max tokens: {max_tokens}")
        msg_size = self.calculate_token_length(messages)
        if not isinstance(max_tokens, int) or max_tokens > self.context_size or max_tokens < 0:
            max_tokens = self.MAX_RESPONSE_TOKENS
        else:
            max_tokens = self.context_size - msg_size

        logger.debug(f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Calculated tokens: {max_tokens}")

        # API call
        request = {
            'prompt': messages, 
            'temperature': float(temperature), 
            'max_new_tokens': max_tokens
        }

        # Merge model_properties into request
        if model_properties is not None:
            request.update(model_properties)

        logger.debug(f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Sending request:\n{json.dumps(request, indent=4)}\n\n")

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
        
        
    def select_model(self) -> str:
        """
        Present the user with a list of models to choose from, and return the ID of the selected model.
        
        Returns:
            str: The ID of the selected model.
        """

        selected_model = ''

        request = {
            'action': 'list'
        }

        model_list = ''

        try:
            endpoint = f'{self.base_url}{self.API_ENDPOINT_MODELS}'
            logger.debug(f'{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET}: Getting models from {endpoint}')
            response = requests.post(endpoint, json=request)
            model_list = response.json()['result']
            if isinstance(model_list, str):
                model_list = [model_list]
                
        except Exception as e:
            logger.debug(
                f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET}\n"
                f"{Fore.RED}Error trying to get model to select: {e}{Fore.RESET}"
            )
            
            # Terminate the application
            os._exit(1)

        if len(model_list) == 0:
            raise Exception('No models found. Aborting.')
        elif len(model_list) > 1:
            selected_model = self.prompt_for_model(model_list)
        else:
            selected_model = model_list[0]

        print(f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Using model: {selected_model}")

        return selected_model
    

    def prompt_for_model(self, model_list) -> str:
        """
        Prompt the user to select a model
        
        Args:
            model_list (list): The list of models to choose from.
            
        Returns:
            str: The ID of the selected model.
        """

        model_id = ''

        # Loop through the model list and present the user with a choice
        print(f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Please select a model by number:")
        model_number = 1
        for model in model_list:
            print(f"{model_number}) {model}")
            model_number += 1

        # Get the user's choice
        selected_model = ''
        while selected_model == '':
            try:
                selected_model = int(input(f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Enter a number: "))
                if selected_model < 1 or selected_model > len(model_list):
                    print(f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Invalid selection. Please try again.")
                    selected_model = ''
            except:
                print(f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Invalid selection. Please try again.")

        model_id = model_list[selected_model - 1]

        return model_id


    def get_context_size(self, model:str) -> int:
        """
        Get the context size of a model.
        
        Args:
            model (str): The ID of the model to get the context size of.
            
        Returns:
            int: The context size of the model.
        """

        context_size = 0

        request = {
            'action': 'load',
            'model_name': model
        }

        try:
            endpoint = f'{self.base_url}{self.API_ENDPOINT_MODELS}'
            logger.debug(f'{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET}: Getting context size from {endpoint}')
            print(f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Loading your model. This may take a few moments...")
            response = requests.post(endpoint, json=request)
            model_info = response.json()['result']
            context_size = model_info['shared.settings']['truncation_length']
            logger.debug(f'{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET}: Context size is {context_size}')
        except Exception as e:
            logger.debug(
                f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET}\n"
                f"{Fore.RED}Error trying to get context size: {e}{Fore.RESET}"
            )
            os._exit(1)
        
        return context_size
    

    def calculate_token_length(self, message:str) -> int:
        """
        Calculate the length of a message in tokens.
        
        Args:
            message (str): The message to calculate the length of.
            
        Returns:
            int: The length of the message in tokens.
        """

        result = 0

        uri = f'{self.base_url}{self.API_ENDPOINT_TOKENCOUNT}'

        try:
            post = {
                'prompt': message
            }
            reply = requests.post(uri, json=post)

            if reply.status_code == 200:
                api_response = reply.json()
                try:
                    result = api_response['results'][0]['tokens']
                except:
                    pass
        except Exception as e:
            logger.debug(
                f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET}\n"
                f"{Fore.RED}Error trying to calculate token length: {e}{Fore.RESET}"
            )
            os._exit(1)

        return result