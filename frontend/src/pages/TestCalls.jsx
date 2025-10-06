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
        <div className="bg-white shadow-sm rounded-lg border border-neutral-200 p-6">
          <h2 className="text-2xl font-semibold text-neutral-900 mb-4">
            Web Call Active
          </h2>
          
          <div className="mb-6 p-4 bg-primary-50 border border-primary-200 rounded-lg space-y-2">
            <p className="text-sm text-neutral-700">
              <strong className="font-medium text-neutral-900">Driver:</strong> {formData.driver_name}
            </p>
            <p className="text-sm text-neutral-700">
              <strong className="font-medium text-neutral-900">Load:</strong> {formData.load_number}
            </p>
            <p className="text-sm text-neutral-700">
              <strong className="font-medium text-neutral-900">Scenario:</strong> {formData.scenario_type}
            </p>
          </div>

          <RetellWebCall 
            accessToken={webCallData.access_token}
            onCallEnd={handleCallEnd}
          />

          <div className="mt-4 text-center">
            <button
              onClick={() => window.location.href = `/calls/${webCallData.call_id}`}
              className="text-primary-600 hover:text-primary-700 hover:underline text-sm font-medium"
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
      <div className="bg-white shadow-sm rounded-lg border border-neutral-200 p-6">
        <h2 className="text-2xl font-semibold text-neutral-900 mb-2">
          Test Web Call
        </h2>
        <p className="text-sm text-neutral-600 mb-6">
          Browser-based voice call (no phone number needed)
        </p>

        {error && (
          <div className="mb-4 p-3 bg-error-50 border border-error-200 rounded-md">
            <p className="text-error-700 text-sm">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-1.5">
              Driver Name
            </label>
            <input
              type="text"
              name="driver_name"
              value={formData.driver_name}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-neutral-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="John Doe"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-1.5">
              Load Number
            </label>
            <input
              type="text"
              name="load_number"
              value={formData.load_number}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-neutral-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="LOAD-12345"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-2">
              Scenario Type
            </label>
            <div className="flex space-x-2">
              <label className="flex items-center min-w-[120px] px-4 py-2 border-2 border-neutral-300 rounded-md cursor-pointer transition-all hover:border-primary-500 has-[:checked]:border-primary-600 has-[:checked]:bg-primary-50">
                <input
                  type="radio"
                  name="scenario_type"
                  value={SCENARIO_TYPES.CHECKIN}
                  checked={formData.scenario_type === SCENARIO_TYPES.CHECKIN}
                  onChange={handleChange}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-neutral-300"
                />
                <span className="ml-2 text-sm text-neutral-700 font-medium">Check-in</span>
              </label>
              <label className="flex items-center min-w-[120px] px-4 py-2 border-2 border-neutral-300 rounded-md cursor-pointer transition-all hover:border-primary-500 has-[:checked]:border-primary-600 has-[:checked]:bg-primary-50">
                <input
                  type="radio"
                  name="scenario_type"
                  value={SCENARIO_TYPES.EMERGENCY}
                  checked={formData.scenario_type === SCENARIO_TYPES.EMERGENCY}
                  onChange={handleChange}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-neutral-300"
                />
                <span className="ml-2 text-sm text-neutral-700 font-medium">Emergency</span>
              </label>
            </div>
          </div>

          <div className="pt-4">
            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary w-full py-2.5"
            >
              {isLoading ? 'Preparing Call...' : 'Start Web Call'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
