import api from './authService';

export interface Transcription {
  id: number;
  filename: string;
  transcription_text: string;
  file_size: number;
  duration?: number;
  created_at: string;
}

export interface APIKey {
  id: number;
  name: string;
  key: string;
  created_at: string;
}

export const transcriptionService = {
  async transcribeAudio(file: File): Promise<Transcription> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/transcribe', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async getTranscriptions(skip = 0, limit = 100): Promise<Transcription[]> {
    const response = await api.get(`/transcriptions?skip=${skip}&limit=${limit}`);
    return response.data;
  },

  async createAPIKey(name: string): Promise<APIKey> {
    const response = await api.post('/api-keys', { name });
    return response.data;
  },

  async getAPIKeys(): Promise<APIKey[]> {
    const response = await api.get('/api-keys');
    return response.data;
  },
};