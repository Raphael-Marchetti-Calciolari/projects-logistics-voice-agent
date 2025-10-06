import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { callsAPI } from '../api/calls';
import { formatDate, getStatusConfig } from '../utils/formatters';
import { CALL_STATUS_CONFIG } from '../constants';

export default function PreviousCalls() {
  const [calls, setCalls] = useState([]);
  const [filteredCalls, setFilteredCalls] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortOrder, setSortOrder] = useState('desc'); // 'asc' or 'desc'
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadCalls = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const ascending = sortOrder === 'asc';
      const data = await callsAPI.listCalls('created_at', ascending);
      setCalls(data);
      setFilteredCalls(data);
    } catch (err) {
      console.error('Failed to load calls:', err);
      setError('Failed to load previous calls. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, [sortOrder]);

  useEffect(() => {
    loadCalls();
  }, [loadCalls]);

  // Filter calls by driver name when search query changes
  useEffect(() => {
    if (!searchQuery.trim()) {
      setFilteredCalls(calls);
    } else {
      const query = searchQuery.toLowerCase();
      const filtered = calls.filter(call =>
        call.driver_name.toLowerCase().includes(query)
      );
      setFilteredCalls(filtered);
    }
  }, [searchQuery, calls]);

  const handleSortToggle = () => {
    setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc');
  };

  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-neutral-500 text-sm">Loading previous calls...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="alert-error">
        <p className="text-sm">{error}</p>
        <button
          onClick={loadCalls}
          className="mt-3 text-error-700 hover:text-error-800 hover:underline text-sm font-medium touch-manipulation"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-4 sm:space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <h2 className="text-xl sm:text-2xl font-semibold text-neutral-900">Previous Calls</h2>
        <button
          onClick={loadCalls}
          className="text-primary-600 hover:text-primary-700 hover:underline text-sm font-medium self-start sm:self-auto touch-manipulation"
        >
          Refresh
        </button>
      </div>

      {/* Search and Sort Controls */}
      <div className="card">
        <div className="flex flex-col gap-3 sm:gap-4">
          {/* Search by Driver Name */}
          <div className="flex-1">
            <label htmlFor="search" className="form-label">
              Search by Driver Name
            </label>
            <input
              type="text"
              id="search"
              value={searchQuery}
              onChange={handleSearchChange}
              placeholder="Enter driver name..."
              className="form-input"
            />
          </div>

          {/* Sort and Results */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div className="text-xs sm:text-sm text-neutral-600">
              Showing {filteredCalls.length} of {calls.length} call{calls.length !== 1 ? 's' : ''}
            </div>
            
            <button
              onClick={handleSortToggle}
              className="btn-secondary w-full sm:w-auto sm:min-w-[160px] justify-center"
              aria-label={`Sort by time, currently ${sortOrder === 'desc' ? 'newest first' : 'oldest first'}`}
            >
              {sortOrder === 'desc' ? (
                <>
                  <span>Newest First</span>
                  <svg className="ml-2 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </>
              ) : (
                <>
                  <span>Oldest First</span>
                  <svg className="ml-2 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                  </svg>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Calls List */}
      {filteredCalls.length === 0 ? (
        <div className="card text-center py-8 sm:py-12">
          <p className="text-neutral-500 text-sm">
            {searchQuery ? 'No calls found matching your search.' : 'No previous calls found.'}
          </p>
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="mt-4 text-primary-600 hover:text-primary-700 hover:underline text-sm font-medium touch-manipulation"
            >
              Clear Search
            </button>
          )}
        </div>
      ) : (
        <>
          {/* Desktop Table View */}
          <div className="hidden md:block card p-0 overflow-hidden">
            <div className="table-wrapper">
              <table className="responsive-table">
                <thead>
                  <tr>
                    <th>Driver Name</th>
                    <th>Load Number</th>
                    <th>Scenario</th>
                    <th>Status</th>
                    <th>Time</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-neutral-200">
                  {filteredCalls.map((call) => {
                    const statusConfig = getStatusConfig(call.call_status, CALL_STATUS_CONFIG);
                    return (
                      <tr key={call.id} className="hover:bg-neutral-50 transition-colors">
                        <td className="font-medium text-neutral-900">
                          {call.driver_name}
                        </td>
                        <td className="text-neutral-600">
                          {call.load_number}
                        </td>
                        <td className="text-neutral-600 capitalize">
                          {call.scenario_type}
                        </td>
                        <td>
                          <span className={`status-badge ${statusConfig.className}`}>
                            {statusConfig.label}
                          </span>
                        </td>
                        <td className="text-neutral-600 whitespace-nowrap">
                          {formatDate(call.created_at)}
                        </td>
                        <td>
                          <Link
                            to={`/calls/${call.id}`}
                            className="text-primary-600 hover:text-primary-700 hover:underline font-medium text-sm"
                          >
                            View Details
                          </Link>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Mobile Card View */}
          <div className="md:hidden space-y-3">
            {filteredCalls.map((call) => {
              const statusConfig = getStatusConfig(call.call_status, CALL_STATUS_CONFIG);
              return (
                <div key={call.id} className="card">
                  <div className="flex justify-between items-start mb-3">
                    <div className="flex-1 min-w-0">
                      <h3 className="text-sm font-semibold text-neutral-900 truncate">
                        {call.driver_name}
                      </h3>
                      <p className="text-xs text-neutral-600 mt-0.5">
                        Load: {call.load_number}
                      </p>
                    </div>
                    <span className={`status-badge ${statusConfig.className} ml-2 flex-shrink-0`}>
                      {statusConfig.label}
                    </span>
                  </div>
                  
                  <div className="space-y-1.5 mb-3">
                    <div className="flex justify-between text-xs">
                      <span className="text-neutral-500">Scenario:</span>
                      <span className="text-neutral-700 capitalize font-medium">{call.scenario_type}</span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-neutral-500">Time:</span>
                      <span className="text-neutral-700">{formatDate(call.created_at)}</span>
                    </div>
                  </div>

                  <Link
                    to={`/calls/${call.id}`}
                    className="block w-full text-center px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 text-sm font-medium transition-colors touch-manipulation"
                  >
                    View Details
                  </Link>
                </div>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}
