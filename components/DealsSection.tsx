'use client'

import { useState, useMemo } from 'react'
import { ShoppingBag, ChefHat } from 'lucide-react'
import Link from 'next/link'
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

interface DealsSectionProps {
  currentSales?: WeeklySalesData
  nextSales?: WeeklySalesData
}

export default function DealsSection({
  currentSales,
  nextSales
}: DealsSectionProps) {
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

  // 마트 색상
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

  // 상품 카드 렌더링 (컴팩트 버전)
  const renderProductCard = (product: SaleProduct, index: number) => {
    const storeName = product.store || product.supermarket || 'Unknown'
    const productName = product.product_name || product.name || 'Unknown'
    const price = product.price || product.price_info || ''
    const discount = product.discount || product.discount_info || ''
    const salePeriod = formatSalePeriod(product)
    const colors = getStoreColors(storeName)
    const storeAbbr = getStoreAbbr(storeName)

    return (
      <Link
        key={`${storeName}-${productName}-${index}`}
        href="/#recipes-section"
        className="bg-white rounded-lg border border-gray-200 hover:shadow-md hover:border-orange-300 transition-all duration-200 p-3 flex flex-col"
      >
        {/* 마트 배지 및 세일 기간 */}
        <div className="flex items-start justify-between mb-2">
          <div className={`${colors.bg} ${colors.text} ${colors.border} px-2 py-0.5 rounded-full text-xs font-bold border`}>
            {storeAbbr}
          </div>
          {salePeriod && (
            <span className="text-xs text-gray-500">{salePeriod}</span>
          )}
        </div>

        {/* 상품명 (2줄 제한) */}
        <h3 className="text-sm font-semibold text-gray-900 mb-2 line-clamp-2 flex-1">
          {productName}
        </h3>

        {/* 가격 및 할인 정보 */}
        <div className="flex items-center justify-between gap-2 mt-auto">
          {price && (
            <span className="text-xs text-gray-600 truncate">{price}</span>
          )}
          {discount && (
            <span className="text-xs font-bold text-orange-600 bg-orange-50 px-2 py-0.5 rounded whitespace-nowrap">
              {discount}
            </span>
          )}
        </div>
      </Link>
    )
  }

  // 이번 주 데이터 분류
  const categorizedCurrent = useMemo(() => {
    if (!currentSales?.products) return { main: [], sub: [], fruits: [] }
    return categorizeProducts(currentSales.products)
  }, [currentSales])

  // 다음 주 데이터 분류
  const categorizedNext = useMemo(() => {
    if (!nextSales?.products) return { main: [], sub: [], fruits: [] }
    return categorizeProducts(nextSales.products)
  }, [nextSales])

  const currentProducts = currentSales?.products || []
  const nextProducts = nextSales?.products || []
  const hasCurrentData = currentProducts.length > 0
  const hasNextData = nextProducts.length > 0

  return (
    <section className="w-full bg-white py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* 섹션 헤더 */}
        <div className="mb-6">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
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
                    <div className="space-y-6">
                      {/* 주재료 섹션 */}
                      {categorizedCurrent.main.length > 0 && (
                        <div>
                          <h3 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
                            <ShoppingBag size={18} />
                            주재료 (고기, 생선, 주요 채소)
                          </h3>
                          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                            {categorizedCurrent.main.map((product, index) => renderProductCard(product, index))}
                          </div>
                        </div>
                      )}

                      {/* 부재료/양념 섹션 */}
                      {categorizedCurrent.sub.length > 0 && (
                        <div>
                          <h3 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
                            🧂 부재료/양념
                          </h3>
                          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                            {categorizedCurrent.sub.map((product, index) => renderProductCard(product, index))}
                          </div>
                        </div>
                      )}

                      {/* 과일/디저트 섹션 */}
                      {categorizedCurrent.fruits.length > 0 && (
                        <div>
                          <h3 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
                            🍎 과일 / 사이드 / 디저트
                          </h3>
                          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
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
                    <div className="space-y-6">
                      {categorizedNext.main.length > 0 && (
                        <div>
                          <h3 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
                            <ShoppingBag size={18} />
                            주재료 (고기, 생선, 주요 채소)
                          </h3>
                          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                            {categorizedNext.main.map((product, index) => renderProductCard(product, index))}
                          </div>
                        </div>
                      )}

                      {categorizedNext.sub.length > 0 && (
                        <div>
                          <h3 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
                            🧂 부재료/양념
                          </h3>
                          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                            {categorizedNext.sub.map((product, index) => renderProductCard(product, index))}
                          </div>
                        </div>
                      )}

                      {categorizedNext.fruits.length > 0 && (
                        <div>
                          <h3 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
                            🍎 과일 / 사이드 / 디저트
                          </h3>
                          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                            {categorizedNext.fruits.map((product, index) => renderProductCard(product, index))}
                          </div>
                        </div>
                      )}
                    </div>
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
