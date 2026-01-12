'use client'

import { ExternalLink, ShoppingBag, TrendingDown } from 'lucide-react'

interface AffiliateLink {
  url: string
  price: string
  currency: string
}

interface PlatformData {
  url: string
  price: string
  currency: string
  badge?: string
  benefit?: string
  usp?: string
}

interface AffiliateProduct {
  id: string
  name: string
  description: string
  image: string
  // 새로운 구조 (platforms)
  platforms?: {
    bol?: PlatformData
    amazon?: PlatformData
  }
  // 기존 구조 (하위 호환성)
  affiliate_links?: {
    bol?: AffiliateLink
    amazon?: AffiliateLink
  }
  category: string
  tags?: string[]
}

interface AffiliateComparisonProps {
  product: AffiliateProduct
  className?: string
}

/**
 * 제휴 링크 비교 컴포넌트
 * - Bol.com과 Amazon.nl 가격 비교
 * - 법적 준수: rel="nofollow sponsored" 자동 적용
 * - 투명성 공지 포함
 * - platforms와 affiliate_links 두 구조 모두 지원
 */
export default function AffiliateComparison({
  product,
  className = ''
}: AffiliateComparisonProps) {
  // 새로운 구조(platforms) 또는 기존 구조(affiliate_links) 지원
  const bol = product.platforms?.bol || product.affiliate_links?.bol
  const amazon = product.platforms?.amazon || product.affiliate_links?.amazon

  // 가격 비교 (더 저렴한 곳 찾기)
  const getCheaperStore = () => {
    if (!bol || !amazon) return null
    
    const bolPrice = parseFloat(bol.price.replace(/[€,\s]/g, ''))
    const amazonPrice = parseFloat(amazon.price.replace(/[€,\s]/g, ''))
    
    if (bolPrice < amazonPrice) return 'bol'
    if (amazonPrice < bolPrice) return 'amazon'
    return null
  }

  const cheaperStore = getCheaperStore()

  return (
    <div className={`affiliate-comparison bg-white rounded-lg border border-gray-200 p-4 ${className}`}>
      {/* 제품 정보 */}
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-1">{product.name}</h3>
        {product.description && (
          <p className="text-sm text-gray-600">{product.description}</p>
        )}
      </div>

      {/* 가격 비교 */}
      <div className="space-y-3">
        {/* Bol.com */}
        {bol && (
          <a
            href={bol.url}
            target="_blank"
            rel="nofollow sponsored noopener noreferrer"
            className={`
              block p-3 rounded-lg border-2 transition-all
              ${cheaperStore === 'bol' 
                ? 'border-green-500 bg-green-50' 
                : 'border-gray-200 hover:border-gray-300'
              }
            `}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <ShoppingBag className="w-5 h-5 text-blue-600" />
                <span className="font-medium text-gray-900">Bol.com</span>
                {cheaperStore === 'bol' && (
                  <span className="flex items-center gap-1 text-xs text-green-600 bg-green-100 px-2 py-0.5 rounded">
                    <TrendingDown className="w-3 h-3" />
                    최저가
                  </span>
                )}
              </div>
              <div className="flex items-center gap-2">
                <span className="text-lg font-bold text-gray-900">{bol.price}</span>
                <ExternalLink className="w-4 h-4 text-gray-400" />
              </div>
            </div>
          </a>
        )}

        {/* Amazon.nl */}
        {amazon && (
          <a
            href={amazon.url}
            target="_blank"
            rel="nofollow sponsored noopener noreferrer"
            className={`
              block p-3 rounded-lg border-2 transition-all
              ${cheaperStore === 'amazon' 
                ? 'border-green-500 bg-green-50' 
                : 'border-gray-200 hover:border-gray-300'
              }
            `}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <ShoppingBag className="w-5 h-5 text-orange-600" />
                <span className="font-medium text-gray-900">Amazon.nl</span>
                {cheaperStore === 'amazon' && (
                  <span className="flex items-center gap-1 text-xs text-green-600 bg-green-100 px-2 py-0.5 rounded">
                    <TrendingDown className="w-3 h-3" />
                    최저가
                  </span>
                )}
              </div>
              <div className="flex items-center gap-2">
                <span className="text-lg font-bold text-gray-900">{amazon.price}</span>
                <ExternalLink className="w-4 h-4 text-gray-400" />
              </div>
            </div>
          </a>
        )}

        {/* 둘 다 없는 경우 */}
        {!bol && !amazon && (
          <div className="text-center py-4 text-gray-500 text-sm">
            제휴 링크 정보가 없습니다.
          </div>
        )}
      </div>

      {/* 법적 준수: 투명성 공지 */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <p className="text-xs text-gray-500 leading-relaxed">
          <strong className="text-gray-700">투명성 공지:</strong> 위 링크를 통해 구매하시면 
          저희가 소정의 수수료를 받을 수 있습니다. 이는 서비스 운영에 도움이 되며, 
          구매 가격에는 영향을 주지 않습니다.
        </p>
      </div>
    </div>
  )
}
