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
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Test data file {filename} not found.")
    except IOError as e:
        raise IOError(f"Error reading file {filename}: {e}")

# AzureOpenAIのモッククライアントを提供するフィクスチャ
@pytest.fixture
def mock_azure_openai_client():
    with patch('moral_keeper_ai.llm.AzureOpenAI') as mock:
        mock_client = MagicMock()
        mock.return_value = mock_client
        yield mock_client

# MoralKeeperAIのインスタンスを提供するフィクスチャ
@pytest.fixture
def moral_keeper_ai_instance():
    return MoralKeeperAI()

class TestMoralKeeperAI:
    # チェック機能でTrueが返る場合のテスト
    def test_check_function_returns_true(self, mock_azure_openai_client, moral_keeper_ai_instance):
        # テストデータを読み込み、モックレスポンスを作成
        response_content = load_test_data('check_true.json')
        mock_response = create_mock_completion_response(response_content)
        mock_azure_openai_client.chat.completions.create.return_value = mock_response
        
        # checkメソッドを呼び出し、結果を検証
        result = moral_keeper_ai_instance.check("test_content")
        expected_result = (True, [])
        assert result == expected_result, f"Expected {expected_result} but got {result}"

    # チェック機能でFalseが返る場合のテスト
    def test_check_function_returns_false(self, mock_azure_openai_client, moral_keeper_ai_instance):
        response_content = load_test_data('check_false.json')
        mock_response = create_mock_completion_response(response_content)
        mock_azure_openai_client.chat.completions.create.return_value = mock_response

        result = moral_keeper_ai_instance.check("test_content")

        expected_result = (False, ['No personal attacks'])
        assert result == expected_result, f"Expected {expected_result} but got {result}"

    # サジェスト機能のテスト
    def test_suggest_function(self, mock_azure_openai_client, moral_keeper_ai_instance):
        response_content = load_test_data('suggest.json')
        mock_response = create_mock_completion_response(response_content)
        mock_azure_openai_client.chat.completions.create.return_value = mock_response

        result = moral_keeper_ai_instance.suggest(
            "このデータは古すぎて役に立たない。もっと新しいものをアップロードしてくれ。"
        )

        expected_result = (
            '公開されているデータが古いため、最新のデータをご提供いただけると大変助かります。例えば、（具体的な例：最新の人口統計情報や交通状況のデータ）などがあると、より有益です。どうぞご検討ください。'
        )
        assert result == expected_result, f"Expected {expected_result} but got {result}"