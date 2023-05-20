import json
import yaml
from .client import Client


class TextGenPluginController():
    """
    This is a wrapper class to account for possible future extension to support
    multiple APIs
    """

    def __init__(self, plugin, base_url, prompt_profile):
        """
        Args:
            plugin (AutoGPTPluginTemplate): The plugin that is using this controller.
        """

        self._plugin = plugin

        # Constants
        self.DEFAULT_PROMPT = {
            "template_type": "monolithic",
            "prescript": "",
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
                "closing_command": "Determine which next command to use, and respond using the format specified above:"
            },
            "postscript": ""
        }

        # Load the profile
        prompt_config = self.load_prompt_config(prompt_profile)
        if prompt_config is None:
            prompt_config = self.DEFAULT_PROMPT
        self.api = Client(base_url, prompt_config)


    def load_prompt_config(self, prompt_profile) -> dict|list|str|None:
        """
        Load the prompt from the defined file.

        Args:
            prompt_profile (str): The path to the prompt profile.

        Returns:
            dict|list|str|None: The loaded prompt profile.
        """

        try:
            with open(prompt_profile, 'r') as f:
                data = yaml.load(f, Loader=yaml.FullLoader)
                return data
        except:
            return None
        
    
    def handle_chat_completion(self, messages, temperature, max_tokens) -> str:
        """
        This method cllls the chat_completion method of whatever API is loaded
        
        Args:
            messages (list): The messages to be used as context.
            temperature (float): The temperature to use for the completion.
            max_tokens (int): The maximum number of tokens to generate.
            
        Returns:
            str: The resulting response.
        """
        
        return self.api.create_chat_completion(messages, temperature, max_tokens)
    
    
    def handle_get_embedding(self, text) -> list:
        """
        This method cllls the get_embedding method of whatever API is loaded
        
        Args:
            text (str): The text to be converted to embedding.
            
        Returns:
            list: The resulting embedding.
        """

        return self.api.get_embedding(text)




