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
        user_name = self.get_user_name() + ': '

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
        message_string += self.get_profile_attribute('postscript') + '\n\n'

        # Add all the other messages
        end_strip = self.get_end_strip()
        message_string += self.messages_to_conversation(messages[1:-end_strip], user_name)
        message_string += self.get_agent_name() + ': '

        return message_string
    

    def reshape_response(self, message:str) -> str:
        """
        Convert the API response to a dictionary, then convert thoughts->plan to a YAML list
        then return a JSON string of the object
        
        Args:
            message (str): The response from the API.
               
        Returns:
            str: The response as a dictionary, or the original message if it cannot be converted.
        """

        try:
            message_dict = json.loads(message)
        except:
            logger.debug(f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Could not convert message to JSON, returning original message\n\n")
            return message

        if isinstance(message_dict, dict):
            plan = message_dict.get('thoughts', {}).get('plan')
            if plan is not None:
                message_dict['thoughts']['plan'] = self.list_to_yaml_string(plan)
                logger.debug(f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Converted thoughts->plan to YAML list\n\n")

        return json.dumps(message_dict)