import json
from autogpt.config import Config
from autogpt.config.ai_config import AIConfig
from autogpt.logs import logger
from autogpt.prompts.generator import PromptGenerator

class MonolithicPrompt:

    def __init__(self, prompt_profile:str = '') -> None:
        """Initializes the MonolithicPrompt class."""

        # Constants
        self.DEFAULT_PROMPT = {
            "template_type": "monolithic",
            "strings": {
                "lead_in": "You are ",
                "goal_label": "GOALS:\n\n",
                "constraints_label": "Constraints:\n",
                "constraints": [
                    "~4000 word limit for short term memory. Your short term memory is short, so immediately save important information to files.",
                    "If you are unsure how you previously did something or want to recall past events, thinking about similar events will help you remember.",
                    "No user assistance",
                    "Exclusively use the commands listed in double quotes e.g. \"command name\""
                ],
                "commands_label": "Commands:\n",
                "resources_label": "Resources:\n",
                "resources": [
                    "Internet access for searches and information gathering.",
                    "Long Term memory management.",
                    "GPT-3.5 powered Agents for delegation of simple tasks."
                ],
                "performance_eval_label": "Performance Evaluation:\n",
                "performance_eval": [
                    "Continuously review and analyze your actions to ensure you are performing to the best of your abilities.",
                    "Constructively self-criticize your big-picture behavior constantly.",
                    "Reflect on past decisions and strategies to refine your approach.",
                    "Every command has a cost, so be smart and efficient. Aim to complete tasks in the least number of steps.",
                    "Write all code to a file."
                ],
                "response_format_pre_prompt": "You should only respond in JSON format as described below \nResponse Format: \n",
                "response_format": {
                    "thoughts": {
                        "text": "thought",
                        "reasoning": "reasoning",
                        "plan": "- short bulleted\n- list that conveys\n- long-term plan",
                        "criticism": "constructive self-criticism",
                        "speak": "thoughts summary to say to user"
                    },
                    "command": {
                        "name": "command name",
                        "args": {
                            "arg name": "value"
                        }
                    }
                },
                "response_format_post_prompt": " \nEnsure the response can be parsed by Python json.loads",
                "closing_command": "Determine which next command to use, and respond using the format specified above:",
                "postscript": ""
            }
        }

        # Initialize variables
        self.prompt_profile = self.load_profile(prompt_profile)
        self.prompt_generator = PromptGenerator()
        self.config = Config()
        self.ai_config = AIConfig.load(self.config.ai_settings_file)

        self.prompt_profile = prompt_profile

        
    def load_profile(self, prompt_profile:str = '') -> dict:
        """Loads the prompt profile from the specified file.

        Args:
            prompt_profile (str, optional): The path to the prompt profile file. Defaults to ''.

        Returns:
            dict: The loaded prompt profile.
        """
        
        # Load the prompt profile and use defaults if that fails.
        try:
            with open(prompt_profile, 'r') as f:
                prompt_profile = json.load(f)
        except:
            prompt_profile = self.DEFAULT_PROMPT

        return prompt_profile
    
    
    def remove_whitespace(self, text:str) -> str:
        """
        Flatten multiple whitespace characters into a single space.

        Args:
            text (str): The text to remove whitespace from.

        Returns:
            str: The text with extra whitespace removed.
        """

        return " ".join(text.split())
    

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
        prompt_string += json.dumps(prompt_profile['strings']['response_format'])
        prompt_string += self.prompt_profile['strings']['response_format_post_prompt']
        prompt_string += '\n' + self.prompt_profile['strings']['postscript']

        return prompt_string


