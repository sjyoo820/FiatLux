import React, { useState, useEffect } from 'react';
import { Item, GridCell, GRID_DIMENSIONS, formatGridPosition, parseGridPosition, CATEGORY_COLORS } from '@/types';
import { motion, AnimatePresence } from 'framer-motion';

interface InventoryGridProps {
  items: Item[];
  selectedItem?: Item | null;
  onCellClick?: (cell: GridCell) => void;
  highlightPositions?: string[];
  className?: string;
}

const InventoryGrid: React.FC<InventoryGridProps> = ({
  items,
  selectedItem,
  onCellClick,
  highlightPositions = [],
  className = ''
}) => {
  const [grid, setGrid] = useState<GridCell[][]>([]);

  // 그리드 초기화
  useEffect(() => {
    const newGrid: GridCell[][] = [];
    
    // 빈 그리드 생성
    for (let row = 0; row < GRID_DIMENSIONS.ROWS; row++) {
      const gridRow: GridCell[] = [];
      for (let col = 0; col < GRID_DIMENSIONS.COLS; col++) {
        const position = formatGridPosition(row, col);
        gridRow.push({
          position,
          isEmpty: true
        });
      }
      newGrid.push(gridRow);
    }

    // 물품으로 그리드 채우기
    items.forEach(item => {
      const positions = parseItemPosition(item.grid_position);
      positions.forEach(pos => {
        const { row, col } = parseGridPosition(pos);
        if (row >= 0 && row < GRID_DIMENSIONS.ROWS && col >= 0 && col < GRID_DIMENSIONS.COLS) {
          newGrid[row][col] = {
            position: pos,
            item,
            isEmpty: false,
            category: item.category
          };
        }
      });
    });

    setGrid(newGrid);
  }, [items]);

  // 물품 위치 파싱 (예: "A1-A3" -> ["A1", "A2", "A3"])
  const parseItemPosition = (gridPosition: string): string[] => {
    if (!gridPosition.includes('-')) {
      return [gridPosition];
    }

    const [start, end] = gridPosition.split('-');
    const startPos = parseGridPosition(start);
    const endPos = parseGridPosition(end);
    const positions: string[] = [];

    if (startPos.row === endPos.row) {
      // 같은 행에서 연속
      for (let col = startPos.col; col <= endPos.col; col++) {
        positions.push(formatGridPosition(startPos.row, col));
      }
    } else if (startPos.col === endPos.col) {
      // 같은 열에서 연속
      for (let row = startPos.row; row <= endPos.row; row++) {
        positions.push(formatGridPosition(row, startPos.col));
      }
    } else {
      // 복잡한 경우는 시작과 끝만
      positions.push(start, end);
    }

    return positions;
  };

  // 셀 클릭 핸들러
  const handleCellClick = (cell: GridCell) => {
    if (onCellClick) {
      onCellClick(cell);
    }
  };

  // 셀 스타일 결정
  const getCellClassName = (cell: GridCell): string => {
    const baseClasses = 'grid-cell relative';
    
    if (cell.isEmpty) {
      return `${baseClasses} grid-cell-empty`;
    }

    const categoryColor = CATEGORY_COLORS[cell.category || '기타'] || 'miscellaneous';
    let cellClasses = `${baseClasses} grid-cell-${categoryColor}`;

    // 선택된 물품 강조
    if (selectedItem && cell.item?.id === selectedItem.id) {
      cellClasses += ' ring-4 ring-yellow-400 ring-opacity-75';
    }

    // 하이라이트된 위치
    if (highlightPositions.includes(cell.position)) {
      cellClasses += ' animate-pulse-slow ring-2 ring-red-400';
    }

    return cellClasses;
  };

  // 행 레이블 (A, B, C, D, E)
  const rowLabels = Array.from({ length: GRID_DIMENSIONS.ROWS }, (_, i) => 
    String.fromCharCode(65 + i)
  );

  // 열 레이블 (1, 2, 3, ..., 8)
  const colLabels = Array.from({ length: GRID_DIMENSIONS.COLS }, (_, i) => i + 1);

  return (
    <div className={`inventory-grid ${className}`}>
      {/* 제목 */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">물품 배치 현황</h2>
        <p className="text-gray-600">5x8 그리드에서 물품의 실시간 위치를 확인하세요</p>
      </div>

      {/* 범례 */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
        <h3 className="text-sm font-medium text-gray-700 mb-3">카테고리 범례</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          {Object.entries(CATEGORY_COLORS).map(([category, color]) => (
            <div key={category} className="flex items-center space-x-2">
              <div className={`w-4 h-4 rounded grid-cell-${color}`}></div>
              <span className="text-sm text-gray-600">{category}</span>
            </div>
          ))}
        </div>
      </div>

      {/* 그리드 컨테이너 */}
      <div className="grid-container bg-white rounded-xl shadow-lg p-6 overflow-x-auto">
        <div className="min-w-max">
          {/* 열 헤더 */}
          <div className="flex mb-2">
            <div className="w-8 h-8"></div> {/* 빈 공간 */}
            {colLabels.map(col => (
              <div key={col} className="w-16 h-8 flex items-center justify-center text-sm font-medium text-gray-500">
                {col}
              </div>
            ))}
          </div>

          {/* 그리드 행 */}
          {grid.map((row, rowIndex) => (
            <div key={rowIndex} className="flex mb-1">
              {/* 행 헤더 */}
              <div className="w-8 h-16 flex items-center justify-center text-sm font-medium text-gray-500">
                {rowLabels[rowIndex]}
              </div>

              {/* 그리드 셀 */}
              {row.map((cell, colIndex) => (
                <motion.div
                  key={`${rowIndex}-${colIndex}`}
                  className={getCellClassName(cell)}
                  onClick={() => handleCellClick(cell)}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  layout
                >
                  <AnimatePresence>
                    {!cell.isEmpty && cell.item && (
                      <motion.div
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.8 }}
                        className="text-center"
                      >
                        <div className="truncate text-xs font-medium">
                          {cell.item.name.length > 8 
                            ? `${cell.item.name.substring(0, 6)}..` 
                            : cell.item.name
                          }
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>

                  {/* 위치 표시 */}
                  <div className="absolute top-0 left-0 text-xs opacity-50 p-1">
                    {cell.position}
                  </div>

                  {/* 하이라이트 효과 */}
                  {highlightPositions.includes(cell.position) && (
                    <motion.div
                      className="absolute inset-0 bg-red-400 opacity-30 rounded-lg"
                      animate={{
                        opacity: [0.3, 0.6, 0.3],
                      }}
                      transition={{
                        duration: 1.5,
                        repeat: Infinity,
                        ease: "easeInOut"
                      }}
                    />
                  )}
                </motion.div>
              ))}
            </div>
          ))}
        </div>
      </div>

      {/* 통계 정보 */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg p-4 shadow-sm border">
          <div className="text-2xl font-bold text-gray-900">{items.length}</div>
          <div className="text-sm text-gray-500">총 물품 수</div>
        </div>
        <div className="bg-white rounded-lg p-4 shadow-sm border">
          <div className="text-2xl font-bold text-gray-900">
            {items.length}/{GRID_DIMENSIONS.TOTAL}
          </div>
          <div className="text-sm text-gray-500">그리드 사용률</div>
        </div>
        <div className="bg-white rounded-lg p-4 shadow-sm border">
          <div className="text-2xl font-bold text-gray-900">
            {new Set(items.map(item => item.category)).size}
          </div>
          <div className="text-sm text-gray-500">카테고리 수</div>
        </div>
        <div className="bg-white rounded-lg p-4 shadow-sm border">
          <div className="text-2xl font-bold text-gray-900">
            {GRID_DIMENSIONS.TOTAL - items.length}
          </div>
          <div className="text-sm text-gray-500">빈 공간</div>
        </div>
      </div>
    </div>
  );
};

export default InventoryGrid;
