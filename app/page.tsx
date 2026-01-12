'use client'

import { useEffect, useState, useMemo } from 'react'
import dynamic from 'next/dynamic'
import Tabs from '@/components/Tabs'
import AdSlot from '@/components/AdSlot'

// 코드 스플리팅: Dashboard 컴포넌트 lazy loading
const Dashboard = dynamic(() => import('@/components/Dashboard'), {
  loading: () => (
    <div className="flex items-center justify-center py-12">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
    </div>
  ),
  ssr: true,
})

interface Recipe {
  id: string
  store: string
  menu_name: string
  main_ingredients: string[]
  description: string
  tags: any
  shopping_list: string[]
  cost_saving_tip?: string
  valid_from?: string
  valid_until?: string
}

interface AffiliateProduct {
  id: string
  platform: 'amazon' | 'bol'
  name: string
  description: string
  image: string
  url: string
  price: string
  currency: string
  badge?: string
  benefit?: string
  category: string
  tags?: string[]
}

export default function Home() {
  const [allRecipes, setAllRecipes] = useState<Recipe[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string>('')
  const [activeTab, setActiveTab] = useState<'current' | 'upcoming'>('current')
  const [affiliateProducts, setAffiliateProducts] = useState<AffiliateProduct[]>([])

  useEffect(() => {
    const loadData = async () => {
      try {
        // 모든 레시피 데이터 로드 (current + next)
        const recipes: Recipe[] = []
        
        // 현재 주 레시피
        try {
          const currentModule = await import('@/data/current_recipes.json')
          const currentRecipes = currentModule.default as Recipe[]
          console.log(`[What2Cook NL] current_recipes.json 로드: ${currentRecipes.length}개`)
          recipes.push(...currentRecipes)
        } catch (err) {
          console.log('[What2Cook NL] current_recipes.json 없음, weekly_recipes.json 시도')
          // fallback: weekly_recipes.json (모든 레시피 포함)
          try {
            const weeklyModule = await import('@/data/weekly_recipes.json')
            const weeklyRecipes = weeklyModule.default as Recipe[]
            console.log(`[What2Cook NL] weekly_recipes.json 로드: ${weeklyRecipes.length}개`)
            recipes.push(...weeklyRecipes)
          } catch (e) {
            console.log('[What2Cook NL] current_recipes.json and weekly_recipes.json 모두 없음')
          }
        }

        // 다음 주 레시피
        try {
          const nextModule = await import('@/data/next_recipes.json')
          const nextRecipes = nextModule.default as Recipe[]
          console.log(`[What2Cook NL] next_recipes.json 로드: ${nextRecipes.length}개`)
          recipes.push(...nextRecipes)
        } catch (err) {
          console.log('[What2Cook NL] next_recipes.json 없음')
        }

        // 제휴 상품 데이터 로드
        try {
          const affiliateModule = await import('@/data/affiliate_products.json')
          const products = affiliateModule.default as AffiliateProduct[]
          console.log(`[What2Cook NL] affiliate_products.json 로드: ${products.length}개`)
          setAffiliateProducts(products)
        } catch (err) {
          console.log('[What2Cook NL] affiliate_products.json 없음 (선택사항)')
        }
        
        console.log(`[What2Cook NL] 총 ${recipes.length}개 레시피 로드 완료`)

        setAllRecipes(recipes)
        setLoading(false)
      } catch (err: any) {
        console.error('Error loading recipes:', err)
        setError(err.message)
        setLoading(false)
      }
    }

    loadData()
  }, [])

  // 주차 기준으로 레시피 분류 (이번 주 vs 다음 주)
  const { currentRecipes, upcomingRecipes } = useMemo(() => {
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    const todayTime = today.getTime()

    // 이번 주 월요일과 일요일 계산
    const daysSinceMonday = today.getDay() === 0 ? 6 : today.getDay() - 1
    const thisWeekMonday = new Date(today)
    thisWeekMonday.setDate(today.getDate() - daysSinceMonday)
    thisWeekMonday.setHours(0, 0, 0, 0)
    
    const thisWeekSunday = new Date(thisWeekMonday)
    thisWeekSunday.setDate(thisWeekMonday.getDate() + 6)
    thisWeekSunday.setHours(23, 59, 59, 999)

    const current: Recipe[] = []
    const upcoming: Recipe[] = []

    // 마트별 세일 시작일 매핑 (fallback용)
    const STORE_SALE_START_DAY: { [key: string]: number } = {
      'Albert Heijn': 0,  // 월요일
      'Jumbo': 2,         // 수요일
      'Dirk': 2,          // 수요일
      'Aldi': 0,          // 월요일
      'Plus': 0,          // 월요일
      'Hoogvliet': 0,     // 월요일
      'Coop': 0,          // 월요일
    }

    console.log(`[What2Cook NL] 데이터 분석 시작 - 오늘: ${today.toISOString().split('T')[0]}, 이번 주: ${thisWeekMonday.toISOString().split('T')[0]} ~ ${thisWeekSunday.toISOString().split('T')[0]}, 총 레시피: ${allRecipes.length}개`)

    allRecipes.forEach(recipe => {
      let validFrom: Date | null = null
      let validUntil: Date | null = null

      // 날짜 정보 파싱
      if (recipe.valid_from) {
        try {
          validFrom = new Date(recipe.valid_from)
          validFrom.setHours(0, 0, 0, 0)
        } catch (e) {
          console.warn(`[What2Cook NL] 날짜 파싱 실패 (valid_from): ${recipe.valid_from}`)
        }
      }

      if (recipe.valid_until) {
        try {
          validUntil = new Date(recipe.valid_until)
          validUntil.setHours(23, 59, 59, 999)
        } catch (e) {
          console.warn(`[What2Cook NL] 날짜 파싱 실패 (valid_until): ${recipe.valid_until}`)
        }
      }

      // 날짜 정보가 없으면 마트별 세일 시작일로 계산 (fallback)
      if (!validFrom || !validUntil) {
        const storeName = recipe.store
        const startDayOfWeek = STORE_SALE_START_DAY[storeName] || 0
        
        const daysSinceMonday = today.getDay() === 0 ? 6 : today.getDay() - 1
        const currentMonday = new Date(today)
        currentMonday.setDate(today.getDate() - daysSinceMonday)
        currentMonday.setHours(0, 0, 0, 0)
        
        // 이번 주 세일 시작일 계산
        const daysToStart = (startDayOfWeek - currentMonday.getDay() + 7) % 7
        const thisWeekStart = new Date(currentMonday)
        thisWeekStart.setDate(currentMonday.getDate() + daysToStart)
        thisWeekStart.setHours(0, 0, 0, 0)
        
        // 시작일이 지났으면 다음 주
        if (thisWeekStart.getTime() < todayTime) {
          thisWeekStart.setDate(thisWeekStart.getDate() + 7)
        }
        
        validFrom = thisWeekStart
        validUntil = new Date(thisWeekStart)
        validUntil.setDate(thisWeekStart.getDate() + 6)
        validUntil.setHours(23, 59, 59, 999)
      }

      if (validFrom && validUntil) {
        const fromTime = validFrom.getTime()
        const untilTime = validUntil.getTime()
        const thisWeekMondayTime = thisWeekMonday.getTime()
        const thisWeekSundayTime = thisWeekSunday.getTime()

        // 이번 주 세일: 시작일이 이번 주 내에 있거나 이미 시작했고 아직 종료하지 않음
        if (fromTime <= thisWeekSundayTime && untilTime >= thisWeekMondayTime) {
          current.push(recipe)
          console.log(`[What2Cook NL] 이번 주: ${recipe.store} - ${recipe.menu_name} (${validFrom.toISOString().split('T')[0]} ~ ${validUntil.toISOString().split('T')[0]})`)
        }
        // 다음 주 세일: 시작일이 이번 주 이후
        else if (fromTime > thisWeekSundayTime) {
          upcoming.push(recipe)
          console.log(`[What2Cook NL] 다음 주: ${recipe.store} - ${recipe.menu_name} (${validFrom.toISOString().split('T')[0]} ~ ${validUntil.toISOString().split('T')[0]})`)
        }
        // 이미 종료된 세일은 제외
        else {
          console.log(`[What2Cook NL] 종료된 세일: ${recipe.store} - ${recipe.menu_name} (${validFrom.toISOString().split('T')[0]} ~ ${validUntil.toISOString().split('T')[0]})`)
        }
      } else {
        // 날짜 정보가 없으면 기본적으로 current에 포함 (하위 호환성)
        console.warn(`[What2Cook NL] 날짜 정보 없음: ${recipe.store} - ${recipe.menu_name}`)
        current.push(recipe)
      }
    })

    console.log(`[What2Cook NL] 데이터 분석 완료 - 이번 주: ${current.length}개, 다음 주: ${upcoming.length}개`)

    return { currentRecipes: current, upcomingRecipes: upcoming }
  }, [allRecipes])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mx-auto mb-4"></div>
          <p className="text-gray-600">레시피 로딩 중...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center text-red-600">
          <p className="text-xl mb-2">⚠️ 에러 발생</p>
          <p>{error}</p>
        </div>
      </div>
    )
  }

  if (currentRecipes.length === 0 && upcomingRecipes.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center text-gray-600">
          <p className="text-xl mb-2">📭 레시피가 없습니다</p>
          <p>먼저 크롤러를 실행해주세요.</p>
        </div>
      </div>
    )
  }

  return (
    <main className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            뭐해먹지 NL
            <span className="text-2xl text-gray-500 font-normal ml-3">What2Cook NL</span>
          </h1>
          <p className="text-gray-600">네덜란드 마트 세일 정보로 결정하는 오늘 한식 식단</p>
        </div>

        {/* 상단 광고 슬롯 */}
        <div className="mb-8">
          <AdSlot 
            slotId="header-banner"
            adType="adsense"
            size="banner"
          />
        </div>

        {/* Tabs */}
        <Tabs
          tabs={[
            {
              id: 'current',
              label: `📅 이번 주 ${currentRecipes.length > 0 ? `(${currentRecipes.length})` : ''}`,
              content: (
                <div>
                  {currentRecipes.length > 0 ? (
                    <>
                      <div className="mb-4 text-sm text-gray-600">
                        이번 주(월~일) 동안 진행되는 세일 품목과 레시피입니다. 수요일 시작 마트(Jumbo, Dirk)도 포함됩니다.
                      </div>
                      <Dashboard 
                        recipes={currentRecipes} 
                        showDateBadge={true}
                        affiliateProducts={affiliateProducts}
                      />
                    </>
                  ) : (
                    <div className="text-center py-12 text-gray-500">
                      <p className="text-lg mb-2">이번 주 세일이 없습니다</p>
                      <p className="text-sm">다음 주 세일을 확인해보세요!</p>
                    </div>
                  )}
                </div>
              ),
            },
            {
              id: 'upcoming',
              label: `🔜 다음 주 ${upcomingRecipes.length > 0 ? `(${upcomingRecipes.length})` : ''}`,
              content: (
                <div>
                  {upcomingRecipes.length > 0 ? (
                    <>
                      <div className="mb-4 text-sm text-gray-600">
                        다음 주 월요일부터 시작될 세일 품목과 레시피입니다. 미리 준비하세요!
                      </div>
                      <Dashboard 
                        recipes={upcomingRecipes} 
                        showDateBadge={true}
                        affiliateProducts={affiliateProducts}
                      />
                    </>
                  ) : (
                    <div className="text-center py-12 text-gray-500">
                      <p className="text-lg mb-2">아직 공개된 다음 주 세일이 없어요!</p>
                      <p className="text-sm">주말에 다시 와주세요. 보통 토요일~일요일에 다음 주 세일 정보가 공개됩니다.</p>
                    </div>
                  )}
                </div>
              ),
            },
          ]}
          activeTab={activeTab}
          onTabChange={(tabId) => setActiveTab(tabId as 'current' | 'upcoming')}
        />

      </div>
    </main>
  )
}
