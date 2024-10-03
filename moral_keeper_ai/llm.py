import json
from logging import getLogger

from openai import (
    AuthenticationError,
    AzureOpenAI,
    BadRequestError,
    PermissionDeniedError,
    RateLimitError,
)

logger = getLogger(__name__)


class Llm:
    def __init__(self, azure_endpoint, api_key, model, timeout, max_retries, repeat=1):
        self.model = model
        self.client = AzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_key=api_key,
            api_version='2024-06-01',
            timeout=timeout,
            max_retries=max_retries,
        )
        self.repeat = repeat

    def get_base_model_name(self):
        try:
            return self.client.chat.completions.create(
                model=self.model,
                messages=[{'role': 'system', 'content': ''}],
                max_tokens=1,
            ).model
        except Exception as e:
            logger.error(e)
            return ""

    def chat(self, messages: list) -> list:
        for error_retry in range(3):
            try:
                choices = self.client.chat.completions.create(
                    model=self.model,
                    response_format={'type': 'json_object'},
                    messages=messages,
                    n=self.repeat,
                ).choices
                contents = [json.loads(choice.message.content) for choice in choices]
            except BadRequestError as e:
                logger.warning(e)
                contents = [
                    {
                        'OpenAI Filter': False,
                    }
                ]
            except RateLimitError as e:
                logger.warning(e)
                contents = [
                    {
                        'RateLimitError': False,
                    }
                ]
            except PermissionDeniedError as e:
                logger.warning(e)
                contents = [
                    {
                        'APIConnectionError': False,
                    }
                ]
            except AuthenticationError as e:
                logger.warning(e)
                contents = [
                    {
                        'APIAuthenticationError': False,
                    }
                ]
            except json.decoder.JSONDecodeError:
                continue

            return contents
