'use client'

import { useState, useMemo } from 'react'
import { ChevronRight, ShoppingBag } from 'lucide-react'
import Tabs from './Tabs'

interface SaleProduct {
  store?: string
  supermarket?: string
  product_name?: string
  name?: string
  price?: string | null
  price_info?: string | null
  discount?: string | null
  discount_info?: string | null
  valid_from?: string
  valid_until?: string
  start_date?: string
  end_date?: string
}

interface WeeklySalesData {
  products: SaleProduct[]
  week_type?: 'current' | 'next'
}

interface WeeklySalesListProps {
  currentSales?: WeeklySalesData
  nextSales?: WeeklySalesData
  onRecipeFilter?: (productName: string, store: string) => void
}

export default function WeeklySalesList({
  currentSales,
  nextSales,
  onRecipeFilter
}: WeeklySalesListProps) {
  const [activeTab, setActiveTab] = useState<'current' | 'next'>('current')

  // 제품을 주재료/부재료/과일로 분류
  const categorizeProducts = (products: SaleProduct[]) => {
    const fruitKeywords = [
      'druiven', 'druif', 'grape', 'appel', 'apple', 'aardbei', 'strawberry',
      'banaan', 'banana', 'sinaasappel', 'orange', 'mandarijn', 'mandarin',
      'blauwe bessen', 'blueberry', 'framboos', 'raspberry', 'citroen', 'lemon',
      'kiwi', 'peer', 'pear', 'mango', 'ananas', 'pineapple', 'perzik', 'peach',
      'kersen', 'cherry', 'pruim', 'plum', 'abrikoos', 'apricot', 'fruit'
    ]

    const mainKeywords = [
      'speklappen', 'kipfilet', 'kippendijen', 'rundvlees', 'varkensvlees',
      'gehakt', 'zalm', 'vis', 'fish', 'tofu', 'aardappelen', 'aardappel',
      'kool', 'cabbage', 'ui', 'uien', 'onion', 'wortel', 'wortelen',
      'carrot', 'paprika', 'pepper', 'tomaat', 'tomaten', 'tomato', 'champignon',
      'mushroom', 'broccoli', 'spinazie', 'spinach'
    ]

    const subKeywords = [
      'knoflook', 'garlic', 'gember', 'ginger', 'soja', 'soy', 'azijn', 'vinegar',
      'olijfolie', 'olive oil', 'zout', 'salt', 'peper', 'pepper', 'suiker', 'sugar',
      'melk', 'milk', 'kaas', 'cheese', 'boter', 'butter', 'ei', 'eieren', 'egg'
    ]

    const main: SaleProduct[] = []
    const sub: SaleProduct[] = []
    const fruits: SaleProduct[] = []

    products.forEach(product => {
      const name = (product.product_name || product.name || '').toLowerCase()
      
      // 과일 판단
      if (fruitKeywords.some(keyword => name.includes(keyword))) {
        fruits.push(product)
        return
      }

      // 주재료 판단
      if (mainKeywords.some(keyword => name.includes(keyword))) {
        main.push(product)
        return
      }

      // 부재료 판단
      if (subKeywords.some(keyword => name.includes(keyword))) {
        sub.push(product)
        return
      }

      // 판단 불가능한 경우 주재료로 분류
      main.push(product)
    })

    return { main, sub, fruits }
  }

  // 날짜 포맷팅
  const formatDate = (dateStr?: string) => {
    if (!dateStr) return ''
    try {
      const date = new Date(dateStr)
      const month = date.getMonth() + 1
      const day = date.getDate()
      return `${month}/${day}`
    } catch {
      return ''
    }
  }

  // 세일 기간 포맷팅
  const formatSalePeriod = (product: SaleProduct) => {
    const startDate = product.valid_from || product.start_date
    const endDate = product.valid_until || product.end_date
    
    const start = formatDate(startDate)
    const end = formatDate(endDate)
    
    if (start && end) {
      return `${start} ~ ${end}`
    }
    return ''
  }

  // 마트 색상 가져오기
  const getStoreColors = (storeName: string) => {
    const colorMap: Record<string, { bg: string; text: string; border: string }> = {
      'Albert Heijn': {
        bg: 'bg-orange-100',
        text: 'text-orange-800',
        border: 'border-orange-300',
      },
      'Jumbo': {
        bg: 'bg-yellow-100',
        text: 'text-yellow-800',
        border: 'border-yellow-300',
      },
      'Lidl': {
        bg: 'bg-blue-100',
        text: 'text-blue-800',
        border: 'border-blue-300',
      },
      'Plus': {
        bg: 'bg-green-100',
        text: 'text-green-800',
        border: 'border-green-300',
      },
      'Hoogvliet': {
        bg: 'bg-red-100',
        text: 'text-red-800',
        border: 'border-red-300',
      },
      'Dirk': {
        bg: 'bg-purple-100',
        text: 'text-purple-800',
        border: 'border-purple-300',
      },
      'ALDI': {
        bg: 'bg-indigo-100',
        text: 'text-indigo-800',
        border: 'border-indigo-300',
      },
      'Aldi': {
        bg: 'bg-indigo-100',
        text: 'text-indigo-800',
        border: 'border-indigo-300',
      },
      'Coop': {
        bg: 'bg-amber-100',
        text: 'text-amber-800',
        border: 'border-amber-300',
      },
    }

    return colorMap[storeName] || {
      bg: 'bg-gray-100',
      text: 'text-gray-800',
      border: 'border-gray-300',
    }
  }

  // 마트 약칭
  const getStoreAbbr = (storeName: string) => {
    const abbrMap: Record<string, string> = {
      'Albert Heijn': 'AH',
      'Jumbo': 'Jumbo',
      'Lidl': 'Lidl',
      'Plus': 'Plus',
      'Hoogvliet': 'Hoogvliet',
      'Dirk': 'Dirk',
      'ALDI': 'ALDI',
      'Aldi': 'ALDI',
      'Coop': 'Coop',
    }
    return abbrMap[storeName] || storeName.slice(0, 3).toUpperCase()
  }

  // 이번 주 데이터 분류
  const categorizedCurrent = useMemo(() => {
    if (!currentSales?.products) return { main: [], sub: [], fruits: [] }
    return categorizeProducts(currentSales.products)
  }, [currentSales])

  // 다음 주 데이터는 WeeklySalesListContent에서 분류

  const handleRecipeFilter = (product: SaleProduct) => {
    const store = product.store || product.supermarket || ''
    const productName = product.product_name || product.name || ''
    if (onRecipeFilter) {
      onRecipeFilter(productName, store)
    }
  }

  const renderProductCard = (product: SaleProduct, index: number) => {
    const storeName = product.store || product.supermarket || 'Unknown'
    const productName = product.product_name || product.name || 'Unknown'
    const price = product.price || product.price_info || ''
    const discount = product.discount || product.discount_info || ''
    const salePeriod = formatSalePeriod(product)
    const colors = getStoreColors(storeName)
    const storeAbbr = getStoreAbbr(storeName)

    return (
      <div
        key={`${storeName}-${productName}-${index}`}
        className="bg-white rounded-lg border border-gray-200 hover:shadow-md transition-shadow duration-200 p-4"
      >
        <div className="flex items-start justify-between mb-3">
          {/* 마트 배지 */}
          <div className={`${colors.bg} ${colors.text} ${colors.border} px-3 py-1 rounded-full text-xs font-bold border`}>
            {storeAbbr}
          </div>
          
          {/* 세일 기간 */}
          {salePeriod && (
            <span className="text-xs text-gray-500">{salePeriod}</span>
          )}
        </div>

        {/* 상품명 */}
        <h3 className="text-base font-semibold text-gray-900 mb-2 line-clamp-2">
          {productName}
        </h3>

        {/* 가격 및 할인 정보 */}
        <div className="flex items-center gap-2 mb-3">
          {price && (
            <span className="text-sm text-gray-600">{price}</span>
          )}
          {discount && (
            <span className="text-sm font-bold text-orange-600 bg-orange-50 px-2 py-1 rounded">
              {discount}
            </span>
          )}
        </div>

        {/* 레시피 연결 버튼 */}
        <button
          onClick={() => handleRecipeFilter(product)}
          className="w-full flex items-center justify-center gap-2 text-sm font-medium text-orange-600 hover:text-orange-700 hover:bg-orange-50 py-2 px-3 rounded-lg transition-colors duration-200 border border-orange-200"
        >
          <ShoppingBag size={16} />
          <span>이 재료로 추천하는 레시피 보기</span>
          <ChevronRight size={16} />
        </button>
      </div>
    )
  }

  const currentProducts = currentSales?.products || []
  const nextProducts = nextSales?.products || []
  const hasCurrentData = currentProducts.length > 0
  const hasNextData = nextProducts.length > 0

  return (
    <section className="w-full py-8 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* 헤더 */}
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            🛒 마트별 주간 세일 리스트
          </h2>
          <p className="text-sm text-gray-600">
            이번 주 장볼 거리를 미리 확인하고 추천 레시피를 확인하세요!
          </p>
        </div>

        {/* 탭 */}
        <Tabs
          tabs={[
            {
              id: 'current',
              label: `📅 이번 주 ${hasCurrentData ? `(${currentProducts.length})` : ''}`,
              content: (
                <div className="mt-6">
                  {!hasCurrentData ? (
                    <div className="text-center py-12 text-gray-500">
                      <p className="text-lg mb-2">이번 주 세일 정보가 없습니다</p>
                      <p className="text-sm">다음 주 세일을 확인해보세요!</p>
                    </div>
                  ) : (
                    <div className="space-y-8">
                      {/* 주재료 섹션 */}
                      {categorizedCurrent.main.length > 0 && (
                        <div>
                          <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                            <ShoppingBag size={20} />
                            주재료 (고기, 생선, 주요 채소)
                          </h3>
                          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {categorizedCurrent.main.map((product, index) => renderProductCard(product, index))}
                          </div>
                        </div>
                      )}

                      {/* 부재료/양념 섹션 */}
                      {categorizedCurrent.sub.length > 0 && (
                        <div>
                          <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                            🧂 부재료/양념
                          </h3>
                          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {categorizedCurrent.sub.map((product, index) => renderProductCard(product, index))}
                          </div>
                        </div>
                      )}

                      {/* 과일/디저트 섹션 */}
                      {categorizedCurrent.fruits.length > 0 && (
                        <div>
                          <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                            🍎 과일 / 사이드 / 디저트
                          </h3>
                          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {categorizedCurrent.fruits.map((product, index) => renderProductCard(product, index))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ),
            },
            {
              id: 'next',
              label: `🔜 다음 주 ${hasNextData ? `(${nextProducts.length})` : ''}`,
              content: (
                <div className="mt-6">
                  {!hasNextData ? (
                    <div className="text-center py-12 text-gray-500">
                      <p className="text-lg mb-2">아직 공개된 다음 주 세일이 없어요!</p>
                      <p className="text-sm">주말에 다시 와주세요. 보통 토요일~일요일에 다음 주 세일 정보가 공개됩니다.</p>
                    </div>
                  ) : (
                    <WeeklySalesListContent
                      products={nextProducts}
                      onRecipeFilter={onRecipeFilter}
                    />
                  )}
                </div>
              ),
            },
          ]}
          activeTab={activeTab}
          onTabChange={(tabId) => setActiveTab(tabId as 'current' | 'next')}
        />
      </div>
    </section>
  )
}

// 다음 주 데이터를 위한 별도 컴포넌트 (재사용)
function WeeklySalesListContent({
  products,
  onRecipeFilter
}: {
  products: SaleProduct[]
  onRecipeFilter?: (productName: string, store: string) => void
}) {
  const categorizeProducts = (products: SaleProduct[]) => {
    const fruitKeywords = [
      'druiven', 'druif', 'grape', 'appel', 'apple', 'aardbei', 'strawberry',
      'banaan', 'banana', 'sinaasappel', 'orange', 'mandarijn', 'mandarin',
      'blauwe bessen', 'blueberry', 'framboos', 'raspberry', 'citroen', 'lemon',
      'kiwi', 'peer', 'pear', 'mango', 'ananas', 'pineapple', 'perzik', 'peach',
      'kersen', 'cherry', 'pruim', 'plum', 'abrikoos', 'apricot', 'fruit'
    ]

    const mainKeywords = [
      'speklappen', 'kipfilet', 'kippendijen', 'rundvlees', 'varkensvlees',
      'gehakt', 'zalm', 'vis', 'fish', 'tofu', 'aardappelen', 'aardappel',
      'kool', 'cabbage', 'ui', 'uien', 'onion', 'wortel', 'wortelen',
      'carrot', 'paprika', 'pepper', 'tomaat', 'tomaten', 'tomato', 'champignon',
      'mushroom', 'broccoli', 'spinazie', 'spinach'
    ]

    const subKeywords = [
      'knoflook', 'garlic', 'gember', 'ginger', 'soja', 'soy', 'azijn', 'vinegar',
      'olijfolie', 'olive oil', 'zout', 'salt', 'peper', 'pepper', 'suiker', 'sugar',
      'melk', 'milk', 'kaas', 'cheese', 'boter', 'butter', 'ei', 'eieren', 'egg'
    ]

    const main: SaleProduct[] = []
    const sub: SaleProduct[] = []
    const fruits: SaleProduct[] = []

    products.forEach(product => {
      const name = (product.product_name || product.name || '').toLowerCase()
      
      if (fruitKeywords.some(keyword => name.includes(keyword))) {
        fruits.push(product)
        return
      }

      if (mainKeywords.some(keyword => name.includes(keyword))) {
        main.push(product)
        return
      }

      if (subKeywords.some(keyword => name.includes(keyword))) {
        sub.push(product)
        return
      }

      main.push(product)
    })

    return { main, sub, fruits }
  }

  const categorized = categorizeProducts(products)

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return ''
    try {
      const date = new Date(dateStr)
      const month = date.getMonth() + 1
      const day = date.getDate()
      return `${month}/${day}`
    } catch {
      return ''
    }
  }

  const formatSalePeriod = (product: SaleProduct) => {
    const startDate = product.valid_from || product.start_date
    const endDate = product.valid_until || product.end_date
    
    const start = formatDate(startDate)
    const end = formatDate(endDate)
    
    if (start && end) {
      return `${start} ~ ${end}`
    }
    return ''
  }

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

  const handleRecipeFilter = (product: SaleProduct) => {
    const store = product.store || product.supermarket || ''
    const productName = product.product_name || product.name || ''
    if (onRecipeFilter) {
      onRecipeFilter(productName, store)
    }
  }

  const renderProductCard = (product: SaleProduct, index: number) => {
    const storeName = product.store || product.supermarket || 'Unknown'
    const productName = product.product_name || product.name || 'Unknown'
    const price = product.price || product.price_info || ''
    const discount = product.discount || product.discount_info || ''
    const salePeriod = formatSalePeriod(product)
    const colors = getStoreColors(storeName)
    const storeAbbr = getStoreAbbr(storeName)

    return (
      <div
        key={`${storeName}-${productName}-${index}`}
        className="bg-white rounded-lg border border-gray-200 hover:shadow-md transition-shadow duration-200 p-4"
      >
        <div className="flex items-start justify-between mb-3">
          <div className={`${colors.bg} ${colors.text} ${colors.border} px-3 py-1 rounded-full text-xs font-bold border`}>
            {storeAbbr}
          </div>
          {salePeriod && <span className="text-xs text-gray-500">{salePeriod}</span>}
        </div>

        <h3 className="text-base font-semibold text-gray-900 mb-2 line-clamp-2">
          {productName}
        </h3>

        <div className="flex items-center gap-2 mb-3">
          {price && <span className="text-sm text-gray-600">{price}</span>}
          {discount && (
            <span className="text-sm font-bold text-orange-600 bg-orange-50 px-2 py-1 rounded">
              {discount}
            </span>
          )}
        </div>

        <button
          onClick={() => handleRecipeFilter(product)}
          className="w-full flex items-center justify-center gap-2 text-sm font-medium text-orange-600 hover:text-orange-700 hover:bg-orange-50 py-2 px-3 rounded-lg transition-colors duration-200 border border-orange-200"
        >
          <ShoppingBag size={16} />
          <span>이 재료로 추천하는 레시피 보기</span>
          <ChevronRight size={16} />
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {categorized.main.length > 0 && (
        <div>
          <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <ShoppingBag size={20} />
            주재료 (고기, 생선, 주요 채소)
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {categorized.main.map((product, index) => renderProductCard(product, index))}
          </div>
        </div>
      )}

      {categorized.sub.length > 0 && (
        <div>
          <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            🧂 부재료/양념
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {categorized.sub.map((product, index) => renderProductCard(product, index))}
          </div>
        </div>
      )}

      {categorized.fruits.length > 0 && (
        <div>
          <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            🍎 과일 / 사이드 / 디저트
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {categorized.fruits.map((product, index) => renderProductCard(product, index))}
          </div>
        </div>
      )}
    </div>
  )
}
