'use client'

import AffiliateComparison from './AffiliateComparison'
import AffiliateDisclosure from './ads/AffiliateDisclosure'
import { ShoppingBag } from 'lucide-react'

interface AffiliateProduct {
  id: string
  name: string
  description: string
  image: string
  // 새로운 구조 (platforms)
  platforms?: {
    bol?: { url: string; price: string; currency: string; badge?: string; benefit?: string; usp?: string }
    amazon?: { url: string; price: string; currency: string; badge?: string; benefit?: string; usp?: string }
  }
  // 기존 구조 (하위 호환성)
  affiliate_links?: {
    bol?: { url: string; price: string; currency: string }
    amazon?: { url: string; price: string; currency: string }
  }
  category: string
  tags?: string[]
}

interface AffiliateProductGridProps {
  products: AffiliateProduct[]
  title?: string
  className?: string
}

/**
 * 제휴 상품 그리드 컴포넌트
 * - 여러 제휴 상품을 그리드 형태로 표시
 * - 카테고리별 필터링 가능
 */
export default function AffiliateProductGrid({
  products,
  title = '추천 상품',
  className = ''
}: AffiliateProductGridProps) {
  if (!products || products.length === 0) {
    return (
      <div className={`text-center py-8 text-gray-500 ${className}`}>
        <ShoppingBag className="w-12 h-12 mx-auto mb-3 text-gray-300" />
        <p>추천 상품이 없습니다.</p>
      </div>
    )
  }

  return (
    <section className={`affiliate-products ${className}`}>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">{title}</h2>
        <p className="text-sm text-gray-600">
          한식 요리에 필요한 추천 상품을 비교해보세요
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {products.map((product) => (
          <AffiliateComparison
            key={product.id}
            product={product}
          />
        ))}
      </div>

      {/* 법적 준수: 제휴 링크 공지 (상품 리스트 최하단) */}
      <div className="mt-8 pt-6 border-t border-gray-200">
        <AffiliateDisclosure />
      </div>
    </section>
  )
}
