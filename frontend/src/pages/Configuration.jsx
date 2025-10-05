import { useState, useEffect } from 'react';
import { configurationsAPI } from '../api/configurations';

export default function Configuration() {
  const [scenarioType, setScenarioType] = useState('checkin');
  const [systemPrompt, setSystemPrompt] = useState('');
  const [retellSettings, setRetellSettings] = useState({
    enable_backchannel: true,
    backchannel_frequency: 0.8,
    interruption_sensitivity: 0.7,
    ambient_sound: 'off',
    ambient_sound_volume: 0.3,
    voice_temperature: 1.0,
    voice_speed: 1.0,
    responsiveness: 1.0,
    voice_id: '11labs-Adrian',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    loadConfiguration();
  }, [scenarioType]);

  const loadConfiguration = async () => {
    setIsLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const config = await configurationsAPI.getConfiguration(scenarioType);
      setSystemPrompt(config.system_prompt);
      setRetellSettings(config.retell_settings);
    } catch (err) {
      if (err.response?.status === 404) {
        // No config exists yet, use defaults
        setSystemPrompt('');
        setRetellSettings({
          enable_backchannel: true,
          backchannel_frequency: 0.8,
          interruption_sensitivity: 0.7,
          ambient_sound: 'off',
          ambient_sound_volume: 0.3,
          voice_temperature: 1.0,
          voice_speed: 1.0,
          responsiveness: 1.0,
          voice_id: '11labs-Adrian',
        });
      } else {
        setError('Failed to load configuration');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setIsSaving(true);
    setError(null);
    setSuccess(false);

    try {
      await configurationsAPI.saveConfiguration({
        scenario_type: scenarioType,
        system_prompt: systemPrompt,
        retell_settings: retellSettings,
      });
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save configuration');
    } finally {
      setIsSaving(false);
    }
  };

  const updateSetting = (key, value) => {
    setRetellSettings({ ...retellSettings, [key]: value });
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-500">Loading configuration...</div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          Agent Configuration
        </h2>
        <p className="text-gray-600 mb-6">
          Configure system prompts and voice settings for AI agents
        </p>

        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}

        {success && (
          <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-md">
            <p className="text-green-800 text-sm">Configuration saved successfully!</p>
          </div>
        )}

        <form onSubmit={handleSave} className="space-y-6">
          {/* Scenario Type Selector */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Scenario Type
            </label>
            <div className="flex space-x-4">
              <button
                type="button"
                onClick={() => setScenarioType('checkin')}
                className={`px-4 py-2 rounded-md text-sm font-medium ${
                  scenarioType === 'checkin'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                Check-in
              </button>
              <button
                type="button"
                onClick={() => setScenarioType('emergency')}
                className={`px-4 py-2 rounded-md text-sm font-medium ${
                  scenarioType === 'emergency'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                Emergency
              </button>
            </div>
          </div>

          {/* System Prompt */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              System Prompt
            </label>
            <textarea
              value={systemPrompt}
              onChange={(e) => setSystemPrompt(e.target.value)}
              required
              rows={12}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 font-mono text-sm"
              placeholder="Enter the system prompt that guides the agent's conversation..."
            />
            <p className="mt-1 text-xs text-gray-500">
              This prompt defines how the agent behaves during calls
            </p>
          </div>

          {/* Voice Settings */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Voice Settings</h3>

            {/* Enable Backchannel */}
            <div className="mb-4">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={retellSettings.enable_backchannel}
                  onChange={(e) => updateSetting('enable_backchannel', e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span className="ml-2 text-sm text-gray-700">Enable Backchannel</span>
              </label>
              <p className="ml-6 text-xs text-gray-500">Natural sounds like "mm-hmm" during conversation</p>
            </div>

            {/* Backchannel Frequency */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Backchannel Frequency: {retellSettings.backchannel_frequency}
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={retellSettings.backchannel_frequency}
                onChange={(e) => updateSetting('backchannel_frequency', parseFloat(e.target.value))}
                className="w-full"
              />
            </div>

            {/* Interruption Sensitivity */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Interruption Sensitivity: {retellSettings.interruption_sensitivity}
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={retellSettings.interruption_sensitivity}
                onChange={(e) => updateSetting('interruption_sensitivity', parseFloat(e.target.value))}
                className="w-full"
              />
              <p className="text-xs text-gray-500">How easily the agent can be interrupted</p>
            </div>

            {/* Voice Speed */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Voice Speed: {retellSettings.voice_speed}
              </label>
              <input
                type="range"
                min="0.5"
                max="2"
                step="0.1"
                value={retellSettings.voice_speed}
                onChange={(e) => updateSetting('voice_speed', parseFloat(e.target.value))}
                className="w-full"
              />
            </div>

            {/* Responsiveness */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Responsiveness: {retellSettings.responsiveness}
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={retellSettings.responsiveness}
                onChange={(e) => updateSetting('responsiveness', parseFloat(e.target.value))}
                className="w-full"
              />
              <p className="text-xs text-gray-500">How quickly agent responds</p>
            </div>
          </div>

          {/* Submit Button */}
          <div className="pt-4">
            <button
              type="submit"
              disabled={isSaving}
              className="w-full px-6 py-3 bg-blue-600 text-white font-medium rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSaving ? 'Saving...' : 'Save Configuration'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
