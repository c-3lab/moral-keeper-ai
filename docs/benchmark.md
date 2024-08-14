# Benchmark verification program

A program that outputs a score using test comments to measure the performance of prompts when using moral-keeper-ai

## Target program

evaluate and mitigation under the benchmark directory

## Settings

Add various settings in .env or environment variables (see moral-keeper-ai README ([Environment variables and settings](../README.md)))

## Test comments
By placing them under ./data, the verification program can read test comments.
In the test comments, you can write viewpoints and classify which comments conflict with which viewpoints.

## How to run

### Prerequisites

- Run in a python virtual environment
- poetry must be executable
- moral_keeper_ai must be installed

### Activate virtual environment

```sh
source .venv/bin/activate
```

### Install prerequisite modules

```sh
poetry install
```

### Run verification program

#### When verifying check function
```sh
cd moral-keeper-ai/benchmark/evaluate
python evaluate.py ja
```

#### When verifying suggest function
```sh
cd moral-keeper-ai/benchmark/mitigation
python mitigation.py ja
```