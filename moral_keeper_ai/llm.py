import asyncio
import json
import os

from openai import (
    AsyncAzureOpenAI,
    AzureOpenAI,
    BadRequestError,
    PermissionDeniedError,
    RateLimitError,
)


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


class AsyncLLM:
    def __init__(self, repeat, timeout, max_retries, api_key, azure_endpoint, model):
        self.model = model or os.getenv("LLM_MODEL")
        self.client = AsyncAzureOpenAI(
            api_key=api_key or os.getenv("AZURE_OPENAI_KEY"),
            api_version="2023-05-15",
            azure_endpoint=azure_endpoint or os.getenv("AZURE_ENDPOINT"),
            timeout=timeout,
            max_retries=max_retries,
        )
        self.repeat = repeat

    async def _chat(self, request, json_mode=False):
        args = {
            'model': request.get('model', self.model),
            'messages': request.get('message'),
            'n': self.repeat,
        }
        if json_mode:
            args['response_format'] = {"type": "json_object"}
        return await self.client.chat.completions.create(**args)

    def chat(self, requests, json_mode=False):
        for error_retry in range(3):
            try:
                ai_responses = asyncio.get_event_loop().run_until_complete(
                    asyncio.gather(
                        *[self._chat(request, json_mode=True) for request in requests]
                    )
                )
                ans = []
                for response in ai_responses:
                    for choice in response.choices:
                        if not json_mode:
                            ans.append(choice.message.content)
                        else:
                            ans.append(json.loads(choice.message.content))
                return ans
            except BadRequestError:
                if not json_mode:
                    ans = None
                else:
                    ans = [
                        {
                            "OpenAI Filter": False,
                        }
                    ]
            except RateLimitError:
                if not json_mode:
                    ans = None
                else:
                    ans = [
                        {
                            "RateLimitError": False,
                        }
                    ]
            except PermissionDeniedError as e:
                print(e)
                if not json_mode:
                    ans = None
                else:
                    ans = [
                        {
                            "APIConnectionError": False,
                        }
                    ]
            except json.decoder.JSONDecodeError:
                continue
            return ans
