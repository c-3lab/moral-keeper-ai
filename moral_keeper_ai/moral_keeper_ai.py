import json

from langchain_core.prompts import PromptTemplate

from moral_keeper_ai.criateria import Criteria

from .llm import LLM


class CheckAI:
    def __init__(self, repeat, timeout, max_retries, api_key, azure_endpoint, model):
        self.llm = LLM(repeat, timeout, max_retries, api_key, azure_endpoint, model)

        self.system_template = PromptTemplate.from_template(
            'You are an excellent PR representative for a company.\n'
            'Please evaluate the received text based on the following '
            'criteria to output JSON.\n'
            '# output\n'
            '```JSON\n'
            '{criteria_prompt}'
            '```\n'
        )

    def check(self, content, criteria, perspectives):
        _criteria_dict = {criterion: True for criterion in criteria.to_prompts()}
        if perspectives:
            _criteria_dict.update({perspective: True for perspective in perspectives})
        _system_prompt = self.system_template.format(
            criteria_prompt=json.dumps(_criteria_dict, indent=2)
        )
        messages = [{"role": "system", "content": _system_prompt}] + [
            {"role": "user", "content": content}
        ]
        details = []
        for ans in self.llm.chat(messages, json_mode=True):
            if ans is not None:
                print('.', end='')
                details.extend([k for k, v in ans.items() if not v])
        details = list(dict.fromkeys(details))
        judgment = bool(0 == len(details))
        return (judgment, details)


class SuggestAI:
    def __init__(self, repeat, timeout, max_retries, api_key, azure_endpoint, model):
        self.llm = LLM(repeat, timeout, max_retries, api_key, azure_endpoint, model)

        self.system_template = (
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

    def suggest(self, content):
        system_prompt = self.system_template
        messages = [{"role": "system", "content": system_prompt}] + [
            {"role": "user", "content": content}
        ]

        for _ in range(3):
            response = self.llm.chat(
                messages,
                json_mode=True,
            )
            for ans in response:
                if ret := ans.get('revised_and_moderated_comments', False):
                    return ret
        return None


class MoralKeeperAI:
    def __init__(
        self,
        api_key=None,
        azure_endpoint=None,
        model=None,
        repeat=1,
        timeout=60,
        max_retries=3,
    ):
        self.check_ai = CheckAI(
            repeat=repeat,
            timeout=timeout,
            max_retries=max_retries,
            api_key=api_key,
            azure_endpoint=azure_endpoint,
            model=model,
        )
        self.suggest_ai = SuggestAI(
            repeat=repeat,
            timeout=timeout,
            max_retries=max_retries,
            api_key=api_key,
            azure_endpoint=azure_endpoint,
            model=model,
        )

    def check(self, content, criteria=Criteria.ALL, perspectives=[]):
        return self.check_ai.check(
            content=content, criteria=criteria, perspectives=perspectives
        )

    def suggest(self, content):
        return self.suggest_ai.suggest(content=content)
