import pytest
import os
from unittest.mock import patch

@pytest.fixture(autouse=True)
def set_default_environment():
    default_environment = {
        'AZURE_OPENAI_ENDPOINT': 'https://example.com/azure',
        'AZURE_OPENAI_API_KEY': 'dummy-apikey',
        'AZURE_OPENAI_DEPLOY_NAME': 'gpt-35-turbo'
    }
    with patch.dict(os.environ, default_environment):
        yield