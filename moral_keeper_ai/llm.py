import json
from enum import IntFlag, auto

from openai import AzureOpenAI, BadRequestError, PermissionDeniedError, RateLimitError


class LLM:
    def __init__(self, azure_endpoint, api_key, model, timeout, max_retries, repeat):
        self.model = model
        self.client = AzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=api_key,
            api_version="2023-05-15",
            timeout=timeout,
            max_retries=max_retries,
        )
        self.repeat = repeat

    def chat(self, messages: list, json_mode=False) -> list:
        args = {
            'model': self.model,
            'messages': messages,
            'n': self.repeat,
        }
        if json_mode:
            args['response_format'] = {"type": "json_object"}

        for error_retry in range(3):
            try:
                ai_responses = [
                    ret.message.content
                    for ret in self.client.chat.completions.create(**args).choices
                ]
                if not json_mode:
                    ret = ai_responses
                else:
                    ret = [json.loads(response) for response in ai_responses]
            except BadRequestError:
                if not json_mode:
                    ret = None
                else:
                    ret = [
                        {
                            "OpenAI Filter": False,
                        }
                    ]
            except RateLimitError:
                if not json_mode:
                    ret = None
                else:
                    ret = [
                        {
                            "RateLimitError": False,
                        }
                    ]
            except PermissionDeniedError as e:
                print(e)
                if not json_mode:
                    ret = None
                else:
                    ret = [
                        {
                            "APIConnectionError": False,
                        }
                    ]
            except json.decoder.JSONDecodeError:
                continue

            return ret


class Models(IntFlag):
    GPT35_turbo = auto()
    GPT4o = auto()
    GPT4o_mini = auto()
