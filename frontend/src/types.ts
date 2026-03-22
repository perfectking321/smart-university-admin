export interface Student {
  id: number;
  name: string;
  roll_number: string;
  department: string;
  gpa: number;
  attendance_percentage: number;
}

export interface Department {
  id: number;
  name: string;
  head: string;
}

export interface QueryResult {
  columns: string[];
  rows: any[];
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sql?: string;
  results?: QueryResult;
}
