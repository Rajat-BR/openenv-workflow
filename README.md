# FlowForge: API Workflow Orchestration

## Overview
This project implements an OpenEnv-compatible environment where an agent generates structured API workflows to fulfill user requests.

The system evaluates workflows based on:
- API correctness
- Execution order
- Parameter accuracy
- Efficiency

## Why this project

Modern systems often require orchestrating multiple APIs with strict dependencies and correct parameter usage. 

This project models that problem as a structured environment where an agent must:
- select the correct APIs
- respect execution order
- provide valid parameters

Unlike simple classification tasks, this setup evaluates both planning and execution correctness, making it closer to real-world backend workflows.

## Design Choice

This environment intentionally uses a small set of APIs to keep the evaluation focused and interpretable.

The goal is not API coverage, but to test whether an agent can:
- select the correct tools
- respect dependencies between steps
- provide valid structured parameters

Keeping the API set minimal ensures that performance reflects reasoning and planning ability, rather than memorization of a large toolset.

## Available APIs
- `flight_api(from_city, to_city)`
- `calendar_api(date, time)`
- `email_api(to)`
- `database_api(data)`  
  *(data must include: destination, date, time)*

## Tasks
- **Easy**: Schedule a meeting  
- **Medium**: Book a flight and send email  
- **Hard**: Full workflow (flight → calendar → database → email)

## How it works
1. The agent generates a JSON workflow
2. The environment executes each API step
3. The grader assigns a score (0.0–1.0)
4. Scores are aggregated across tasks

## Running the project

### Local (quick run)

```bash
pip install -r requirements.txt
python inference.py
```

### Docker (recommended for evaluation)

```bash
docker build -t flowforge .
docker run flowforge
