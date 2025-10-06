"""
Custom exception classes for the Logistics Voice Agent system.
"""

from fastapi import HTTPException
from typing import Optional


class AgentConfigurationError(HTTPException):
    """Raised when agent configuration is missing or invalid."""
    
    def __init__(self, scenario_type: str, detail: Optional[str] = None):
        detail = detail or f"No agent configured for {scenario_type} scenario"
        super().__init__(status_code=400, detail=detail)


class CallLogCreationError(HTTPException):
    """Raised when call log creation fails."""
    
    def __init__(self, detail: Optional[str] = None):
        detail = detail or "Failed to create call log"
        super().__init__(status_code=500, detail=detail)


class CallNotFoundError(HTTPException):
    """Raised when a call cannot be found."""
    
    def __init__(self, call_id: str):
        super().__init__(status_code=404, detail=f"Call {call_id} not found")


class ConfigurationNotFoundError(HTTPException):
    """Raised when configuration cannot be found."""
    
    def __init__(self, scenario_type: str):
        super().__init__(
            status_code=404, 
            detail=f"Configuration for {scenario_type} not found"
        )


class EnvironmentVariableError(HTTPException):
    """Raised when required environment variable is missing."""
    
    def __init__(self, var_name: str):
        super().__init__(
            status_code=500,
            detail=f"{var_name} not configured"
        )


class InvalidPhoneNumberError(HTTPException):
    """Raised when phone number validation fails."""
    
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=detail)
