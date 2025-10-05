import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { callsAPI } from '../api/calls';

export default function CallResults() {
  const { id } = useParams();
  const [call, setCall] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadCall();
    
    const interval = setInterval(() => {
      if (call?.call_status === 'initiated' || call?.call_status === 'in_progress') {
        loadCall();
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [id, call?.call_status]);

  const loadCall = async () => {
    try {
      const data = await callsAPI.getCall(id);
      setCall(data);
    } catch (err) {
      setError('Failed to load call details');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-500">Loading call details...</div>
      </div>
    );
  }

  if (error || !call) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <p className="text-red-800">{error || 'Call not found'}</p>
        <Link to="/test" className="text-blue-600 hover:underline mt-2 inline-block">
          Back to Test Calls
        </Link>
      </div>
    );
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'initiated':
        return 'bg-yellow-100 text-yellow-800';
      case 'in_progress':
        return 'bg-blue-100 text-blue-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Call Details</h2>
        <Link to="/test" className="text-blue-600 hover:underline text-sm">
          Back to Test Calls
        </Link>
      </div>

      <div className="bg-white shadow rounded-lg p-6">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-500">Driver Name</p>
            <p className="font-medium text-gray-900">{call.driver_name}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Phone Number</p>
            <p className="font-medium text-gray-900">{call.driver_phone}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Load Number</p>
            <p className="font-medium text-gray-900">{call.load_number}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Scenario</p>
            <p className="font-medium text-gray-900 capitalize">{call.scenario_type}</p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Status</p>
            <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(call.call_status)}`}>
              {call.call_status}
            </span>
          </div>
          <div>
            <p className="text-sm text-gray-500">Created</p>
            <p className="font-medium text-gray-900">
              {new Date(call.created_at).toLocaleString()}
            </p>
          </div>
        </div>

        {call.retell_call_id && (
          <div className="mt-4 pt-4 border-t">
            <p className="text-sm text-gray-500">Retell Call ID</p>
            <p className="font-mono text-xs text-gray-700">{call.retell_call_id}</p>
          </div>
        )}
      </div>

      {call.raw_transcript && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Transcript</h3>
          <div className="bg-gray-50 rounded p-4">
            <p className="text-gray-800 whitespace-pre-wrap">{call.raw_transcript}</p>
          </div>
        </div>
      )}

      {call.structured_data && (
        <div className="bg-white shadow rounded-lg p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Extracted Data</h3>
          <div className="space-y-3">
            {Object.entries(call.structured_data).map(([key, value]) => (
              <div key={key} className="flex">
                <span className="text-sm font-medium text-gray-500 w-1/3 capitalize">
                  {key.replace(/_/g, ' ')}:
                </span>
                <span className="text-sm text-gray-900 w-2/3">
                  {typeof value === 'boolean' ? (value ? 'Yes' : 'No') : value}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {!call.raw_transcript && call.call_status !== 'failed' && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-blue-800 text-sm">
            {call.call_status === 'completed' 
              ? 'Call completed. Transcript processing...'
              : 'Call in progress. Updates will appear automatically.'}
          </p>
        </div>
      )}
    </div>
  );
}
