import json
import os

from dotenv import load_dotenv
from openai import AsyncAzureOpenAI, AzureOpenAI, BadRequestError

load_dotenv()


class LLM:
    def __init__(self, api_key=None, azure_endpoint=None, model=None):
        self.api_key = api_key if api_key is not None else os.getenv("AZURE_OPENAI_KEY")
        self.azure_endpoint = (
            azure_endpoint
            if azure_endpoint is not None
            else os.getenv("AZURE_ENDPOINT")
        )
        self.model = model if model is not None else os.getenv("LLM_MODEL")

        self.client = AzureOpenAI(
            api_key=self.api_key,
            api_version="2023-05-15",
            azure_endpoint=self.azure_endpoint,
        )

    def chat(self, system_prompt: str, prompt: str):
        prompt = [{"role": "system", "content": system_prompt}] + [
            {"role": "user", "content": prompt}
        ]
        try:
            response = self.client.chat.completions.create(
                model=self.model, messages=prompt
            )
        except BadRequestError as e:
            return e
        except Exception as e:
            print(e)
            return None

        return response.choices[0].message.content

    def json_mode_chat(self, system_prompt, prompt: str):
        prompt = [{"role": "system", "content": system_prompt}] + [
            {"role": "user", "content": prompt}
        ]
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=prompt,
            )
        except BadRequestError:
            return {
                "OpenAI Filter": False,
            }
        except Exception as e:
            print(e)
            return None

        return json.loads(response.choices[0].message.content)


class AsyncLLM:
    def __init__(self, api_key=None, azure_endpoint=None, model=None):
        self.api_key = api_key if api_key is not None else os.getenv("AZURE_OPENAI_KEY")
        self.azure_endpoint = (
            azure_endpoint
            if azure_endpoint is not None
            else os.getenv("AZURE_ENDPOINT")
        )
        self.model = model if model is not None else os.getenv("LLM_MODEL")

        self.client = AsyncAzureOpenAI(
            api_key=self.api_key,
            api_version="2023-05-15",
            azure_endpoint=self.azure_endpoint,
        )

    async def chat(self, system_prompt, prompt: str):
        prompt = [{"role": "system", "content": system_prompt}] + [
            {"role": "user", "content": prompt}
        ]
        try:
            response = await self.client.chat.completions.create(
                model=self.model, messages=prompt
            )
        except Exception as e:
            print(e)
            return None

        return response.choices[0].message.content

    async def json_mode_chat(self, system_prompt, prompt: str):
        prompt = [{"role": "system", "content": system_prompt}] + [
            {"role": "user", "content": prompt}
        ]
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=prompt,
            )
        except BadRequestError:
            return {
                "OpenAI Filter": False,
            }
        except Exception as e:
            print(e)
            return None

        return json.loads(response.choices[0].message.content)
