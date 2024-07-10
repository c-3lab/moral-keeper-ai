from . import llm


def check(content):
    system_prompt = (
        'You are an excellent PR representative for a company.\n'
        'Please evaluate the received text based on the following criteria to output '
        'JSON.\n'
        '# output\n'
        '```JSON\n'
        '{\n'
        '  "Legal compliance": true,\n'
        '  "Compliance with company policies": true,\n'
        '  "Use appropriate expressions for public communication": true,\n'
        '  "No violent or obscene content": true,\n'
        '  "No privacy violations": true,\n'
        '  "Protection of brand image": true,\n'
        '  "Confirmation of positive feedback": true,\n'
        '  "Maintain integrity in the message": true,\n'
        '  "Spam check": true,\n'
        '  "No political statements": true\n'
        '}\n'
        '```\n'
    )

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
