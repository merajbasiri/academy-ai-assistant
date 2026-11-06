# Academy AI Assistant

A small, read-only agent demo for an educational academy. It answers Persian-language questions about fictional student records and tuition balances using LangChain tools backed by ordinary Python functions.

The central idea is simple: **the model can choose a lookup, but the financial calculations belong in ordinary Python.** The system prompt asks it to use tools; model responses still need verification against the source data.

![Academy AI Assistant dashboard](assets/dashboard-preview.png)

## What it does

- Looks up sample students by ID, including their course and enrollment status.
- Calculates total tuition, payments, outstanding balance, and overpayment credit in **toman**.
- Exposes the same data through a FastAPI REST API and a browser dashboard.
- Uses a LangChain `create_agent` workflow with two tools: `find_student` and `check_tuition_balance`.
- Reports the tool names selected by the model in each chat response.
- Runs the dashboard, REST endpoints, and deterministic tests **without an OpenAI API key**. Only live LLM chat requires a key.

This is a focused engineering exercise, not an academy management product. The dataset contains **five made-up students**; no personal or payment information from a real academy is included.

## Architecture

```text
Browser / API client
       |
       +-- GET /students, /summary, /students/{id}/balance
       |          |
       |          +--> Python services --> data/students.json
       |
       +-- POST /chat --> LangChain agent --> ChatOpenAI
                                |
                                +--> find_student ---------+
                                +--> check_tuition_balance-+--> Python services
```

There is no database, vector store, RAG pipeline, or autonomous background job. In this implementation, the agent is useful because it can choose a restricted tool based on the question, not because it has unrestricted access to the system.

## Run locally

Use Python 3.11 or newer.

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) for the demo dashboard or [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for Swagger.

The demo ledger works without credentials. For live chat, edit `.env` and provide a platform API key:

```dotenv
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=gpt-5-nano
```

An OpenAI API key is billed separately from ChatGPT. Never commit `.env` to version control.

## Try the API

| Endpoint | Use |
| --- | --- |
| `GET /health` | Basic health check |
| `GET /config` | Whether chat credentials are configured (never returns secrets) |
| `GET /summary` | Aggregated demo tuition metrics |
| `GET /students` | Minimal list for the student picker |
| `GET /students/ST001` | Fictional student record |
| `GET /students/ST001/balance` | Deterministic financial summary |
| `POST /chat` | Live agent response; needs an API key |

Example question for `POST /chat`:

```json
{"message": "مانده شهریه هنرجوی ST001 چقدر است؟"}
```

The chat response includes `answer` and `tools_used`. The latter records which tools the model *requested*; it is not a guarantee that the final answer is correct. For a useful sanity check, compare the chat output with `GET /students/ST001/balance`.

For ST001, the test fixture contains 8,000,000 toman in tuition and 3,500,000 paid, so the outstanding amount is 4,500,000 toman. ST003 demonstrates an overpayment: 0 outstanding and 500,000 toman of credit.

## Tests

```bash
python -m pytest -q
```

The test suite covers the read-only API, ledger calculations, payment edge cases, the demo assets, and the missing-key response. It makes no external model requests. GitHub Actions also runs these tests on Python 3.11 and 3.12.

## Design boundaries

The student records are public sample data served by local HTTP endpoints. **Do not put real student data, national IDs, phone numbers, or payment records in this demo.** Before adapting this to a real academy, it would need authentication, per-record authorization, persistent storage, audit logging, rate limiting, data validation, and an evaluation suite for model behavior. The current API is not designed for public deployment with sensitive data.

The deterministic API and browser UI are covered by automated tests. The live LLM tool-selection path has not been validated against an external model in this package and may differ between models or provider versions.

## Project structure

```text
app/                 FastAPI routes, agent setup, services, tools
web/                 Browser dashboard (vanilla HTML, CSS, JS)
data/students.json   Five fictional records
assets/              Dashboard screenshot
tests/              Unit and API tests
.github/workflows/   CI tests
```

Built as a practical exercise in separating probabilistic language-model behavior from predictable application logic.

**Meraj Basiri** · 2026