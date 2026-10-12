# Foodie AI Agent

A LangChain-based AI agent that helps you find restaurants, cafés, bakeries, bars and other food venues. You describe what you are looking for in natural language (cuisine, neighbourhood, occasion, budget, ...), and the agent turns that request into a short search query, looks up real venues with the **Google Places API (New)**, and returns a concise shortlist of the best matches.

> **Example queries**
> - "Find me a good kebab in Warsaw near the Old Town"
> - "Find a restaurant suitable for a date in Warsaw"
> - "Recommend something budget-friendly near me"
> - "Find a good bakery in central Warsaw"
> - "Recommend an Italian restaurant with good reviews"
> - "Find a café where we can talk quietly"

The agent is built to rely only on data returned by Google Places. It must not invent names, addresses, ratings or other details. When a field is missing, it is reported as `null` / "not available" rather than guessed.

---

## Table of contents

- [How it works](#how-it-works)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the agent](#running-the-agent)
- [Running the tests](#running-the-tests)
- [Project structure](#project-structure)
- [Data model](#data-model)
- [Development conventions](#development-conventions)
- [Current limitations](#current-limitations)

---

## How it works

```
 user query
     │
     ▼
 ┌────────────────────┐   build_idea (LLM, structured output → Idea)
 │  LangChain agent   │ ─────────────────────────────────────────────┐
 │  (ReAct loop)      │                                              │
 └────────────────────┘                                              ▼
     │  get_restaurants / get_restaurants_pages           short search phrases
     ▼                                                              │
 Google Places API (New) ◄──────────── one search per phrase ◄──────┘
     │
     ▼
 agent selects the 3–5 best matches → raw JSON
     │
     ▼
 parse_answer()  →  Pydantic models (Restaurant / RestaurantLink)
     │
     ▼
 format_restaurants()  →  plain-text shortlist for the user
```

1. **Intent extraction.** The `build_idea` tool sends the raw request to an OpenAI chat model with structured output, producing an `Idea` object: a list of short Google Places search phrases that keep the venue type, cuisine, location and any essential constraints (such as budget).
2. **Venue search.** `get_restaurants` (or `get_restaurants_pages`, when the user only wants links) runs a Google Places *Text Search* for each phrase. Only the fields needed for the answer are requested through a field mask.
3. **Selection.** The agent picks the 3–5 best-matching venues from the returned data and answers with a raw JSON array.
4. **Validation and presentation.** `parse_answer` normalises the JSON and validates it against the Pydantic models. `format_restaurants` renders it as a short, readable list.

---

## Requirements

| Requirement | Version / notes |
| --- | --- |
| Python | **3.14** (see `.python-version`) |
| Package manager | [uv](https://docs.astral.sh/uv/) (the project uses `pyproject.toml` and `uv.lock`) |
| OpenAI API key | Used by the LLM (`gpt-5.1`) for intent extraction and agent reasoning |
| Google Places API (New) key | Must have the **Places API (New)** enabled in Google Cloud |

The main dependencies are declared in `pyproject.toml`:

- `langchain`, `langchain-community`, `langchain-openai`: agent, tools and LLM integration
- `langchain-google-community[places]` and `google-maps-places`: Google Places client
- `pytest` (dev group): unit tests

Both the OpenAI and Google Places APIs are paid services. Unit tests do not call them (see [Running the tests](#running-the-tests)).

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/KacprusJeden/Foodie_AI_Agent.git
cd Foodie_AI_Agent

# 2. Create the virtual environment and install all dependencies from uv.lock
uv sync
```

`uv sync` creates a `.venv/` directory, installs the locked dependencies and installs the project itself in editable mode.

If you do not have uv yet:

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

---

## Configuration

The agent reads its credentials from environment variables. **Never hard-code keys in the source** and never commit them.

| Variable | Required | Used by | Description |
| --- | --- | --- | --- |
| `OPENAI_API_KEY` | Yes | `agent.py`, `tools.py` | OpenAI API key for the `gpt-5.1` model |
| `Google Place API Key` | Yes | `tools.py` | Google Places API (New) key. Note that the variable name contains spaces, as it is read exactly as written in the code |

Set them in your shell before running the agent.

**PowerShell (Windows):**

```powershell
$env:OPENAI_API_KEY = "sk-..."
${env:Google Place API Key} = "your-google-places-key"
```

**bash / zsh (macOS / Linux):** shells cannot `export` names containing spaces, so pass the Google key for a single command with `env`:

```bash
export OPENAI_API_KEY="sk-..."
env "Google Place API Key=your-google-places-key" uv run python -m foodie_ai_agent.agent
```

> The project does not load `.env` files automatically. If you keep keys in a local `.env` file, the file is ignored by git (see `.gitignore`), but you must export its values into the environment yourself.

---

## Running the agent

The agent runs as an interactive command-line program:

```bash
uv run python -m foodie_ai_agent.agent
```

You will be asked for a query:

```
Enter the query: Find a budget-friendly pizzeria in Mokotów
```

The program prints a numbered shortlist with the available details of each venue, for example:

```
1. Example Pizzeria  (4.6/5)
   Address:  Example Street 1, Warsaw
   Hours:    Mon-Fri 11:00-22:00; Sat-Sun 12:00-23:00
   Prices:   30-60 PLN
   Food:     pizza, pasta
   Contact:  +48 000 000 000
   Website:  https://example.com
   Pin:      https://maps.google.com/?cid=...
```

Fields that Google does not return are simply omitted from the output. The sample above is illustrative and does not describe a real venue.

---

## Running the tests

The unit tests live in `tests/` and run with pytest. They use stubs for LangChain and the Google Places client, so they need neither API keys nor network access.

```bash
uv run pytest tests/ -v
```

On some locked-down Windows machines, pytest's plugin autoload can fail (for example, when a security policy blocks a DLL that a third-party plugin such as `langsmith` loads), and the `pytest.exe` launcher itself may be blocked. In that case, run the tests through the project's helper module, which disables plugin autoload before starting pytest:

```bash
uv run python -m foodie_ai_agent.test_runner tests/ -v
```

The test configuration (`[tool.pytest.ini_options]` in `pyproject.toml`) adds `src/` to the Python path and collects files named `*_UT.py`.

---

## Project structure

```
Foodie_AI_Agent/
├── src/
│   └── foodie_ai_agent/          # main application package
│       ├── __init__.py           # package entry (placeholder `main()`)
│       ├── agent.py              # LangChain agent, system prompt, JSON parsing, output formatting
│       ├── tools.py              # LangChain tools: build_idea, get_restaurants, get_restaurants_pages
│       ├── models.py             # Pydantic models: Idea, Restaurant, RestaurantLink
│       └── test_runner.py        # pytest helper that disables plugin autoload
├── tests/
│   ├── conftest.py               # stubs for langchain and google.maps so unit tests run offline
│   ├── agent_UT.py               # tests for parse_answer and format_restaurants
│   ├── models_UT.py              # tests for the Pydantic models
│   └── tools_UT.py               # tests for the tools with mocked API clients
├── translations/
│   └── en/                       # English translations of the project guidelines and agent configs
├── .claude/, .codex/, .kimi/     # AI-assistant agent, command and output-style configs
├── .vscode/                      # editor settings
├── AGENTS.md                     # project guidelines (Polish)
├── CLAUDE.md                     # project guidelines for Claude Code (Polish)
├── pyproject.toml                # project metadata, dependencies, pytest and build config
├── uv.lock                       # locked dependency versions
├── .python-version               # Python version (3.14)
└── databricks.yml               # Databricks Asset Bundle definition
```

### Module responsibilities

| Module | Responsibility |
| --- | --- |
| `models.py` | Validation and structure of data: the search intent (`Idea`), the full venue (`Restaurant`) and the links-only variant (`RestaurantLink`). Missing optional fields default to `None` or an empty list. |
| `tools.py` | Everything that talks to external services: the OpenAI model used for intent extraction, and the two Google Places text-search tools with their field masks. |
| `agent.py` | Agent wiring (system prompt, model, tools), parsing of the agent's JSON answer into Pydantic models, and rendering of the final text output. |
| `test_runner.py` | Convenience entry point (`foodie-ai-pytest`) for running pytest on restricted machines. |

Keeping these responsibilities separate makes it possible to change the data source, the model or the presentation layer independently.

---

## Data model

**`Idea`** — a short search intent derived from the user's request.

```python
Idea(idea=["Kebab Warszawa Stare Miasto", "Tania pizza Mokotow"])
```

**`Restaurant`** — a venue with the full set of details. Every field except `name` and `address` is optional.

| Field | Type | Source |
| --- | --- | --- |
| `name` | `str` | Google `displayName` |
| `address` | `str` | Google `formattedAddress` |
| `opening_hours` | `str \| None` | Google `regularOpeningHours` |
| `price_range` | `str \| None` | Google `priceRange` |
| `food` | `list[str]` | Dish or cuisine examples, when available |
| `rating` | `float \| None` | Google `rating` |
| `contact` | `str \| None` | Google `nationalPhoneNumber` |
| `link` | `str \| None` | Google `websiteUri` |
| `location_pin` | `str \| None` | Google `googleMapsUri` |

**`RestaurantLink`** — returned when the user asks only for websites or map pins: `link` and `location_pin`, both optional.

---

## Development conventions

- **Python 3.14**, managed with uv.
- **Naming:** `snake_case` for functions and variables.
- **Type hints** on parameters and return values.
- **Docstrings** on every function, describing purpose, arguments, return value and raised exceptions where relevant.
- **Formatting and linting:** `ruff` (the project guidelines require it; it is not yet declared in `pyproject.toml`).
- **Secrets** come only from environment variables or a git-ignored `.env` file.
- **Separation of concerns:** agent logic, data access, Pydantic models and presentation live in different modules.

---

## Current limitations

- **No requirements.txt.** Dependencies are managed with `pyproject.toml` and `uv.lock`; use `uv sync` instead of `pip install -r requirements.txt`.
- **No integration tests yet.** The guidelines ask for integration tests against the live Google Places API, kept separate from the default suite. They are not implemented.
- **No `.env` loading.** Variables must be exported in the shell (see [Configuration](#configuration)).
- **Placeholder entry point.** The `foodie-ai-agent` console script points to `foodie_ai_agent:main`, which currently only prints a greeting. Use `python -m foodie_ai_agent.agent` to run the agent.
- **Search results are not yet deduplicated across phrases**, and the agent's shortlist depends on the LLM's selection of the best 3–5 venues.
- **Opening hours and prices** are only as complete as Google's data for each venue; many venues will have gaps.
- **Language:** the agent prompt and intent extraction are in English, while the sample queries in the guidelines are in Polish. Queries in either language should work, but this has not been formally evaluated.

---

## Licence

No licence file has been added to the repository yet.
