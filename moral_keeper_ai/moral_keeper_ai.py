import asyncio

from langchain_core.prompts import PromptTemplate

from . import llm


class Criteria:
    # check category mask
    VIOLENT = 0b00000001
    INAPPROPRIATE = 0b00000010
    SENSITIVE = 0b00000100
    INACCURATE = 0b00001000
    DISREPUTE = 0b00010000

    # check category string
    violent = 'violent'
    inappropriate = 'inappropriate'
    sensitive = 'sensitive'
    inaccurate = 'inaccurate'
    disrepute = 'disrepute'

    category_mask_to_name = {
        VIOLENT: violent,
        INAPPROPRIATE: inappropriate,
        SENSITIVE: sensitive,
        INACCURATE: inaccurate,
        DISREPUTE: disrepute,
    }

    category_mask_list = [VIOLENT, INAPPROPRIATE, SENSITIVE, INACCURATE, DISREPUTE]

    # check points
    check_list = {
        violent: [
            "No personal attacks",
            "No discrimination",
            "No threats or violence",
            "No privacy violations",
        ],
        inappropriate: [
            "No obscene language",
            "No sexual content",
            "Child-friendly",
            "No harassment",
        ],
        sensitive: [
            "No political promotion",
            "No religious solicitation",
        ],
        inaccurate: [
            "Accurate info",
            "No rumors",
            "Correct health info",
        ],
        disrepute: [
            "Protection of brand image",
            "No defamation or unwarranted criticism",
            "Legal compliance and regulations",
            "Adherence to company policies",
        ],
        # violent: [
        #     "Legal compliance",
        #     "Compliance with company policies",
        #     "Use appropriate expressions for public communication",
        #     "No violent or obscene content",
        #     "No privacy violations",
        #     "Protection of brand image",
        #     "Confirmation of positive feedback",
        #     "Maintain integrity in the message",
        #     "Spam check",
        #     "No political statements",
        # ],
    }

    def get_check_point_list(check_category_mask=0b11111111):
        # ret = set([]) 順番が保たれない
        ret = []
        for mask in Criteria.category_mask_list:
            if not check_category_mask & mask:
                continue
            for checkpoint in Criteria.check_list[Criteria.category_mask_to_name[mask]]:
                if checkpoint not in ret:
                    ret.append(checkpoint)
        return list(ret)


class CheckAI:
    def __init__(self, api_key=None, azure_endpoint=None, model=None, async_mode=False):
        self.async_mode = async_mode
        if async_mode:
            self.llm = llm.AsyncLLM(api_key, azure_endpoint, model)
        else:
            self.llm = llm.LLM(api_key, azure_endpoint, model)

        self.criteria = Criteria

        self.check_system_template = PromptTemplate.from_template(
            'You are an excellent PR representative for a company.\n'
            'Please evaluate the received text based on the following '
            'criteria to output JSON.\n'
            '# output\n'
            '```JSON\n'
            '{checklist}'
            '```\n'
        )
        # checkメソッドでチェックカテゴリの指定が無い場合、全てのチェック観点を使用する。
        check_list_prompt = '{\n'
        for check_point in Criteria.get_check_point_list(0b11111111):
            check_list_prompt += f'  "{check_point}": True,\n'
        check_list_prompt += '}\n'
        self.default_check_system_prompt = self.check_system_template.format(
            checklist=check_list_prompt
        )

    def _get_system_prompt(self, check_category):
        if check_category is not None:
            # チェックリストをシステムプロンプトに含めるJSON形式の文字列に成型
            check_list_prompt = '{\n'
            for check_point in Criteria.get_check_point_list(check_category):
                check_list_prompt += f'  "{check_point}": True,\n'
            check_list_prompt += '}\n'
            # システムプロンプトの作成
            system_prompt = self.check_system_template.format(
                checklist=check_list_prompt
            )
        else:
            system_prompt = self.default_check_system_prompt
        return system_prompt

    def _get_responce(self, system_prompt, content, repeat_check):
        responces = []
        if self.async_mode:
            check_tasks = [
                self.llm.json_mode_chat(system_prompt=system_prompt, prompt=content)
                for _ in range(repeat_check)
            ]

            responces = asyncio.get_event_loop().run_until_complete(
                asyncio.gather(*check_tasks)
            )
        else:
            for _ in range(repeat_check):
                responces.append(
                    self.llm.json_mode_chat(system_prompt=system_prompt, prompt=content)
                )
        return responces

    def check(self, content, check_category=None, repeat_check=1):
        system_prompt = self._get_system_prompt(check_category)
        responces = self._get_responce(system_prompt, content, repeat_check)
        responces = [responce for responce in responces if responce is not None]

        if not len(responces):
            return (False, ['Error'])

        judgment = True
        details = set([])
        for responce in responces:
            for key, value in responce.items():
                if value is False:
                    judgment = False
                    details.add(key)

        return (judgment, list(details))


# class SuggestAI(LLM):
#     def __init__(self, api_key=None, azure_endpoint=None, model=None):
#         pass


class MoralKeeperAI:
    def __init__(self, api_key=None, azure_endpoint=None, model=None):
        # AIからレスポンスを得る時に使用する。
        self.api_key = api_key
        self.azure_endpoint = azure_endpoint
        self.model = model
        self.check_ai = CheckAI(api_key, azure_endpoint, model, async_mode=True)
        # self.suggest_ai = SuggestAI(api_key, azure_endpoint, model)

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

        self.criteria = Criteria()

    def check(self, content, check_category=None, repeat_check=1, async_mode=True):
        if async_mode and type(self.check_ai) is not llm.AsyncAzureOpenAI:
            self.check_ai = CheckAI(
                self.api_key, self.azure_endpoint, self.model, async_mode=True
            )
        if async_mode is False and type(self.check_ai) is not llm.AzureOpenAI:
            self.check_ai = CheckAI(
                self.api_key, self.azure_endpoint, self.model, async_mode=False
            )

        return self.check_ai.check(
            content=content, check_category=check_category, repeat_check=repeat_check
        )

    def suggest(self, content):
        system_prompt = self.default_suggest_system_prompt

        ai = llm.LLM(system_prompt, json_mode=True)
        for _ in range(3):
            responce = ai.chat(content)
            if ret := responce.get('revised_and_moderated_comments', False):
                return ret
        return None
