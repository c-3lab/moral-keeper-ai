import asyncio
import json
from enum import IntFlag, auto

from openai import (
    AsyncAzureOpenAI,
    AzureOpenAI,
    BadRequestError,
    PermissionDeniedError,
    RateLimitError,
)


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


class AsyncLLM:
    def __init__(self, azure_endpoint, api_key, model, timeout, max_retries, repeat):
        self.model = model
        self.client = AsyncAzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=api_key,
            api_version="2023-05-15",
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
            except BadRequestError as e:
                print(e)
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


class Models(IntFlag):
    GPT35_turbo = auto()
    GPT4o = auto()
    GPT4o_mini = auto()
