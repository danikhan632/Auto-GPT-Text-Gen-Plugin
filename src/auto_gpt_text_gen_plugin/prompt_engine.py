import re
from autogpt.config import Config
from autogpt.config.ai_config import AIConfig
from autogpt.prompts.generator import PromptGenerator

class PromptEngine:

    def __init__(self):

        # Constants
        self.USER_NAME = "User: "

        # Pull-in from Auto-GPT
        self.prompt_generator = PromptGenerator()
        self.config = Config()
        self.ai_config = AIConfig.load(self.config.ai_settings_file)

        # Variables
        self.prompt_profile = {}
        self.original_system_msg = ''

        # Regular expressions
        self.regex_os = r'The OS you are running on is:(.*?)\n\nGOALS'


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


    def get_profile_attribute(self, attribute:str, container:str = '') -> str:
        """
        Get an attribute from the AI config.

        Args:
            attribute (str): The attribute to get.

        Returns:
            str: The attribute's value.
        """

        if container == '':
            base = self.prompt_profile
        else:
            base = self.prompt_profile[container]

        if base[attribute] is not None:
            return base[attribute]
        else:
            return ''

    
    def get_agent_name(self) -> str:
        """
        Get the agent's name from the AI config.

        Returns:
            str: The agent's name.
        """

        return self.ai_config.ai_name
    

    def get_agent_role(self) -> str:
        """
        Get the agent's role from the AI config.

        Returns:
            str: The agent's role.
        """

        return self.ai_config.ai_role
    

    def get_agent_goals(self) -> str:
        """
        Get the agent's goals from the AI config.

        Returns:
            list: The agent's goals.
        """

        goals_list = ''
        for i, goal in enumerate(self.ai_config.ai_goals):
            goals_list += f"{i+1}. {goal}"

        return goals_list
    

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

        if container == '':
            base = self.prompt_profile
        else:
            base = self.prompt_profile[container]

        if attribute in base:
            for item in base[attribute]:
                response += item + ' '

        return response
    

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

        return response
    

    def get_ai_profile(self) -> str:
        """
        Build the AI profile string
        
        Returns:
            str: The AI profile string.
        """

        response = ''

        response += self.get_profile_attribute('lead_in') + ', '
        response += self.get_agent_name() + ', '
        response += self.get_agent_role() + '. '
        response += self.get_profile_list_as_line('general_guidance', 'strings')
        response += self.get_profile_attribute('os_prompt', 'strings')
        response += self.extract_from_original(self.regex_os)
        response += self.get_profile_attribute('goal_label', 'strings')
        response += self.get_profile_list_as_line('goals', 'strings')
        response += self.get_agent_goals()

        return response

