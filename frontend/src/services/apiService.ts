const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

export interface QueryResponse {
  sql: string;
  results: {
    columns: string[];
    rows: any[];
    row_count: number;
  };
  cached: boolean;
  execution_time: number;
}

export interface DemoCategory {
  id: string;
  label: string;
  section: string;
}

export interface DemoQueryResult {
  title: string;
  question: string;
  sql: string;
  columns: string[];
  rows: string[][];
  row_count: number;
  error?: string;
}

export interface DemoCategoryResponse {
  category: string;
  label: string;
  section: string;
  queries: DemoQueryResult[];
}

export async function queryDatabase(question: string): Promise<QueryResponse> {
  const response = await fetch(`${API_BASE_URL}/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Query failed');
  }

  return response.json();
}

export async function getDemoCategories(): Promise<{ categories: DemoCategory[] }> {
  const response = await fetch(`${API_BASE_URL}/demo/categories`);

  if (!response.ok) {
    throw new Error('Failed to fetch demo categories');
  }

  return response.json();
}

export async function getDemoCategoryResults(categoryId: string): Promise<DemoCategoryResponse> {
  const response = await fetch(`${API_BASE_URL}/demo/${categoryId}`);

  if (!response.ok) {
    throw new Error(`Failed to fetch demo category: ${categoryId}`);
  }

  return response.json();
}

export async function getCacheStats(): Promise<{ cache_size: number; max_size: number }> {
  const response = await fetch(`${API_BASE_URL}/cache/stats`);

  if (!response.ok) {
    throw new Error('Failed to fetch cache stats');
  }

  return response.json();
}

export async function clearCache(): Promise<{ message: string }> {
  const response = await fetch(`${API_BASE_URL}/cache/clear`, {
    method: 'DELETE',
  });

  if (!response.ok) {
    throw new Error('Failed to clear cache');
  }

  return response.json();
}
