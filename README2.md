# FastAPI + MCP + OpenAI Agent — Ready to Run

This project gives you three layers:

1. `app/api_server.py` — your normal FastAPI backend.
2. `app/mcp_server.py` — MCP tools that wrap the FastAPI endpoints.
3. `app/chat_client.py` — a ChatGPT-like CLI assistant using your OpenAI API key and the MCP tools.

## 1. Requirements

Python 3.10+ is required.

## 2. Setup in VS Code terminal

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install packages:

```bash
pip install -r requirements.txt
```

Create `.env`:

```bash
cp .env.example .env
```

On Windows PowerShell, if `cp` fails:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and put your real OpenAI key:

```env
OPENAI_API_KEY=sk-your-real-key
OPENAI_MODEL=gpt-5.5
API_BASE_URL=http://127.0.0.1:9000
API_KEY=dev-secret
```

## 3. Run the API

Open terminal 1:

```bash
uvicorn app.api_server:app --reload --port 9000
```

Test it:

```bash
curl -H "X-API-Key: dev-secret" http://127.0.0.1:9000/health
```

Open API docs:

```text
http://127.0.0.1:9000/docs
```

## 4. Run the MCP server

Open terminal 2:

```bash
python -m app.mcp_server
```

MCP endpoint:

```text
http://127.0.0.1:8000/mcp
```

Optional: inspect the MCP server:

```bash
npx -y @modelcontextprotocol/inspector
```

Then connect to:

```text
http://127.0.0.1:8000/mcp
```

Optional smoke test:

```bash
python -m app.test_mcp_connection
```

## 5. Run the ChatGPT-like client

Open terminal 3:

```bash
python -m app.chat_client
```

Try:

```text
list products
```

```text
find customer Samer
```

```text
create an order for customer cus_001 for MCP Integration Package
```

```text
show orders for cus_001
```

## 6. How to connect your real API

Replace the demo endpoints in `app/api_server.py` with your real business endpoints.
Then update the MCP tools in `app/mcp_server.py` so every important API action has one safe MCP tool.

Recommended pattern:

- Read-only tools: no approval needed.
- Write tools: create/update/delete should be limited and logged.
- Never expose raw admin endpoints directly to the LLM.
- Validate every MCP tool input with type hints and server-side checks.
- Use real auth in production: OAuth2/JWT/API gateway, not the demo `X-API-Key`.
