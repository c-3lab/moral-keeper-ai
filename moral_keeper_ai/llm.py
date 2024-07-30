import json
import os

from openai import AzureOpenAI, BadRequestError, RateLimitError


class LLM:
    def __init__(self, repeat, timeout, max_retries, api_key, azure_endpoint, model):
        self.model = model or os.getenv("LLM_MODEL")
        self.client = AzureOpenAI(
            api_key=api_key or os.getenv("AZURE_OPENAI_KEY"),
            api_version="2023-05-15",
            azure_endpoint=azure_endpoint or os.getenv("AZURE_ENDPOINT"),
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
            if not json_mode:
                return None
            else:
                return [
                    {
                        "OpenAI Filter": False,
                    }
                ]
        except RateLimitError:
            if not json_mode:
                return None
            else:
                return [
                    {
                        "RateLimitError": False,
                    }
                ]
