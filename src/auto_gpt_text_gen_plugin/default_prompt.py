from autogpt.logs import logger
from .prompt_engine import PromptEngine

class DefaultPrompt(PromptEngine):

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

        return self.messages_to_conversation(messages, 'User: ')