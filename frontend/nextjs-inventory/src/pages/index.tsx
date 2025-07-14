import React, { useState, useEffect } from 'react';
import InventoryGrid from '@/components/InventoryGrid';
import SearchInterface from '@/components/SearchInterface';
import ItemManager from '@/components/ItemManager';
import { Item, Category } from '@/types';
import { InventoryAPI } from '@/lib/api';

// 간단한 아이콘 컴포넌트 (heroicons 대신 사용)
const MagnifyingGlassIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
  </svg>
);

const Cog6ToothIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
  </svg>
);

const ViewColumnsIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 4H5a2 2 0 00-2 2v12a2 2 0 002 2h4M9 4V2m0 2v12a2 2 0 002 2h4a2 2 0 002-2V6a2 2 0 00-2-2h-4V2m0 0V4a2 2 0 002 2h4a2 2 0 002-2V2" />
  </svg>
);

const ChatBubbleLeftRightIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m-7 8l4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
  </svg>
);

type ActiveTab = 'grid' | 'search' | 'manage';

const InventoryManagementPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<ActiveTab>('grid');
  const [items, setItems] = useState<Item[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedItem, setSelectedItem] = useState<Item | null>(null);
  const [searchResults, setSearchResults] = useState<Item[]>([]);
  const [highlightPositions, setHighlightPositions] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const api = new InventoryAPI('http://localhost:8001');

  // 데이터 로드
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [itemsData, categoriesData] = await Promise.all([
        api.getAllItems(),
        api.getCategories()
      ]);
      
      setItems(itemsData);
      setCategories(categoriesData);
      setSearchResults(itemsData);
    } catch (err) {
      setError('데이터를 불러오는 중 오류가 발생했습니다.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // 물품 추가
  const handleItemAdd = async (itemData: Omit<Item, 'id'>) => {
    try {
      await api.addItem(itemData);
      await loadData(); // 데이터 새로고침
    } catch (err) {
      throw new Error('물품 추가 중 오류가 발생했습니다.');
    }
  };

  // 물품 수정
  const handleItemUpdate = async (id: number, itemData: Partial<Item>) => {
    try {
      await api.updateItem(id, itemData);
      await loadData(); // 데이터 새로고침
    } catch (err) {
      throw new Error('물품 수정 중 오류가 발생했습니다.');
    }
  };

  // 물품 삭제
  const handleItemDelete = async (id: number) => {
    try {
      await api.deleteItem(id);
      await loadData(); // 데이터 새로고침
    } catch (err) {
      throw new Error('물품 삭제 중 오류가 발생했습니다.');
    }
  };

  // 물품 선택
  const handleItemSelect = (item: Item) => {
    setSelectedItem(item);
    
    // 위치 하이라이트
    const positions = parseItemPositions(item.grid_position);
    setHighlightPositions(positions);

    // LED 하이라이트 (실제 구현시 API 호출)
    highlightItemOnLED(item);
    
    // 그리드 탭으로 이동
    setActiveTab('grid');
  };

  // 물품 위치 파싱
  const parseItemPositions = (gridPosition: string): string[] => {
    if (!gridPosition.includes('-')) {
      return [gridPosition];
    }

    const [start, end] = gridPosition.split('-');
    // 간단한 구현 - 실제로는 더 복잡한 로직 필요
    return [start, end];
  };

  // LED 하이라이트 (실제 API 호출)
  const highlightItemOnLED = async (item: Item) => {
    try {
      await api.highlightPosition(item.grid_position);
    } catch (err) {
      console.warn('LED 하이라이트 실패:', err);
    }
  };

  // Streamlit 챗봇 열기
  const openChatbot = () => {
    window.open('http://localhost:8501', '_blank');
  };

  const tabs = [
    { id: 'grid' as ActiveTab, name: '그리드 뷰', icon: ViewColumnsIcon },
    { id: 'search' as ActiveTab, name: '검색', icon: MagnifyingGlassIcon },
    { id: 'manage' as ActiveTab, name: '물품 관리', icon: Cog6ToothIcon },
  ];

  if (loading && items.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">데이터를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 헤더 */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">
                스마트 물품 관리 시스템
              </h1>
              <span className="ml-3 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                실시간 연동
              </span>
            </div>
            
            {/* 챗봇 버튼 */}
            <button
              onClick={openChatbot}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              <ChatBubbleLeftRightIcon />
              <span className="ml-2">AI 챗봇</span>
            </button>
          </div>
        </div>
      </header>

      {/* 탭 네비게이션 */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon />
                  <span className="ml-2">{tab.name}</span>
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* 에러 메시지 */}
      {error && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <p className="text-sm text-red-700">{error}</p>
            <button
              onClick={() => setError(null)}
              className="mt-2 text-sm text-red-600 hover:text-red-500"
            >
              닫기
            </button>
          </div>
        </div>
      )}

      {/* 메인 콘텐츠 */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'grid' && (
          <InventoryGrid
            items={searchResults}
            selectedItem={selectedItem}
            highlightPositions={highlightPositions}
            onCellClick={(cell) => {
              if (cell.item) {
                handleItemSelect(cell.item);
              }
            }}
          />
        )}

        {activeTab === 'search' && (
          <SearchInterface
            items={items}
            categories={categories}
            onSearchResults={setSearchResults}
            onItemSelect={handleItemSelect}
          />
        )}

        {activeTab === 'manage' && (
          <ItemManager
            items={items}
            categories={categories}
            onItemAdd={handleItemAdd}
            onItemUpdate={handleItemUpdate}
            onItemDelete={handleItemDelete}
          />
        )}
      </main>

      {/* 선택된 물품 정보 */}
      {selectedItem && (
        <div className="fixed bottom-4 right-4 bg-white rounded-lg shadow-lg p-4 max-w-sm border">
          <div className="flex items-center justify-between mb-2">
            <h4 className="font-medium text-gray-900">선택된 물품</h4>
            <button
              onClick={() => {
                setSelectedItem(null);
                setHighlightPositions([]);
              }}
              className="text-gray-400 hover:text-gray-600"
            >
              ×
            </button>
          </div>
          <div className="text-sm text-gray-600">
            <p><strong>{selectedItem.name}</strong></p>
            <p>카테고리: {selectedItem.category}</p>
            <p>위치: {selectedItem.grid_position}</p>
            {selectedItem.description && (
              <p className="mt-1">{selectedItem.description}</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default InventoryManagementPage;
