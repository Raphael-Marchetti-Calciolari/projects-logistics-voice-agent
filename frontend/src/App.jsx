import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Configuration from './pages/Configuration';
import TestCalls from './pages/TestCalls';
import CallResults from './pages/CallResults';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Configuration />} />
          <Route path="/test" element={<TestCalls />} />
          <Route path="/calls/:id" element={<CallResults />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
