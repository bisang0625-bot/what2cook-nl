'use client'

import { useState, useMemo } from 'react'
import { useI18n } from './i18n/I18nProvider'

interface StoreFilterProps {
  products: Array<{ store?: string; supermarket?: string }>
  selectedStores: Set<string>
  onStoreToggle: (storeName: string) => void
  onSelectAll: () => void
  selectAll: boolean
}

export default function StoreFilter({
  products,
  selectedStores,
  onStoreToggle,
  onSelectAll,
  selectAll
}: StoreFilterProps) {
  const { t } = useI18n()

  // 사용 가능한 마트 목록 추출
  const availableStores = useMemo(() => {
    const storesSet = new Set<string>()
    products.forEach(product => {
      const storeName = product.store || product.supermarket
      if (storeName) {
        storesSet.add(storeName)
      }
    })
    return Array.from(storesSet).sort()
  }, [products])

  // 마트별 브랜드 색상
  const getStoreColors = (storeName: string) => {
    const colorMap: Record<string, { bg: string; text: string; border: string }> = {
      'Albert Heijn': { bg: 'bg-orange-100', text: 'text-orange-800', border: 'border-orange-300' },
      'Jumbo': { bg: 'bg-yellow-100', text: 'text-yellow-800', border: 'border-yellow-300' },
      'Lidl': { bg: 'bg-blue-100', text: 'text-blue-800', border: 'border-blue-300' },
      'Plus': { bg: 'bg-green-100', text: 'text-green-800', border: 'border-green-300' },
      'Hoogvliet': { bg: 'bg-red-100', text: 'text-red-800', border: 'border-red-300' },
      'Dirk': { bg: 'bg-purple-100', text: 'text-purple-800', border: 'border-purple-300' },
      'ALDI': { bg: 'bg-indigo-100', text: 'text-indigo-800', border: 'border-indigo-300' },
      'Aldi': { bg: 'bg-indigo-100', text: 'text-indigo-800', border: 'border-indigo-300' },
      'Coop': { bg: 'bg-amber-100', text: 'text-amber-800', border: 'border-amber-300' },
    }
    return colorMap[storeName] || { bg: 'bg-gray-100', text: 'text-gray-800', border: 'border-gray-300' }
  }

  const getStoreAbbr = (storeName: string) => {
    const abbrMap: Record<string, string> = {
      'Albert Heijn': 'AH', 'Jumbo': 'Jumbo', 'Lidl': 'Lidl', 'Plus': 'Plus',
      'Hoogvliet': 'Hoogvliet', 'Dirk': 'Dirk', 'ALDI': 'ALDI', 'Aldi': 'ALDI', 'Coop': 'Coop',
    }
    return abbrMap[storeName] || storeName.slice(0, 3).toUpperCase()
  }

  if (availableStores.length === 0) {
    return null
  }

  return (
    <div className="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-gray-700">{t('storeFilter.title')}</h3>
        <button
          onClick={onSelectAll}
          className={`text-xs px-3 py-1 rounded-full transition-colors ${
            selectAll
              ? 'bg-orange-500 text-white'
              : 'bg-white text-gray-600 border border-gray-300 hover:bg-gray-100'
          }`}
        >
          {t('storeFilter.all')}
        </button>
      </div>
      <div className="flex flex-wrap gap-2">
        {availableStores.map((storeName) => {
          const isSelected = selectAll || selectedStores.has(storeName)
          const colors = getStoreColors(storeName)
          const storeAbbr = getStoreAbbr(storeName)

          return (
            <button
              key={storeName}
              onClick={() => onStoreToggle(storeName)}
              className={`
                px-3 py-1.5 rounded-full text-xs font-medium transition-all
                ${isSelected
                  ? `${colors.bg} ${colors.text} ${colors.border} border-2`
                  : 'bg-white text-gray-600 border border-gray-300 hover:bg-gray-50'
                }
              `}
            >
              {storeAbbr}
            </button>
          )
        })}
      </div>
    </div>
  )
}
