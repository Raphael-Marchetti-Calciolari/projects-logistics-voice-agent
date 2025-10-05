from pydantic import BaseModel, Field
from typing import Optional

class RetellSettings(BaseModel):
    enable_backchannel: bool = True
    backchannel_frequency: float = Field(default=0.8, ge=0.0, le=1.0)
    interruption_sensitivity: float = Field(default=0.7, ge=0.0, le=1.0)
    ambient_sound: Optional[str] = Field(default="off")
    ambient_sound_volume: float = Field(default=0.3, ge=0.0, le=1.0)
    voice_temperature: float = Field(default=1.0, ge=0.0, le=2.0)
    voice_speed: float = Field(default=1.0, ge=0.5, le=2.0)
    responsiveness: float = Field(default=1.0, ge=0.0, le=1.0)
    voice_id: str = "11labs-Adrian"

class ConfigurationCreate(BaseModel):
    scenario_type: str = Field(..., pattern="^(checkin|emergency)$")
    system_prompt: str = Field(..., min_length=10)
    retell_settings: RetellSettings

class ConfigurationResponse(BaseModel):
    id: str
    scenario_type: str
    system_prompt: str
    retell_settings: dict
    llm_id: Optional[str] = None
    agent_id: Optional[str] = None
    created_at: str
