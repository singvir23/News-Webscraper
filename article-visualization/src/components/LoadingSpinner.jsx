// src/components/LoadingSpinner.jsx
import React from 'react';

function LoadingSpinner() {
  return (
    <div className="flex flex-col items-center">
      <div className="w-16 h-16 border-4 border-t-4 border-gray-300 border-t-gray-500 rounded-full animate-spin"></div>
      <span className="mt-4 text-lg">Loading data...</span>
    </div>
  );
}

export default LoadingSpinner;
