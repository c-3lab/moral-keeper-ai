import pytest
from unittest.mock import patch, call, MagicMock
from moral_keeper_ai import MoralKeeperAI

# 指定されたコンテンツでモックレスポンスを作成
def create_mock_response(content):
    mock_choice = MagicMock()
    mock_choice.message.content = content
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    return mock_response

class TestMoralKeeperAI:
    # Trueが返ってくる想定のパターンテスト
    @patch('moral_keeper_ai.llm.AzureOpenAI')
    def test_check_true(self, mock_client):
        # AzureOpenAIからの模擬応答
        content = """{
    "No personal attacks": true,
    "No discrimination": true,
    "No threats or violence": true,
    "No privacy violations": true,
    "No obscene language": true,
    "No sexual content": true,
    "Child-friendly": true,
    "No harassment": true,
    "No political promotion": true,
    "No religious solicitation": true,
    "Accurate info": true,
    "No rumors": true,
    "Correct health info": true,
    "Protection of brand image": true,
    "No defamation or unwarranted criticism": true,
    "Legal compliance and regulations": true,
    "Adherence to company policies": true
}"""

        # 関数を呼び出し、模擬応答オブジェクトを作成
        mock_response = create_mock_response(content)
        mock_azure_open_ai = MagicMock()
        mock_azure_open_ai.chat.completions.create.return_value = mock_response
        mock_client.return_value = mock_azure_open_ai
        
        # インスタンスを作成し、モッククライアントを割り当てる
        ai = MoralKeeperAI()
        ai.check_ai = mock_client
        
        # checkメソッドを呼び出し結果を取得
        result = ai.check("test_content")

        # 結果が期待通りの結果かチェック
        expected_result = (True, [])
        assert result == expected_result

    # Falseが返ってくる想定のパターンテスト
    @patch('moral_keeper_ai.llm.AzureOpenAI')
    def test_check_false(self, mock_client):
        content = """{
    "No personal attacks": false,
    "No discrimination": true,
    "No threats or violence": true,
    "No privacy violations": true,
    "No obscene language": true,
    "No sexual content": true,
    "Child-friendly": true,
    "No harassment": true,
    "No political promotion": true,
    "No religious solicitation": true,
    "Accurate info": true,
    "No rumors": true,
    "Correct health info": true,
    "Protection of brand image": true,
    "No defamation or unwarranted criticism": true,
    "Legal compliance and regulations": true,
    "Adherence to company policies": true
}"""

        mock_response = create_mock_response(content)
        mock_azure_open_ai = MagicMock()
        mock_azure_open_ai.chat.completions.create.return_value = mock_response
        mock_client.return_value = mock_azure_open_ai
        
        ai = MoralKeeperAI()
        ai.check_ai = mock_client
        
        result = ai.check("test_content")
        print(result)

        expected_result = (False, ['No personal attacks'])
        assert result == expected_result
