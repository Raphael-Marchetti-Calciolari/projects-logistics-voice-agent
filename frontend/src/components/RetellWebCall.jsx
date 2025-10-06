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
    <div className="bg-white border-2 border-primary-200 rounded-lg p-4 sm:p-6">
      <div className="text-center mb-4 sm:mb-6">
        <div className={`inline-flex items-center px-4 py-2 rounded-full text-xs sm:text-sm font-medium transition-colors ${
          isCallActive 
            ? 'bg-success-100 text-success-700' 
            : 'bg-neutral-100 text-neutral-700'
        }`}>
          {isCallActive && (
            <span className="w-2 h-2 bg-success-500 rounded-full mr-2 animate-pulse" aria-hidden="true"></span>
          )}
          <span>{callStatus}</span>
        </div>
      </div>

      {!isCallActive ? (
        <button
          onClick={startCall}
          className="w-full px-6 py-3 sm:py-3.5 bg-success-600 text-white font-medium rounded-md hover:bg-success-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-success-500 transition-colors touch-manipulation text-sm sm:text-base"
          aria-label="Start web call"
        >
          <span className="flex items-center justify-center">
            <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
              <path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z" />
            </svg>
            Start Web Call
          </span>
        </button>
      ) : (
        <button
          onClick={stopCall}
          className="w-full px-6 py-3 sm:py-3.5 bg-error-600 text-white font-medium rounded-md hover:bg-error-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-error-500 transition-colors touch-manipulation text-sm sm:text-base"
          aria-label="End call"
        >
          <span className="flex items-center justify-center">
            <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
              <path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z" />
            </svg>
            End Call
          </span>
        </button>
      )}

      <p className="text-xs text-neutral-500 mt-4 text-center leading-relaxed">
        Make sure to allow microphone access in your browser
      </p>
    </div>
  );
}
