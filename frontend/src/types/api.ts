/**
 * Generic API schemas, pagination, and error representations.
 */

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}

export interface ApiErrorEnvelope {
  error: {
    code: string;
    message: string;
    details?: unknown;
  };
}

export interface SystemHealth {
  status: string;
  version: string;
  project: string;
}

export interface DatabaseHealth {
  status: string;
  database: string;
  host: string;
  port: number | null;
  dialect?: string;
  error?: string;
}

