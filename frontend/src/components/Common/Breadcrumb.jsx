import React from 'react';
import { Link } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';

export default function Breadcrumb({ items = [] }) {
  return (
    <nav className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400 mb-4">
      <Link to="/dashboard" className="flex items-center hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
        <Home className="w-4 h-4 mr-1" />
        <span>Dashboard</span>
      </Link>
      {items.map((item, index) => (
        <React.Fragment key={index}>
          <ChevronRight className="w-4 h-4 text-gray-400" />
          {item.href ? (
            <Link to={item.href} className="hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors">
              {item.label}
            </Link>
          ) : (
            <span className="font-semibold text-gray-800 dark:text-gray-200">{item.label}</span>
          )}
        </React.Fragment>
      ))}
    </nav>
  );
}
