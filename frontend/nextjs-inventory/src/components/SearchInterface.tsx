import React, { useState, useEffect } from 'react';
import { Item, Category } from '@/types';
import { MagnifyingGlassIcon, FunnelIcon, XMarkIcon } from '@heroicons/react/24/outline';

interface SearchInterfaceProps {
  items: Item[];
  categories: Category[];
  onSearchResults: (results: Item[]) => void;
  onItemSelect: (item: Item) => void;
  className?: string;
}

const SearchInterface: React.FC<SearchInterfaceProps> = ({
  items,
  categories,
  onSearchResults,
  onItemSelect,
  className = ''
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [searchResults, setSearchResults] = useState<Item[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showFilters, setShowFilters] = useState(false);

  // 검색 실행
  useEffect(() => {
    const performSearch = () => {
      setIsSearching(true);
      
      let results = items;

      // 카테고리 필터
      if (selectedCategory) {
        results = results.filter(item => item.category === selectedCategory);
      }

      // 텍스트 검색
      if (searchTerm.trim()) {
        const term = searchTerm.toLowerCase().trim();
        results = results.filter(item =>
          item.name.toLowerCase().includes(term) ||
          item.description?.toLowerCase().includes(term) ||
          item.grid_position.toLowerCase().includes(term)
        );
      }

      setSearchResults(results);
      onSearchResults(results);
      setIsSearching(false);
    };

    // 검색 디바운싱 (300ms)
    const debounceTimer = setTimeout(performSearch, 300);
    return () => clearTimeout(debounceTimer);
  }, [searchTerm, selectedCategory, items, onSearchResults]);

  // 검색 초기화
  const clearSearch = () => {
    setSearchTerm('');
    setSelectedCategory('');
    setSearchResults([]);
    onSearchResults(items);
  };

  // 하이라이트된 텍스트 렌더링
  const highlightText = (text: string, highlight: string) => {
    if (!highlight.trim()) return text;
    
    const regex = new RegExp(`(${highlight.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    const parts = text.split(regex);
    
    return parts.map((part, index) =>
      regex.test(part) ? (
        <span key={index} className="bg-yellow-200 text-yellow-800 px-1 rounded">
          {part}
        </span>
      ) : (
        part
      )
    );
  };

  return (
    <div className={`search-interface ${className}`}>
      {/* 검색 헤더 */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">물품 검색</h2>
        <p className="text-gray-600">이름, 설명, 위치로 물품을 빠르게 찾으세요</p>
      </div>

      {/* 검색 바 */}
      <div className="bg-white rounded-lg shadow-sm border p-4 mb-6">
        <div className="flex gap-4">
          {/* 검색 입력 */}
          <div className="flex-1 relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="물품 이름, 설명, 위치 검색..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* 필터 토글 버튼 */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`inline-flex items-center px-4 py-2 border rounded-md text-sm font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${
              showFilters || selectedCategory
                ? 'border-blue-300 text-blue-700 bg-blue-50'
                : 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50'
            }`}
          >
            <FunnelIcon className="h-4 w-4 mr-2" />
            필터
          </button>

          {/* 초기화 버튼 */}
          {(searchTerm || selectedCategory) && (
            <button
              onClick={clearSearch}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <XMarkIcon className="h-4 w-4 mr-2" />
              초기화
            </button>
          )}
        </div>

        {/* 필터 옵션 */}
        {showFilters && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* 카테고리 선택 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  카테고리
                </label>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="block w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">모든 카테고리</option>
                  {categories.map((category) => (
                    <option key={category.id} value={category.name}>
                      {category.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 검색 결과 */}
      <div className="bg-white rounded-lg shadow-sm border">
        {/* 결과 헤더 */}
        <div className="px-4 py-3 border-b border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900">
              검색 결과
              {isSearching ? (
                <span className="ml-2 text-sm text-blue-500">검색 중...</span>
              ) : (
                <span className="ml-2 text-sm text-gray-500">
                  ({searchResults.length}개 항목)
                </span>
              )}
            </h3>
          </div>
        </div>

        {/* 결과 목록 */}
        <div className="max-h-96 overflow-y-auto">
          {searchResults.length === 0 ? (
            <div className="px-4 py-8 text-center">
              {searchTerm || selectedCategory ? (
                <div>
                  <MagnifyingGlassIcon className="mx-auto h-12 w-12 text-gray-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900">검색 결과 없음</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    다른 검색어를 시도해보세요
                  </p>
                </div>
              ) : (
                <div>
                  <h3 className="text-sm font-medium text-gray-900">모든 물품</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    검색어를 입력하여 물품을 찾아보세요
                  </p>
                </div>
              )}
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {searchResults.map((item) => (
                <div
                  key={item.id}
                  onClick={() => onItemSelect(item)}
                  className="px-4 py-4 hover:bg-gray-50 cursor-pointer transition-colors duration-150"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <h4 className="text-sm font-medium text-gray-900 truncate">
                        {searchTerm 
                          ? highlightText(item.name, searchTerm)
                          : item.name
                        }
                      </h4>
                      <p className="text-sm text-gray-500 mt-1">
                        {item.description && searchTerm
                          ? highlightText(item.description, searchTerm)
                          : item.description || '설명 없음'
                        }
                      </p>
                      <div className="flex items-center mt-2 space-x-4">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          {item.category}
                        </span>
                        <span className="text-xs text-gray-500">
                          위치: {searchTerm 
                            ? highlightText(item.grid_position, searchTerm)
                            : item.grid_position
                          }
                        </span>
                      </div>
                    </div>
                    <div className="ml-4 flex-shrink-0">
                      <div className="w-2 h-2 rounded-full bg-green-400"></div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* 검색 팁 */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h4 className="text-sm font-medium text-blue-900 mb-2">검색 팁</h4>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>• 물품 이름의 일부만 입력해도 검색됩니다</li>
          <li>• 위치 코드(예: A1, B3)로도 검색할 수 있습니다</li>
          <li>• 카테고리 필터를 사용하여 검색 범위를 좁혀보세요</li>
        </ul>
      </div>
    </div>
  );
};

export default SearchInterface;
