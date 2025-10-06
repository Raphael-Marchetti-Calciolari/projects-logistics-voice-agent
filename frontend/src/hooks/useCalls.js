import { useState, useCallback } from 'react';
import { callsAPI } from '../api/calls';

/**
 * Custom hook for managing call-related operations.
 * 
 * @returns {Object} Call operations and state
 */
export const useCalls = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const initiateWebCall = useCallback(async (callData) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const result = await callsAPI.initiateWeb(callData);
      return result;
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Failed to initiate call';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const initiatePhoneCall = useCallback(async (callData) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const result = await callsAPI.initiate(callData);
      return result;
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Failed to initiate call';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const getCall = useCallback(async (callId) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const result = await callsAPI.getCall(callId);
      return result;
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Failed to fetch call';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    initiateWebCall,
    initiatePhoneCall,
    getCall,
    isLoading,
    error,
    clearError: () => setError(null),
  };
};
