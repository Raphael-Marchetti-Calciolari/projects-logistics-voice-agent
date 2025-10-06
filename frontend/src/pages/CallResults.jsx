import { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useCalls } from '../hooks/useCalls';
import { formatDate, formatFieldName, formatBoolean, getStatusConfig } from '../utils/formatters';
import { CALL_STATUS, CALL_STATUS_CONFIG, POLLING_INTERVALS } from '../constants';

export default function CallResults() {
  const { id } = useParams();
  const [call, setCall] = useState(null);
  const { getCall, isLoading, error } = useCalls();

  const loadCall = useCallback(async () => {
    try {
      const data = await getCall(id);
      setCall(data);
    } catch (err) {
      console.error('Failed to load call:', err);
    }
  }, [id, getCall]);

  useEffect(() => {
    loadCall();
  }, [loadCall]);

  // Poll for updates if call is in progress
  useEffect(() => {
    if (!call) return;

    const shouldPoll = 
      call.call_status === CALL_STATUS.INITIATED || 
      call.call_status === CALL_STATUS.IN_PROGRESS;

    if (!shouldPoll) return;

    const interval = setInterval(() => {
      loadCall();
    }, POLLING_INTERVALS.CALL_STATUS);

    return () => clearInterval(interval);
  }, [call, loadCall]);

  if (isLoading && !call) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-neutral-500 text-sm">Loading call details...</div>
      </div>
    );
  }

  if (error || !call) {
    return (
      <div className="alert-error">
        <p className="text-sm">{error || 'Call not found'}</p>
        <Link to="/test" className="mt-3 inline-block text-error-700 hover:text-error-800 hover:underline text-sm font-medium touch-manipulation">
          Back to Test Calls
        </Link>
      </div>
    );
  }

  const statusConfig = getStatusConfig(call.call_status, CALL_STATUS_CONFIG);

  return (
    <div className="max-w-4xl mx-auto space-y-4 sm:space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <h2 className="text-xl sm:text-2xl font-semibold text-neutral-900">Call Details</h2>
        <Link to="/test" className="text-primary-600 hover:text-primary-700 hover:underline text-sm font-medium self-start sm:self-auto touch-manipulation">
          Back to Test Calls
        </Link>
      </div>

      {/* Call Information */}
      <div className="card">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <p className="text-xs font-medium text-neutral-500 uppercase tracking-wider mb-1">Driver Name</p>
            <p className="text-sm font-medium text-neutral-900">{call.driver_name}</p>
          </div>
          <div>
            <p className="text-xs font-medium text-neutral-500 uppercase tracking-wider mb-1">Phone Number</p>
            <p className="text-sm font-medium text-neutral-900">{call.driver_phone}</p>
          </div>
          <div>
            <p className="text-xs font-medium text-neutral-500 uppercase tracking-wider mb-1">Load Number</p>
            <p className="text-sm font-medium text-neutral-900">{call.load_number}</p>
          </div>
          <div>
            <p className="text-xs font-medium text-neutral-500 uppercase tracking-wider mb-1">Scenario</p>
            <p className="text-sm font-medium text-neutral-900 capitalize">{call.scenario_type}</p>
          </div>
          <div>
            <p className="text-xs font-medium text-neutral-500 uppercase tracking-wider mb-1">Status</p>
            <span className={`status-badge ${statusConfig.className}`}>
              {statusConfig.label}
            </span>
          </div>
          <div>
            <p className="text-xs font-medium text-neutral-500 uppercase tracking-wider mb-1">Created</p>
            <p className="text-sm font-medium text-neutral-900">{formatDate(call.created_at)}</p>
          </div>
        </div>

        {call.retell_call_id && (
          <div className="mt-4 pt-4 border-t border-neutral-200">
            <p className="text-xs font-medium text-neutral-500 uppercase tracking-wider mb-1">Retell Call ID</p>
            <p className="font-mono text-xs text-neutral-700 break-all">{call.retell_call_id}</p>
          </div>
        )}
      </div>

      {/* Transcript */}
      {call.raw_transcript && (
        <div className="card">
          <h3 className="text-base sm:text-lg font-medium text-neutral-900 mb-3 sm:mb-4">Transcript</h3>
          <div className="bg-neutral-50 rounded-md p-3 sm:p-4 border border-neutral-200 max-h-96 overflow-y-auto">
            <p className="text-xs sm:text-sm text-neutral-800 whitespace-pre-wrap leading-relaxed">{call.raw_transcript}</p>
          </div>
        </div>
      )}

      {/* Extracted Data */}
      {call.structured_data && (
        <div className="card">
          <h3 className="text-base sm:text-lg font-medium text-neutral-900 mb-3 sm:mb-4">Extracted Data</h3>
          <div className="space-y-2.5 sm:space-y-3">
            {Object.entries(call.structured_data).map(([key, value]) => (
              <div key={key} className="flex flex-col sm:flex-row gap-1 sm:gap-0">
                <span className="text-xs sm:text-sm font-medium text-neutral-500 sm:w-1/3">
                  {formatFieldName(key)}:
                </span>
                <span className="text-xs sm:text-sm text-neutral-900 sm:w-2/3 break-words">
                  {typeof value === 'boolean' ? formatBoolean(value) : value}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Status Messages */}
      {!call.raw_transcript && call.call_status !== CALL_STATUS.FAILED && (
        <div className="alert-info">
          <p className="text-sm">
            {call.call_status === CALL_STATUS.COMPLETED
              ? 'Call completed. Transcript processing...'
              : 'Call in progress. Updates will appear automatically.'}
          </p>
        </div>
      )}
    </div>
  );
}
