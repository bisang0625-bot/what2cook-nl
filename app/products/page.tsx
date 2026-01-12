'use client'

import { useEffect, useState } from 'react'
import AdBanner from '@/components/ads/AdBanner'
import AffiliateCard from '@/components/ads/AffiliateCard'
import AffiliateBalancer from '@/components/ads/AffiliateBalancer'
import AffiliateDisclosure from '@/components/ads/AffiliateDisclosure'

interface PlatformData {
  url: string
  price: string
  currency: string
  badge: string
  benefit: string
  usp: string
}

interface AffiliateProduct {
  id: string
  name: string
  description: string
  image: string
  platforms?: {
    bol?: PlatformData
    amazon?: PlatformData
  }
  // 하위 호환성을 위한 기존 구조
  affiliate_links?: {
    bol?: { url: string; price: string; currency: string }
    amazon?: { url: string; price: string; currency: string }
  }
  category: string
  tags?: string[]
}

export default function ProductsPage() {
  const [products, setProducts] = useState<AffiliateProduct[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string>('')
  const [viewMode, setViewMode] = useState<'balancer' | 'card'>('balancer')

  useEffect(() => {
    const loadProducts = async () => {
      try {
        const module = await import('@/data/affiliate_products.json')
        const productsData = module.default as AffiliateProduct[]
        setProducts(productsData)
        setLoading(false)
      } catch (err) {
        console.error('제휴 상품 데이터 로드 실패:', err)
        setError('제휴 상품 데이터를 불러올 수 없습니다.')
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
          <p className="text-gray-600">상품 로딩 중...</p>
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

  // 새로운 platforms 구조를 가진 상품 필터링
  const balancerProducts = products.filter(p => p.platforms)
  const cardProducts = products.filter(p => !p.platforms && p.affiliate_links)

  return (
    <main className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">뭐해먹지 NL 추천 상품</h1>
          <p className="text-gray-600">한식 요리에 필요한 추천 상품을 비교해보세요</p>
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
            🎯 지능형 비교 (Balancer)
          </button>
          <button
            onClick={() => setViewMode('card')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              viewMode === 'card'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            📋 기본 카드 (Card)
          </button>
        </div>

        {/* 상단 광고 배너 (Custom 모드 테스트) */}
        <div className="mb-8">
          <AdBanner
            type="custom"
            imageUrl="/images/banners/custom-banner.jpg"
            linkUrl="https://example.com"
            altText="커스텀 광고 배너"
            size="banner"
          />
        </div>

        {/* 지능형 제휴 마케팅 위젯 (Balancer) */}
        {viewMode === 'balancer' && balancerProducts.length > 0 && (
          <div className="mb-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              🎯 지능형 가격 비교
            </h2>
            <p className="text-sm text-gray-600 mb-6">
              가격, 배송, 신뢰도를 종합적으로 비교해보세요. 버튼 위치는 매번 랜덤하게 배치됩니다.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {balancerProducts.map((product) => (
                <AffiliateBalancer
                  key={product.id}
                  product={product as any}
                />
              ))}
            </div>
          </div>
        )}

        {/* 기본 제휴 상품 카드 */}
        {viewMode === 'card' && cardProducts.length > 0 && (
          <div className="mb-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              📋 기본 상품 카드
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {cardProducts.map((product) => (
                <AffiliateCard
                  key={product.id}
                  product={product as any}
                />
              ))}
            </div>
          </div>
        )}

        {/* 상품이 없는 경우 */}
        {products.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            <p className="text-lg mb-2">추천 상품이 없습니다</p>
            <p className="text-sm">곧 추가될 예정입니다.</p>
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
