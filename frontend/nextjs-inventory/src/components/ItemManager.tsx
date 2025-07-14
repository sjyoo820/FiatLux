import React, { useState } from 'react';
import { Item, Category } from '@/types';
import { PlusIcon, PencilIcon, TrashIcon, CheckIcon, XMarkIcon } from '@heroicons/react/24/outline';

interface ItemManagerProps {
  items: Item[];
  categories: Category[];
  onItemAdd: (item: Omit<Item, 'id'>) => Promise<void>;
  onItemUpdate: (id: number, item: Partial<Item>) => Promise<void>;
  onItemDelete: (id: number) => Promise<void>;
  className?: string;
}

interface ItemFormData {
  name: string;
  description: string;
  category: string;
  grid_position: string;
}

const ItemManager: React.FC<ItemManagerProps> = ({
  items,
  categories,
  onItemAdd,
  onItemUpdate,
  onItemDelete,
  className = ''
}) => {
  const [isAddingItem, setIsAddingItem] = useState(false);
  const [editingItem, setEditingItem] = useState<Item | null>(null);
  const [formData, setFormData] = useState<ItemFormData>({
    name: '',
    description: '',
    category: '',
    grid_position: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 폼 초기화
  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      category: '',
      grid_position: ''
    });
    setError(null);
  };

  // 추가 모드 시작
  const startAddingItem = () => {
    resetForm();
    setIsAddingItem(true);
    setEditingItem(null);
  };

  // 편집 모드 시작
  const startEditingItem = (item: Item) => {
    setFormData({
      name: item.name,
      description: item.description || '',
      category: item.category,
      grid_position: item.grid_position
    });
    setEditingItem(item);
    setIsAddingItem(false);
    setError(null);
  };

  // 취소
  const cancelEditing = () => {
    setIsAddingItem(false);
    setEditingItem(null);
    resetForm();
  };

  // 유효성 검사
  const validateForm = (): boolean => {
    if (!formData.name.trim()) {
      setError('물품 이름을 입력해주세요.');
      return false;
    }
    if (!formData.category) {
      setError('카테고리를 선택해주세요.');
      return false;
    }
    if (!formData.grid_position.trim()) {
      setError('그리드 위치를 입력해주세요.');
      return false;
    }

    // 그리드 위치 형식 검증 (예: A1, A1-A3)
    const gridPattern = /^[A-E][1-8](-[A-E][1-8])?$/;
    if (!gridPattern.test(formData.grid_position.trim())) {
      setError('올바른 그리드 위치 형식을 입력해주세요. (예: A1, A1-A3)');
      return false;
    }

    return true;
  };

  // 물품 저장
  const saveItem = async () => {
    if (!validateForm()) return;

    setLoading(true);
    setError(null);

    try {
      if (editingItem) {
        // 편집 모드
        await onItemUpdate(editingItem.id, {
          name: formData.name.trim(),
          description: formData.description.trim() || null,
          category: formData.category,
          grid_position: formData.grid_position.trim()
        });
      } else {
        // 추가 모드
        await onItemAdd({
          name: formData.name.trim(),
          description: formData.description.trim() || null,
          category: formData.category,
          grid_position: formData.grid_position.trim()
        });
      }
      
      cancelEditing();
    } catch (err) {
      setError(err instanceof Error ? err.message : '오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 물품 삭제
  const deleteItem = async (item: Item) => {
    if (!confirm(`"${item.name}"을(를) 정말 삭제하시겠습니까?`)) {
      return;
    }

    setLoading(true);
    try {
      await onItemDelete(item.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : '삭제 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`item-manager ${className}`}>
      {/* 헤더 */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">물품 관리</h2>
          <p className="text-gray-600">물품을 추가, 수정, 삭제할 수 있습니다</p>
        </div>
        <button
          onClick={startAddingItem}
          disabled={isAddingItem || editingItem !== null}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <PlusIcon className="h-4 w-4 mr-2" />
          새 물품 추가
        </button>
      </div>

      {/* 에러 메시지 */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {/* 물품 추가/편집 폼 */}
      {(isAddingItem || editingItem) && (
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            {editingItem ? '물품 수정' : '새 물품 추가'}
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* 물품 이름 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                물품 이름 *
              </label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="물품 이름을 입력하세요"
                className="block w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* 카테고리 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                카테고리 *
              </label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="block w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">카테고리 선택</option>
                {categories.map((category) => (
                  <option key={category.id} value={category.name}>
                    {category.name}
                  </option>
                ))}
              </select>
            </div>

            {/* 그리드 위치 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                그리드 위치 *
              </label>
              <input
                type="text"
                value={formData.grid_position}
                onChange={(e) => setFormData({ ...formData, grid_position: e.target.value })}
                placeholder="예: A1, A1-A3"
                className="block w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* 설명 */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                설명
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="물품에 대한 설명을 입력하세요"
                rows={3}
                className="block w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          {/* 폼 버튼 */}
          <div className="flex justify-end space-x-3 mt-6">
            <button
              onClick={cancelEditing}
              disabled={loading}
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              <XMarkIcon className="h-4 w-4 mr-2" />
              취소
            </button>
            <button
              onClick={saveItem}
              disabled={loading}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  저장 중...
                </>
              ) : (
                <>
                  <CheckIcon className="h-4 w-4 mr-2" />
                  {editingItem ? '수정' : '추가'}
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* 물품 목록 */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="px-4 py-3 border-b border-gray-200 bg-gray-50">
          <h3 className="text-lg font-medium text-gray-900">
            등록된 물품 ({items.length}개)
          </h3>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  물품명
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  카테고리
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  위치
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  설명
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  작업
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {items.map((item) => (
                <tr key={item.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{item.name}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {item.category}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {item.grid_position}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
                    {item.description || '설명 없음'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="flex justify-end space-x-2">
                      <button
                        onClick={() => startEditingItem(item)}
                        disabled={loading || isAddingItem || editingItem !== null}
                        className="text-blue-600 hover:text-blue-900 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <PencilIcon className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => deleteItem(item)}
                        disabled={loading || isAddingItem || editingItem !== null}
                        className="text-red-600 hover:text-red-900 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <TrashIcon className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {items.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center">
                    <div className="text-gray-500">
                      <p className="text-sm">등록된 물품이 없습니다.</p>
                      <p className="text-xs mt-1">새 물품을 추가해보세요.</p>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default ItemManager;
