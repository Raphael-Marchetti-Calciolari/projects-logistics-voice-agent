# Logistics Voice Agent - Backend

FastAPI backend for the Logistics Voice Agent system.

## Prerequisites

- Python 3.11+
- Supabase account
- Retell AI account
- OpenAI API account

## Setup

### 1. Create Supabase Project

1. Go to [supabase.com](https://supabase.com) and create a new project
2. Wait for the project to finish provisioning

### 2. Create Database Tables

Go to SQL Editor in Supabase and run:

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

-- Create indexes for better query performance
CREATE INDEX idx_call_logs_retell_call_id ON call_logs(retell_call_id);
CREATE INDEX idx_call_logs_created_at ON call_logs(created_at DESC);
CREATE INDEX idx_agent_configurations_scenario ON agent_configurations(scenario_type);
```

### 3. Get API Credentials

**Supabase:**
- Go to Project Settings → API
- Copy `URL` and `anon/public` key

**Retell AI:**
- Sign up at [retellai.com](https://www.retellai.com)
- Get API key from dashboard

**OpenAI:**
- Get API key from [platform.openai.com](https://platform.openai.com)

### 4. Configure Environment Variables

```bash
# Copy example file
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-anon-key-here

# Retell AI
RETELL_API_KEY=key_xxxxx
RETELL_WEBHOOK_SECRET=key_yyyyyy
RETELL_FROM_NUMBER=+1234567890  # Optional: only needed for phone calls

# OpenAI
OPENAI_API_KEY=sk-xxxxx
```

### 5. Install Dependencies

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

### 6. Set Up Webhook Tunnel (ngrok)

In a separate terminal:

```bash
ngrok http 8000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

### 7. Configure Retell Webhook

1. Go to Retell dashboard → Settings → Webhooks
2. Set webhook URL to: `https://YOUR-NGROK-URL.ngrok.io/api/webhooks/retell`
3. Save
4. Go to your `.env` and set the `WEBHOOK_BASE_URL` to the value you copied e.g., `https://abc123.ngrok.io`

### 8. Run the Server

```bash
# Make sure you're in the backend directory with venv activated
uvicorn main:app --reload --port 8000
```

Or if uvicorn is not in PATH:

```bash
venv/bin/uvicorn main:app --reload --port 8000
```
