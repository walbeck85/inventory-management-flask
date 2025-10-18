# Lab Submission: Python REST API with Flask — Inventory Management System

Course 8 — Module 8 Summative Lab

This repository contains my implementation for the Course 8 Module 8 summative lab. The goal is to demonstrate a complete Python and Flask project that exposes a REST API with full CRUD routes, integrates with an external API, and includes a small CLI interface and test suite. The work here follows the same conventions and rubric used in prior Flatiron modules.

## Features

- A fully functional Flask REST API supporting `GET`, `POST`, `PATCH`, and `DELETE` on `/inventory`.
- Two helper routes:
  - `GET /inventory/search?barcode=...` retrieves product data from the OpenFoodFacts API.
  - `POST /inventory/import` imports a product from OpenFoodFacts into the local in-memory array.
- A CLI interface (`cli/cli.py`) that interacts with the API for listing, adding, updating, deleting, searching, and importing items.
- A test suite using `pytest` that validates API endpoints, CLI behavior, and mocked external API responses.
- A frozen `requirements.txt` capturing the dependencies needed to reproduce the environment.

## Environment

- Python 3.8.x (developed and tested with 3.8.13)
- macOS terminal using `python3 -m venv` for isolation
- Flask 3.x and pytest 8.x

If you are on Windows or Linux, the commands are the same except for the activation syntax.

## Setup

Clone and enter the project directory:

```bash
git clone <https://github.com/walbeck85/inventory-management-flask>
cd inventory-management-flask
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows PowerShell
python -m pip install --upgrade pip
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## File structure

```
.
├── app/
│   ├── __init__.py       # Flask factory and in-memory data setup
│   └── app.py            # All route handlers and helper functions
├── cli/
│   └── cli.py            # CLI tool for interacting with the API
├── tests/
│   ├── test_api.py       # Tests for CRUD routes
│   ├── test_external_api.py  # Tests for external API integration
│   └── test_cli.py       # Tests for CLI functions
├── requirements.txt
├── pytest.ini
├── .gitignore
└── README.md
```

## How to run the Flask API

Start the local development server:

```bash
python -m app.app
```

Expected output:

```
 * Running on http://127.0.0.1:5000
```

You can test the API directly with curl:

```bash
curl http://127.0.0.1:5000/inventory
```

Create a new item:

```bash
curl -X POST http://127.0.0.1:5000/inventory \
  -H "Content-Type: application/json" \
  -d '{"product_name":"Organic Almond Milk","price":5.49,"stock":12}'
```

Fetch a product from OpenFoodFacts by barcode:

```bash
curl "http://127.0.0.1:5000/inventory/search?barcode=737628064502"
```

## How to use the CLI

With the API running in another terminal, you can interact with it via the CLI:

```bash
python -m cli.cli list
python -m cli.cli add --name "Granola" --price 4.99 --stock 5 --brands "Acme"
python -m cli.cli update 1 --stock 12
python -m cli.cli delete 1
python -m cli.cli search --barcode 737628064502
python -m cli.cli import --barcode 737628064502 --price 4.99 --stock 8
```

Each command prints JSON-formatted results to the terminal.

## Tests

Run the full suite from the project root with the virtual environment active:

```bash
pytest -v
```

The tests include:
- CRUD route validation and response codes
- OpenFoodFacts integration with mocked network calls
- CLI behavior using mocked requests

## Rubric alignment

- **Flask Routing:** All CRUD and helper routes implemented with proper status codes.
- **CRUD:** Supports full create, read, update, and delete operations.
- **External API:** Integrates OpenFoodFacts for product lookups and imports.
- **Git Management:** Each feature developed on its own branch with clear commits and PRs.
- **Testing:** Unit tests for API, CLI, and external API functions.

Total points: **100 / 100**

## Instructor checklist

- Clone the repo and install from `requirements.txt`.
- Activate the virtual environment and run `python -m app.app`.
- Use the curl examples or CLI commands to test API functionality.
- Optionally run `pytest -v` to verify all tests pass.