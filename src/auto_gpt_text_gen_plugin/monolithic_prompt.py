import json
from autogpt.config import Config
from autogpt.config.ai_config import AIConfig
from autogpt.logs import logger
from autogpt.prompts.generator import PromptGenerator
from .prompt_engine import PromptEngine

class MonolithicPrompt(PromptEngine):

    def __init__(self, prompt_profile) -> None:
        """Initializes the MonolithicPrompt class."""

        super().__init__()

        # Initialize variables
        self.prompt_profile = prompt_profile
        self.prompt_generator = PromptGenerator()
        self.config = Config()
        self.ai_config = AIConfig.load(self.config.ai_settings_file)

        self.prompt_profile = prompt_profile
    

    def reshape_message(self, messages:list) -> str:
        """
        Convert the OpenAI message format to a string that can be used by the API.

        Args:
            messages (list): List of messages. Defaults to [].

        Returns:
            str: String representation of the messages.
        """

        # Prime the variables
        message_string = ''
        
        # Consolidate messages by role
        for message in messages:
            # Capitalize the first letter of the name
            name = message['role'].capitalize()      
            user_msg = self.remove_whitespace(message['content'])  
            message_string += f"{name}: {user_msg}\n\n"

        return message_string
    

    def build_prompt_payload(self, commands:str = '') -> str:
        """ 
        Build the prompt for the API.

        Args:
            commands (str): The commands to add to the prompt. Defaults to ''.

        Returns:
            str: The prompt to send to the API.
        """

        prompt_string = ''

        # Build the agent profile
        prompt_string += self.prompt_profile['strings']['lead_in']
        prompt_string += self.ai_config.ai_name
        prompt_string += ', '
        prompt_string += self.ai_config.ai_role + '\n\n'
        prompt_string += self.prompt_profile['strings']['goal_label']

        # Goals
        for i, goal in enumerate(self.ai_config.ai_goals):
            prompt_string += f"{i+1}. {goal}\n"

        # Build prompt strings
        for constraint in self.prompt_profile['strings']['constraints']:
            self.prompt_generator.add_constraint(constraint)

        for resource in self.prompt_profile['strings']['resources']:
            self.prompt_generator.add_resource(resource)

        for evaluation in self.prompt_profile['strings']['performance_eval']:
            self.prompt_generator.add_performance_evaluation(evaluation)

        # Assemble
        prompt_string += self.prompt_profile['strings']['constraints_label']
        prompt_string += self.prompt_generator._generate_numbered_list(self.prompt_generator.constraints)
        prompt_string += self.prompt_profile['strings']['commands_label']
        prompt_string += commands
        prompt_string += self.prompt_profile['strings']['resources_label']
        prompt_string += self.prompt_generator._generate_numbered_list(self.prompt_generator.resources)
        prompt_string += self.prompt_profile['strings']['performance_eval_label']
        prompt_string += self.prompt_generator._generate_numbered_list(self.prompt_generator.performance_evaluation)
        prompt_string += self.prompt_profile['strings']['response_format_pre_prompt']
        prompt_string += json.dumps(self.prompt_profile['strings']['response_format'])
        prompt_string += self.prompt_profile['strings']['response_format_post_prompt']
        prompt_string += '\n' + self.prompt_profile['strings']['postscript']

        return prompt_string


