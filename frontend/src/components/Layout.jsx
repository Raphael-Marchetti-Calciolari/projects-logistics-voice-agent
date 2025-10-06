import { Link, useLocation } from 'react-router-dom';

export default function Layout({ children }) {
  const location = useLocation();

  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <div className="min-h-screen bg-neutral-50">
      {/* Navigation */}
      <nav className="bg-white border-b border-neutral-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              {/* Logo/Title */}
              <div className="flex-shrink-0 flex items-center mr-8">
                <h1 className="text-lg font-semibold text-neutral-900 tracking-tight">
                  Logistics Voice Agent
                </h1>
              </div>

              {/* Navigation Tabs */}
              <div className="flex space-x-1">
                <Link
                  to="/"
                  className={`tab-link ${
                    isActive('/')
                      ? 'tab-link-active'
                      : 'tab-link-inactive'
                  }`}
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
                >
                  Previous Calls
                </Link>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  );
}
