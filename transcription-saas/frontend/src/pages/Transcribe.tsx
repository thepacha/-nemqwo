import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { transcriptionService } from '../services/transcriptionService';

const Transcribe: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [transcription, setTranscription] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const selectedFile = acceptedFiles[0];
    if (selectedFile) {
      // Check if it's an audio file
      if (!selectedFile.type.startsWith('audio/')) {
        setError('Please select an audio file');
        return;
      }
      
      // Check file size (max 25MB)
      if (selectedFile.size > 25 * 1024 * 1024) {
        setError('File size must be less than 25MB');
        return;
      }

      setFile(selectedFile);
      setError('');
      setTranscription('');
      setSuccess(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'audio/*': ['.mp3', '.wav', '.m4a', '.flac', '.ogg', '.aac']
    },
    multiple: false
  });

  const handleTranscribe = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const result = await transcriptionService.transcribeAudio(file);
      setTranscription(result.transcription_text);
      setSuccess(true);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Transcription failed');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setTranscription('');
    setError('');
    setSuccess(false);
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(transcription);
  };

  const downloadTranscription = () => {
    const element = document.createElement('a');
    const file = new Blob([transcription], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = `transcription-${Date.now()}.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Audio Transcription</h1>
        <p className="text-gray-600 mt-2">Upload your audio file and get an accurate transcription in seconds.</p>
      </div>

      {/* File Upload Area */}
      <div className="bg-white rounded-lg shadow mb-8">
        <div className="p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Upload Audio File</h2>
          
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
              isDragActive
                ? 'border-blue-400 bg-blue-50'
                : file
                ? 'border-green-400 bg-green-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
          >
            <input {...getInputProps()} />
            
            {file ? (
              <div>
                <svg className="w-12 h-12 text-green-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-lg font-medium text-gray-900 mb-2">{file.name}</p>
                <p className="text-sm text-gray-600 mb-4">
                  Size: {formatFileSize(file.size)} • Type: {file.type}
                </p>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleReset();
                  }}
                  className="text-red-600 hover:text-red-800 text-sm font-medium"
                >
                  Remove file
                </button>
              </div>
            ) : (
              <div>
                <svg className="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <p className="text-lg font-medium text-gray-900 mb-2">
                  {isDragActive ? 'Drop your audio file here' : 'Drag & drop your audio file here'}
                </p>
                <p className="text-sm text-gray-600 mb-4">
                  or click to browse files
                </p>
                <p className="text-xs text-gray-500">
                  Supported formats: MP3, WAV, M4A, FLAC, OGG, AAC (Max 25MB)
                </p>
              </div>
            )}
          </div>

          {error && (
            <div className="mt-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {file && !loading && !success && (
            <div className="mt-6">
              <button
                onClick={handleTranscribe}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 px-6 rounded-lg font-semibold transition-colors"
              >
                Start Transcription
              </button>
            </div>
          )}

          {loading && (
            <div className="mt-6">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mr-3"></div>
                  <p className="text-blue-800 font-medium">Transcribing your audio file...</p>
                </div>
                <div className="mt-2">
                  <div className="bg-blue-200 rounded-full h-2">
                    <div className="bg-blue-600 h-2 rounded-full animate-pulse" style={{ width: '60%' }}></div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Transcription Result */}
      {transcription && (
        <div className="bg-white rounded-lg shadow">
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Transcription Result</h2>
              <div className="flex space-x-2">
                <button
                  onClick={copyToClipboard}
                  className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                >
                  Copy Text
                </button>
                <button
                  onClick={downloadTranscription}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                >
                  Download
                </button>
              </div>
            </div>
            
            <div className="bg-gray-50 rounded-lg p-4">
              <textarea
                value={transcription}
                onChange={(e) => setTranscription(e.target.value)}
                className="w-full h-64 p-4 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Your transcription will appear here..."
              />
            </div>

            <div className="mt-4 flex justify-between items-center">
              <p className="text-sm text-gray-600">
                Characters: {transcription.length} • Words: {transcription.split(' ').filter(word => word.length > 0).length}
              </p>
              <button
                onClick={handleReset}
                className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg font-medium transition-colors"
              >
                Transcribe Another File
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Tips */}
      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-3">Tips for Better Transcription</h3>
        <ul className="space-y-2 text-blue-800">
          <li className="flex items-start">
            <span className="text-blue-600 mr-2">•</span>
            Use high-quality audio recordings for best results
          </li>
          <li className="flex items-start">
            <span className="text-blue-600 mr-2">•</span>
            Minimize background noise and ensure clear speech
          </li>
          <li className="flex items-start">
            <span className="text-blue-600 mr-2">•</span>
            Supported file formats: MP3, WAV, M4A, FLAC, OGG, AAC
          </li>
          <li className="flex items-start">
            <span className="text-blue-600 mr-2">•</span>
            Maximum file size: 25MB per upload
          </li>
        </ul>
      </div>
    </div>
  );
};

export default Transcribe;