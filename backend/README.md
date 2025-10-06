# Logistics Voice Agent - Backend

FastAPI backend service for the Logistics Voice Agent system.

## 🚀 Quick Start with Docker Compose

**Recommended:** Use Docker Compose from the project root (see [main README](../README.md)).

This guide covers Docker Compose setup and local development options.

## Prerequisites

- Docker and Docker Compose (for containerized setup)
- OR Python 3.11+ (for local development)
- [Supabase](https://supabase.com) account
- [Retell AI](https://www.retellai.com) account
- [OpenAI](https://platform.openai.com) API key
- [ngrok](https://ngrok.com) for webhook tunneling

## Setup Instructions

### 1. Configure Environment Variables

```bash
# From backend directory
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Supabase - Get from Project Settings → API
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-anon-key-here

# Retell AI - Get from Retell dashboard
RETELL_API_KEY=key_xxxxx
RETELL_WEBHOOK_SECRET=key_yyyyyy
RETELL_FROM_NUMBER=+1234567890  # Optional: for outbound phone calls

# OpenAI - Get from platform.openai.com
OPENAI_API_KEY=sk-xxxxx

# Webhook - Set after starting ngrok (step 4)
WEBHOOK_BASE_URL=https://abc123.ngrok.io
```

### 2. Create Supabase Database Tables

Go to your Supabase project → SQL Editor and execute:

```sql
-- Create agent_configurations table
CREATE TABLE agent_configurations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_type TEXT NOT NULL UNIQUE CHECK (scenario_type IN ('checkin', 'emergency')),
    system_prompt TEXT NOT NULL,
    retell_settings JSONB NOT NULL DEFAULT '{}'::jsonb,
    llm_id TEXT,
    agent_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create call_logs table
CREATE TABLE call_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    retell_call_id TEXT,
    driver_name TEXT NOT NULL,
    driver_phone TEXT NOT NULL,
    load_number TEXT NOT NULL,
    scenario_type TEXT NOT NULL CHECK (scenario_type IN ('checkin', 'emergency')),
    call_status TEXT NOT NULL DEFAULT 'initiated' CHECK (call_status IN ('initiated', 'in_progress', 'completed', 'failed')),
    raw_transcript TEXT,
    structured_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_call_logs_retell_call_id ON call_logs(retell_call_id);
CREATE INDEX idx_call_logs_created_at ON call_logs(created_at DESC);
CREATE INDEX idx_agent_configurations_scenario ON agent_configurations(scenario_type);
```

### 3. Get API Credentials

**Supabase:**
1. Go to Project Settings → API
2. Copy `URL` (for `SUPABASE_URL`)
3. Copy `anon public` key (for `SUPABASE_KEY`)

**Retell AI:**
1. Sign up at [retellai.com](https://www.retellai.com)
2. Navigate to Settings → API Keys
3. Copy your API key and webhook secret

**OpenAI:**
1. Get API key from [platform.openai.com](https://platform.openai.com)
2. Ensure you have API credits

### 4. Set Up Webhook Tunnel with ngrok

In a separate terminal:
```bash
ngrok http 8000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`) and update `WEBHOOK_BASE_URL` in `.env`.

### 5. Configure Retell Webhook

1. Go to Retell dashboard → Settings → Webhooks
2. Set webhook URL to: `https://YOUR-NGROK-URL/api/webhooks/retell`
3. Save the configuration

### 6. Run with Docker Compose

From the **project root**:
```bash
docker compose up
```

The backend will be available at:
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- OpenAPI Spec: http://localhost:8000/openapi.json

**No code modifications are necessary** - everything is configured via environment variables.

## Local Development (Without Docker)

If you prefer to run the backend locally:

### Install Dependencies
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Run the Server
```bash
# Make sure you're in the backend directory with venv activated
uvicorn main:app --reload --port 8000
```

Or if uvicorn is not in PATH:
```bash
python -m uvicorn main:app --reload --port 8000
```

## 🔧 Troubleshooting

### Port 8000 Already in Use
```bash
# Find and kill the process
lsof -i :8000
kill -9 <PID>

# Or change the port in docker-compose.yml
```

### Database Connection Errors
- Verify `SUPABASE_URL` and `SUPABASE_KEY` are correct
- Ensure database tables are created (step 2)
- Check that your Supabase project is active (not paused)

### Webhook Not Receiving Events
- Ensure ngrok is running and URL matches `WEBHOOK_BASE_URL` in `.env`
- Verify Retell webhook configuration points to `https://YOUR-NGROK-URL/api/webhooks/retell`
- Check backend logs for incoming webhook requests: `docker compose logs -f backend`

### Environment Variables Not Loading
- Restart the container after changing `.env`: `docker compose restart backend`
- Verify `.env` file is in the `backend/` directory
- Check for syntax errors in `.env` file (no spaces around `=`)

### Import or Module Errors
```bash
# Rebuild the container
docker compose down
docker compose build --no-cache backend
docker compose up
```

## 📊 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Main Endpoints

- `POST /api/calls/initiate` - Start a new voice call
- `GET /api/calls` - List all calls
- `GET /api/calls/{call_id}` - Get call details
- `POST /api/webhooks/retell` - Retell webhook receiver
- `GET /api/configurations` - List agent configurations
- `PUT /api/configurations/{scenario_type}` - Update agent configuration

## 🧪 Testing

Run tests locally:
```bash
# Activate venv first
source venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_call_flow.py
```

## 📁 Project Structure

```
backend/
├── main.py              # FastAPI application entry point
├── database.py          # Supabase connection
├── models.py            # Pydantic models
├── constants.py         # Configuration constants
├── requirements.txt     # Python dependencies
├── routers/             # API route handlers
│   ├── calls.py
│   ├── configurations.py
│   └── webhooks.py
├── services/            # Business logic
│   ├── call_service.py
│   ├── configuration_service.py
│   ├── database_service.py
│   └── webhook_service.py
└── tests/               # Test files
```

## 📝 Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `SUPABASE_URL` | Yes | Supabase project URL |
| `SUPABASE_KEY` | Yes | Supabase anon/public key |
| `RETELL_API_KEY` | Yes | Retell AI API key |
| `RETELL_WEBHOOK_SECRET` | Yes | Retell webhook secret |
| `RETELL_FROM_NUMBER` | No | Phone number for outbound calls |
| `OPENAI_API_KEY` | Yes | OpenAI API key |
| `WEBHOOK_BASE_URL` | Yes | Public URL for webhook callbacks |
