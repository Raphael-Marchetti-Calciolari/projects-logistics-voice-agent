import apiClient from '../client';

export const configurationsAPI = {
  // Get configuration for a specific scenario
  getConfiguration: async (scenarioType) => {
    const response = await apiClient.get(`/api/configurations/${scenarioType}`);
    return response.data;
  },

  // Create or update configuration
  saveConfiguration: async (configData) => {
    const response = await apiClient.post('/api/configurations', configData);
    return response.data;
  },

  // List all configurations
  listConfigurations: async () => {
    const response = await apiClient.get('/api/configurations');
    return response.data;
  },
};
