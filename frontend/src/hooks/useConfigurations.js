import { useState, useCallback, useEffect } from 'react';
import { configurationsAPI } from '../api/configurations';

/**
 * Custom hook for managing agent configuration operations.
 * 
 * @param {string} scenarioType - Type of scenario (checkin or emergency)
 * @returns {Object} Configuration operations and state
 */
export const useConfigurations = (scenarioType) => {
  const [configuration, setConfiguration] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const loadConfiguration = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const config = await configurationsAPI.getConfiguration(scenarioType);
      setConfiguration(config);
      return config;
    } catch (error) {
      if (error.response?.status === 404) {
        // No config exists yet, return null
        setConfiguration(null);
        return null;
      }
      const errorMessage = 'Failed to load configuration';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [scenarioType]);

  const saveConfiguration = useCallback(async (configData) => {
    setIsSaving(true);
    setError(null);
    setSuccess(false);

    try {
      const result = await configurationsAPI.saveConfiguration(configData);
      setConfiguration(result);
      setSuccess(true);
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(false), 3000);
      
      return result;
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Failed to save configuration';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsSaving(false);
    }
  }, []);

  const listAllConfigurations = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const configs = await configurationsAPI.listConfigurations();
      return configs;
    } catch {
      const errorMessage = 'Failed to list configurations';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Load configuration when scenario type changes
  useEffect(() => {
    if (scenarioType) {
      loadConfiguration();
    }
  }, [scenarioType, loadConfiguration]);

  return {
    configuration,
    isLoading,
    isSaving,
    error,
    success,
    loadConfiguration,
    saveConfiguration,
    listAllConfigurations,
    clearError: () => setError(null),
  };
};
