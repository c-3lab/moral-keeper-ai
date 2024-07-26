import json
import os

from openai import AsyncAzureOpenAI, AzureOpenAI, BadRequestError, RateLimitError


class LLM:
    def __init__(self, api_key=None, azure_endpoint=None, model=None):
        self.model = model or os.getenv("LLM_MODEL")
        self.client = AzureOpenAI(
            api_key=api_key or os.getenv("AZURE_OPENAI_KEY"),
            api_version="2023-05-15",
            azure_endpoint=azure_endpoint or os.getenv("AZURE_ENDPOINT"),
            max_retries=10,
            timeout=300,
        )

    def chat(self, system_prompt: str, content: str):
        messages = [{"role": "system", "content": system_prompt}] + [
            {"role": "user", "content": content}
        ]
        try:
            response = self.client.chat.completions.create(
                model=self.model, messages=messages
            )
        except BadRequestError as e:
            return e
        except Exception as e:
            print(e)
            return None

        return response.choices[0].message.content

    def chat_as_json(self, messages):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=messages,
            )
            return json.loads(response.choices[0].message.content)
        except BadRequestError:
            return {
                "OpenAI Filter": False,
            }
        except Exception as e:
            print(e)
            return None


class AsyncLLM:
    def __init__(self, api_key=None, azure_endpoint=None, model=None):
        self.model = model or os.getenv("LLM_MODEL")
        self.client = AsyncAzureOpenAI(
            api_key=api_key or os.getenv("AZURE_OPENAI_KEY"),
            api_version="2023-05-15",
            azure_endpoint=azure_endpoint or os.getenv("AZURE_ENDPOINT"),
            max_retries=10,
            timeout=300,
        )

    async def chat(self, system_prompt, content: str):
        messages = [{"role": "system", "content": system_prompt}] + [
            {"role": "user", "content": content}
        ]
        try:
            response = await self.client.chat.completions.create(
                model=self.model, messages=messages
            )
        except Exception as e:
            print(e)
            return None

        return response.choices[0].message.content

    async def chat_as_json(self, messages):
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=messages,
            )
            return json.loads(response.choices[0].message.content)
        except BadRequestError:
            print("BadRequestError")
            return {
                "OpenAI Filter": False,
            }
        except RateLimitError as e:
            print("RateLimitError")
            print(e.response.headers)
            print(e)
            return None
        except Exception as e:
            print("Other Error")
            print(e)
            return None
