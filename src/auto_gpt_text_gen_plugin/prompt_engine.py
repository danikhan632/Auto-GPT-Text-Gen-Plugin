import re

class PromptEngine:

    def __init__(self):
        pass


    def remove_whitespace(self, text:str) -> str:
        """
        Flatten multiple whitespace characters into a single space.

        Args:
            text (str): The text to remove whitespace from.

        Returns:
            str: The text with extra whitespace removed.
        """

        return " ".join(text.split())

    def extract_commands(self, message = '') -> str:
        """
        Extract commands from the system prompt
        
        Args:
            message (str): The message to extract commands from. Defaults to ''.
        
        Returns:
            str: The extracted commands as a string.
        """

        try:
            if message is None:
                return ''
            match = re.search(r"(Commands:.*?Resources:)", message, re.DOTALL)
            if match is None:
                return ''
            match = match.group(1).strip()
            return match
        except AttributeError:
            return ''

