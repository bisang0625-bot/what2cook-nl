'use client'

import { useEffect, useState, useMemo } from 'react'
import Link from 'next/link'
import { ChefHat, Search, X } from 'lucide-react'
// 모든 컴포넌트와 데이터를 상대 경로(../../)로 변경하여 Vercel 빌드 에러 방지
import Tabs from '../../components/Tabs'
import DealsGrid from '../../components/DealsGrid'
import BottomNav from '../../components/BottomNav'
import StoreFilter from '../../components/StoreFilter'
import LanguageSwitcher from '../../components/i18n/LanguageSwitcher'
import { useI18n } from '../../components/i18n/I18nProvider'

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
  const [selectedStores, setSelectedStores] = useState<Set<string>>(new Set())
  const [selectAll, setSelectAll] = useState<boolean>(true)
  const [searchQuery, setSearchQuery] = useState<string>('')
  const { t, lang } = useI18n()

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true)
        
        // 1. 이번 주 세일 데이터 시도 (물리적 상대 경로 사용)
        try {
          const currentModule = await import('../../data/current_sales.json')
          const products = currentModule.default.products || currentModule.default
          setCurrentSales({ products: Array.isArray(products) ? products : [], week_type: 'current' })
        } catch (err) {
          try {
            // current_sales가 없을 경우 weekly_sales 시도
            const weeklyModule = await import('../../data/weekly_sales.json')
            const products = weeklyModule.default.products || weeklyModule.default
            setCurrentSales({ products: Array.isArray(products) ? products : [], week_type: 'current' })
          } catch (e) {
            console.warn('No weekly_sales.json found');
          }
        }

        // 2. 다음 주 세일 데이터 시도
        try {
          const nextModule = await import('../../data/next_sales.json')
          const products = nextModule.default.products || nextModule.default
          setNextSales({ products: Array.isArray(products) ? products : [], week_type: 'next' })
        } catch (err) {
          console.log('No next_sales.json found');
        }
      } catch (err) {
        console.error('Critical data loading error:', err)
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [])

  const categorizeProducts = (products: SaleProduct[]) => {
    const fruitKeywords = ['druiven', 'appel', 'banaan', 'fruit', 'aardbei', 'citroen', 'peer', 'mango', 'orange']
    const mainKeywords = ['kip', 'vlees', 'vis', 'rund', 'varken', 'gehakt', 'aardappel', 'kool', 'ui', 'wortel', 'egg']
    const subKeywords = ['knoflook', 'gember', 'olijf', 'zout', 'peper', 'melk', 'kaas']

    const main: SaleProduct[] = []
    const sub: SaleProduct[] = []
    const fruits: SaleProduct[] = []

    products.forEach(product => {
      const name = (product.product_name || product.name || '').toLowerCase()
      if (fruitKeywords.some(k => name.includes(k))) fruits.push(product)
      else if (mainKeywords.some(k => name.includes(k))) main.push(product)
      else if (subKeywords.some(k => name.includes(k))) sub.push(product)
      else main.push(product)
    })
    return { main, sub, fruits }
  }

  const filteredCurrent = useMemo(() => {
    let products = currentSales?.products || []
    
    // 마트 필터
    if (!selectAll) {
      products = products.filter(p => selectedStores.has(p.store || p.supermarket || ''))
    }
    
    // 검색 필터
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase().trim()
      products = products.filter(p => {
        const productName = (p.product_name || p.name || '').toLowerCase()
        const storeName = (p.store || p.supermarket || '').toLowerCase()
        return productName.includes(query) || storeName.includes(query)
      })
    }
    
    return products
  }, [currentSales, selectAll, selectedStores, searchQuery])

  const filteredNext = useMemo(() => {
    let products = nextSales?.products || []
    
    // 마트 필터
    if (!selectAll) {
      products = products.filter(p => selectedStores.has(p.store || p.supermarket || ''))
    }
    
    // 검색 필터
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase().trim()
      products = products.filter(p => {
        const productName = (p.product_name || p.name || '').toLowerCase()
        const storeName = (p.store || p.supermarket || '').toLowerCase()
        return productName.includes(query) || storeName.includes(query)
      })
    }
    
    return products
  }, [nextSales, selectAll, selectedStores, searchQuery])

  const categorizedCurrent = useMemo(() => categorizeProducts(filteredCurrent), [filteredCurrent])
  const categorizedNext = useMemo(() => categorizeProducts(filteredNext), [filteredNext])

  if (loading) return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500"></div>
    </div>
  )

  return (
    <main className="min-h-screen bg-gray-50 pb-20">
      <div className="bg-white border-b sticky top-0 z-40 px-4 py-4">
        <div className="flex items-center justify-between gap-4">
          <h1 className="text-xl font-bold text-gray-900">{t('home.title')}</h1>
          <LanguageSwitcher />
        </div>
      </div>

      <section className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold">{t('deals.title')}</h2>
            <p className="text-sm text-gray-600 mt-1">{t('deals.subtitle')}</p>
          </div>
          <Link href="/" className="flex items-center gap-2 px-3 py-1.5 border-2 border-orange-500 text-orange-600 rounded-lg text-sm font-bold">
            <ChefHat size={16} /> {t('deals.backToRecipes')}
          </Link>
        </div>

        {/* 검색 바 */}
        <div className="mb-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder={lang === 'ko' ? '상품명 또는 마트명 검색...' : lang === 'nl' ? 'Zoek op product of winkel...' : 'Search by product or store...'}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-10 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                <X size={18} />
              </button>
            )}
          </div>
        </div>

        <StoreFilter 
          products={activeTab === 'current' ? (currentSales?.products || []) : (nextSales?.products || [])}
          selectedStores={selectedStores}
          onStoreToggle={(name) => {
            setSelectAll(false)
            setSelectedStores(prev => {
              const next = new Set(prev)
              if (next.has(name)) next.delete(name); else next.add(name)
              return next
            })
          }}
          onSelectAll={() => { setSelectAll(true); setSelectedStores(new Set()) }}
          selectAll={selectAll}
        />

        <Tabs
          tabs={[
            {
              id: 'current',
              label: `📅 ${t('deals.tab.thisWeek')} (${filteredCurrent.length})`,
              content: (
                <div className="mt-6 space-y-8">
                  {categorizedCurrent.main.length > 0 && (
                    <DealsGrid products={categorizedCurrent.main} category="main" categoryLabel={t('deals.category.main')} />
                  )}
                  {categorizedCurrent.sub.length > 0 && (
                    <DealsGrid products={categorizedCurrent.sub} category="sub" categoryLabel={t('deals.category.sub')} />
                  )}
                  {categorizedCurrent.fruits.length > 0 && (
                    <DealsGrid products={categorizedCurrent.fruits} category="fruits" categoryLabel={t('deals.category.fruits')} />
                  )}
                </div>
              )
            },
            {
              id: 'next',
              label: `🔜 ${t('deals.tab.nextWeek')} (${filteredNext.length})`,
              content: (
                <div className="mt-6 space-y-8">
                  {filteredNext.length > 0 ? (
                    <>
                      {categorizedNext.main.length > 0 && (
                        <DealsGrid products={categorizedNext.main} category="main" categoryLabel={t('deals.category.main')} />
                      )}
                      {categorizedNext.fruits.length > 0 && (
                        <DealsGrid products={categorizedNext.fruits} category="fruits" categoryLabel={t('deals.category.fruits')} />
                      )}
                    </>
                  ) : (
                    <div className="text-center py-10 text-gray-500">{t('deals.nextWeek.empty')}</div>
                  )}
                </div>
              )
            }
          ]}
          activeTab={activeTab}
          onTabChange={(id) => setActiveTab(id as 'current' | 'next')}
        />
      </section>
      <BottomNav />
    </main>
  )
}
