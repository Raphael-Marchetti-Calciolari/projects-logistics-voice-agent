import { Link, useLocation } from 'react-router-dom';
import { useState } from 'react';

export default function Layout({ children }) {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const isActive = (path) => {
    return location.pathname === path;
  };

  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen);
  };

  const closeMobileMenu = () => {
    setMobileMenuOpen(false);
  };

  return (
    <div className="min-h-screen bg-neutral-50">
      {/* Navigation */}
      <nav className="bg-white border-b border-neutral-200 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-14 sm:h-16">
            {/* Logo/Title */}
            <div className="flex items-center flex-shrink-0">
              <h1 className="text-base sm:text-lg font-semibold text-neutral-900 tracking-tight">
                Logistics Voice Agent
              </h1>
            </div>

            {/* Desktop Navigation Tabs */}
            <div className="hidden md:flex space-x-1">
              <Link
                to="/"
                className={`tab-link ${
                  isActive('/')
                    ? 'tab-link-active'
                    : 'tab-link-inactive'
                }`}
                aria-current={isActive('/') ? 'page' : undefined}
              >
                Configuration
              </Link>
              <Link
                to="/test"
                className={`tab-link ${
                  isActive('/test')
                    ? 'tab-link-active'
                    : 'tab-link-inactive'
                }`}
                aria-current={isActive('/test') ? 'page' : undefined}
              >
                Test Calls
              </Link>
              <Link
                to="/previous-calls"
                className={`tab-link ${
                  isActive('/previous-calls')
                    ? 'tab-link-active'
                    : 'tab-link-inactive'
                }`}
                aria-current={isActive('/previous-calls') ? 'page' : undefined}
              >
                Previous Calls
              </Link>
            </div>

            {/* Mobile menu button */}
            <button
              type="button"
              className="md:hidden inline-flex items-center justify-center p-2 rounded-md text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500 transition-colors"
              aria-expanded={mobileMenuOpen}
              aria-label="Toggle navigation menu"
              onClick={toggleMobileMenu}
            >
              <svg
                className="h-6 w-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                {mobileMenuOpen ? (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                ) : (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                )}
              </svg>
            </button>
          </div>

          {/* Mobile Navigation Menu */}
          {mobileMenuOpen && (
            <div className="md:hidden pb-3 pt-2 space-y-1 border-t border-neutral-200 mt-2">
              <Link
                to="/"
                onClick={closeMobileMenu}
                className={`block px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive('/')
                    ? 'bg-primary-600 text-white'
                    : 'text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900'
                }`}
                aria-current={isActive('/') ? 'page' : undefined}
              >
                Configuration
              </Link>
              <Link
                to="/test"
                onClick={closeMobileMenu}
                className={`block px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive('/test')
                    ? 'bg-primary-600 text-white'
                    : 'text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900'
                }`}
                aria-current={isActive('/test') ? 'page' : undefined}
              >
                Test Calls
              </Link>
              <Link
                to="/previous-calls"
                onClick={closeMobileMenu}
                className={`block px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive('/previous-calls')
                    ? 'bg-primary-600 text-white'
                    : 'text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900'
                }`}
                aria-current={isActive('/previous-calls') ? 'page' : undefined}
              >
                Previous Calls
              </Link>
            </div>
          )}
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-6 lg:py-8">
        {children}
      </main>
    </div>
  );
}
