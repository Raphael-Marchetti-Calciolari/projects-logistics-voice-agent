import { useParams } from 'react-router-dom';

export default function CallResults() {
  const { id } = useParams();

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-4">
        Call Results
      </h2>
      <p className="text-gray-600">
        Viewing call: {id}
      </p>
    </div>
  );
}
