'use client'

import { useEffect, useState, useMemo } from 'react'
import Link from 'next/link'
import { ChefHat } from 'lucide-react'
import Tabs from '../../components/Tabs'
import DealsGrid from '../../components/DealsGrid'
import BottomNav from '../../components/BottomNav'
import StoreFilter from '../../components/StoreFilter'

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

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true)
        // 이번 주 데이터 시도
        try {
          const currentModule = await import('../../data/current_sales.json')
          const products = currentModule.default.products || currentModule.default
          setCurrentSales({ products: Array.isArray(products) ? products : [], week_type: 'current' })
        } catch (err) {
          try {
            const weeklyModule = await import('../../data/weekly_sales.json')
            const products = weeklyModule.default.products || weeklyModule.default
            setCurrentSales({ products: Array.isArray(products) ? products : [], week_type: 'current' })
          } catch (e) {
            console.error('No current sales data found')
          }
        }

        // 다음 주 데이터 시도
        try {
          const nextModule = await import('../../data/next_sales.json')
          const products = nextModule.default.products || nextModule.default
          setNextSales({ products: Array.isArray(products) ? products : [], week_type: 'next' })
        } catch (err) {
          console.log('No next sales data found')
        }
      } catch (err) {
        console.error('Data loading error:', err)
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
    const products = currentSales?.products || []
    if (selectAll) return products
    return products.filter(p => selectedStores.has(p.store || p.supermarket || ''))
  }, [currentSales, selectAll, selectedStores])

  const filteredNext = useMemo(() => {
    const products = nextSales?.products || []
    if (selectAll) return products
    return products.filter(p => selectedStores.has(p.store || p.supermarket || ''))
  }, [nextSales, selectAll, selectedStores])

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
        <h1 className="text-xl font-bold text-gray-900">뭐해먹지 NL <span className="text-sm text-gray-400 font-normal">What2Cook NL</span></h1>
      </div>

      <section className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold">세일리스트</h2>
          <Link href="/" className="flex items-center gap-2 px-3 py-1.5 border-2 border-orange-500 text-orange-600 rounded-lg text-sm font-bold">
            <ChefHat size={16} /> 추천식단
          </Link>
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
              label: `📅 이번 주 (${filteredCurrent.length})`,
              content: (
                <div className="mt-6 space-y-8">
                  {categorizedCurrent.main.length > 0 && <DealsGrid products={categorizedCurrent.main} categoryLabel="🥩 주재료 (고기, 채소)" />}
                  {categorizedCurrent.sub.length > 0 && <DealsGrid products={categorizedCurrent.sub} categoryLabel="🧂 부재료 및 양념" />}
                  {categorizedCurrent.fruits.length > 0 && <DealsGrid products={categorizedCurrent.fruits} categoryLabel="🍎 과일 및 후식" />}
                </div>
              )
            },
            {
              id: 'next',
              label: `🔜 다음 주 (${filteredNext.length})`,
              content: (
                <div className="mt-6 space-y-8">
                  {filteredNext.length > 0 ? (
                    <>
                      {categorizedNext.main.length > 0 && <DealsGrid products={categorizedNext.main} categoryLabel="🥩 주재료 (고기, 채소)" />}
                      {categorizedNext.fruits.length > 0 && <DealsGrid products={categorizedNext.fruits} categoryLabel="🍎 과일 및 후식" />}
                    </>
                  ) : (
                    <div className="text-center py-10 text-gray-500">다음 주 세일 정보 준비 중입니다.</div>
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
