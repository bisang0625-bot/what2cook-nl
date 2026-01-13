'use client'

import { useEffect, useState } from 'react'
import AdBanner from '@/components/ads/AdBanner'
import AffiliateCard from '@/components/ads/AffiliateCard'
import AffiliateBalancer from '@/components/ads/AffiliateBalancer'
import AffiliateDisclosure from '@/components/ads/AffiliateDisclosure'
import LanguageSwitcher from '../../components/i18n/LanguageSwitcher'
import { useI18n } from '../../components/i18n/I18nProvider'

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

export default function ProductsPage() {
  const [products, setProducts] = useState<AffiliateProduct[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string>('')
  const [viewMode, setViewMode] = useState<'balancer' | 'card'>('balancer')
  const { t } = useI18n()

  useEffect(() => {
    const loadProducts = async () => {
      try {
        const module = await import('@/data/affiliate_products.json')
        const productsData = module.default as AffiliateProduct[]
        setProducts(productsData)
        setLoading(false)
      } catch (err) {
        console.error('Affiliate product load failed:', err)
        setError(t('products.error.generic'))
        setLoading(false)
      }
    }

    loadProducts()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mx-auto mb-4"></div>
          <p className="text-gray-600">{t('products.loading')}</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center text-red-600">
          <p className="text-xl mb-2">⚠️ {t('home.error.title')}</p>
          <p>{error}</p>
        </div>
      </div>
    )
  }

  // 모든 제품은 단일 플랫폼을 가짐 (platform: 'amazon' | 'bol')
  // AffiliateCard 컴포넌트가 새로운 구조를 지원하므로 모든 제품 사용 가능

  return (
    <main className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="mb-8 flex items-start justify-between gap-4">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">{t('products.title')}</h1>
            <p className="text-gray-600">{t('products.subtitle')}</p>
          </div>
          <LanguageSwitcher className="mt-1" />
        </div>

        {/* 뷰 모드 전환 버튼 */}
        <div className="mb-6 flex gap-2">
          <button
            onClick={() => setViewMode('balancer')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              viewMode === 'balancer'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            🎯 {t('products.viewMode.smart')}
          </button>
          <button
            onClick={() => setViewMode('card')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              viewMode === 'card'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            📋 {t('products.viewMode.cards')}
          </button>
        </div>

        {/* 상단 광고 배너 (Custom 모드 테스트) */}
        <div className="mb-8">
          <AdBanner
            type="custom"
            imageUrl="/images/banners/custom-banner.jpg"
            linkUrl="https://example.com"
            altText={t('products.bannerAlt.custom')}
            size="banner"
          />
        </div>

        {/* 제휴 상품 카드 그리드 */}
        {products.length > 0 && (
          <div className="mb-12">
            {viewMode === 'balancer' && (
              <>
                <h2 className="text-2xl font-bold text-gray-900 mb-4">
                  🎯 {t('products.section.smart.title')}
                </h2>
                <p className="text-sm text-gray-600 mb-6">
                  {t('products.section.smart.subtitle')}
                </p>
              </>
            )}
            {viewMode === 'card' && (
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                📋 {t('products.section.cards.title')}
              </h2>
            )}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {products.map((product) => (
                viewMode === 'balancer' ? (
                  <AffiliateBalancer
                    key={product.id}
                    product={product as any}
                  />
                ) : (
                  <AffiliateCard
                    key={product.id}
                    product={product}
                  />
                )
              ))}
            </div>
          </div>
        )}

        {/* 상품이 없는 경우 */}
        {products.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            <p className="text-lg mb-2">{t('products.empty.title')}</p>
            <p className="text-sm">{t('products.empty.subtitle')}</p>
          </div>
        )}

        {/* 법적 준수: 제휴 링크 공지 (페이지 최하단) */}
        <div className="mt-12 pt-8 border-t border-gray-200">
          <AffiliateDisclosure />
        </div>
      </div>
    </main>
  )
}
