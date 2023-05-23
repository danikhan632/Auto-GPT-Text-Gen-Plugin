import json
from autogpt.logs import logger
from colorama import Fore, Style
from .prompt_engine import PromptEngine

class MonolithicPrompt(PromptEngine):

    def __init__(self, prompt_profile) -> None:
        """Initializes the MonolithicPrompt class."""

        super().__init__()
        self.prompt_profile = prompt_profile


    def reshape_message(self, messages:list) -> str:
        """
        Convert the OpenAI message format to a string that can be used by the API.

        Args:
            messages (list): List of messages. Defaults to [].

        Returns:
            str: String representation of the messages.
        """

        self.original_system_msg = messages[0]['content']

        # Prime the variables
        message_string = ''

        user_name = self.get_user_name()
        if user_name not in ['', None, 'None'] and len(user_name) > 0:
            user_name += ': '
        elif user_name == None:
            user_name = ''
        
        chat_name = self.get_ai_chat_name()
        # If chat_name isn't empty, add a colon and space
        if chat_name not in ['', None, 'None'] and len(chat_name) > 0:
            chat_name += ': '
        elif chat_name == None:
            chat_name = ''
        
        if not self.is_ai_system_prompt(self.original_system_msg):
            logger.debug(f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} The system message is not an agent prompt, returning original message\n\n")
            return self.messages_to_conversation(messages, user_name)
        else:
            logger.debug(f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} The system message is an agent prompt, continuing\n\n")

        # Rebuild prompt
        message_string += user_name
        message_string += self.get_ai_profile()
        message_string += self.get_ai_constraints()
        message_string += self.get_commands()
        message_string += self.get_ai_resources()
        message_string += self.get_ai_critique()
        message_string += self.get_response_format()
        message_string = self.get_profile_attribute('prescript') + message_string

        message_string += '[Begin History]\n\n'
        # Add all the other messages
        end_strip = self.get_end_strip()
        message_string += self.messages_to_conversation(messages[1:-end_strip], user_name)
        message_string += chat_name

        message_string += '[End History]\n\n'

        message_string += self.get_profile_attribute('postscript')

        return message_string
    

    def reshape_response(self, message:str) -> dict:
        """
        Convert the API response to a dictionary, then convert thoughts->plan to a YAML list
        then return a JSON string of the object
        
        Args:
            message (str): The response from the API.
               
        Returns:
            str: The response as a dictionary, or the original message if it cannot be converted.
        """

        message_str = json.dumps(message)
        message_str = message_str.strip()
        try:
            message_dict = json.loads(message_str)
        except json.decoder.JSONDecodeError as e:
            logger.debug(f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Could not convert message to JSON: ({e})\n")
            message_dict = self.recover_json_response(message)
            logger.debug(f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Attempted to recover JSON response.\n\n")
            return message_dict

        return message_dict