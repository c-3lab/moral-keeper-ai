
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

Return value: Tuple

- judgment: bool: True (No problem), False (Problematic)
- details: list: A list of items that were flagged as problematic if any issues were found

Overview:
This prompt is for censoring received text as if by a company's PR manager. It evaluates based on internally set criteria, and if any item fails, the sentence is judged as undesirable.

### moral_keeper_ai.suggest()

Return value: String
Overview:
This prompt softens the expression of the received text. It returns the softened string.

4. As an API server via HTTP

```bash 
moral-keeper-ai-server --port 3000 &
curl -X POST -H "Content-Type: application/json" -d '{"content": "The sentence you want to check"}' http://localhost:3000/check
```

## Environment Variables and Settings

### API Key

```bash
export AZURE_OPENAI_KEY='API Key'
```

### Endpoint

```bash
export AZURE_ENDPOINT='Endpoint URL'
```

### Model to Use

```bash
export LLM_MODEL='Model name/Deployment name'
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
