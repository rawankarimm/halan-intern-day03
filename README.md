# Internship

A small Python practice repository for learning project setup, dependency management, and concurrency basics. It includes a simple starter script and a benchmark script that compares sequential and parallel approaches for I/O-bound and CPU-bound work.

## Project structure

- main.py - a simple entrypoint for the project
- prereqs/concurrency_benchmark.py - a benchmark script for threading and multiprocessing
- pyproject.toml - project metadata and dependencies

## Separate project: my_duckdb_project

The folder my_duckdb_project is a separate project from the earlier starter scripts in this repository. It should be treated as its own workload with its own data requirements, rather than as part of the main.py or concurrency benchmark examples.

## Setup with uv

This project is configured to use uv for dependency and environment management.

### 1. Install uv

If uv is not installed yet, install it with one of the following:

PowerShell:

```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

Or with winget:

```powershell
winget install --id astral-sh.uv -e
```

### 2. Create and activate a virtual environment

```powershell
uv venv .venv
.\.venv\Scripts\Activate.ps1
```

If you prefer to create the environment with Python directly:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

Install the dependencies declared in pyproject.toml:

```powershell
uv sync
```

To add a new dependency:

```powershell
uv add requests
```

To add a development dependency:

```powershell
uv add --dev pytest
```

### 4. Run the project

```powershell
uv run python main.py
```

```powershell
uv run python prereqs/concurrency_benchmark.py
```

## Notes

- If you need to refresh the environment after changing dependencies, run `uv sync` again.
- If you want to inspect the current environment, use `uv pip list`.
- If you are using a standard virtual environment instead of uv, you can still install dependencies with `pip install -e .`.

- The folder my_duckdb_project is a separate project from the earlier starter scripts in this repository. It should be treated as its own workload with its own data requirements, rather than as part of the main.py or concurrency benchmark examples.
The sample data file `paysim_sample.csv` is not included in this repository and must be obtained separately before running data-related workflows.

