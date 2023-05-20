import yaml
from autogpt.logs import logger
from colorama import Fore, Style
from .client import Client


class TextGenPluginController():
    """
    This is a wrapper class to account for possible future extension to support
    multiple APIs
    """

    def __init__(self, plugin, base_url, prompt_profile):
        """
        Args:
            plugin (AutoGPTPluginTemplate): The plugin that is using this controller.
        """

        self._plugin = plugin

        # Load the profile
        prompt_config = self.load_prompt_config(prompt_profile)
        self.api = Client(base_url, prompt_config)


    def load_prompt_config(self, prompt_profile) -> dict|list|str|None:
        """
        Load the prompt from the defined file.

        Args:
            prompt_profile (str): The path to the prompt profile.

        Returns:
            dict|list|str|None: The loaded prompt profile.
        """

        response = None
        try:
            with open(prompt_profile, 'r') as f:
                response = yaml.load(f, Loader=yaml.FullLoader)
        except:
            pass

        logger.debug(f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Loaded prompt profile:\n{response}\n\n")

        return response
        
    
    def handle_chat_completion(self, messages, temperature, max_tokens) -> str:
        """
        This method cllls the chat_completion method of whatever API is loaded
        
        Args:
            messages (list): The messages to be used as context.
            temperature (float): The temperature to use for the completion.
            max_tokens (int): The maximum number of tokens to generate.
            
        Returns:
            str: The resulting response.
        """
        
        return self.api.create_chat_completion(messages, temperature, max_tokens)
    
    
    def handle_get_embedding(self, text) -> list:
        """
        This method cllls the get_embedding method of whatever API is loaded
        
        Args:
            text (str): The text to be converted to embedding.
            
        Returns:
            list: The resulting embedding.
        """

        return self.api.get_embedding(text)




