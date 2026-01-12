'use client'

import { useEffect, useState, useMemo } from 'react'
import Link from 'next/link'
import { ShoppingBag, ChefHat } from 'lucide-react'
import Tabs from '@/components/Tabs'
import DealsGrid from '@/components/DealsGrid'
import BottomNav from '@/components/BottomNav'
import StoreFilter from '@/components/StoreFilter'

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

export default function DealsPage() {
  const [currentSales, setCurrentSales] = useState<WeeklySalesData | undefined>(undefined)
  const [nextSales, setNextSales] = useState<WeeklySalesData | undefined>(undefined)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'current' | 'next'>('current')
  
  // 마트 필터 상태
  const [selectedStores, setSelectedStores] = useState<Set<string>>(new Set())
  const [selectAll, setSelectAll] = useState<boolean>(true)

  useEffect(() => {
    const loadData = async () => {
      try {
        // 세일 데이터 로드
        try {
          const currentSalesModule = await import('@/data/current_sales.json')
          const currentSalesData = currentSalesModule.default as { products: SaleProduct[] }
          console.log(`[What2Cook NL] current_sales.json 로드: ${currentSalesData.products.length}개`)
          console.log('[What2Cook NL] 샘플 데이터:', currentSalesData.products.slice(0, 3))
          setCurrentSales({ products: currentSalesData.products, week_type: 'current' })
        } catch (err) {
          console.error('[What2Cook NL] current_sales.json 로드 실패:', err)
          // fallback: weekly_sales.json 시도
          try {
            const weeklyModule = await import('@/data/weekly_sales.json')
            const weeklyData = weeklyModule.default as { products: SaleProduct[] }
            console.log(`[What2Cook NL] weekly_sales.json 로드 (fallback): ${weeklyData.products.length}개`)
            setCurrentSales({ products: weeklyData.products, week_type: 'current' })
          } catch (fallbackErr) {
            console.error('[What2Cook NL] weekly_sales.json도 없음')
          }
        }

        try {
          const nextSalesModule = await import('@/data/next_sales.json')
          const nextSalesData = nextSalesModule.default as { products: SaleProduct[] }
          console.log(`[What2Cook NL] next_sales.json 로드: ${nextSalesData.products.length}개`)
          setNextSales({ products: nextSalesData.products, week_type: 'next' })
        } catch (err) {
          console.error('[What2Cook NL] next_sales.json 로드 실패:', err)
        }

        setLoading(false)
      } catch (err: any) {
        console.error('Error loading sales data:', err)
        setLoading(false)
      }
    }

    loadData()
  }, [])

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

  // 마트 필터링된 이번 주 데이터
  const filteredCurrentProducts = useMemo(() => {
    if (!currentSales?.products) return []
    if (selectAll) return currentSales.products
    return currentSales.products.filter(product => {
      const storeName = product.store || product.supermarket
      return storeName && selectedStores.has(storeName)
    })
  }, [currentSales, selectAll, selectedStores])

  // 마트 필터링된 다음 주 데이터
  const filteredNextProducts = useMemo(() => {
    if (!nextSales?.products) return []
    if (selectAll) return nextSales.products
    return nextSales.products.filter(product => {
      const storeName = product.store || product.supermarket
      return storeName && selectedStores.has(storeName)
    })
  }, [nextSales, selectAll, selectedStores])

  // 이번 주 데이터 분류
  const categorizedCurrent = useMemo(() => {
    if (filteredCurrentProducts.length === 0) {
      console.log('[What2Cook NL] 이번 주 필터링된 데이터 없음')
      return { main: [], sub: [], fruits: [] }
    }
    const categorized = categorizeProducts(filteredCurrentProducts)
    console.log(`[What2Cook NL] 이번 주 분류 결과 - 주재료: ${categorized.main.length}, 부재료: ${categorized.sub.length}, 과일: ${categorized.fruits.length}`)
    return categorized
  }, [filteredCurrentProducts])

  // 다음 주 데이터 분류
  const categorizedNext = useMemo(() => {
    if (filteredNextProducts.length === 0) {
      console.log('[What2Cook NL] 다음 주 필터링된 데이터 없음')
      return { main: [], sub: [], fruits: [] }
    }
    const categorized = categorizeProducts(filteredNextProducts)
    console.log(`[What2Cook NL] 다음 주 분류 결과 - 주재료: ${categorized.main.length}, 부재료: ${categorized.sub.length}, 과일: ${categorized.fruits.length}`)
    return categorized
  }, [filteredNextProducts])

  // 마트 필터 토글 함수
  const toggleStore = (storeName: string) => {
    setSelectAll(false)
    setSelectedStores((prev) => {
      const newSet = new Set(prev)
      if (newSet.has(storeName)) {
        newSet.delete(storeName)
      } else {
        newSet.add(storeName)
      }
      return newSet
    })
  }

  const handleSelectAll = () => {
    setSelectAll(true)
    setSelectedStores(new Set())
  }

  const currentProducts = filteredCurrentProducts
  const nextProducts = filteredNextProducts
  const hasCurrentData = currentProducts.length > 0
  const hasNextData = nextProducts.length > 0

  // 디버깅: 데이터 로드 상태 확인
  useEffect(() => {
    console.log('[What2Cook NL] 세일 데이터 상태:', {
      loading,
      currentSalesCount: currentProducts.length,
      nextSalesCount: nextProducts.length,
      hasCurrentData,
      hasNextData,
      categorizedCurrent: {
        main: categorizedCurrent.main.length,
        sub: categorizedCurrent.sub.length,
        fruits: categorizedCurrent.fruits.length,
      },
      categorizedNext: {
        main: categorizedNext.main.length,
        sub: categorizedNext.sub.length,
        fruits: categorizedNext.fruits.length,
      },
    })
  }, [loading, currentProducts.length, nextProducts.length, hasCurrentData, hasNextData, categorizedCurrent, categorizedNext])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50 pb-20 md:pb-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mx-auto mb-4"></div>
          <p className="text-gray-600">세일 정보 로딩 중...</p>
        </div>
      </div>
    )
  }

  return (
    <main className="min-h-screen bg-gray-50 pb-20 md:pb-8">
      {/* 헤더 */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-2xl font-bold text-gray-900">
            뭐해먹지 NL
            <span className="text-lg text-gray-500 font-normal ml-2">What2Cook NL</span>
          </h1>
        </div>
      </div>

      {/* 세일 섹션 */}
      <section className="w-full bg-white py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* 섹션 헤더 */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-3xl font-bold text-gray-900">
                세일리스트
              </h2>
              <Link
                href="/"
                className="flex items-center gap-2 px-4 py-2 bg-white text-orange-600 border-2 border-orange-500 rounded-lg hover:bg-orange-50 transition-colors duration-200 font-medium text-sm"
              >
                <ChefHat size={16} />
                <span>추천식단 보기</span>
              </Link>
            </div>
            <p className="text-sm text-gray-600 mb-1">
              이번 주 장볼 거리를 미리 확인하고 추천 레시피를 확인하세요!
            </p>
            <p className="text-xs text-orange-600 font-medium">
              ⭐ 추천항목: 한식 요리에 활용 가능한 세일 상품만 선별하여 표시합니다
            </p>
          </div>

          {/* 마트 필터 */}
          {(currentSales?.products && currentSales.products.length > 0) || 
           (nextSales?.products && nextSales.products.length > 0) ? (
            <StoreFilter
              products={activeTab === 'current' 
                ? (currentSales?.products || [])
                : (nextSales?.products || [])
              }
              selectedStores={selectedStores}
              onStoreToggle={toggleStore}
              onSelectAll={handleSelectAll}
              selectAll={selectAll}
            />
          ) : null}

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
                        {/* 모든 카테고리 출력 (빈 배열은 DealsGrid에서 자동 처리) */}
                        {categorizedCurrent.main.length > 0 && (
                          <DealsGrid
                            products={categorizedCurrent.main}
                            category="main"
                            categoryLabel="주재료 (고기, 생선, 주요 채소)"
                          />
                        )}
                        {categorizedCurrent.sub.length > 0 && (
                          <DealsGrid
                            products={categorizedCurrent.sub}
                            category="sub"
                            categoryLabel="🧂 부재료/양념"
                          />
                        )}
                        {categorizedCurrent.fruits.length > 0 && (
                          <DealsGrid
                            products={categorizedCurrent.fruits}
                            category="fruits"
                            categoryLabel="🍎 과일 / 사이드 / 디저트"
                          />
                        )}
                        {/* 디버깅: 분류되지 않은 경우 전체 표시 */}
                        {(categorizedCurrent.main.length === 0 && 
                          categorizedCurrent.sub.length === 0 && 
                          categorizedCurrent.fruits.length === 0) && (
                          <div className="text-center py-8 text-orange-600">
                            <p className="mb-2">⚠️ 상품이 분류되지 않았습니다.</p>
                            <p className="text-sm text-gray-600">총 {currentProducts.length}개 상품 로드됨</p>
                            <details className="mt-4 text-left">
                              <summary className="cursor-pointer text-sm">상품 목록 보기</summary>
                              <div className="mt-2 text-xs text-gray-500 space-y-1">
                                {currentProducts.slice(0, 10).map((p, idx) => (
                                  <div key={idx}>{p.product_name || p.name || '이름 없음'}</div>
                                ))}
                              </div>
                            </details>
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
                          <DealsGrid
                            products={categorizedNext.main}
                            category="main"
                            categoryLabel="주재료 (고기, 생선, 주요 채소)"
                          />
                        )}
                        {categorizedNext.sub.length > 0 && (
                          <DealsGrid
                            products={categorizedNext.sub}
                            category="sub"
                            categoryLabel="🧂 부재료/양념"
                          />
                        )}
                        {categorizedNext.fruits.length > 0 && (
                          <DealsGrid
                            products={categorizedNext.fruits}
                            category="fruits"
                            categoryLabel="🍎 과일 / 사이드 / 디저트"
                          />
                        )}
                        {/* 디버깅: 분류되지 않은 경우 */}
                        {(categorizedNext.main.length === 0 && 
                          categorizedNext.sub.length === 0 && 
                          categorizedNext.fruits.length === 0) && (
                          <div className="text-center py-8 text-orange-600">
                            <p className="mb-2">⚠️ 상품이 분류되지 않았습니다.</p>
                            <p className="text-sm text-gray-600">총 {nextProducts.length}개 상품 로드됨</p>
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

      {/* 하단 네비게이션 (모바일만) */}
      <BottomNav />
    </main>
  )
}
