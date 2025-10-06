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
        <div className="text-neutral-500 text-sm">Loading configuration...</div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white shadow-sm rounded-lg border border-neutral-200 p-6">
        <h2 className="text-2xl font-semibold text-neutral-900 mb-2">
          Agent Configuration
        </h2>
        <p className="text-sm text-neutral-600 mb-6">
          Configure system prompts and voice settings for AI agents
        </p>

        {error && (
          <div className="mb-4 p-3 bg-error-50 border border-error-200 rounded-md">
            <p className="text-error-700 text-sm">{error}</p>
          </div>
        )}

        {success && (
          <div className="mb-4 p-3 bg-success-50 border border-success-200 rounded-md">
            <p className="text-success-700 text-sm">Configuration saved successfully!</p>
          </div>
        )}

        <form onSubmit={handleSave} className="space-y-6">
          {/* Scenario Type Selector */}
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-2">
              Scenario Type
            </label>
            <div className="flex space-x-2">
              {Object.values(SCENARIO_TYPES).map((type) => (
                <button
                  key={type}
                  type="button"
                  onClick={() => handleScenarioChange(type)}
                  className={`min-w-[120px] px-4 py-2 rounded-md text-sm font-medium transition-all duration-150 ${
                    scenarioType === type
                      ? 'bg-primary-600 text-white shadow-sm'
                      : 'bg-neutral-100 text-neutral-700 hover:bg-neutral-200'
                  }`}
                >
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {/* System Prompt */}
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-2">
              System Prompt
            </label>
            <textarea
              value={systemPrompt}
              onChange={(e) => setSystemPrompt(e.target.value)}
              required
              rows={12}
              className="w-full px-3 py-2 border border-neutral-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent font-mono"
              placeholder="Enter the system prompt that guides the agent's conversation..."
            />
            <p className="mt-1.5 text-xs text-neutral-500">
              This prompt defines how the agent behaves during calls
            </p>
          </div>

          {/* Voice Settings */}
          <div className="border-t border-neutral-200 pt-6">
            <h3 className="text-lg font-medium text-neutral-900 mb-4">Voice Settings</h3>

            {/* Enable Backchannel */}
            <div className="mb-4">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={retellSettings.enable_backchannel}
                  onChange={(e) => updateSetting('enable_backchannel', e.target.checked)}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-neutral-300 rounded"
                />
                <span className="ml-2 text-sm text-neutral-700">Enable Backchannel</span>
              </label>
              <p className="ml-6 text-xs text-neutral-500 mt-0.5">Natural sounds like "mm-hmm" during conversation</p>
            </div>

            {/* Backchannel Frequency */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-neutral-700 mb-1.5">
                Backchannel Frequency: <span className="text-primary-600 font-mono">{retellSettings.backchannel_frequency}</span>
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={retellSettings.backchannel_frequency}
                onChange={(e) => updateSetting('backchannel_frequency', parseFloat(e.target.value))}
                className="w-full h-2 bg-neutral-200 rounded-lg appearance-none cursor-pointer accent-primary-600"
              />
            </div>

            {/* Interruption Sensitivity */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-neutral-700 mb-1.5">
                Interruption Sensitivity: <span className="text-primary-600 font-mono">{retellSettings.interruption_sensitivity}</span>
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={retellSettings.interruption_sensitivity}
                onChange={(e) => updateSetting('interruption_sensitivity', parseFloat(e.target.value))}
                className="w-full h-2 bg-neutral-200 rounded-lg appearance-none cursor-pointer accent-primary-600"
              />
              <p className="text-xs text-neutral-500 mt-0.5">How easily the agent can be interrupted</p>
            </div>

            {/* Voice Speed */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-neutral-700 mb-1.5">
                Voice Speed: <span className="text-primary-600 font-mono">{retellSettings.voice_speed}</span>
              </label>
              <input
                type="range"
                min="0.5"
                max="2"
                step="0.1"
                value={retellSettings.voice_speed}
                onChange={(e) => updateSetting('voice_speed', parseFloat(e.target.value))}
                className="w-full h-2 bg-neutral-200 rounded-lg appearance-none cursor-pointer accent-primary-600"
              />
            </div>

            {/* Responsiveness */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-neutral-700 mb-1.5">
                Responsiveness: <span className="text-primary-600 font-mono">{retellSettings.responsiveness}</span>
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={retellSettings.responsiveness}
                onChange={(e) => updateSetting('responsiveness', parseFloat(e.target.value))}
                className="w-full h-2 bg-neutral-200 rounded-lg appearance-none cursor-pointer accent-primary-600"
              />
              <p className="text-xs text-neutral-500 mt-0.5">How quickly agent responds</p>
            </div>
          </div>

          {/* Submit Button */}
          <div className="pt-4">
            <button
              type="submit"
              disabled={isSaving}
              className="btn-primary w-full py-2.5"
            >
              {isSaving ? 'Saving...' : 'Save Configuration'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
