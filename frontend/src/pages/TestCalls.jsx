import { useState } from 'react';
import { useCalls } from '../hooks/useCalls';
import RetellWebCall from '../components/RetellWebCall';
import { SCENARIO_TYPES } from '../constants';

export default function TestCalls() {
  const [formData, setFormData] = useState({
    driver_name: '',
    load_number: '',
    scenario_type: SCENARIO_TYPES.CHECKIN,
  });
  const [webCallData, setWebCallData] = useState(null);

  const { initiateWebCall, isLoading, error, clearError } = useCalls();

  const handleSubmit = async (e) => {
    e.preventDefault();
    clearError();

    try {
      const result = await initiateWebCall(formData);
      setWebCallData(result);
    } catch (err) {
      // Error is handled by the hook
      console.error('Failed to initiate call:', err);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleCallEnd = () => {
    window.location.href = `/calls/${webCallData.call_id}`;
  };

  if (webCallData) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Web Call Active
          </h2>
          
          <div className="mb-6 p-4 bg-blue-50 rounded-lg space-y-2">
            <p className="text-sm text-gray-700">
              <strong>Driver:</strong> {formData.driver_name}
            </p>
            <p className="text-sm text-gray-700">
              <strong>Load:</strong> {formData.load_number}
            </p>
            <p className="text-sm text-gray-700">
              <strong>Scenario:</strong> {formData.scenario_type}
            </p>
          </div>

          <RetellWebCall 
            accessToken={webCallData.access_token}
            onCallEnd={handleCallEnd}
          />

          <div className="mt-4 text-center">
            <button
              onClick={() => window.location.href = `/calls/${webCallData.call_id}`}
              className="text-blue-600 hover:underline text-sm"
            >
              View Call Details
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          Test Web Call
        </h2>
        <p className="text-gray-600 mb-6">
          Browser-based voice call (no phone number needed)
        </p>

        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Driver Name
            </label>
            <input
              type="text"
              name="driver_name"
              value={formData.driver_name}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="John Doe"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Load Number
            </label>
            <input
              type="text"
              name="load_number"
              value={formData.load_number}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="LOAD-12345"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Scenario Type
            </label>
            <div className="flex space-x-4">
              <label className="flex items-center">
                <input
                  type="radio"
                  name="scenario_type"
                  value={SCENARIO_TYPES.CHECKIN}
                  checked={formData.scenario_type === SCENARIO_TYPES.CHECKIN}
                  onChange={handleChange}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                />
                <span className="ml-2 text-sm text-gray-700">Check-in</span>
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  name="scenario_type"
                  value={SCENARIO_TYPES.EMERGENCY}
                  checked={formData.scenario_type === SCENARIO_TYPES.EMERGENCY}
                  onChange={handleChange}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                />
                <span className="ml-2 text-sm text-gray-700">Emergency</span>
              </label>
            </div>
          </div>

          <div className="pt-4">
            <button
              type="submit"
              disabled={isLoading}
              className="w-full px-6 py-3 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Preparing Call...' : 'Start Web Call'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
