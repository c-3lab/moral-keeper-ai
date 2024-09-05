
# moral-keeper-ai

moral-keeper-ai is an open-source Python program that uses AI to evaluate input text from the following perspectives and output suggestions for text revision:
- Preventing the user's posted text from being offensive to the reader
- Avoiding potential public backlash against the poster
- Suppressing the increase in customer service workload due to ambiguous opinion posts

This helps maintain a positive and respectful online presence.

## Technology Used

- OpenAI API

## Supported API Servers

- Azure OpenAI Service

## Recommended Models

- GPT-4o mini
- GPT-4o
- GPT-3turbo

## Main Features

- Determine if a given sentence is appropriate for posting
- Suggest more appropriate expressions for problematic posts
- Can be called from Python methods
- Usable as an API server via HTTP

## Quick Start

1. Installation

```sh
pip install moral-keeper-ai
```

2. Configuration

Add various settings in .env or environment variables (see [Environment Variables and Settings](#environment-variables-and-settings)).


3. Example Usage

```python
import moral_keeper_ai
judgment, details = moral_keeper_ai.check('The sentence you want to check')
suggested_message = moral_keeper_ai.suggest('The sentence you want to make appropriate for posting')
```

### moral_keeper_ai.check()

Parameters

- content: string: Text to be censored

Return value: Tuple

- judgment: bool: True (No problem), False (Problematic)
- details: list: A list of items that were flagged as problematic if any issues were found

Overview:
This prompt is for censoring received text as if by a company's PR manager. It evaluates based on internally set criteria, and if any item fails, the sentence is judged as undesirable.

### moral_keeper_ai.suggest()

Parameters

- content: string: Text before expression change


Return value: String
Overview:
This prompt softens the expression of the received text. It returns the softened string.

4. As an API server via HTTP

```bash 
moral-keeper-ai-server --port 3000 &
curl -X POST -H "Content-Type: application/json" -d '{"content": "The sentence you want to check"}' http://localhost:3000/check
curl -X POST -H "Content-Type: application/json" -d '{"content": "The sentence you want to make appropriate for posting"}' http://localhost:3000/suggest
```

### `POST /check`

Submit a text string to be judged for appropriateness.

Request:
```json
{
    "content": "The sentence you want to check."
}
```

Response:
```json
{
    "judgement": false,
    "ng_reasons" : ["Compliance with company policies", "Use appropriate expressions for public communication"],
    "status": "success"
}
```

- `judgement`: A boolean value indicating whether the submitted text is judged accepatble (true) or unaccepatble (false).
- `ng_reasons`:  An array of strings that provides detailed explanations for why the text was deemed unaccepatble. Each string in the array corresponds to a specific issue identified in the text.
- `status`: A string that indicates the result of the API execution. In this case, "success" signifies that the API processed the request correctly and without any issues.

### `POST /suggest`

Submit a text string to be make its expression softer or more polite. The response includes the softened version of the submitted text.

Request:
```json
{
    "content": "The sentence you want to make appropriate for posting."
}
```

Response:
```json
{
    "softened": "The softened sentence the api made.", 
    "status": "success"
}
```

- `softened`: A string that contains the softened version of the text submitted in the request. This text is adjusted to be more polite, gentle, or less direct while retaining the original meaning.
- `status`: A string that indicates the result of the API execution. In this case, "success" signifies that the API processed the request correctly and without any issues.

## Environment Variables and Settings

### API Key

```bash
export AZURE_OPENAI_API_KEY='API Key'
```

### Endpoint

```bash
export AZURE_OPENAI_ENDPOINT='Endpoint URL'
```

### Model to Use

```bash
export AZURE_OPENAI_DEPLOY_NAME='Model name/Deployment name'
```

## For Developers

### Setup Environment

1. Clone the `moral-keeper-ai` repository from GitHub to your local environment and navigate to the cloned directory.

```sh
git clone https://github.com/c-3lab/moral-keeper-ai.git
cd moral-keeper-ai
```

2. Install poetry if it's not installed yet.

```sh
pip install poetry
```

3. Set up the linters and formatters.

```sh
poetry install
poetry run pre-commit install
```

* From now on, every time you run git commit, isort, black, and pflake8 will automatically be applied to the staged files. If these tools make any changes, the commit will be aborted.
* If you want to manually run isort, black, and pflake8, you can do so with the following command: `poetry run pre-commit`

### Running Tests

1. Run the following command to execute the tests:

```sh
poetry run pytest --cov-report=xml:/tmp/coverage.xml --cov=moral_keeper_ai --cov-branch --disable-warnings --cov-report=term-missing
```

## Directory Structure
<pre>
.
├── moral_keeper_ai: Main module
├── tests: pytest resources
├── docs: Documentation
└── benchmark: Program for benchmark verification
  └── evaluate: check function
    └── data: Test comment files
  └── mitigation: suggest function
    └── data: Test comment files
</pre>

## LICENSE

[MIT license](https://github.com/c-3lab/moral-keeper-ai#MIT-1-ov-file)

## CopyRight

Copyright (c) 2024 C3Lab
