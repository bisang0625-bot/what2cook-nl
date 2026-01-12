'use client'

import { useState, useMemo, useEffect, Fragment } from 'react'
import { Clock, ShoppingBag, ChefHat, Baby, Flame, Leaf, X, ChevronRight, Timer, Percent, PartyPopper, Beer } from 'lucide-react'
import AffiliateDisclosure from './ads/AffiliateDisclosure'
import AffiliateCard from './ads/AffiliateCard'

interface Recipe {
  id: string
  store: string
  menu_name: string
  main_ingredients: string[]
  description: string
  tags: {
    is_spicy: boolean
    is_vegetarian: boolean
    is_kid_friendly: boolean
    is_party_food?: boolean
    is_alcohol_snack?: boolean
    cooking_time: string
  }
  shopping_list: string[]
  cost_saving_tip?: string
  valid_from?: string
  valid_until?: string
}

interface AffiliateProduct {
  id: string
  name: string
  description: string
  image: string
  platforms?: {
    bol?: { url: string; price: string; currency: string; badge?: string; benefit?: string; usp?: string }
    amazon?: { url: string; price: string; currency: string; badge?: string; benefit?: string; usp?: string }
  }
  affiliate_links?: {
    bol?: { url: string; price: string; currency: string }
    amazon?: { url: string; price: string; currency: string }
  }
  category: string
  tags?: string[]
}

interface AffiliateProduct {
  id: string
  name: string
  description: string
  image: string
  platforms?: {
    bol?: { url: string; price: string; currency: string; badge?: string; benefit?: string; usp?: string }
    amazon?: { url: string; price: string; currency: string; badge?: string; benefit?: string; usp?: string }
  }
  affiliate_links?: {
    bol?: { url: string; price: string; currency: string }
    amazon?: { url: string; price: string; currency: string }
  }
  category: string
  tags?: string[]
}

interface DashboardProps {
  recipes: Recipe[]
  showDateBadge?: boolean
  affiliateProducts?: AffiliateProduct[]
}

// 조리 시간 파싱 헬퍼 함수
function parseCookingTime(timeStr: string): number {
  const num = parseInt(timeStr.replace(/[^0-9]/g, ''))
  return isNaN(num) ? 0 : num
}

// 할인 팁에서 '1+1' 등의 키워드 확인 헬퍼 함수
function hasBestDeal(recipe: Recipe): boolean {
  const keywords = ['1+1', '2e halve', 'gratis', 'korting', 'sale', 'bonus']
  const targetText = (recipe.cost_saving_tip || '') + ' ' + recipe.main_ingredients.join(' ')
  return keywords.some(k => targetText.toLowerCase().includes(k))
}

// 날짜 뱃지 생성 함수
function getDateBadge(recipe: Recipe): { text: string; type: 'active' | 'upcoming' | 'none' } {
  if (!recipe.valid_from && !recipe.valid_until) {
    return { text: '', type: 'none' }
  }

  const today = new Date()
  today.setHours(0, 0, 0, 0)

  const validFrom = recipe.valid_from ? new Date(recipe.valid_from) : null
  const validUntil = recipe.valid_until ? new Date(recipe.valid_until) : null

  if (validFrom && validUntil) {
    validFrom.setHours(0, 0, 0, 0)
    validUntil.setHours(23, 59, 59, 999)

    // 현재 활성화된 세일
    if (validFrom <= today && today <= validUntil) {
      const daysLeft = Math.ceil((validUntil.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))
      return {
        text: `🔥 D-${daysLeft} (${validUntil.toLocaleDateString('ko-KR', { month: 'numeric', day: 'numeric' })}까지)`,
        type: 'active'
      }
    }
    // 곧 시작될 세일
    else if (validFrom > today) {
      const daysUntil = Math.ceil((validFrom.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))
      const weekdayKr = ['월', '화', '수', '목', '금', '토', '일'][validFrom.getDay()]
      return {
        text: `📅 ${validFrom.toLocaleDateString('ko-KR', { month: 'numeric', day: 'numeric' })}(${weekdayKr}) 오픈`,
        type: 'upcoming'
      }
    }
  }

  // 종료일만 있는 경우
  if (validUntil && validUntil >= today) {
    const daysLeft = Math.ceil((validUntil.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))
    return {
      text: `🔥 D-${daysLeft} (${validUntil.toLocaleDateString('ko-KR', { month: 'numeric', day: 'numeric' })}까지)`,
      type: 'active'
    }
  }

  return { text: '', type: 'none' }
}

