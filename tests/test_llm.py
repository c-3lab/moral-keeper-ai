import os
from unittest.mock import MagicMock, call, patch

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
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


@pytest.fixture
def mock_azure_openai_client():
    with patch('moral_keeper_ai.llm.AzureOpenAI') as mock:
        mock_client = MagicMock()
        mock.return_value = mock_client
        yield mock_client


class TestLlm:
    def test_chat(self, mock_azure_openai_client):
        response_content = load_test_data('check_gpt_4o_true.json')
        mock_response = create_mock_completion_response(response_content)
        mock_azure_openai_client.chat.completions.create.return_value = mock_response

        llm = Llm(
            azure_endpoint='test_endpoint',
            api_key='test_api_key',
            model='test_model',
            timeout=10,
            max_retries=1,
        )

        result = llm.chat('test_content')

        parameter = mock_azure_openai_client.chat.completions.create.mock_calls
        expected_parameter = [
            call(
                model='test_model',
                response_format={'type': 'json_object'},
                messages='test_content',
                n=1,
            )
        ]
        assert parameter == expected_parameter

        expected_result = [
            {
                'No personal attacks': True,
                'No discrimination': True,
                'No threats or violence': True,
                'No privacy violations': True,
                'No obscene language': True,
                'No sexual content': True,
                'Child-friendly': True,
                'No harassment': True,
                'No political promotion': True,
                'No religious solicitation': True,
                'Accurate info': True,
                'No rumors': True,
                'Correct health info': True,
                'Protection of brand image': True,
                'No defamation or unwarranted criticism': True,
                'Legal compliance and regulations': True,
                'Adherence to company policies': True,
            }
        ]
        assert result == expected_result

    def test_chat_handle_bad_request_error(self, mock_azure_openai_client):
        mock_azure_openai_client.chat.completions.create.side_effect = BadRequestError(
            message='error', response=MagicMock(), body=MagicMock()
        )

        llm = Llm(
            azure_endpoint='test_endpoint',
            api_key='test_api_key',
            model='test_model',
            timeout=10,
            max_retries=1,
        )

        expected_result = [
            {
                'OpenAI Filter': False,
            }
        ]
        assert llm.chat('test_content') == expected_result

    def test_chat_handle_rate_limit_error(self, mock_azure_openai_client):
        mock_azure_openai_client.chat.completions.create.side_effect = RateLimitError(
            message='error', response=MagicMock(), body=MagicMock()
        )

        llm = Llm(
            azure_endpoint='test_endpoint',
            api_key='test_api_key',
            model='test_model',
            timeout=10,
            max_retries=1,
        )

        expected_result = [
            {
                'RateLimitError': False,
            }
        ]
        assert llm.chat('test_content') == expected_result

    def test_chat_handle_permission_denied_error(self, mock_azure_openai_client):
        mock_azure_openai_client.chat.completions.create.side_effect = (
            PermissionDeniedError(
                message='error', response=MagicMock(), body=MagicMock()
            )
        )

        llm = Llm(
            azure_endpoint='test_endpoint',
            api_key='test_api_key',
            model='test_model',
            timeout=10,
            max_retries=1,
        )

        expected_result = [
            {
                'APIConnectionError': False,
            }
        ]
        assert llm.chat('test_content') == expected_result

    def test_chat_handle_json_decode(self, mock_azure_openai_client):
        mock_error_response = create_mock_completion_response('not json format string')
        response_content = load_test_data('check_gpt_4o_true.json')
        mock_response = create_mock_completion_response(response_content)
        mock_azure_openai_client.chat.completions.create.side_effect = [
            mock_error_response,
            mock_error_response,
            mock_response,
        ]

        llm = Llm(
            azure_endpoint='test_endpoint',
            api_key='test_api_key',
            model='test_model',
            timeout=10,
            max_retries=1,
        )

        expected_result = [
            {
                'No personal attacks': True,
                'No discrimination': True,
                'No threats or violence': True,
                'No privacy violations': True,
                'No obscene language': True,
                'No sexual content': True,
                'Child-friendly': True,
                'No harassment': True,
                'No political promotion': True,
                'No religious solicitation': True,
                'Accurate info': True,
                'No rumors': True,
                'Correct health info': True,
                'Protection of brand image': True,
                'No defamation or unwarranted criticism': True,
                'Legal compliance and regulations': True,
                'Adherence to company policies': True,
            }
        ]
        assert llm.chat('test_content') == expected_result

    def test_chat_handle_json_decode_error(self, mock_azure_openai_client):
        mock_response = create_mock_completion_response('not json format string')
        mock_azure_openai_client.chat.completions.create.side_effect = [
            mock_response,
            mock_response,
            mock_response,
        ]

        llm = Llm(
            azure_endpoint='test_endpoint',
            api_key='test_api_key',
            model='test_model',
            timeout=10,
            max_retries=1,
        )

        assert llm.chat('test_content') is None

    def test_get_base_model_name(self, mock_azure_openai_client):
        mock_azure_openai_client.chat.completions.create.return_value.model = (
            'test_model'
        )

        llm = Llm(
            azure_endpoint='test_endpoint',
            api_key='test_api_key',
            model='test_model',
            timeout=10,
            max_retries=1,
        )

        assert llm.get_base_model_name() == 'test_model'
