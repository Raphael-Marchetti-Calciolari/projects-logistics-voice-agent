import { useState, useEffect } from 'react';
import { useConfigurations } from '../hooks/useConfigurations';
import { SCENARIO_TYPES, DEFAULT_RETELL_SETTINGS } from '../constants';

export default function Configuration() {
  const [scenarioType, setScenarioType] = useState(SCENARIO_TYPES.CHECKIN);
  const [systemPrompt, setSystemPrompt] = useState('');
  const [retellSettings, setRetellSettings] = useState(DEFAULT_RETELL_SETTINGS);

  const {
    configuration,
    isLoading,
    isSaving,
    error,
    success,
    saveConfiguration,
  } = useConfigurations(scenarioType);

  // Update form when configuration loads
  useEffect(() => {
    if (configuration) {
      setSystemPrompt(configuration.system_prompt || '');
      setRetellSettings(configuration.retell_settings || DEFAULT_RETELL_SETTINGS);
    } else {
      setSystemPrompt('');
      setRetellSettings(DEFAULT_RETELL_SETTINGS);
    }
  }, [configuration]);

  const handleSave = async (e) => {
    e.preventDefault();

    try {
      await saveConfiguration({
        scenario_type: scenarioType,
        system_prompt: systemPrompt,
        retell_settings: retellSettings,
      });
    } catch (err) {
      console.error('Failed to save configuration:', err);
    }
  };

  const handleScenarioChange = (newScenarioType) => {
    setScenarioType(newScenarioType);
  };

  const updateSetting = (key, value) => {
    setRetellSettings({ ...retellSettings, [key]: value });
  };

  if (isLoading && !configuration) {
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
              {Object.values(SCENARIO_TYPES).map((type) => (
                <button
                  key={type}
                  type="button"
                  onClick={() => handleScenarioChange(type)}
                  className={`px-4 py-2 rounded-md text-sm font-medium ${
                    scenarioType === type
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </button>
              ))}
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
