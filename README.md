# Logistics Voice Agent

A voice-based logistics system for driver check-ins and emergency situations, powered by Retell AI and OpenAI.

## Design Choices
This logistics voice agent application follows a separation of concerns architecture where conversation intelligence and data processing are handled by specialized components:
LLM Usage Strategy: The system employs two distinct LLM components:
- Retell AI's Built-in LLM handles all real-time driver conversations using configured system prompts
- OpenAI GPT-4o performs post-call transcript analysis and structured data extraction

This design minimizes backend complexity during live calls—the backend simply manages configuration and processes webhooks, while Retell autonomously conducts conversations.

Agent Configuration Strategy: Two persistent Retell agents (one per scenario) are created once and updated when prompts change, avoiding repeated agent creation overhead.

Database Design: Supabase PostgreSQL provides robust storage for configurations and call logs, with JSONB fields for flexible structured data and voice settings.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- [Supabase](https://supabase.com) account
- [Retell AI](https://www.retellai.com) account  
- [OpenAI](https://platform.openai.com) API key
- [ngrok](https://ngrok.com) or similar tunnel service (for webhook support)

### Setup Steps

**1. Clone and Navigate**
```bash
git clone <your-repo-url>
cd <repo-directory>
```

**2. Configure Backend Environment**
```bash
cd backend
cp .env.example .env
```

Edit `backend/.env` with your credentials:
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Your Supabase anon/public key
- `RETELL_API_KEY` - Your Retell AI API key
- `RETELL_WEBHOOK_SECRET` - Your Retell AI webhook secret
- `RETELL_FROM_NUMBER` - (Optional) Phone number for outbound calls
- `OPENAI_API_KEY` - Your OpenAI API key
- `WEBHOOK_BASE_URL` - Your ngrok HTTPS URL (see step 4)

**3. Configure Frontend Environment**
```bash
cd ../frontend
cp .env.example .env
```

The default `VITE_API_BASE_URL=http://localhost:8000` should work as-is.

**4. Set Up Database Tables**

Go to your Supabase project → SQL Editor and run:

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

-- Create indexes
CREATE INDEX idx_call_logs_retell_call_id ON call_logs(retell_call_id);
CREATE INDEX idx_call_logs_created_at ON call_logs(created_at DESC);
CREATE INDEX idx_agent_configurations_scenario ON agent_configurations(scenario_type);
```

**5. Start ngrok Tunnel**

In a separate terminal:
```bash
ngrok http 8000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`) and update `WEBHOOK_BASE_URL` in `backend/.env`.

**6. Configure Retell Webhook**

1. Go to Retell dashboard → Settings → Webhooks
2. Set webhook URL to: `https://YOUR-NGROK-URL/api/webhooks/retell`
3. Save the configuration

**7. Start the Application**

From the project root:
```bash
docker compose up
```

**8. Access the Application**

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 📚 Additional Documentation

- [Backend Setup Guide](backend/README.md) - Detailed backend configuration
- [Frontend Setup Guide](frontend/README.md) - Frontend-specific details

## 🔧 Troubleshooting

### Port Already in Use
```bash
# Check what's using the port
lsof -i :8000  # or :5173
# Kill the process or change the port in docker-compose.yml
```

### Docker Issues
```bash
# Rebuild containers from scratch
docker compose down
docker compose build --no-cache
docker compose up
```

### Environment Variable Issues
- Ensure all required variables in `.env.example` are filled in your `.env` files
- Restart containers after changing `.env` files: `docker compose restart`

### Webhook Not Receiving Calls
- Verify ngrok is running and the URL matches `WEBHOOK_BASE_URL`
- Check Retell dashboard webhook configuration
- Ensure webhook URL ends with `/api/webhooks/retell`

### Database Connection Errors
- Verify `SUPABASE_URL` and `SUPABASE_KEY` are correct
- Ensure database tables are created (step 4)
- Check Supabase project is active and not paused

## 🛠️ Development Notes

### Running Without Docker (Advanced)

If you prefer to run services locally without Docker:

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Hot Reloading

Both services support hot reloading in Docker:
- Backend: Code changes trigger automatic reload
- Frontend: Vite hot module replacement (HMR) is enabled

### Logs
```bash
# View all logs
docker compose logs -f

# View specific service
docker compose logs -f backend
docker compose logs -f frontend
```

## 📋 Architecture

- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: React + Vite
- **Database**: Supabase (PostgreSQL)
- **Voice AI**: Retell AI
- **LLM**: OpenAI GPT-4
