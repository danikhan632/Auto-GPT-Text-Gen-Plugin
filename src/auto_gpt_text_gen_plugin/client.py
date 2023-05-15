import requests
import os
import json
from colorama import Fore, Style
from autogpt.config import Config
from autogpt.logs import logger
from autogpt.prompts.generator import PromptGenerator
from autogpt.commands.command import CommandRegistry

    
class Client:
    def __init__(self):
        self.base_url = os.environ.get('LOCAL_LLM_BASE_URL', "http://127.0.0.1:5000/")
        self.prompt_generator = PromptGenerator()
        self.command_registry = CommandRegistry()
        self.config = Config()

        self.build_command_registry()

        logger.debug(
            f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Using base url {self.base_url}"
        )
        # self.headers = {
        #     "api_key": self.api_key 
        # }

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
    

    def build_command_registry(self) -> CommandRegistry:
        """
        Build the command registry needed for prompt building

        Returns:
            CommandRegistry: The command registry to work against
        """

        # TODO: Fix me. This is a terrible idea. When this functionality
        # is modularized, replace this code.

        command_categories = [
            "autogpt.commands.analyze_code",
            "autogpt.commands.audio_text",
            "autogpt.commands.execute_code",
            "autogpt.commands.file_operations",
            "autogpt.commands.git_operations",
            "autogpt.commands.google_search",
            "autogpt.commands.image_gen",
            "autogpt.commands.improve_code",
            "autogpt.commands.twitter",
            "autogpt.commands.web_selenium",
            "autogpt.commands.write_tests",
            "autogpt.app",
            "autogpt.commands.task_statuses",
        ]

        command_categories = [
            x for x in command_categories if x not in self.config.disabled_command_categories
        ]

        for command_category in command_categories:
            self.command_registry.import_commands(command_category)
    

    def build_prompt_payload(self) -> str:
        """ 
        Build the prompt for the API.
        """

        constraints = [
            'Always save important info to files.'
            'Only use commands in double quotes (e.g. "command name").'
        ]
        resources = [
            'Internet search'
            'Long term memory'
            'Simple agents for Q&A'
            'File output'
        ]
        evaluations = [
            'Always review/analyze your actions are at peak efficiency.'
            'Constantly self-critique your big-picture planning.'
            'Reflect on past decisions to refine your apporoach.'
            'Complete tasks in the fewest steps possible.'
            'Save code to a file'
        ]

        for constraint in constraints:
            self.prompt_generator.add_constraint(constraint)

        for resource in resources:
            self.prompt_generator.add_resource(resource)

        for evaluation in evaluations:
            self.prompt_generator.add_performance_evaluation(evaluation)

        for idx, cmd in enumerate(self.command_registry.commands):
            self.prompt_generator.add_command(cmd, idx)

        self.prompt_generator.response_format = {
            "thoughts": {
                "text": "<your thought>",
                "reasoning": "<your reasoning>",
                "plan": "<your plan as a list>",
                "criticism": "<your self-criticism>",
                "speak": "<your message to the user",
            },
            "command": {
                "name": "<selected command>",
                "args": {
                    "arg name": "<arg value>"
                }   
            }
        }

        return self.prompt_generator.generate_prompt_string()


    def create_chat_completion(self, messages, temperature, max_tokens):
        messages[0]['content'] = self.build_prompt_payload()
        logger.debug(
            f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Creating chat completion with messages {messages}\n"
            f" and temperature {temperature}\n"
            f" and max_tokens {max_tokens}"
        )
        if max_tokens is None:
            max_tokens=400
        if float(temperature)==0.0:
            temperature=0.01
        reshaped_messages = self.reshape_message(messages)
        logger.debug(
            f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Reshaped messages to:\n{reshaped_messages}"
        )
        request = {'prompt': reshaped_messages, 'temperature': float(temperature), 'max_tokens': int(max_tokens)}

        response = requests.post(self.base_url+'/api/v1/generate', json=request)
        
        if response.status_code == 200:
            logger.debug(
                f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Got response {response.json()}"
            )
            response = response.json()
            resp = response['results'][0]['text']
            resp = self.remove_whitespace(resp)
            logger.debug(
                f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Returning response:\n {resp}\n"
                f"(with formatted JSON: \n{resp}\n\n"
            )
            return resp
        else:
            logger.debug(
                f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET}\n"
                f"{Fore.RED}Error: Response status code {response.status_code}{Fore.RESET}"
            )
            return "Error: " + response.text


    def get_embedding(self,text):
        logger.debug(
            f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Getting embedding for text {text}"
        )
        request = {'text':str(text)}

        response = requests.post(self.base_url+'/api/v1/get-embeddings', json=request)
        
        if response.status_code == 200:
            logger.debug(
                f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET} Got response {response.json()}"
            )
            return response.json()['results'][0]['embeddings']
        else:
            logger.debug(
                f"{Fore.LIGHTRED_EX}Auto-GPT-Text-Gen-Plugin:{Fore.RESET}\n"
                f"{Fore.RED}Error: Response status code {response.status_code}{Fore.RESET}"
            )
            return ["Error"]

