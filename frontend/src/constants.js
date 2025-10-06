/**
 * Application-wide constants and configuration values.
 */

// Scenario types
export const SCENARIO_TYPES = {
  CHECKIN: 'checkin',
  EMERGENCY: 'emergency',
};

// Call statuses
export const CALL_STATUS = {
  INITIATED: 'initiated',
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed',
  FAILED: 'failed',
};

// Call status display configuration
export const CALL_STATUS_CONFIG = {
  [CALL_STATUS.INITIATED]: {
    label: 'Initiated',
    className: 'bg-yellow-100 text-yellow-800',
  },
  [CALL_STATUS.IN_PROGRESS]: {
    label: 'In Progress',
    className: 'bg-blue-100 text-blue-800',
  },
  [CALL_STATUS.COMPLETED]: {
    label: 'Completed',
    className: 'bg-green-100 text-green-800',
  },
  [CALL_STATUS.FAILED]: {
    label: 'Failed',
    className: 'bg-red-100 text-red-800',
  },
};

// Default retell settings
export const DEFAULT_RETELL_SETTINGS = {
  enable_backchannel: true,
  backchannel_frequency: 0.8,
  interruption_sensitivity: 0.7,
  ambient_sound: 'off',
  ambient_sound_volume: 0.3,
  voice_temperature: 1.0,
  voice_speed: 1.0,
  responsiveness: 1.0,
  voice_id: '11labs-Adrian',
};

// Polling intervals (in milliseconds)
export const POLLING_INTERVALS = {
  CALL_STATUS: 3000,
};
