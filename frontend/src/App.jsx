import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ErrorBoundary from './components/ErrorBoundary';
import Layout from './components/Layout';
import Configuration from './pages/Configuration';
import TestCalls from './pages/TestCalls';
import CallResults from './pages/CallResults';
import PreviousCalls from './pages/PreviousCalls';

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Configuration />} />
            <Route path="/test" element={<TestCalls />} />
            <Route path="/previous-calls" element={<PreviousCalls />} />
            <Route path="/calls/:id" element={<CallResults />} />
          </Routes>
        </Layout>
      </Router>
    </ErrorBoundary>
  );
}

export default App;
