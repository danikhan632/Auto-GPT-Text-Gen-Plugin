import json
import re
import yaml
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

        send_as_name = self.get_user_name()
        if send_as_name not in ['', None, 'None'] and len(send_as_name) > 0:
            send_as_name += ': '
        elif send_as_name == None:
            send_as_name = ''
        
        if not self.is_ai_system_prompt(self.original_system_msg):
            logger.debug(f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} The system message is not an agent prompt, returning original message\n\n")
            return self.messages_to_conversation(messages, send_as_name)
        else:
            logger.debug(f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} The system message is an agent prompt, continuing\n\n")

        # Rebuild prompt
        message_string += send_as_name
        message_string += self.get_ai_profile()
        message_string += self.get_ai_constraints()
        message_string += self.get_commands()
        message_string += self.get_ai_resources()
        message_string += self.get_ai_critique()
        message_string += self.get_response_format()
        message_string = self.get_profile_attribute('prescript') + message_string

        end_strip = self.get_end_strip()
        history = self.messages_to_conversation(messages[1:-end_strip], send_as_name)
        if history not in ['', None, 'None'] and len(history) > 0:
            message_string += self.get_profile_attribute('history_start') + '\n\n'
            message_string += history
            message_string += self.get_profile_attribute('history_end') + '\n\n'
        else:
            message_string += self.get_profile_attribute('history_none') + '\n\n'

        postscript = self.get_profile_attribute('postscript')
        if postscript not in ['', None, 'None'] and len(postscript) > 0:
            message_string += send_as_name
            message_string += postscript

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

        message_str = message.strip()

        # If the message has a start template tag, remove it and everything before it
        if '--START TEMPLATE--' in message:
            message_str = message[message.find('--START TEMPLATE--')+len('--START TEMPLATE--'):]

        # If the message has an end template tag, remove it and everything after it
        if '--END TEMPLATE--' in message:
            message_str = message_str[:message.find('--END TEMPLATE--')]

        # If \n is double-escaped, fix it.
        if '\\n' in message_str:
            message_str = message_str.replace('\\n', '\n')

        # Look for plain language strings and convert to YAML tokens
        normal_words = ["Plan Summary:", "Next Steps:", "TTS Msg:", "TTS Message:", "Command Name:"]
        replacement_tokens = ["plan_summary:", "next_steps:", "tts_msg:", "tts_msg:", "command_name:"]
        for normal_word, replacement_token in zip(normal_words, replacement_tokens):
            pattern = re.compile(re.escape(normal_word), re.IGNORECASE)
            message_str = re.sub(pattern, replacement_token, message_str)

        # If a reserved YAML keyword is in the string without a new line before it, add one
        template_keywords = ['reasoning:', 'next_steps:', 'considerations:', 'tts_msg:', 'command_name:', 'args:']
        for keyword in template_keywords:
            if '\n' + keyword not in message_str:
                message_str = message_str.replace(keyword, '\n' + keyword)

        ## Spacing fixing...
        # Remove space before the newline 
        message_str = re.sub(r'\s*\n', '\n', message_str)
        # Look for "plan_summary:" at the start of the message_str
        if not message_str.startswith('plan_summary:'):
            # Does it exist anywhere?
            if 'plan_summary:' in message_str:
                # Removee everything before it.
                message_str = message_str[message_str.find('plan_summary:'):]
            else:
                # Add it to the start of the message
                message_str = 'plan_summary:\n' + message_str

        try:
            logger.debug(f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Attempting to convert the response to a dictionary: {message_str}\n\n")
            message_data = yaml.safe_load(message_str)
            logger.debug(f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Converted the YAML response to a dictionary\n\n")
            converted_obj = self.simple_response_to_autogpt_response(message_data)
        except Exception as e:
            logger.error(f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Could not reshape the response to the Auto-GPT format, returning original message: {e}\n\n")
            return message

        return converted_obj