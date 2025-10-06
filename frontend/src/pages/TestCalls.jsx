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
        <div className="card">
          <h2 className="text-xl sm:text-2xl font-semibold text-neutral-900 mb-3 sm:mb-4">
            Web Call Active
          </h2>
          
          <div className="mb-4 sm:mb-6 p-3 sm:p-4 bg-primary-50 border border-primary-200 rounded-lg space-y-2">
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
              className="text-primary-600 hover:text-primary-700 hover:underline text-sm font-medium touch-manipulation"
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
      <div className="card">
        <h2 className="text-xl sm:text-2xl font-semibold text-neutral-900 mb-1 sm:mb-2">
          Test Web Call
        </h2>
        <p className="text-xs sm:text-sm text-neutral-600 mb-4 sm:mb-6">
          Browser-based voice call (no phone number needed)
        </p>

        {error && (
          <div className="alert-error mb-4">
            <p className="text-sm">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="driver-name" className="form-label">
              Driver Name
            </label>
            <input
              id="driver-name"
              type="text"
              name="driver_name"
              value={formData.driver_name}
              onChange={handleChange}
              required
              className="form-input"
              placeholder="John Doe"
            />
          </div>

          <div>
            <label htmlFor="load-number" className="form-label">
              Load Number
            </label>
            <input
              id="load-number"
              type="text"
              name="load_number"
              value={formData.load_number}
              onChange={handleChange}
              required
              className="form-input"
              placeholder="LOAD-12345"
            />
          </div>

          <div>
            <label className="form-label">
              Scenario Type
            </label>
            <div className="grid grid-cols-2 gap-2 sm:gap-3">
              <label className={`flex items-center justify-center px-4 py-3 sm:py-2.5 border-2 rounded-md cursor-pointer transition-all touch-manipulation ${
                formData.scenario_type === SCENARIO_TYPES.CHECKIN
                  ? 'border-primary-600 bg-primary-50'
                  : 'border-neutral-300 hover:border-primary-400 active:border-primary-500'
              }`}>
                <input
                  type="radio"
                  name="scenario_type"
                  value={SCENARIO_TYPES.CHECKIN}
                  checked={formData.scenario_type === SCENARIO_TYPES.CHECKIN}
                  onChange={handleChange}
                  className="sr-only"
                />
                <span className="text-sm font-medium text-neutral-700">Check-in</span>
              </label>
              <label className={`flex items-center justify-center px-4 py-3 sm:py-2.5 border-2 rounded-md cursor-pointer transition-all touch-manipulation ${
                formData.scenario_type === SCENARIO_TYPES.EMERGENCY
                  ? 'border-primary-600 bg-primary-50'
                  : 'border-neutral-300 hover:border-primary-400 active:border-primary-500'
              }`}>
                <input
                  type="radio"
                  name="scenario_type"
                  value={SCENARIO_TYPES.EMERGENCY}
                  checked={formData.scenario_type === SCENARIO_TYPES.EMERGENCY}
                  onChange={handleChange}
                  className="sr-only"
                />
                <span className="text-sm font-medium text-neutral-700">Emergency</span>
              </label>
            </div>
          </div>

          <div className="pt-2">
            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary w-full"
            >
              {isLoading ? 'Preparing Call...' : 'Start Web Call'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
