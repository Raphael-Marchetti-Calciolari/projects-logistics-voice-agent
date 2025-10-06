"""
Application startup and initialization logic.
"""

import asyncio
from services.database_service import db_service
from retell_client import retell_client
from default_prompts import CHECKIN_PROMPT, EMERGENCY_PROMPT, DEFAULT_RETELL_SETTINGS
from constants import END_CALL_TOOL, SCENARIO_CHECKIN, SCENARIO_EMERGENCY
from logger import app_logger


async def ensure_agent_exists(scenario_type: str, system_prompt: str) -> str:
    """
    Check if agent exists, create if not.
    
    Args:
        scenario_type: Type of scenario (checkin, emergency)
        system_prompt: System prompt for the agent
        
    Returns:
        Agent ID
    """
    try:
        # Check if configuration exists
        config = db_service.get_agent_configuration(scenario_type)
        
        if config:
            # Check if agent_id exists
            if config.get("agent_id") and config.get("llm_id"):
                app_logger.info(f"{scenario_type.title()} agent already exists: {config['agent_id']}")
                
                # Update the LLM to ensure it has the end_call tool
                app_logger.info(f"Ensuring {scenario_type} LLM has end_call tool")
                await retell_client.update_llm(
                    llm_id=config["llm_id"],
                    general_tools=[END_CALL_TOOL]
                )
                app_logger.info(f"Updated {scenario_type} LLM with end_call tool")
                
                return config["agent_id"]
            else:
                app_logger.warning(f"{scenario_type.title()} config exists but no agent_id, creating")
                config_id = config["id"]
        else:
            app_logger.info(f"Creating {scenario_type} configuration")
            # Create configuration
            config_data = {
                "scenario_type": scenario_type,
                "system_prompt": system_prompt,
                "retell_settings": DEFAULT_RETELL_SETTINGS
            }
            config = db_service.save_configuration(scenario_type, config_data)
            config_id = config["id"]
            app_logger.info(f"Created {scenario_type} configuration")
        
        # Create LLM with end_call tool
        app_logger.info(f"Creating {scenario_type} LLM with end_call tool")
        llm_id = await retell_client.create_llm(
            general_prompt=system_prompt,
            general_tools=[END_CALL_TOOL]
        )
        app_logger.info(f"Created LLM: {llm_id}")
        
        # Update config with LLM ID
        db_service.save_configuration(scenario_type, {"llm_id": llm_id})
        
        # Create agent
        app_logger.info(f"Creating {scenario_type} agent")
        agent_name = f"Dispatch {scenario_type.title()} Agent"
        agent_result = await retell_client.create_agent(agent_name, llm_id)
        agent_id = agent_result['agent_id']
        app_logger.info(f"Created agent: {agent_id}")
        
        # Update config with agent ID
        db_service.save_configuration(scenario_type, {"agent_id": agent_id})
        
        app_logger.info(f"{scenario_type.title()} agent fully configured\n")
        return agent_id
    except Exception as e:
        app_logger.error(f"Error ensuring {scenario_type} agent: {e}", exc_info=True)
        return None


async def initialize_agents():
    """Initialize both check-in and emergency agents on startup."""
    app_logger.info("=" * 60)
    app_logger.info("INITIALIZING LOGISTICS VOICE AGENTS")
    app_logger.info("=" * 60)
    
    # Ensure check-in agent exists
    await ensure_agent_exists(SCENARIO_CHECKIN, CHECKIN_PROMPT)
    
    # Ensure emergency agent exists
    await ensure_agent_exists(SCENARIO_EMERGENCY, EMERGENCY_PROMPT)
    
    app_logger.info("=" * 60)
    app_logger.info("AGENT INITIALIZATION COMPLETE")
    app_logger.info("=" * 60)


def run_startup():
    """Synchronous wrapper for startup."""
    asyncio.run(initialize_agents())
