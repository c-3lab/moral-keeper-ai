from langchain_core.prompts import PromptTemplate

from . import llm


class criteria:
    # check category mask
    VIOLENT = 0b00000001
    INAPPROPRIATE = 0b00000010
    SENSITIVE = 0b00000100
    INACCURATE = 0b00001000
    DISREPUTE = 0b00010000
    # OLD_VIOLENT     =0b10000000

    # check category string
    violent = 'violent'
    inappropriate = 'inappropriate'
    sensitive = 'sensitive'
    inaccurate = 'inaccurate'
    disrepute = 'disrepute'
    # old_violent     = 'old_violent'

    category_mask_to_name = {
        VIOLENT: violent,
        INAPPROPRIATE: inappropriate,
        SENSITIVE: sensitive,
        INACCURATE: inaccurate,
        DISREPUTE: disrepute,
        # OLD_VIOLENT: old_violent,
    }

    category_mask_list = [VIOLENT, INAPPROPRIATE, SENSITIVE, INACCURATE, DISREPUTE]

    # check point
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
        # old_violent: [
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

    @staticmethod
    def get_check_point_list(check_category_mask):
        ret = []
        for mask in criteria.category_mask_list:
            if not check_category_mask & mask:
                continue
            ret += criteria.check_list[criteria.category_mask_to_name[mask]]
        return ret


def check(content, check_category):
    prompt_template = PromptTemplate.from_template(
        'You are an excellent PR representative for a company.\n'
        'Please evaluate the received text based on the following criteria to output '
        'JSON.\n'
        '# output\n'
        '```JSON\n'
        '{checklist}'
        '```\n'
    )

    # チェックリストをシステムプロンプトに含めるJSON形式の文字列に成型
    check_list_prompt = '{\n'
    for check_point in criteria.get_check_point_list(check_category):
        check_list_prompt += f'  "{check_point}": True,\n'
    check_list_prompt += '}\n'

    # システムプロンプトの作成
    system_prompt = prompt_template.format(checklist=check_list_prompt)
    # print(system_prompt)

    ai = llm.LLM(system_prompt, json_mode=True)
    responce = ai.chat(content)

    judgment = True
    details = []

    for key, value in responce.items():
        if value is False:
            judgment = False
            details.append(key)
    return (judgment, details)


def suggest(content):
    system_prompt = (
        'You are a professional content moderator.\n'
        '# Task Description\n'
        '- If the received text contains anti-comments, baseless accusations, or '
        'extreme expressions, perform the following tasks.\n'
        '- Alleviate the expressions in the received text, creating a revised version '
        'that removes offensive, defamatory, or excessively extreme expressions.\n'
        '- Adjust the text to appropriate expressions while retaining the original '
        'intent of the comment.\n\n'
        'The purpose of this task is to maintain a healthy communication environment '
        'on the site while maximizing respect for the intent of the comments.\n\n'
        '# output\n'
        '```JSON\n'
        '{\n'
        '    "revised_and_moderated_comments": ""\n'
        '}\n'
        '```\n'
    )

    ai = llm.LLM(system_prompt, json_mode=True)
    for _ in range(3):
        responce = ai.chat(content)
        if responce['revised_and_moderated_comments']:
            return responce['revised_and_moderated_comments']
    return None
