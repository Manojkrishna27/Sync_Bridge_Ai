import React from 'react';

export function TableSkeleton({ rows = 5, cols = 5 }) {
  return (
    <div className="animate-pulse space-y-4">
      <div className="h-10 bg-gray-200 dark:bg-gray-700 rounded-lg w-full"></div>
      {Array.from({ length: rows }).map((_, r) => (
        <div key={r} className="flex space-x-4">
          {Array.from({ length: cols }).map((_, c) => (
            <div key={c} className="h-8 bg-gray-100 dark:bg-gray-800 rounded flex-1"></div>
          ))}
        </div>
      ))}
    </div>
  );
}

export function CardSkeleton({ count = 4 }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="animate-pulse bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700">
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mb-3"></div>
          <div className="h-8 bg-gray-300 dark:bg-gray-600 rounded w-3/4"></div>
        </div>
      ))}
    </div>
  );
}
