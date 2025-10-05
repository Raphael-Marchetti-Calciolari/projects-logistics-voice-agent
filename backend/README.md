# Logistics Voice Agent - Backend

## Database Schema

### Creating database schema

Use the following SQL statement to create the database structure in supabase after creating a new project:

```sql
-- Create agent_configurations table
CREATE TABLE agent_configurations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_type TEXT NOT NULL UNIQUE CHECK (scenario_type IN ('checkin', 'emergency')),
    system_prompt TEXT NOT NULL,
    retell_settings JSONB NOT NULL DEFAULT '{}'::jsonb,
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

### agent_configurations
Stores AI agent prompts and voice settings for different call scenarios.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| scenario_type | TEXT | 'checkin' or 'emergency' |
| system_prompt | TEXT | Instructions for the AI agent |
| retell_settings | JSONB | Voice behavior configuration |
| created_at | TIMESTAMP | Creation timestamp |

**Constraints:**
- `scenario_type` must be unique (one config per scenario)
- `scenario_type` must be either 'checkin' or 'emergency'

**Example retell_settings:**
```json
{
  "enable_backchannel": true,
  "backchannel_frequency": 0.8,
  "interruption_sensitivity": 0.7,
  "ambient_sound_volume": 0.3,
  "enable_filler_words": true,
  "response_delay_ms": 200,
  "voice_id": "string"
}
```

---

### call_logs
Stores information about each phone call made to drivers.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| retell_call_id | TEXT | Retell's unique call identifier |
| driver_name | TEXT | Name of the driver called |
| driver_phone | TEXT | Driver's phone number |
| load_number | TEXT | Load/shipment identifier |
| scenario_type | TEXT | 'checkin' or 'emergency' |
| call_status | TEXT | Current status of the call |
| raw_transcript | TEXT | Full conversation transcript |
| structured_data | JSONB | Extracted key-value pairs |
| created_at | TIMESTAMP | Call initiation timestamp |

**Call Status Values:**
- `initiated` - Call has been triggered
- `in_progress` - Call is actively happening
- `completed` - Call finished successfully
- `failed` - Call failed to complete

**Example structured_data (check-in scenario):**
```json
{
  "call_outcome": "In-Transit Update",
  "driver_status": "Driving",
  "current_location": "I-10 near Indio, CA",
  "eta": "Tomorrow, 8:00 AM",
  "delay_reason": "None",
  "unloading_status": "N/A",
  "pod_reminder_acknowledged": true
}
```

**Example structured_data (emergency scenario):**
```json
{
  "call_outcome": "Emergency Escalation",
  "emergency_type": "Breakdown",
  "safety_status": "Driver confirmed everyone is safe",
  "injury_status": "No injuries reported",
  "emergency_location": "I-15 North, Mile Marker 123",
  "load_secure": true,
  "escalation_status": "Connected to Human Dispatcher"
}
```

---

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure `.env` file with your credentials

4. Start ngrok to expose your local server (optional, for external access):

```bash
ngrok http 8000
```

This will provide a public URL forwarding to your local FastAPI server. That you should add to the `.env`

5. Run server:
```bash
uvicorn main:app --reload --port 8000
```

Obs: verify if you're using the appropriate uvicorn of your venv, check with `which uvicorn`.

If not pointing to your venv, use the following command instead:
```bash
venv/bin/uvicorn main:app --reload --port 8000
```
