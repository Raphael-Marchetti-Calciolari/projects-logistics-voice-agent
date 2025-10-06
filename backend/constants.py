"""
Central constants and configuration values for the Logistics Voice Agent system.
"""

# Scenario types
SCENARIO_CHECKIN = "checkin"
SCENARIO_EMERGENCY = "emergency"
VALID_SCENARIOS = [SCENARIO_CHECKIN, SCENARIO_EMERGENCY]

# Call statuses
CALL_STATUS_INITIATED = "initiated"
CALL_STATUS_IN_PROGRESS = "in_progress"
CALL_STATUS_COMPLETED = "completed"
CALL_STATUS_FAILED = "failed"

# Special markers
WEB_CALL_PHONE_MARKER = "web-call"

# Database tables
TABLE_AGENT_CONFIGURATIONS = "agent_configurations"
TABLE_CALL_LOGS = "call_logs"

# OpenAI settings
OPENAI_MODEL = "gpt-4o"
OPENAI_TEMPERATURE = 0

# Retell settings
RETELL_VOICE_ID = "11labs-Adrian"
RETELL_MODEL = "gpt-4o"

# End call tool definition
END_CALL_TOOL = {
    "type": "end_call",
    "name": "end_call",
    "description": (
        "End the call when: "
        "1) All required information has been collected and goodbye has been said, "
        "2) After 3 attempts to get information from an uncooperative driver who only gives single-word responses, "
        "3) Emergency information has been gathered and escalation statement has been made. "
        "Always say a brief farewell before ending."
    )
}
