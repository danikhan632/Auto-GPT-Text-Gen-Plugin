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

        if not self.is_ai_system_prompt(self.original_system_msg):
            logger.debug(f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} The system message is not an agent prompt, returning original message\n\n")
            return self.messages_to_conversation(messages, self.USER_NAME)
        else:
            logger.debug(f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} The system message is an agent prompt, continuing\n\n")

        # Rebuild prompt
        message_string += self.USER_NAME
        message_string += self.get_ai_profile()
        message_string += self.get_ai_constraints()
        message_string += self.get_commands()
        message_string += self.get_ai_resources()
        message_string += self.get_ai_critique()
        message_string += self.get_response_format()
        message_string = self.get_profile_attribute('prescript') + message_string
        message_string += self.get_profile_attribute('postscript') + '\n\n'

        # Add all the other messages
        message_string += self.messages_to_conversation(messages[1:], self.USER_NAME)
        message_string += self.get_agent_name() + ': '

        return message_string