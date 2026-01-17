'use client'

import { useState } from 'react'
import dynamic from 'next/dynamic'
import { Info } from 'lucide-react'
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
  const { t } = useI18n()

  return (
    <Tabs
      tabs={[
        {
          id: 'current',
          label: `📅 ${t('recipes.tab.thisWeek')} ${currentRecipes.length > 0 ? `(${currentRecipes.length})` : ''}`,
          content: (
            <div>
              {/* 업데이트 일정 안내 */}
              <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-start gap-3">
                  <Info className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                  <div className="flex-1">
                    <h3 className="font-semibold text-blue-900 mb-2 text-sm">
                      {t('recipes.updateSchedule.title')}
                    </h3>
                    <p className="text-sm text-blue-800 mb-1">
                      {t('recipes.updateSchedule.thisWeek')}
                    </p>
                    <p className="text-xs text-blue-700 mt-2">
                      {t('recipes.updateSchedule.note')}
                    </p>
                  </div>
                </div>
              </div>

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
              {/* 업데이트 일정 안내 */}
              <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-start gap-3">
                  <Info className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
                  <div className="flex-1">
                    <h3 className="font-semibold text-green-900 mb-2 text-sm">
                      {t('recipes.updateSchedule.title')}
                    </h3>
                    <p className="text-sm text-green-800 mb-1">
                      {t('recipes.updateSchedule.nextWeek')}
                    </p>
                    <p className="text-xs text-green-700 mt-2">
                      {t('recipes.updateSchedule.note')}
                    </p>
                  </div>
                </div>
              </div>

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
  )
}
