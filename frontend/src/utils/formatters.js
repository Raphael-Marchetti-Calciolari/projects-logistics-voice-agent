/**
 * Utility functions for formatting data.
 */

/**
 * Format a date string to a localized string.
 * 
 * @param {string} dateString - ISO date string
 * @returns {string} Formatted date string
 */
export const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  
  try {
    return new Date(dateString).toLocaleString();
  } catch (error) {
    console.error('Error formatting date:', error);
    return dateString;
  }
};

/**
 * Format a field name by replacing underscores with spaces and capitalizing.
 * 
 * @param {string} fieldName - Field name to format
 * @returns {string} Formatted field name
 */
export const formatFieldName = (fieldName) => {
  if (!fieldName) return '';
  
  return fieldName
    .replace(/_/g, ' ')
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
};

/**
 * Format a boolean value to Yes/No string.
 * 
 * @param {boolean} value - Boolean value
 * @returns {string} 'Yes' or 'No'
 */
export const formatBoolean = (value) => {
  return value ? 'Yes' : 'No';
};

/**
 * Get status display configuration for a call status.
 * 
 * @param {string} status - Call status
 * @param {Object} statusConfig - Status configuration map
 * @returns {Object} Status configuration with label and className
 */
export const getStatusConfig = (status, statusConfig) => {
  return statusConfig[status] || {
    label: status,
    className: 'bg-gray-100 text-gray-800',
  };
};
