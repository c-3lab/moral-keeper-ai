import json
import os
from logging import getLogger

from langchain_core.prompts import PromptTemplate

from moral_keeper_ai.criteria import Criteria

from .llm import Llm

logger = getLogger(__name__)


class CheckAI:
    def __init__(self, api_config):
        self.model = api_config['model']
        self.llm = Llm(
            azure_endpoint=api_config['azure_endpoint'],
            api_key=api_config['api_key'],
            model=api_config['model'],
            timeout=api_config['timeout'],
            max_retries=api_config['max_retries'],
            repeat=api_config['repeat'],
        )

        base_model = self.llm.get_base_model_name()

        if 'gpt-4o' in base_model:
            self.criteria = Criteria.Gpt4o.criteria
        elif 'gpt-4o-mini' in base_model:
            self.criteria = Criteria.Gpt4oMini.criteria
        elif 'gpt-35-turbo' in base_model:
            self.criteria = Criteria.Gpt35Turbo.criteria
        else:
            logger.warning("base_model is either None or unrecognized")
            self.criteria = Criteria.Gpt4oMini.criteria

        self.system_template = PromptTemplate.from_template(
            'You are an excellent PR representative for a company.\n'
            'Please evaluate the received text based on the following '
            'criteria to output JSON.\n'
            '# output\n'
            '```JSON\n'
            '{criteria_prompt}'
            '```\n'
        )

    def check(self, content):
        system_prompt = self.system_template.format(
            criteria_prompt=json.dumps(
                {criterion: True for criterion in self.criteria}, indent=2
            )
        )
        responses = self.llm.chat(
            [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': content},
            ]
        )

        details = []
        for response in responses:
            details.extend([k for k, v in response.items() if not v])
        details = list(dict.fromkeys(details))
        judgment = bool(0 == len(details))
        return (judgment, details)


class SuggestAI:
    def __init__(self, api_config):
        self.model = api_config['model']
        self.llm = Llm(
            azure_endpoint=api_config['azure_endpoint'],
            api_key=api_config['api_key'],
            model=api_config['model'],
            timeout=api_config['timeout'],
            max_retries=api_config['max_retries'],
        )

        self.system_prompt = (
            '# Prerequisite\n'
            'You are a professional screenwriter.\n'
            'The text you have received is a comment on open data on a website '
            'published by a local government.\n'
            'The received text is an inappropriate comment that should not be made '
            'available to the public, so please perform the following task.\n\n'
            '# Task Description\n'
            'Consider the following in English and write in Japanese.\n'
            'Analyze the emotional tone of the comment and revise expressions such '
            'as attacks, sarcasm, sarcasm, and accusations to expressions that can '
            'be made available to the public, even if the purpose of the comment is '
            'changed.\n'
            'Add specific remarks to opinions and one-sided expressions of opinion, '
            'and revise comments to be constructive.\n'
            'If personal information is included, we will comply with privacy laws '
            'and mask personal information in the comments.\n'
            'The results of the above tasks will be output according to the # output '
            'below.\n\n'
            'The purpose of this task is to maintain a healthy communication '
            'environment on the site while respecting the intent of the comments to '
            'the fullest extent possible.\n\n'
            '# Output\n'
            '```JSON\n'
            '{\n'
            '    "Points to Note When Converting This Comment": "",\n'
            '    "Revised and moderated comments": ""\n'
            '}\n'
            '```\n'
        )

    def suggest(self, content):
        messages = [
            {'role': 'system', 'content': self.system_prompt},
            {
                'role': 'user',
                'content': 'こんな馬鹿少ないデータなんかじゃ進む作業も進まないわ。',
            },
            {
                'role': 'assistant',
                'content': '公開されているデータでは必要な情報が不足していると感じています。'
                '具体的には、（具体的な例を記述）の情報を追加していただけると助かります。よろしくお願いいたします。',
            },
            {'role': 'user', 'content': content},
        ]

        for _ in range(3):
            responses = self.llm.chat(messages)
            for response in responses:
                if revised_and_moderated := response.get(
                    'Revised and moderated comments', ''
                ):
                    return revised_and_moderated
        return None


class MoralKeeperAI:
    def __init__(
        self,
        timeout=60,
        max_retries=3,
        repeat=1,
    ):
        self.api_config = {
            'azure_endpoint': os.getenv('AZURE_OPENAI_ENDPOINT'),
            'api_key': os.getenv('AZURE_OPENAI_API_KEY'),
            'model': os.getenv('AZURE_OPENAI_DEPLOY_NAME'),
            'timeout': timeout,
            'max_retries': max_retries,
            'repeat': repeat,
        }

        self.check_ai = CheckAI(self.api_config)
        self.suggest_ai = SuggestAI(self.api_config)

    def check(self, content):
        return self.check_ai.check(content)

    def suggest(self, content):
        return self.suggest_ai.suggest(content)
