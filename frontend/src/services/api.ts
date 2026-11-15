import axios, { AxiosError } from 'axios';
import type { SystemHealth, DatabaseHealth, ApiErrorEnvelope } from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

// Interceptor to extract backend error envelopes
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiErrorEnvelope>) => {
    if (error.response?.data?.error) {
      const err = error.response.data.error;
      const customError = new Error(err.message || 'Server error occurred');
      (customError as Error & { code?: string; details?: unknown }).code = err.code;
      (customError as Error & { code?: string; details?: unknown }).details = err.details;
      return Promise.reject(customError);
    }
    return Promise.reject(error);
  }
);

export const fetchHealth = async (): Promise<SystemHealth> => {
  const response = await apiClient.get<SystemHealth>('/v1/health');
  return response.data;
};

export const fetchDatabaseHealth = async (): Promise<DatabaseHealth> => {
  const response = await apiClient.get<DatabaseHealth>('/v1/health/db');
  return response.data;
};

export const fetchVersion = async (): Promise<{ version: string; project_name: string }> => {
  const response = await apiClient.get<{ version: string; project_name: string }>('/version');
  return response.data;
};