export default function Dashboard({ 
  recipes, 
  showDateBadge = false,
  affiliateProducts = []
}: DashboardProps) {
  // 여러 마트 선택 가능하도록 Set 사용
  // 초기 상태: 모든 마트 선택 (필터 미적용)
  const [selectedStores, setSelectedStores] = useState<Set<string>>(new Set())
  const [selectAll, setSelectAll] = useState<boolean>(true)
  
  // 개선된 필터 상태
  const [selectedFilters, setSelectedFilters] = useState<{
    kidFriendly: boolean
    spicy: boolean
    vegetarian: boolean
    quickMeal: boolean // 30분 이내
    bestDeal: boolean // 1+1 등 할인
    partyFood: boolean // 파티음식
    alcoholSnack: boolean // 술안주
  }>({
    kidFriendly: false,
    spicy: false,
    vegetarian: false,
    quickMeal: false,
    bestDeal: false,
    partyFood: false,
    alcoholSnack: false,
  })
  
  const [selectedRecipe, setSelectedRecipe] = useState<Recipe | null>(null)

  // 필터링 로직
  const filteredRecipes = useMemo(() => {
    return recipes.filter((recipe) => {
      // Store 필터 (전체 선택이거나 선택된 마트 중 하나)
      if (!selectAll && !selectedStores.has(recipe.store)) return false

      // Tag 필터
      // 1. 아이 식단: 태그 체크 AND 매운 음식 제외 (안전 장치)
      if (selectedFilters.kidFriendly) {
        if (!recipe.tags.is_kid_friendly) return false
        if (recipe.tags.is_spicy) return false // 매운 음식 절대 제외
      }

      if (selectedFilters.spicy && !recipe.tags.is_spicy) return false
      if (selectedFilters.vegetarian && !recipe.tags.is_vegetarian) return false
      if (selectedFilters.partyFood && !recipe.tags.is_party_food) return false
      if (selectedFilters.alcoholSnack && !recipe.tags.is_alcohol_snack) return false
      
      // 2. 조리 시간 필터 (30분 이내)
      if (selectedFilters.quickMeal) {
        const minutes = parseCookingTime(recipe.tags.cooking_time)
        if (minutes > 30 || minutes === 0) return false
      }
      
      // 3. Best Deal 필터
      if (selectedFilters.bestDeal && !hasBestDeal(recipe)) return false

      return true
    })
  }, [recipes, selectedStores, selectAll, selectedFilters])

  // 레시피 데이터에서 실제 존재하는 마트 목록 추출 (함수 이전에 정의)
  const availableStores = useMemo(() => {
    const storesSet = new Set(recipes.map((recipe) => recipe.store))
    return Array.from(storesSet).sort()
  }, [recipes])

  // 필터가 적용되었는지 확인
  const isFilterActive = useMemo(() => {
    // 마트 필터가 적용되었는지 (전체 선택이 아니거나 일부 마트만 선택)
    const storeFilterActive = !selectAll && (selectedStores.size < availableStores.length || selectedStores.size === 0)
    
    // 태그 필터가 적용되었는지
    const tagFilterActive = Object.values(selectedFilters).some(value => value === true)
    
    return storeFilterActive || tagFilterActive
  }, [selectAll, selectedStores, availableStores.length, selectedFilters])

  const toggleFilter = (filterKey: keyof typeof selectedFilters) => {
    setSelectedFilters((prev) => {
      const newState = { ...prev, [filterKey]: !prev[filterKey] }
      
      // 로직 개선: 아이 식단 선택 시 매운맛 자동 해제
      if (filterKey === 'kidFriendly' && newState.kidFriendly) {
        newState.spicy = false
      }
      
      // 로직 개선: 매운맛 선택 시 아이 식단 자동 해제
      if (filterKey === 'spicy' && newState.spicy) {
        newState.kidFriendly = false
      }
      
      return newState
    })
  }

  // 마트 선택 토글 함수
  const toggleStore = (storeName: string) => {
    setSelectAll(false) // 개별 선택 시 전체 선택 해제
    setSelectedStores((prev) => {
      const newSet = new Set(prev)
      if (newSet.has(storeName)) {
        newSet.delete(storeName)
      } else {
        newSet.add(storeName)
      }
      // 모든 마트가 선택되면 전체 선택으로 전환
      if (newSet.size === availableStores.length) {
        setSelectAll(true)
        return new Set()
      }
      return newSet
    })
  }

  // 전체 선택 토글 함수
  const toggleSelectAll = () => {
    if (selectAll) {
      setSelectAll(false)
      setSelectedStores(new Set(['Albert Heijn'])) // 기본값으로 복귀
    } else {
      setSelectAll(true)
      setSelectedStores(new Set())
    }
  }

  // 기본 마트 목록 (데이터가 없어도 표시) - 확장됨
  const allStores = ['Albert Heijn', 'Jumbo', 'Lidl', 'Plus', 'Hoogvliet', 'Dirk', 'ALDI', 'Coop']
  
  // 실제 데이터가 있는 마트와 없는 마트 구분
  const stores = allStores.map((store) => ({
    name: store,
    available: availableStores.includes(store),
  }))

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                <span className="text-nl-orange-500">K</span>-Bonus
              </h1>
              <p className="text-gray-600 mt-1">
                이번 주 마트 세일로 차리는 알뜰 밥상
              </p>
            </div>
            <div className="text-sm text-gray-500">
              {isFilterActive 
                ? `${filteredRecipes.length}개의 레시피 (전체 ${recipes.length}개 중)`
                : `${recipes.length}개의 레시피`
              }
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filter Bar */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
          {/* Store Filter */}
          <div className="mb-6">
            <label className="block text-sm font-semibold text-gray-700 mb-3">
              마트 선택 (여러 개 선택 가능)
            </label>
            <div className="flex flex-wrap gap-2">
              {/* 전체 선택 버튼 */}
              <button
                onClick={toggleSelectAll}
                className={`
                  px-4 py-2 rounded-lg font-medium transition-all duration-200
                  ${selectAll
                    ? 'bg-nl-orange-600 text-white shadow-sm border-2 border-nl-orange-700'
                    : 'bg-white text-gray-700 border-2 border-gray-300 hover:bg-gray-50 hover:border-nl-orange-300'
                  }
                `}
              >
                전체 ({availableStores.length})
              </button>
              
              {/* 개별 마트 버튼 */}
              {stores.filter(store => store.available).map((store) => {
                const isActive = selectAll || selectedStores.has(store.name)
                
                return (
                  <button
                    key={store.name}
                    onClick={() => toggleStore(store.name)}
                    className={`
                      px-4 py-2 rounded-lg font-medium transition-all duration-200 relative
                      ${isActive && !selectAll
                        ? 'bg-nl-orange-500 text-white shadow-sm border-2 border-nl-orange-600'
                        : selectAll
                        ? 'bg-nl-orange-100 text-nl-orange-700 border-2 border-nl-orange-300'
                        : 'bg-white text-gray-700 border-2 border-gray-300 hover:bg-gray-50 hover:border-nl-orange-300'
                      }
                    `}
                  >
                    {store.name}
                    {isActive && !selectAll && (
                      <span className="ml-1.5 text-xs">✓</span>
                    )}
                  </button>
                )
              })}
            </div>
            {availableStores.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <p>현재 등록된 세일 정보가 없습니다.</p>
                <p className="text-sm mt-1">매주 일요일 업데이트됩니다.</p>
              </div>
            )}
            {selectedStores.size > 0 && !selectAll && availableStores.length > 0 && (
              <p className="mt-2 text-xs text-gray-500">
                {selectedStores.size}개 마트 선택됨
              </p>
            )}
          </div>

          {/* Tag Filter (Improved) */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-3">
              필터
            </label>
            
            <div className="space-y-3">
              {/* 그룹 1: 상황별 추천 */}
              <div className="flex flex-wrap gap-2">
                <span className="text-xs font-medium text-gray-400 py-2 mr-1">추천:</span>
                <button
                  onClick={() => toggleFilter('kidFriendly')}
                  className={`
                    flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium transition-all duration-200
                    ${selectedFilters.kidFriendly
                      ? 'bg-green-500 text-white shadow-sm'
                      : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                    }
                  `}
                >
                  <Baby size={16} />
                  <span>아이 식단</span>
                </button>
                
                <button
                  onClick={() => toggleFilter('vegetarian')}
                  className={`
                    flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium transition-all duration-200
                    ${selectedFilters.vegetarian
                      ? 'bg-green-600 text-white shadow-sm'
                      : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                    }
                  `}
                >
                  <Leaf size={16} />
                  <span>채식</span>
                </button>

                <button
                  onClick={() => toggleFilter('partyFood')}
                  className={`
                    flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium transition-all duration-200
                    ${selectedFilters.partyFood
                      ? 'bg-pink-500 text-white shadow-sm'
                      : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                    }
                  `}
                >
                  <PartyPopper size={16} />
                  <span>파티/손님초대</span>
                </button>

                <button
                  onClick={() => toggleFilter('alcoholSnack')}
                  className={`
                    flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium transition-all duration-200
                    ${selectedFilters.alcoholSnack
                      ? 'bg-orange-500 text-white shadow-sm'
                      : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                    }
                  `}
                >
                  <Beer size={16} />
                  <span>술안주</span>
                </button>
              </div>

              {/* 그룹 2: 맛/특징 */}
              <div className="flex flex-wrap gap-2">
                <span className="text-xs font-medium text-gray-400 py-2 mr-1">특징:</span>
                <button
                  onClick={() => toggleFilter('spicy')}
                  disabled={selectedFilters.kidFriendly} // 아이 식단 선택 시 비활성화
                  className={`
                    flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium transition-all duration-200
                    ${selectedFilters.spicy
                      ? 'bg-red-500 text-white shadow-sm'
                      : selectedFilters.kidFriendly
                      ? 'bg-gray-100 text-gray-300 cursor-not-allowed border border-gray-200'
                      : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                    }
                  `}
                >
                  <Flame size={16} />
                  <span>매운맛</span>
                </button>

                <button
                  onClick={() => toggleFilter('quickMeal')}
                  className={`
                    flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium transition-all duration-200
                    ${selectedFilters.quickMeal
                      ? 'bg-blue-500 text-white shadow-sm'
                      : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                    }
                  `}
                >
                  <Timer size={16} />
                  <span>30분 이내</span>
                </button>

                <button
                  onClick={() => toggleFilter('bestDeal')}
                  className={`
                    flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium transition-all duration-200
                    ${selectedFilters.bestDeal
                      ? 'bg-purple-500 text-white shadow-sm'
                      : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                    }
                  `}
                >
                  <Percent size={16} />
                  <span>1+1 / 파격할인</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Recipe Grid */}
        {filteredRecipes.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-xl shadow-sm border border-gray-200">
            <ChefHat className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <p className="text-gray-600">필터 조건에 맞는 레시피가 없습니다.</p>
            <button
              onClick={() => {
                setSelectedFilters({
                  kidFriendly: false,
                  spicy: false,
                  vegetarian: false,
                  quickMeal: false,
                  bestDeal: false,
                  partyFood: false,
                  alcoholSnack: false,
                })
                setSelectAll(false)
                setSelectedStores(new Set(['Albert Heijn']))
              }}
              className="mt-4 text-nl-orange-500 hover:text-nl-orange-600 font-medium"
            >
              필터 초기화
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredRecipes.map((recipe, index) => {
              // 5:1 비율로 광고 삽입 (5번째 레시피 뒤에 광고, 즉 6, 12, 18... 번째 슬롯)
              // index는 0부터 시작하므로, 5번째 레시피는 index=4, 그 뒤에 광고 삽입
              const shouldShowAd = (index + 1) % 5 === 0 && affiliateProducts.length > 0
              // 첫 번째 광고는 index=4일 때, 두 번째는 index=9일 때...
              const adProductIndex = Math.floor(index / 5) % affiliateProducts.length
              const adProduct = shouldShowAd ? affiliateProducts[adProductIndex] : null

              return (
                <Fragment key={recipe.id}>
                  <RecipeCard
                    recipe={recipe}
                    onClick={() => setSelectedRecipe(recipe)}
                    showDateBadge={showDateBadge}
                  />
                  {/* In-Feed 광고 삽입 (5:1 비율, 1x1 그리드 크기) */}
                  {shouldShowAd && adProduct && (
                    <AffiliateCard 
                      key={`ad-${adProduct.id}-${index}`}
                      product={adProduct}
                      inFeedMode={true}
                    />
                  )}
                </Fragment>
              )
            })}
          </div>
        )}

        {/* 법적 준수: 제휴 링크 공지 (레시피 리스트 최하단) */}
        {filteredRecipes.length > 0 && (
          <div className="mt-8 pt-6 border-t border-gray-200">
            <AffiliateDisclosure />
          </div>
        )}

        {/* Modal */}
        {selectedRecipe && (
          <RecipeModal
            recipe={selectedRecipe}
            onClose={() => setSelectedRecipe(null)}
          />
        )}
      </main>
    </div>
  )
}

