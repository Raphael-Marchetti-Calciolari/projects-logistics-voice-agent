import { useEffect, useRef, useState } from 'react';
import { RetellWebClient } from 'retell-client-js-sdk';

export default function RetellWebCall({ accessToken, onCallEnd }) {
  const [isCallActive, setIsCallActive] = useState(false);
  const [callStatus, setCallStatus] = useState('Ready');
  const retellClientRef = useRef(null);

  useEffect(() => {
    // Initialize Retell client
    retellClientRef.current = new RetellWebClient();

    // Set up event listeners
    retellClientRef.current.on('call_started', () => {
      setCallStatus('Call started');
      setIsCallActive(true);
    });

    retellClientRef.current.on('call_ended', () => {
      setCallStatus('Call ended');
      setIsCallActive(false);
      if (onCallEnd) onCallEnd();
    });

    retellClientRef.current.on('agent_start_talking', () => {
      setCallStatus('Agent speaking...');
    });

    retellClientRef.current.on('agent_stop_talking', () => {
      setCallStatus('Your turn to speak');
    });

    retellClientRef.current.on('error', (error) => {
      console.error('Retell error:', error);
      setCallStatus(`Error: ${error.message}`);
    });

    return () => {
      if (retellClientRef.current) {
        retellClientRef.current.stopCall();
      }
    };
  }, [onCallEnd]);

  const startCall = async () => {
    try {
      await retellClientRef.current.startCall({
        accessToken: accessToken,
      });
    } catch (error) {
      console.error('Failed to start call:', error);
      setCallStatus(`Failed to start: ${error.message}`);
    }
  };

  const stopCall = async () => {
    try {
      await retellClientRef.current.stopCall();
    } catch (error) {
      console.error('Failed to stop call:', error);
    }
  };

  return (
    <div className="bg-white border-2 border-primary-200 rounded-lg p-6">
      <div className="text-center mb-4">
        <div className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-medium ${
          isCallActive 
            ? 'bg-success-100 text-success-700' 
            : 'bg-neutral-100 text-neutral-700'
        }`}>
          {isCallActive && (
            <span className="w-2 h-2 bg-success-500 rounded-full mr-2 animate-pulse"></span>
          )}
          {callStatus}
        </div>
      </div>

      {!isCallActive ? (
        <button
          onClick={startCall}
          className="w-full px-6 py-3 bg-success-600 text-white font-medium rounded-md hover:bg-success-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-success-500 transition-colors"
        >
          Start Web Call
        </button>
      ) : (
        <button
          onClick={stopCall}
          className="w-full px-6 py-3 bg-error-600 text-white font-medium rounded-md hover:bg-error-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-error-500 transition-colors"
        >
          End Call
        </button>
      )}

      <p className="text-xs text-neutral-500 mt-4 text-center">
        Make sure to allow microphone access in your browser
      </p>
    </div>
  );
}
