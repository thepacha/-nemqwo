import React, { useState, useEffect } from 'react';
import { transcriptionService, APIKey } from '../services/transcriptionService';

const APIKeys: React.FC = () => {
  const [apiKeys, setApiKeys] = useState<APIKey[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [error, setError] = useState('');
  const [newlyCreatedKey, setNewlyCreatedKey] = useState<string>('');

  useEffect(() => {
    fetchAPIKeys();
  }, []);

  const fetchAPIKeys = async () => {
    try {
      const keys = await transcriptionService.getAPIKeys();
      setApiKeys(keys);
    } catch (error) {
      console.error('Failed to fetch API keys:', error);
      setError('Failed to load API keys');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateKey = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newKeyName.trim()) {
      setError('Please enter a name for the API key');
      return;
    }

    setCreating(true);
    setError('');

    try {
      const newKey = await transcriptionService.createAPIKey(newKeyName.trim());
      setApiKeys([...apiKeys, newKey]);
      setNewlyCreatedKey(newKey.key);
      setNewKeyName('');
      setShowCreateForm(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create API key');
    } finally {
      setCreating(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-8"></div>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="bg-white p-6 rounded-lg shadow">
                <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-3/4"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">API Keys</h1>
        <p className="text-gray-600 mt-2">
          Manage your API keys to integrate transcription services into your applications.
        </p>
      </div>

      {/* Newly Created Key Alert */}
      {newlyCreatedKey && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
          <div className="flex items-start">
            <svg className="w-5 h-5 text-green-500 mt-0.5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div className="flex-1">
              <h3 className="text-sm font-medium text-green-800 mb-2">
                API Key Created Successfully!
              </h3>
              <p className="text-sm text-green-700 mb-3">
                Make sure to copy your API key now. You won't be able to see it again!
              </p>
              <div className="bg-white border border-green-300 rounded p-3 font-mono text-sm break-all">
                {newlyCreatedKey}
              </div>
              <div className="mt-3 flex space-x-2">
                <button
                  onClick={() => copyToClipboard(newlyCreatedKey)}
                  className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm"
                >
                  Copy Key
                </button>
                <button
                  onClick={() => setNewlyCreatedKey('')}
                  className="bg-gray-200 hover:bg-gray-300 text-gray-700 px-3 py-1 rounded text-sm"
                >
                  Dismiss
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Create New Key */}
      <div className="bg-white rounded-lg shadow mb-6">
        <div className="p-6">
          {!showCreateForm ? (
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-medium text-gray-900">Create New API Key</h2>
                <p className="text-sm text-gray-600 mt-1">
                  Generate a new API key for your applications
                </p>
              </div>
              <button
                onClick={() => setShowCreateForm(true)}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium"
              >
                Create API Key
              </button>
            </div>
          ) : (
            <form onSubmit={handleCreateKey}>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-medium text-gray-900">Create New API Key</h2>
                <button
                  type="button"
                  onClick={() => {
                    setShowCreateForm(false);
                    setNewKeyName('');
                    setError('');
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                  {error}
                </div>
              )}

              <div className="mb-4">
                <label htmlFor="keyName" className="block text-sm font-medium text-gray-700 mb-2">
                  API Key Name
                </label>
                <input
                  type="text"
                  id="keyName"
                  value={newKeyName}
                  onChange={(e) => setNewKeyName(e.target.value)}
                  className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  placeholder="e.g., Production App, Development, Mobile App"
                  required
                />
                <p className="text-xs text-gray-500 mt-1">
                  Choose a descriptive name to help you identify this key later
                </p>
              </div>

              <div className="flex space-x-3">
                <button
                  type="submit"
                  disabled={creating}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium disabled:opacity-50"
                >
                  {creating ? 'Creating...' : 'Create Key'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowCreateForm(false);
                    setNewKeyName('');
                    setError('');
                  }}
                  className="bg-gray-200 hover:bg-gray-300 text-gray-700 px-4 py-2 rounded-lg font-medium"
                >
                  Cancel
                </button>
              </div>
            </form>
          )}
        </div>
      </div>

      {/* API Keys List */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Your API Keys</h2>
          
          {apiKeys.length === 0 ? (
            <div className="text-center py-8">
              <svg className="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
              </svg>
              <p className="text-gray-600 mb-4">No API keys created yet</p>
              <button
                onClick={() => setShowCreateForm(true)}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium"
              >
                Create Your First API Key
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {apiKeys.map((key) => (
                <div key={key.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h3 className="text-sm font-medium text-gray-900">{key.name}</h3>
                      <div className="mt-1 flex items-center space-x-4">
                        <code className="text-xs bg-gray-100 px-2 py-1 rounded font-mono">
                          {key.key}
                        </code>
                        <span className="text-xs text-gray-500">
                          Created {formatDate(key.created_at)}
                        </span>
                      </div>
                    </div>
                    <div className="flex space-x-2 ml-4">
                      <button
                        onClick={() => copyToClipboard(key.key)}
                        className="p-2 text-gray-400 hover:text-gray-600"
                        title="Copy API key"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                        </svg>
                      </button>
                      <button
                        className="p-2 text-red-400 hover:text-red-600"
                        title="Delete API key"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* API Documentation */}
      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-3">API Usage</h3>
        <div className="space-y-4 text-blue-800">
          <div>
            <h4 className="font-medium mb-2">Authentication</h4>
            <p className="text-sm mb-2">Include your API key in the Authorization header:</p>
            <code className="block bg-blue-100 p-2 rounded text-xs font-mono">
              Authorization: Bearer YOUR_API_KEY
            </code>
          </div>
          
          <div>
            <h4 className="font-medium mb-2">Transcribe Audio</h4>
            <p className="text-sm mb-2">POST request to transcribe audio files:</p>
            <code className="block bg-blue-100 p-2 rounded text-xs font-mono">
              POST /transcribe<br/>
              Content-Type: multipart/form-data<br/>
              Body: file (audio file)
            </code>
          </div>

          <div>
            <h4 className="font-medium mb-2">Rate Limits</h4>
            <ul className="text-sm space-y-1">
              <li>• 100 requests per hour for free tier</li>
              <li>• 1000 requests per hour for paid plans</li>
              <li>• Maximum file size: 25MB</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default APIKeys;