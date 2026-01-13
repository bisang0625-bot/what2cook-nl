'use client'

import { useState } from 'react'
import dynamic from 'next/dynamic'
import Tabs from './Tabs'
import { useI18n } from './i18n/I18nProvider'

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

interface RecipeSectionProps {
  currentRecipes: Recipe[]
  upcomingRecipes: Recipe[]
  affiliateProducts: AffiliateProduct[]
}

export default function RecipeSection({
  currentRecipes,
  upcomingRecipes,
  affiliateProducts
}: RecipeSectionProps) {
  const [activeTab, setActiveTab] = useState<'current' | 'upcoming'>('current')
  const { t } = useI18n()

  return (
    <section className="w-full bg-white py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* 섹션 헤더 */}
        <div className="mb-6">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            {t('home.section.mealIdeas.title')}
          </h2>
          <p className="text-sm text-gray-600">
            {t('home.section.mealIdeas.subtitle')}
          </p>
        </div>

        {/* 탭 */}
        <Tabs
          tabs={[
            {
              id: 'current',
              label: `📅 ${t('recipes.tab.thisWeek')} ${currentRecipes.length > 0 ? `(${currentRecipes.length})` : ''}`,
              content: (
                <div>
                  {currentRecipes.length > 0 ? (
                    <>
                      <div className="mb-4 text-sm text-gray-600">
                        {t('recipes.thisWeek.description')}
                      </div>
                      <Dashboard 
                        recipes={currentRecipes} 
                        showDateBadge={true}
                        affiliateProducts={affiliateProducts}
                      />
                    </>
                  ) : (
                    <div className="text-center py-12 text-gray-500">
                      <p className="text-lg mb-2">{t('recipes.thisWeek.empty.title')}</p>
                      <p className="text-sm">{t('recipes.thisWeek.empty.subtitle')}</p>
                    </div>
                  )}
                </div>
              ),
            },
            {
              id: 'upcoming',
              label: `🔜 ${t('recipes.tab.nextWeek')} ${upcomingRecipes.length > 0 ? `(${upcomingRecipes.length})` : ''}`,
              content: (
                <div>
                  {upcomingRecipes.length > 0 ? (
                    <>
                      <div className="mb-4 text-sm text-gray-600">
                        {t('recipes.nextWeek.description')}
                      </div>
                      <Dashboard 
                        recipes={upcomingRecipes} 
                        showDateBadge={true}
                        affiliateProducts={affiliateProducts}
                      />
                    </>
                  ) : (
                    <div className="text-center py-12 text-gray-500">
                      <p className="text-lg mb-2">{t('recipes.nextWeek.empty.title')}</p>
                      <p className="text-sm">{t('recipes.nextWeek.empty.subtitle')}</p>
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
    </section>
  )
}
