import React, { useState } from 'react';
import { Copy, Check, ShieldAlert, X } from 'lucide-react';

export default function ApiKeyModal({ isOpen, rawApiKey, keyName, onClose }) {
  const [copied, setCopied] = useState(false);

  if (!isOpen || !rawApiKey) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(rawApiKey);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl max-w-lg w-full p-6 shadow-2xl border border-gray-200 dark:border-gray-700 relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center space-x-3 mb-4">
          <div className="p-3 bg-amber-100 dark:bg-amber-950/40 text-amber-600 dark:text-amber-400 rounded-full">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100">API Key Created</h3>
            <p className="text-xs text-amber-600 dark:text-amber-400 font-medium">Save this key now. It will NEVER be shown again!</p>
          </div>
        </div>

        <p className="text-sm text-gray-600 dark:text-gray-300 mb-2">
          Key Description: <strong className="text-gray-800 dark:text-gray-200">{keyName}</strong>
        </p>

        <div className="flex items-center space-x-2 bg-gray-900 text-amber-400 p-4 rounded-xl font-mono text-sm break-all my-4 shadow-inner">
          <span className="flex-1">{rawApiKey}</span>
          <button
            onClick={handleCopy}
            className="p-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg transition-colors flex items-center shrink-0"
            title="Copy to clipboard"
          >
            {copied ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
          </button>
        </div>

        <div className="flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-sm rounded-lg shadow transition-colors"
          >
            I have saved the key
          </button>
        </div>
      </div>
    </div>
  );
}
