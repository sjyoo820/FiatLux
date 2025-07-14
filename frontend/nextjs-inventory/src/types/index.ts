export interface Item {
  id: number;
  name: string;
  description: string;
  grid_position: string;
  category: string;
  created_at?: string;
  updated_at?: string;
}

export interface GridPosition {
  row: number;
  col: number;
  position: string; // 예: "A1", "B3"
}

export interface GridCell {
  position: string;
  item?: Item;
  isEmpty: boolean;
  category?: string;
}

export interface SearchResult {
  items: Item[];
  total_count: number;
  query: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message: string;
  error?: string;
}

export interface LEDControlRequest {
  item_id: number;
  duration?: number;
  color?: string;
}

export type CategoryColor = 
  | 'electronics' 
  | 'office' 
  | 'books' 
  | 'furniture' 
  | 'tools' 
  | 'miscellaneous';

export const CATEGORY_COLORS: Record<string, CategoryColor> = {
  '전자기기': 'electronics',
  '문구류': 'office',
  '도서': 'books',
  '가구': 'furniture',
  '도구': 'tools',
  '기타': 'miscellaneous'
};

export const GRID_DIMENSIONS = {
  ROWS: 5,
  COLS: 8,
  TOTAL: 40
};

// 그리드 위치를 행/열로 변환
export const parseGridPosition = (position: string): GridPosition => {
  const row = position.charCodeAt(0) - 65; // A=0, B=1, etc.
  const col = parseInt(position.slice(1)) - 1; // 1=0, 2=1, etc.
  return { row, col, position };
};

// 행/열을 그리드 위치로 변환
export const formatGridPosition = (row: number, col: number): string => {
  const letter = String.fromCharCode(65 + row); // 0=A, 1=B, etc.
  const number = col + 1; // 0=1, 1=2, etc.
  return `${letter}${number}`;
};

export interface Category {
  id: number;
  name: string;
  description?: string;
}
