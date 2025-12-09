import React from 'react';
import { X } from 'lucide-react';

export default function CompletedIssuesSidebar({ issues, isOpen, onClose }) {
  const completedIssues = issues.filter(i => i.status === 'completed');

  return (
    <>
      {/* Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <div
        className={`fixed right-0 top-0 h-screen w-80 bg-white dark:bg-gray-950 border-l border-gray-200 dark:border-gray-800 transform transition-transform duration-300 z-50 ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">
              Completed Issues
            </h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
            >
              <X size={20} />
            </button>
          </div>

          <div className="space-y-3 max-h-[calc(100vh-120px)] overflow-y-auto">
            {completedIssues.length === 0 ? (
              <p className="text-sm text-gray-600 dark:text-gray-400">No completed issues</p>
            ) : (
              completedIssues.map(issue => (
                <div
                  key={issue._id}
                  className="p-3 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800"
                >
                  <h4 className="font-medium text-sm text-gray-900 dark:text-white mb-1">
                    {issue.title}
                  </h4>
                  <p className="text-xs text-gray-600 dark:text-gray-400">
                    {issue.description}
                  </p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </>
  );
}
