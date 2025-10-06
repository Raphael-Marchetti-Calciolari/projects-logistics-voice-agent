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
      <div className="bg-error-50 border border-error-200 rounded-lg p-6">
        <p className="text-error-700">{error}</p>
        <button
          onClick={loadCalls}
          className="mt-4 text-primary-600 hover:text-primary-700 hover:underline text-sm font-medium"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold text-neutral-900">Previous Calls</h2>
        <button
          onClick={loadCalls}
          className="text-primary-600 hover:text-primary-700 hover:underline text-sm font-medium"
        >
          Refresh
        </button>
      </div>

      {/* Search and Sort Controls */}
      <div className="bg-white shadow-sm rounded-lg border border-neutral-200 p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          {/* Search by Driver Name */}
          <div className="flex-1">
            <label htmlFor="search" className="block text-sm font-medium text-neutral-700 mb-1.5">
              Search by Driver Name
            </label>
            <input
              type="text"
              id="search"
              value={searchQuery}
              onChange={handleSearchChange}
              placeholder="Enter driver name..."
              className="w-full px-3 py-2 border border-neutral-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          {/* Sort by Time */}
          <div className="flex flex-col justify-end">
            <label className="block text-sm font-medium text-neutral-700 mb-1.5">
              Sort by Time
            </label>
            <button
              onClick={handleSortToggle}
              className="min-w-[160px] px-4 py-2 bg-neutral-100 text-neutral-700 rounded-md hover:bg-neutral-200 focus:outline-none focus:ring-2 focus:ring-primary-500 flex items-center justify-center text-sm font-medium transition-colors"
            >
              {sortOrder === 'desc' ? (
                <>
                  <span>Newest First</span>
                  <svg className="ml-2 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </>
              ) : (
                <>
                  <span>Oldest First</span>
                  <svg className="ml-2 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                  </svg>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Results Count */}
        <div className="mt-4 text-xs text-neutral-600">
          Showing {filteredCalls.length} of {calls.length} call{calls.length !== 1 ? 's' : ''}
        </div>
      </div>

      {/* Calls List */}
      {filteredCalls.length === 0 ? (
        <div className="bg-white shadow-sm rounded-lg border border-neutral-200 p-8 text-center">
          <p className="text-neutral-500 text-sm">
            {searchQuery ? 'No calls found matching your search.' : 'No previous calls found.'}
          </p>
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="mt-4 text-primary-600 hover:text-primary-700 hover:underline text-sm font-medium"
            >
              Clear Search
            </button>
          )}
        </div>
      ) : (
        <div className="bg-white shadow-sm rounded-lg border border-neutral-200 overflow-hidden">
          <table className="min-w-full divide-y divide-neutral-200">
            <thead className="bg-neutral-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-700 uppercase tracking-wider">
                  Driver Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-700 uppercase tracking-wider">
                  Load Number
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-700 uppercase tracking-wider">
                  Scenario
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-700 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-700 uppercase tracking-wider">
                  Time
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-neutral-700 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-neutral-200">
              {filteredCalls.map((call) => {
                const statusConfig = getStatusConfig(call.call_status, CALL_STATUS_CONFIG);
                return (
                  <tr key={call.id} className="hover:bg-neutral-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-neutral-900">
                      {call.driver_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-600">
                      {call.load_number}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-600 capitalize">
                      {call.scenario_type}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`status-badge ${statusConfig.className}`}>
                        {statusConfig.label}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-600">
                      {formatDate(call.created_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <Link
                        to={`/calls/${call.id}`}
                        className="text-primary-600 hover:text-primary-700 hover:underline font-medium"
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
      )}
    </div>
  );
}
