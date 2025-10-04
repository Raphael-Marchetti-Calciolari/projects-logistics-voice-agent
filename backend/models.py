from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class RetellSettings(BaseModel):
    enable_backchannel: bool = True
    backchannel_frequency: float = Field(default=0.8, ge=0.0, le=1.0)
    interruption_sensitivity: float = Field(default=0.7, ge=0.0, le=1.0)
    ambient_sound_volume: float = Field(default=0.3, ge=0.0, le=1.0)
    enable_filler_words: bool = True
    response_delay_ms: int = Field(default=200, ge=0)
    voice_id: str = "default_voice"

class ConfigurationCreate(BaseModel):
    scenario_type: str = Field(..., pattern="^(checkin|emergency)$")
    system_prompt: str = Field(..., min_length=10)
    retell_settings: RetellSettings

class ConfigurationResponse(BaseModel):
    id: str
    scenario_type: str
    system_prompt: str
    retell_settings: dict
    created_at: str

class ConfigurationUpdate(BaseModel):
    system_prompt: Optional[str] = None
    retell_settings: Optional[RetellSettings] = None
