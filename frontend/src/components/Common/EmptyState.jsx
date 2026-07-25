import React from 'react';
import { FolderOpen } from 'lucide-react';

export default function EmptyState({
  title = "No data found",
  description = "Get started by creating a new record.",
  actionLabel,
  onAction,
  icon: Icon = FolderOpen
}) {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center bg-white dark:bg-gray-800 rounded-xl border border-dashed border-gray-300 dark:border-gray-700 my-4">
      <div className="p-4 bg-indigo-50 dark:bg-indigo-950/40 rounded-full text-indigo-600 dark:text-indigo-400 mb-4">
        <Icon className="w-8 h-8" />
      </div>
      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-1">{title}</h3>
      <p className="text-sm text-gray-500 dark:text-gray-400 max-w-sm mb-6">{description}</p>
      {actionLabel && onAction && (
        <button
          onClick={onAction}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-sm rounded-lg shadow transition-colors"
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
}
