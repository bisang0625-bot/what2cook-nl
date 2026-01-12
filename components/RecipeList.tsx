'use client'

import { useState } from 'react'
import dynamic from 'next/dynamic'
import Tabs from './Tabs'

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

interface RecipeListProps {
  currentRecipes: Recipe[]
  upcomingRecipes: Recipe[]
  affiliateProducts: AffiliateProduct[]
}

export default function RecipeList({
  currentRecipes,
  upcomingRecipes,
  affiliateProducts
}: RecipeListProps) {
  const [activeTab, setActiveTab] = useState<'current' | 'upcoming'>('current')

  return (
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
  )
}
