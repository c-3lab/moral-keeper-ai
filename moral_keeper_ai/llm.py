import json
import os

from dotenv import load_dotenv
from openai import AzureOpenAI, BadRequestError

load_dotenv()


class LLM:
    def __init__(self, system_prompt, json_mode=False):
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version="2023-05-15",
            azure_endpoint=os.getenv("AZURE_ENDPOINT"),
        )
        self.model = os.getenv("LLM_MODEL")

        self.system_prompt = system_prompt
        if json_mode:
            self.response_format = {"type": "json_object"}
        else:
            self.response_format = None

    def chat(self, prompt: str):
        prompt = [{"role": "system", "content": self.system_prompt}] + [
            {"role": "user", "content": prompt}
        ]
        try:
            response = self.client.chat.completions.create(
                model=self.model, response_format=self.response_format, messages=prompt
            )
        except BadRequestError as e:
            # print(e)
            if self.response_format:
                return {
                    "OpenAI Filter": False,
                }
            else:
                return e
        except Exception as e:
            print(e)
            return None

        if self.response_format:
            return json.loads(response.choices[0].message.content)
        else:
            return response.choices[0].message.content
