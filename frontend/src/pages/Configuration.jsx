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
      <div className="card">
        <h2 className="text-xl sm:text-2xl font-semibold text-neutral-900 mb-1 sm:mb-2">
          Agent Configuration
        </h2>
        <p className="text-xs sm:text-sm text-neutral-600 mb-4 sm:mb-6">
          Configure system prompts and voice settings for AI agents
        </p>

        {error && (
          <div className="alert-error mb-4">
            <p className="text-sm">{error}</p>
          </div>
        )}

        {success && (
          <div className="alert-success mb-4">
            <p className="text-sm">Configuration saved successfully!</p>
          </div>
        )}

        <form onSubmit={handleSave} className="space-y-4 sm:space-y-6">
          {/* Scenario Type Selector */}
          <div>
            <label className="form-label">
              Scenario Type
            </label>
            <div className="flex flex-col sm:flex-row gap-2">
              {Object.values(SCENARIO_TYPES).map((type) => (
                <button
                  key={type}
                  type="button"
                  onClick={() => handleScenarioChange(type)}
                  className={`flex-1 sm:flex-none sm:min-w-[140px] px-4 py-2.5 sm:py-2 rounded-md text-sm font-medium transition-all duration-150 touch-manipulation ${
                    scenarioType === type
                      ? 'bg-primary-600 text-white shadow-sm'
                      : 'bg-neutral-100 text-neutral-700 hover:bg-neutral-200 active:bg-neutral-300'
                  }`}
                  aria-pressed={scenarioType === type}
                >
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {/* System Prompt */}
          <div>
            <label htmlFor="system-prompt" className="form-label">
              System Prompt
            </label>
            <textarea
              id="system-prompt"
              value={systemPrompt}
              onChange={(e) => setSystemPrompt(e.target.value)}
              required
              rows={10}
              className="form-textarea font-mono text-xs sm:text-sm"
              placeholder="Enter the system prompt that guides the agent's conversation..."
            />
            <p className="form-helper">
              This prompt defines how the agent behaves during calls
            </p>
          </div>

          {/* Voice Settings */}
          <div className="border-t border-neutral-200 pt-4 sm:pt-6">
            <h3 className="text-base sm:text-lg font-medium text-neutral-900 mb-3 sm:mb-4">Voice Settings</h3>

            <div className="space-y-4 sm:space-y-5">
              {/* Enable Backchannel */}
              <div>
                <label className="flex items-start sm:items-center">
                  <input
                    type="checkbox"
                    checked={retellSettings.enable_backchannel}
                    onChange={(e) => updateSetting('enable_backchannel', e.target.checked)}
                    className="mt-0.5 sm:mt-0 h-4 w-4 text-primary-600 focus:ring-primary-500 border-neutral-300 rounded cursor-pointer"
                  />
                  <span className="ml-2 text-sm text-neutral-700">Enable Backchannel</span>
                </label>
                <p className="ml-6 form-helper mt-0.5">Natural sounds like "mm-hmm" during conversation</p>
              </div>

              {/* Backchannel Frequency */}
              <div>
                <label htmlFor="backchannel-freq" className="form-label">
                  Backchannel Frequency: <span className="text-primary-600 font-mono text-sm">{retellSettings.backchannel_frequency.toFixed(1)}</span>
                </label>
                <input
                  id="backchannel-freq"
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={retellSettings.backchannel_frequency}
                  onChange={(e) => updateSetting('backchannel_frequency', parseFloat(e.target.value))}
                  className="w-full"
                  aria-label="Backchannel frequency slider"
                />
                <div className="flex justify-between text-xs text-neutral-500 mt-1">
                  <span>Less</span>
                  <span>More</span>
                </div>
              </div>

              {/* Interruption Sensitivity */}
              <div>
                <label htmlFor="interruption-sens" className="form-label">
                  Interruption Sensitivity: <span className="text-primary-600 font-mono text-sm">{retellSettings.interruption_sensitivity.toFixed(1)}</span>
                </label>
                <input
                  id="interruption-sens"
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={retellSettings.interruption_sensitivity}
                  onChange={(e) => updateSetting('interruption_sensitivity', parseFloat(e.target.value))}
                  className="w-full"
                  aria-label="Interruption sensitivity slider"
                />
                <p className="form-helper">How easily the agent can be interrupted</p>
              </div>

              {/* Voice Speed */}
              <div>
                <label htmlFor="voice-speed" className="form-label">
                  Voice Speed: <span className="text-primary-600 font-mono text-sm">{retellSettings.voice_speed.toFixed(1)}</span>
                </label>
                <input
                  id="voice-speed"
                  type="range"
                  min="0.5"
                  max="2"
                  step="0.1"
                  value={retellSettings.voice_speed}
                  onChange={(e) => updateSetting('voice_speed', parseFloat(e.target.value))}
                  className="w-full"
                  aria-label="Voice speed slider"
                />
                <div className="flex justify-between text-xs text-neutral-500 mt-1">
                  <span>Slower</span>
                  <span>Faster</span>
                </div>
              </div>

              {/* Responsiveness */}
              <div>
                <label htmlFor="responsiveness" className="form-label">
                  Responsiveness: <span className="text-primary-600 font-mono text-sm">{retellSettings.responsiveness.toFixed(1)}</span>
                </label>
                <input
                  id="responsiveness"
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={retellSettings.responsiveness}
                  onChange={(e) => updateSetting('responsiveness', parseFloat(e.target.value))}
                  className="w-full"
                  aria-label="Responsiveness slider"
                />
                <p className="form-helper">How quickly agent responds</p>
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <div className="pt-2 sm:pt-4">
            <button
              type="submit"
              disabled={isSaving}
              className="btn-primary w-full"
            >
              {isSaving ? 'Saving...' : 'Save Configuration'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
