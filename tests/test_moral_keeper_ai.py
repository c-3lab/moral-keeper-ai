import pytest
import json
import os
from unittest.mock import patch, MagicMock

from moral_keeper_ai import MoralKeeperAI

# モックレスポンスを作成するヘルパー関数
def create_mock_completion_response(content):
    mock_choice = MagicMock()
    mock_choice.message = MagicMock()
    mock_choice.message.content = content

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    return mock_response

# テストデータを外部ファイルから読み込む
def load_test_data(filename):
    file_path = os.path.join(os.path.dirname(__file__), 'test_data', filename)
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# AzureOpenAIのモッククライアントを提供するフィクスチャ
@pytest.fixture
def mock_azure_openai_client():
    with patch('moral_keeper_ai.llm.AzureOpenAI') as mock:
        mock_client = MagicMock()
        mock.return_value = mock_client
        yield mock_client

class TestMoralKeeperAI:
    def test_initialize_ai_moral_keeper(self, mock_azure_openai_client):
        moral_keeper_ai = MoralKeeperAI()
        expected_result = {'azure_endpoint': 'https://example.com/azure', 'api_key': 'dummy-apikey', 'model': 'gpt-35-turbo', 'timeout': 60, 'max_retries': 3, 'repeat': 1}
        assert moral_keeper_ai.api_config == expected_result

    # チェック機能でTrueが返る場合のテスト
    @pytest.mark.parametrize(
        'model',
        ['gpt-4o', 'gpt-4o-mini', 'gpt-35-turbo']
    )
    def test_check_function_with_true_response(self, mock_azure_openai_client, model):
        if model in ['gpt-35-turbo']:
            response_content = load_test_data('check_gpt_35_true.json')
        if model in ['gpt-4o', 'gpt-4o-mini']:
            response_content = load_test_data('check_gpt_4o_true.json')
        mock_response = create_mock_completion_response(response_content)

        def mocked_create(*args, model, **kwargs):
            mock_response.model = model
            return mock_response

        mock_azure_openai_client.chat.completions.create.side_effect = mocked_create

        with patch.dict(os.environ, {'AZURE_OPENAI_DEPLOY_NAME': model}):
            moral_keeper_ai = MoralKeeperAI()
            result = moral_keeper_ai.check("この地域の交通量データはとても役立ちますね。将来の交通計画に活かせると思います。")

        assert result == (True, [])

    # チェック機能でFalseが返る場合のテスト
    @pytest.mark.parametrize(
        'model',
        ['gpt-4o', 'gpt-4o-mini', 'gpt-35-turbo']
    )
    def test_check_function_with_false_response(self, mock_azure_openai_client, model):
        if model in ['gpt-35-turbo']:
            response_content = load_test_data('check_gpt_35_false.json')
        if model in ['gpt-4o', 'gpt-4o-mini']:
            response_content = load_test_data('check_gpt_4o_false.json')
        mock_response = create_mock_completion_response(response_content)

        def mocked_create(*args, model, **kwargs):
            mock_response.model = model
            return mock_response

        mock_azure_openai_client.chat.completions.create.side_effect = mocked_create

        with patch.dict(os.environ, {'AZURE_OPENAI_DEPLOY_NAME': model}):
            moral_keeper_ai = MoralKeeperAI()
            result = moral_keeper_ai.check("お前みたいなバカがいるから、このプロジェクトはいつまでたっても進まないんだよ。いい加減にしろ！")

        if '35' in model:
            assert result == (False, ["Use appropriate expressions for public communication", "Protection of brand image", "The feedback is not negative"])
        if '4o' in model:
            assert result == (False, ['No personal attacks', 'No discrimination'])

    # サジェスト機能のテスト
    def test_suggest_function(self, mock_azure_openai_client):
        response_content = load_test_data('suggest.json')
        mock_response = create_mock_completion_response(response_content)
        mock_azure_openai_client.chat.completions.create.return_value = mock_response

        moral_keeper_ai = MoralKeeperAI()
        result = moral_keeper_ai.suggest("このデータは古すぎて役に立たない。もっと新しいものをアップロードしてくれ。")
        expected_result = (
            '公開されているデータが古いため、最新のデータをご提供いただけると大変助かります。例えば、（具体的な例：最新の人口統計情報や交通状況のデータ）などがあると、より有益です。どうぞご検討ください。'
        )
        assert result == expected_result

    # サジェスト機能でNoneが返る場合のテスト
    def test_suggest_function_with_none_response(self, mock_azure_openai_client):
        response_content = "{}"
        mock_response = create_mock_completion_response(response_content)
        mock_azure_openai_client.chat.completions.create.return_value = mock_response

        moral_keeper_ai = MoralKeeperAI()
        result = moral_keeper_ai.suggest("このデータは古すぎて役に立たない。もっと新しいものをアップロードしてくれ。")
        assert result == None