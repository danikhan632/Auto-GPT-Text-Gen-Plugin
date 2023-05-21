import json
import re
from autogpt.config import Config
from autogpt.config.ai_config import AIConfig
from autogpt.prompts.generator import PromptGenerator

class PromptEngine:

    def __init__(self):

        # Pull-in from Auto-GPT
        self.prompt_generator = PromptGenerator()
        self.config = Config()
        self.ai_config = AIConfig.load(self.config.ai_settings_file)

        # Variables
        self.prompt_profile = {}
        self.original_system_msg = ''

        # Regular expressions
        self.regex_os = r'The OS you are running on is:(.*?)\n\nGOALS'
        self.regex_commands = r'Commands:(.*?)\n\nResources'
        self.regex_split_commands = r'\d+\.'


    def is_ai_system_prompt(self, prompt:str) -> bool:
        """
        Check if the prompt is a system prompt used for standard roleplay

        Args:
            prompt (str): The prompt to check.

        Returns:
            bool: True if the prompt is a RP prompt, False otherwise.
        """

        prompt = self.strip_newlines(prompt)
        prompt = self.remove_whitespace(prompt)

        return prompt.startswith('You are')


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
        

    def reshape_message(self, messages:list):
        """
        Inhereted method
        """

        pass


    def reshape_response(self, message) -> dict:
        """
        Inhereted method
        """

        return {}
    

    def get_user_name(self) -> str:
        """
        Return the user's name from the prompt profile.

        Returns:
            str: The user's name.
        """

        return self.get_profile_attribute('send_as')


    def get_profile_attribute(self, attribute:str, container:str = '') -> str:
        """
        Get an attribute from the AI config.

        Args:
            attribute (str): The attribute to get.

        Returns:
            str: The attribute's value.
        """

        response = ''

        if container == '' and attribute in self.prompt_profile:
            response = self.prompt_profile[attribute]
        elif container in self.prompt_profile and attribute in self.prompt_profile[container]:
            response = self.prompt_profile[container][attribute]

        return str(response).replace('\\n', '\n')

    
    def get_agent_name(self) -> str:
        """
        Get the agent's name from the AI config.

        Returns:
            str: The agent's name.
        """

        return str(self.ai_config.ai_name)
    

    def get_agent_role(self) -> str:
        """
        Get the agent's role from the AI config.

        Returns:
            str: The agent's role.
        """

        return str(self.ai_config.ai_role).replace('\\n', '\n')
    

    def get_agent_goals(self) -> str:
        """
        Get the agent's goals from the AI config.

        Returns:
            list: The agent's goals.
        """

        goals_list = ''
        for i, goal in enumerate(self.ai_config.ai_goals):
            goals_list += f"{i+1}. {goal}\n"

        return str(goals_list).replace('\\n', '\n')
    

    def get_profile_list_as_line(self, attribute:str, container:str = '') -> str:
        """
        Get a list from the profile.

        Args:
            attribute (str): The attribute to get.
            container (str, optional): The container to put the list in. Defaults to None.

        Returns:
            str: The list as a string.
        """

        response = ''
        list_items = []

        if container == '' and attribute in self.prompt_profile:
            list_items = self.prompt_profile[attribute]
        elif container in self.prompt_profile and attribute in self.prompt_profile[container]:
            list_items = self.prompt_profile[container][attribute]

        for item in list_items:
            response += item + ' '

        return str(response).replace('\\n', '\n')
    

    def get_profile_numbered_list(self, attribute:str, container:str = '') -> str:
        """
        Get a numbered list from the profile.
        
        Args:
            attribute (str): The attribute to get.
            container (str, optional): The container to put the list in. Defaults to None.
            
        Returns:
            str: The list as a string.
        """

        response = ''
        list_items = []

        if container == '' and attribute in self.prompt_profile:
            list_items = self.prompt_profile[attribute]
        elif container in self.prompt_profile and attribute in self.prompt_profile[container]:
            list_items = self.prompt_profile[container][attribute]

        for i, item in enumerate(list_items):
            response += f'{i + 1}. {item}\n'

        return str(response).replace('\\n', '\n')

    def extract_from_original(self, regex:str) -> str:
        """
        Extract a string from the original system message.
        
        Args:
            regex (str): The regular expression to use.
            
        Returns:
            str: The extracted string.
        """

        response = ''

        match = re.search(regex, self.original_system_msg, re.DOTALL)
        if match is not None:
            response = match.group(1).strip()
            response = self.remove_whitespace(response)        

        return str(response)
    

    def string_to_numbered_list(self, text:str) -> str:
        """
        Convert a string of a numbered list to a numbered list.
        
        Args:
            string (str): The string to convert.
            
        Returns:
            str: The numbered list.
        """

        response = ''

        # Remove extra whitespace and new lines.
        text = self.remove_whitespace(text)
        text = text.replace('\n', ' ')

        # Split the string on the number and period.
        response_list = re.split(self.regex_split_commands, text)
        
        # Combine the list into a string with new lines between each item.
        for i, item in enumerate(response_list):
            clean_item = self.remove_whitespace(item)
            if clean_item != '':
                response += f'{i}. {item}\n'

        return str(response)
    

    def list_to_yaml_string(self, old_list:list) -> str:
        """
        Convert a list to a YAML list string.
        
        Args:
            old_list (list): The list to convert.

        Returns:
            str: The YAML list string.
        """

        response = ''

        # Combine the list into a string where each item starts with a dash and a space
        for item in old_list:
            clean_item = self.remove_whitespace(item)
            if clean_item != '':
                response += f'- {item}\n'

        return response
    

    def get_as_json(self, attribute:str, container:str = '') -> str:
        """
        Get an attribute from the AI config as a JSON string.

        Args:
            attribute (str): The attribute to get.

        Returns:
            str: The attribute's value as a JSON string.
        """

        response = ''

        if container == '' and attribute in self.prompt_profile:
            response = json.dumps(self.prompt_profile[attribute])
        elif container in self.prompt_profile and attribute in self.prompt_profile[container]:
            response = json.dumps(self.prompt_profile[container][attribute])

        response = response.replace('\n', '')
        response = self.remove_whitespace(response)

        return str(response)
    

    def strip_newlines(self, text:str) -> str:
        """
        Strip new lines from a string.
        
        Args:
            text (str): The string to strip.
            
        Returns:
            str: The stripped string.
        """

        return str(text).replace('\n', ' ')
    

    def get_command_list(self) -> str:
        """
        Get the command list from the system message.
        
        Returns:
            str: The command list.
        """

        response = ''

        commands = self.extract_from_original(self.regex_commands)
        response = self.string_to_numbered_list(commands)

        return str(response)
    

    def get_ai_profile(self) -> str:
        """
        Build the AI profile string
        
        Returns:
            str: The AI profile string.
        """

        response = ''

        response += self.get_profile_attribute('lead_in', 'strings')
        response += self.get_agent_name() + ', '
        response += self.get_agent_role() + ' '
        response += self.get_profile_list_as_line('general_guidance', 'strings')
        response += self.get_profile_attribute('os_prompt', 'strings')
        response += self.extract_from_original(self.regex_os)
        response += self.get_profile_attribute('goal_label', 'strings')
        response += self.get_profile_list_as_line('goals', 'strings')
        response += self.get_agent_goals()

        return str(response)
    

    def get_ai_constraints(self) -> str:
        """
        Build the AI constraints string
        
        Returns:
            str: The AI constraints string.
        """

        response = ''

        response += self.get_profile_attribute('constraints_label', 'strings')
        response += self.get_profile_numbered_list('constraints', 'strings')

        return str(response)
    

    def get_commands(self) -> str:
        """
        Build the commands string
        
        Returns:
            str: The commands string.
        """

        response = ''

        response += self.get_profile_attribute('commands_label', 'strings')
        response += self.get_command_list()

        return str(response)
    

    def get_ai_resources(self) -> str:
        """
        Build the AI resources string
        
        Returns:
            str: The AI resources string.
        """

        response = ''

        response += self.get_profile_attribute('resources_label', 'strings')
        response += self.get_profile_numbered_list('resources', 'strings')

        return str(response)
    

    def get_ai_critique(self) -> str:
        """
        Build the AI critique string
        
        Returns:
            str: The AI critique string.
        """

        response = ''

        response += self.get_profile_attribute('performance_eval_label', 'strings')
        response += self.get_profile_numbered_list('performance_eval', 'strings')

        return str(response)
    

    def get_end_strip(self) -> int:
        """
        Get the end strip index from the profile.
        
        Returns:
            int: The end strip index.
        """

        end_index = 0

        try:
            end_index = self.get_profile_attribute('strip_messages_from_end')
        except:
            pass

        return int(end_index)
    

    def get_response_format(self) -> str:
        """
        Build the response format string
        
        Returns:
            str: The response format string.
        """

        response = ''

        response += self.get_profile_attribute('response_format_label', 'strings')
        response += self.get_profile_attribute('response_format_pre_prompt', 'strings')
        response += self.get_as_json('response_format')
        response += self.get_profile_attribute('response_format_post_prompt', 'strings')

        return str(response)


    def messages_to_conversation(self, messages:list, attribution:str = '') -> str:
        """
        Convert a list of messages to a conversation.
        
        Args:
            messages (list): The messages to convert.
            attribution (str): The attribution to use for the messages.
            
        Returns:
            str: The conversation.
        """

        response = ''

        for message in messages:
            clean_message = self.strip_newlines(message['content'])
            clean_message = self.remove_whitespace(clean_message)
            response += attribution + clean_message + '\n\n'

        return str(response)