import React from 'react';
import { X } from 'lucide-react';

export default function AssignmentConfirmationModal({
  isOpen,
  issue,
  user,
  onConfirm,
  onCancel,
  isLoading,
}) {
  if (!isOpen || !issue || !user) return null;

  return (
    <>
      {/* Overlay */}
      <div className="fixed inset-0 bg-black bg-opacity-50 z-50" onClick={onCancel} />

      {/* Modal */}
      <div className="fixed inset-0 flex items-center justify-center z-50">
        <div className="bg-white dark:bg-gray-950 rounded-lg shadow-xl max-w-md w-full mx-4 border border-gray-200 dark:border-gray-800">
          {/* Header */}
          <div className="flex justify-between items-center p-6 border-b border-gray-200 dark:border-gray-800">
            <h2 className="text-lg font-bold text-gray-900 dark:text-white">
              Confirm Assignment
            </h2>
            <button
              onClick={onCancel}
              disabled={isLoading}
              className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 disabled:opacity-50"
            >
              <X size={20} />
            </button>
          </div>

          {/* Content */}
          <div className="p-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Issue
              </label>
              <p className="text-sm text-gray-900 dark:text-white bg-gray-50 dark:bg-gray-900 p-2 rounded border border-gray-200 dark:border-gray-800">
                {issue.title}
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Assigned To
              </label>
              <p className="text-sm text-gray-900 dark:text-white bg-gray-50 dark:bg-gray-900 p-2 rounded border border-gray-200 dark:border-gray-800">
                {user.name || user.id}
              </p>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3 p-6 border-t border-gray-200 dark:border-gray-800">
            <button
              onClick={onCancel}
              disabled={isLoading}
              className="flex-1 px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-800 disabled:opacity-50 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={() => onConfirm(issue._id, user.id)}
              disabled={isLoading}
              className="flex-1 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {isLoading ? 'Assigning...' : 'Confirm'}
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
