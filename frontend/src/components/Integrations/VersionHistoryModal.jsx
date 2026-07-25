import React from 'react';
import { History, RotateCcw, X, User, Calendar } from 'lucide-react';

export default function VersionHistoryModal({
  isOpen,
  integrationName,
  versions = [],
  currentVersion,
  onRollback,
  onClose,
  isLoading
}) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-end bg-black/50 backdrop-blur-sm">
      <div className="bg-white dark:bg-gray-800 w-full max-w-xl h-full shadow-2xl border-l border-gray-200 dark:border-gray-700 p-6 overflow-y-auto flex flex-col relative animate-in slide-in-from-right duration-200">
        <div className="flex items-center justify-between border-b border-gray-200 dark:border-gray-700 pb-4 mb-6">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 bg-indigo-100 dark:bg-indigo-950/40 text-indigo-600 dark:text-indigo-400 rounded-lg">
              <History className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100">Version History</h2>
              <p className="text-xs text-gray-500 dark:text-gray-400">{integrationName}</p>
            </div>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex-1 space-y-4">
          {versions.map((ver) => {
            const isCurrent = ver.version_number === currentVersion;
            return (
              <div
                key={ver.id || ver.version_number}
                className={`p-4 rounded-xl border transition-all ${
                  isCurrent
                    ? 'border-indigo-500 bg-indigo-50/50 dark:bg-indigo-950/20'
                    : 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800/50'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-bold px-2.5 py-0.5 rounded-full bg-indigo-100 dark:bg-indigo-900 text-indigo-700 dark:text-indigo-300">
                      v{ver.version_number}
                    </span>
                    {isCurrent && (
                      <span className="text-xs font-semibold px-2 py-0.5 rounded bg-green-100 text-green-700 dark:bg-green-950 dark:text-green-300">
                        Active Snapshot
                      </span>
                    )}
                  </div>
                  {!isCurrent && (
                    <button
                      onClick={() => onRollback(ver.version_number)}
                      disabled={isLoading}
                      className="px-3 py-1 bg-gray-100 dark:bg-gray-700 hover:bg-indigo-600 hover:text-white text-gray-700 dark:text-gray-300 font-medium text-xs rounded-lg transition-colors flex items-center space-x-1"
                    >
                      <RotateCcw className="w-3.5 h-3.5" />
                      <span>Rollback to v{ver.version_number}</span>
                    </button>
                  )}
                </div>

                <p className="text-sm text-gray-700 dark:text-gray-300 mb-3">{ver.change_notes || "Configuration update"}</p>

                <div className="flex items-center justify-between text-xs text-gray-400">
                  <span className="flex items-center">
                    <User className="w-3.5 h-3.5 mr-1" />
                    {ver.created_by || "System"}
                  </span>
                  <span className="flex items-center">
                    <Calendar className="w-3.5 h-3.5 mr-1" />
                    {ver.created_at ? new Date(ver.created_at).toLocaleString() : "N/A"}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
