"""
Database service layer for Supabase operations.
"""

from typing import Dict, Any, Optional, List
from database import supabase
from constants import TABLE_AGENT_CONFIGURATIONS, TABLE_CALL_LOGS
from exceptions import CallNotFoundError, ConfigurationNotFoundError
from logger import service_logger


class DatabaseService:
    """Service class for database operations."""
    
    # PUBLIC_INTERFACE
    def get_agent_configuration(self, scenario_type: str) -> Optional[Dict[str, Any]]:
        """
        Get agent configuration for a scenario type.
        
        Args:
            scenario_type: Type of scenario (checkin, emergency)
            
        Returns:
            Configuration dictionary or None if not found
        """
        try:
            result = supabase.table(TABLE_AGENT_CONFIGURATIONS)\
                .select("*")\
                .eq("scenario_type", scenario_type)\
                .execute()
            
            return result.data[0] if result.data else None
        except Exception as e:
            service_logger.error(f"Error fetching agent configuration: {e}")
            raise
    
    # PUBLIC_INTERFACE
    def get_agent_id(self, scenario_type: str) -> Optional[str]:
        """
        Get agent ID for a scenario type.
        
        Args:
            scenario_type: Type of scenario (checkin, emergency)
            
        Returns:
            Agent ID or None if not found
        """
        config = self.get_agent_configuration(scenario_type)
        return config.get("agent_id") if config else None
    
    # PUBLIC_INTERFACE
    def create_call_log(self, call_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new call log entry.
        
        Args:
            call_data: Call log data
            
        Returns:
            Created call log record
            
        Raises:
            Exception: If creation fails
        """
        try:
            result = supabase.table(TABLE_CALL_LOGS).insert(call_data).execute()
            
            if not result.data:
                raise Exception("No data returned from insert")
            
            service_logger.info(f"Created call log: {result.data[0]['id']}")
            return result.data[0]
        except Exception as e:
            service_logger.error(f"Error creating call log: {e}")
            raise
    
    # PUBLIC_INTERFACE
    def update_call_log(
        self, 
        call_id: str, 
        update_data: Dict[str, Any],
        id_field: str = "id"
    ) -> bool:
        """
        Update a call log entry.
        
        Args:
            call_id: ID of the call to update
            update_data: Data to update
            id_field: Field name to match on (id or retell_call_id)
            
        Returns:
            True if update successful
        """
        try:
            result = supabase.table(TABLE_CALL_LOGS)\
                .update(update_data)\
                .eq(id_field, call_id)\
                .execute()
            
            service_logger.info(f"Updated call log {call_id}: {len(result.data)} rows affected")
            return bool(result.data)
        except Exception as e:
            service_logger.error(f"Error updating call log: {e}")
            raise
    
    # PUBLIC_INTERFACE
    def get_call_log(self, call_id: str) -> Dict[str, Any]:
        """
        Get call log by ID.
        
        Args:
            call_id: Call ID
            
        Returns:
            Call log dictionary
            
        Raises:
            CallNotFoundError: If call not found
        """
        try:
            result = supabase.table(TABLE_CALL_LOGS)\
                .select("*")\
                .eq("id", call_id)\
                .execute()
            
            if not result.data:
                raise CallNotFoundError(call_id)
            
            return result.data[0]
        except CallNotFoundError:
            raise
        except Exception as e:
            service_logger.error(f"Error fetching call log: {e}")
            raise
    
    # PUBLIC_INTERFACE
    def get_call_by_retell_id(self, retell_call_id: str) -> Optional[Dict[str, Any]]:
        """
        Get call log by Retell call ID.
        
        Args:
            retell_call_id: Retell call ID
            
        Returns:
            Call log dictionary or None
        """
        try:
            result = supabase.table(TABLE_CALL_LOGS)\
                .select("*")\
                .eq("retell_call_id", retell_call_id)\
                .execute()
            
            return result.data[0] if result.data else None
        except Exception as e:
            service_logger.error(f"Error fetching call by Retell ID: {e}")
            raise
    
    # PUBLIC_INTERFACE
    def list_call_logs(self, order_by: str = "created_at", ascending: bool = False) -> List[Dict[str, Any]]:
        """
        List all call logs with optional ordering.
        
        Args:
            order_by: Field to order by (default: created_at)
            ascending: Sort order direction (default: False for descending)
            
        Returns:
            List of call log dictionaries
        """
        try:
            query = supabase.table(TABLE_CALL_LOGS).select("*")
            
            # Apply ordering
            query = query.order(order_by, desc=not ascending)
            
            result = query.execute()
            return result.data
        except Exception as e:
            service_logger.error(f"Error listing call logs: {e}")
            raise
    
    # PUBLIC_INTERFACE
    def save_configuration(
        self, 
        scenario_type: str, 
        config_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create or update agent configuration.
        
        Args:
            scenario_type: Scenario type
            config_data: Configuration data
            
        Returns:
            Created/updated configuration
        """
        try:
            existing = self.get_agent_configuration(scenario_type)
            
            if existing:
                result = supabase.table(TABLE_AGENT_CONFIGURATIONS)\
                    .update(config_data)\
                    .eq("scenario_type", scenario_type)\
                    .execute()
            else:
                result = supabase.table(TABLE_AGENT_CONFIGURATIONS)\
                    .insert(config_data)\
                    .execute()
            
            if not result.data:
                raise Exception("No data returned from save")
            
            service_logger.info(f"Saved configuration for {scenario_type}")
            return result.data[0]
        except Exception as e:
            service_logger.error(f"Error saving configuration: {e}")
            raise
    
    # PUBLIC_INTERFACE
    def list_configurations(self) -> List[Dict[str, Any]]:
        """
        List all agent configurations.
        
        Returns:
            List of configuration dictionaries
        """
        try:
            result = supabase.table(TABLE_AGENT_CONFIGURATIONS)\
                .select("*")\
                .order("scenario_type")\
                .execute()
            
            return result.data
        except Exception as e:
            service_logger.error(f"Error listing configurations: {e}")
            raise


# Singleton instance
db_service = DatabaseService()
