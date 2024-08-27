import json
import os
from unittest.mock import MagicMock, patch

import pytest
from openai import BadRequestError, PermissionDeniedError, RateLimitError

from moral_keeper_ai.llm import Llm


def create_mock_completion_response(content):
    mock_choice = MagicMock()
    mock_choice.message = MagicMock()
    mock_choice.message.content = content

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    return mock_response


def load_test_data(filename):
    file_path = os.path.join(os.path.dirname(__file__), 'test_data', filename)
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Test data file {filename} not found.")
    except IOError as e:
        raise IOError(f"Error reading file {filename}: {e}")


@pytest.fixture
def mock_azure_openai_client():
    with patch('moral_keeper_ai.llm.AzureOpenAI') as mock:
        mock_client = MagicMock()
        mock.return_value = mock_client
        yield mock_client


@pytest.fixture
def llm_instance():
    return Llm(
        azure_endpoint='test_endpoint',
        api_key='xxx',
        model='test_model',
        timeout=10,
        max_retries=1,
    )


class TestLlm:
    def test_chat(self, mock_azure_openai_client):
        response_content = load_test_data('check_true.json')
        mock_response = create_mock_completion_response(response_content)
        mock_azure_openai_client.chat.completions.create.return_value = mock_response

        llm = Llm(
            'test_endpoint',
            'test_api_key',
            'test_model',
            30,
            3,
        )

        result = llm.chat("test_content")
        expected_result = [json.loads(response_content)]
        assert result == expected_result, f"Expected {expected_result} but got {result}"

    def test_BadRequestError(self, mock_azure_openai_client):
        mock_azure_openai_client.chat.completions.create.side_effect = BadRequestError(
            message='error', response=MagicMock(), body=MagicMock()
        )

        llm = Llm(
            'test_endpoint',
            'test_api_key',
            'test_model',
            30,
            3,
        )

        result = llm.chat("test_content")
        expected_result = [
            {
                "OpenAI Filter": False,
            }
        ]
        assert result == expected_result, f"Expected {expected_result} but got {result}"

    def test_RateLimitError(self, mock_azure_openai_client):
        mock_azure_openai_client.chat.completions.create.side_effect = RateLimitError(
            message='error', response=MagicMock(), body=MagicMock()
        )

        llm = Llm(
            'test_endpoint',
            'test_api_key',
            'test_model',
            30,
            3,
        )

        result = llm.chat("test_content")
        expected_result = [
            {
                "RateLimitError": False,
            }
        ]
        assert result == expected_result, f"Expected {expected_result} but got {result}"

    def test_PermissionDeniedError(self, mock_azure_openai_client):
        mock_azure_openai_client.chat.completions.create.side_effect = (
            PermissionDeniedError(
                message='error', response=MagicMock(), body=MagicMock()
            )
        )

        llm = Llm(
            'test_endpoint',
            'test_api_key',
            'test_model',
            30,
            3,
        )

        result = llm.chat("test_content")
        expected_result = [
            {
                "APIConnectionError": False,
            }
        ]
        assert result == expected_result, f"Expected {expected_result} but got {result}"

    def test_JSONDecodeError(self, mock_azure_openai_client):
        mock_response = create_mock_completion_response("not json format string")
        mock_azure_openai_client.chat.completions.create.side_effect = [
            mock_response,
            mock_response,
            mock_response,
        ]

        llm = Llm(
            'test_endpoint',
            'test_api_key',
            'test_model',
            30,
            3,
        )

        result = llm.chat("test_content")
        expected_result = None
        assert result == expected_result, f"Expected {expected_result} but got {result}"

    def test_get_base_model_name(self, mock_azure_openai_client):
        mock_azure_openai_client.chat.completions.create.return_value.model = 'test_model'

        llm = Llm(
            'test_endpoint',
            'test_api_key',
            'test_model',
            30,
            3,
        )

        result = llm.get_base_model_name()
        expected_result = 'test_model'
        assert result == expected_result
