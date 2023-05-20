import json
from autogpt.logs import logger
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

        # Rebuild prompt
        message_string += self.get_ai_profile()


        return str(messages)