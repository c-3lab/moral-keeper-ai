import json

from openai import AzureOpenAI, BadRequestError, PermissionDeniedError, RateLimitError


class Llm:
    def __init__(self, azure_endpoint, api_key, model, timeout, max_retries, repeat=1):
        self.model = model
        self.client = AzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=api_key,
            api_version="2024-06-01",
            timeout=timeout,
            max_retries=max_retries,
        )
        self.repeat = repeat

    def get_base_model_name(self):
        return self.client.chat.completions.create(
            model=self.model, messages=[{'role': 'system', 'content': ''}], max_tokens=1
        ).model

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
