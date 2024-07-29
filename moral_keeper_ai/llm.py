import json
import os

from openai import AzureOpenAI, BadRequestError, RateLimitError


class LLM:
    def __init__(self, repeat, api_key=None, azure_endpoint=None, model=None):
        self.model = model or os.getenv("LLM_MODEL")
        self.client = AzureOpenAI(
            api_key=api_key or os.getenv("AZURE_OPENAI_KEY"),
            api_version="2023-05-15",
            azure_endpoint=azure_endpoint or os.getenv("AZURE_ENDPOINT"),
            max_retries=10,
            timeout=300,
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

        try:
            ai_responses = [
                ret.message.content
                for ret in self.client.chat.completions.create(**args).choices
            ]
            if not json_mode:
                return ai_responses
            else:
                return [json.loads(response) for response in ai_responses]

        except BadRequestError:
            print("BadRequestError")
            if not json_mode:
                return None
            else:
                return {
                    "OpenAI Filter": False,
                }
        except RateLimitError as e:
            # TODO: 握りつぶさない
            print("RateLimitError")
            print(e.response.headers)
            print(e)
            return None
        except Exception as e:
            # TODO: 握りつぶさない
            print("Other Error")
            print(e)
            return None
