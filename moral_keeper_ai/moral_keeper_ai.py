import asyncio
import json

from langchain_core.prompts import PromptTemplate

from moral_keeper_ai.criateria import Criteria

from . import llm


class CheckAI:
    def __init__(self, repeat, api_key, azure_endpoint, model, async_mode):
        self.async_mode = async_mode
        self.repeat = repeat

        if async_mode:
            self.llm = llm.AsyncLLM(api_key, azure_endpoint, model)
        else:
            self.llm = llm.LLM(api_key, azure_endpoint, model)

        self.system_template = PromptTemplate.from_template(
            'You are an excellent PR representative for a company.\n'
            'Please evaluate the received text based on the following '
            'criteria to output JSON.\n'
            '# output\n'
            '```JSON\n'
            '{criteria_prompt}'
            '```\n'
        )

    def _get_system_prompt(self, category):
        criteria_dict = {prompt: True for prompt in category.to_prompts()}
        criteria_prompt = json.dumps(criteria_dict, indent=2)
        system_prompt = self.system_template.format(criteria_prompt=criteria_prompt)
        return system_prompt

    def _get_response(self, system_prompt, content):
        messages = [{"role": "system", "content": system_prompt}] + [
            {"role": "user", "content": content}
        ]

        responses = []
        if self.async_mode:
            responses = asyncio.get_event_loop().run_until_complete(
                asyncio.gather(
                    *[self.llm.chat_as_json(messages) for _ in range(self.repeat)]
                )
            )
        else:
            responses.extend(
                [self.llm.chat_as_json(messages) for _ in range(self.repeat)]
            )

        return responses

    def check(self, content, category):
        system_prompt = self._get_system_prompt(category)
        responses = self._get_response(system_prompt, content)
        responses = [response for response in responses if response is not None]

        if not len(responses):
            return (False, ['Error'])

        details = []
        for response in responses:
            details.extend([k for k, v in response.items() if not v])

        judgment = bool(details)

        return (judgment, list(details))


# class SuggestAI(LLM):
#     def __init__(self, api_key=None, azure_endpoint=None, model=None):
#         pass


class MoralKeeperAI:
    def __init__(
        self, api_key=None, azure_endpoint=None, model=None, async_mode=False, repeat=1
    ):
        self.check_ai = CheckAI(
            api_key=api_key,
            azure_endpoint=azure_endpoint,
            model=model,
            async_mode=async_mode,
            repeat=repeat,
        )

        # suggestメソッドのsystem prompt
        self.suggest_system_template = (
            'You are a professional content moderator.\n'
            '# Task Description\n'
            '- If the received text contains anti-comments, baseless accusations, or '
            'extreme expressions, perform the following tasks.\n'
            '- Alleviate the expressions in the received text, creating a revised '
            'version that removes offensive, defamatory, or excessively extreme '
            'expressions.\n'
            '- Adjust the text to appropriate expressions while retaining the '
            'original intent of the comment.\n\n'
            'The purpose of this task is to maintain a healthy communication '
            'environment on the site while maximizing respect for the intent of the '
            'comments.\n\n'
            '# output\n'
            '```JSON\n'
            '{\n'
            '    "revised_and_moderated_comments": ""\n'
            '}\n'
            '```\n'
        )
        self.default_suggest_system_prompt = self.suggest_system_template

    def check(self, content, category=Criteria.ALL):
        return self.check_ai.check(content=content, category=category)

    def suggest(self, content):
        system_prompt = self.default_suggest_system_prompt

        ai = llm.LLM(system_prompt, json_mode=True)
        for _ in range(3):
            response = ai.chat(content)
            if ret := response.get('revised_and_moderated_comments', False):
                return ret
        return None
