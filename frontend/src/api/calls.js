import apiClient from '../client';

export const callsAPI = {
  // Initiate a web call (browser-based)
  initiateWeb: async (callData) => {
    const response = await apiClient.post('/api/calls/initiate-web', callData);
    return response.data;
  },

  // Initiate a phone call
  initiate: async (callData) => {
    const response = await apiClient.post('/api/calls/initiate', callData);
    return response.data;
  },

  // Get call details by ID
  getCall: async (callId) => {
    const response = await apiClient.get(`/api/calls/${callId}`);
    return response.data;
  },

  // List all calls with optional ordering
  listCalls: async (orderBy = 'created_at', ascending = false) => {
    const response = await apiClient.get('/api/calls', {
      params: { order_by: orderBy, ascending }
    });
    return response.data;
  },
};
