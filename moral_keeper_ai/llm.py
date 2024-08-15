import json

from openai import AzureOpenAI, BadRequestError, PermissionDeniedError, RateLimitError


class Llm:
    def __init__(self, azure_endpoint, api_key, model):
        self.model = model
        self.client = AzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=api_key,
            api_version="2023-05-15",
        )

    def chat(self, messages: list, json_mode=False) -> list:
        args = {
            'model': self.model,
            'messages': messages,
        }
        if json_mode:
            args['response_format'] = {"type": "json_object"}

        for error_retry in range(3):
            try:
                ai_response = (
                    self.client.chat.completions.create(**args)
                    .choices[0]
                    .message.content
                )
                if not json_mode:
                    ret = ai_response
                else:
                    ret = json.loads(ai_response)
            except BadRequestError:
                if not json_mode:
                    ret = None
                else:
                    ret = {
                        "OpenAI Filter": False,
                    }
            except RateLimitError:
                if not json_mode:
                    ret = None
                else:
                    ret = {
                        "RateLimitError": False,
                    }
            except PermissionDeniedError as e:
                print(e)
                if not json_mode:
                    ret = None
                else:
                    ret = {
                        "APIConnectionError": False,
                    }
            except json.decoder.JSONDecodeError:
                continue

            return ret