// 마트별 브랜드 색상 매핑 (겹치지 않도록 조정)
function getStoreColors(storeName: string): {
  bg: string
  text: string
  border: string
} {
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
    'Coop': {
      bg: 'bg-amber-100',
      text: 'text-amber-800',
      border: 'border-amber-300',
    },
  }

  // 기본값 (알 수 없는 마트)
  return colorMap[storeName] || {
    bg: 'bg-gray-100',
    text: 'text-gray-800',
    border: 'border-gray-300',
  }
}

// Recipe Card Component
function RecipeCard({
  recipe,
  onClick,
  showDateBadge = false,
}: {
  recipe: Recipe
  onClick: () => void
  showDateBadge?: boolean
}) {
  const storeColors = getStoreColors(recipe.store)
  const dateBadge = showDateBadge ? getDateBadge(recipe) : null
  
  return (
    <div
      onClick={onClick}
      className="bg-white rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-shadow duration-200 cursor-pointer overflow-hidden group"
    >
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2 flex-wrap">
              <span className={`inline-flex items-center px-2.5 py-1 rounded-md text-xs font-semibold ${storeColors.bg} ${storeColors.text} border ${storeColors.border}`}>
                {recipe.store}
              </span>
              {dateBadge && dateBadge.type !== 'none' && (
                <span className={`inline-flex items-center px-2.5 py-1 rounded-md text-xs font-semibold ${
                  dateBadge.type === 'active' 
                    ? 'bg-red-50 text-red-600 border border-red-200' 
                    : 'bg-blue-50 text-blue-600 border border-blue-200'
                }`}>
                  {dateBadge.text}
                </span>
              )}
            </div>
            <h3 className="text-xl font-bold text-gray-900 group-hover:text-nl-orange-500 transition-colors">
              {recipe.menu_name}
            </h3>
          </div>
          <ChevronRight
            size={20}
            className="text-gray-400 group-hover:text-nl-orange-500 transition-colors flex-shrink-0 ml-2"
          />
        </div>

        {/* Description */}
        <p className="text-gray-600 text-sm mb-4 line-clamp-2">
          {recipe.description}
        </p>

        {/* Main Ingredients Badges */}
        <div className="flex flex-wrap gap-2 mb-4">
          {recipe.main_ingredients.slice(0, 3).map((ingredient, idx) => (
            <span
              key={idx}
              className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-nl-orange-100 text-nl-orange-700"
            >
              {ingredient}
            </span>
          ))}
          {recipe.main_ingredients.length > 3 && (
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
              +{recipe.main_ingredients.length - 3}
            </span>
          )}
        </div>

        {/* Tags & Cooking Time */}
        <div className="flex items-center justify-between pt-4 border-t border-gray-100">
          <div className="flex items-center gap-3">
            {recipe.tags.is_kid_friendly && (
              <div className="flex items-center gap-1 text-xs text-gray-600">
                <Baby size={14} />
                <span>아이식단</span>
              </div>
            )}
            {recipe.tags.is_spicy && (
              <div className="flex items-center gap-1 text-xs text-gray-600">
                <Flame size={14} />
                <span>매운맛</span>
              </div>
            )}
            {recipe.tags.is_vegetarian && (
              <div className="flex items-center gap-1 text-xs text-gray-600">
                <Leaf size={14} />
                <span>채식</span>
              </div>
            )}
            {recipe.tags.is_party_food && (
              <div className="flex items-center gap-1 text-xs text-gray-600">
                <PartyPopper size={14} />
                <span>파티</span>
              </div>
            )}
            {recipe.tags.is_alcohol_snack && (
              <div className="flex items-center gap-1 text-xs text-gray-600">
                <Beer size={14} />
                <span>안주</span>
              </div>
            )}
          </div>
          <div className="flex items-center gap-1 text-xs text-gray-500">
            <Clock size={14} />
            <span>{recipe.tags.cooking_time}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

// Recipe Modal Component
function RecipeModal({
  recipe,
  onClose,
}: {
  recipe: Recipe
  onClose: () => void
}) {
  const storeColors = getStoreColors(recipe.store)
  
  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div
          className="relative bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between z-10">
            <h2 className="text-2xl font-bold text-gray-900">{recipe.menu_name}</h2>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-full transition-colors"
            >
              <X size={24} className="text-gray-500" />
            </button>
          </div>

          {/* Content */}
          <div className="p-6 space-y-6">
            {/* Description */}
            <div>
              <p className="text-gray-700 leading-relaxed">{recipe.description}</p>
            </div>

            {/* Main Ingredients */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <ChefHat size={20} className="text-nl-orange-500" />
                세일 식재료
              </h3>
              <div className="flex flex-wrap gap-2">
                {recipe.main_ingredients.map((ingredient, idx) => (
                  <span
                    key={idx}
                    className="inline-flex items-center px-3 py-1.5 rounded-full text-sm font-medium bg-nl-orange-100 text-nl-orange-700"
                  >
                    {ingredient}
                  </span>
                ))}
              </div>
            </div>

            {/* Shopping List */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <ShoppingBag size={20} className="text-nl-orange-500" />
                쇼핑 리스트
              </h3>
              <ul className="space-y-2">
                {recipe.shopping_list.map((item, idx) => (
                  <li
                    key={idx}
                    className="flex items-center gap-3 text-gray-700"
                  >
                    <div className="w-2 h-2 rounded-full bg-nl-orange-500"></div>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Cost Saving Tip */}
            {recipe.cost_saving_tip && (
              <div className="bg-nl-orange-50 border border-nl-orange-200 rounded-lg p-4">
                <h3 className="text-sm font-semibold text-nl-orange-900 mb-2">
                  💡 절약 팁
                </h3>
                <p className="text-sm text-nl-orange-800">{recipe.cost_saving_tip}</p>
              </div>
            )}

            {/* Tags & Info */}
            <div className="flex flex-wrap items-center gap-4 pt-4 border-t border-gray-200">
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Clock size={16} />
                <span>조리 시간: {recipe.tags.cooking_time}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className={`inline-flex items-center px-2.5 py-1 rounded-md text-xs font-semibold ${storeColors.bg} ${storeColors.text} border ${storeColors.border}`}>
                  {recipe.store}
                </span>
              </div>
              <div className="flex items-center gap-3">
                {recipe.tags.is_kid_friendly && (
                  <div className="flex items-center gap-1 text-sm text-gray-600">
                    <Baby size={16} />
                    <span>아이식단</span>
                  </div>
                )}
                {recipe.tags.is_spicy && (
                  <div className="flex items-center gap-1 text-sm text-gray-600">
                    <Flame size={16} />
                    <span>매운맛</span>
                  </div>
                )}
                {recipe.tags.is_vegetarian && (
                  <div className="flex items-center gap-1 text-sm text-gray-600">
                    <Leaf size={16} />
                    <span>채식</span>
                  </div>
                )}
                {recipe.tags.is_party_food && (
                  <div className="flex items-center gap-1 text-sm text-gray-600">
                    <PartyPopper size={16} />
                    <span>파티</span>
                  </div>
                )}
                {recipe.tags.is_alcohol_snack && (
                  <div className="flex items-center gap-1 text-sm text-gray-600">
                    <Beer size={16} />
                    <span>안주</span>
                  </div>
                )}
              </div>
            </div>

            {/* 법적 준수: 제휴 링크 공지 (레시피 상세 모달 최하단) */}
            <div className="mt-6 pt-4 border-t border-gray-200">
              <AffiliateDisclosure />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
