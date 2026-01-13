'use client'

import { ExternalLink } from 'lucide-react'
import Image from 'next/image'
import { useI18n } from '../i18n/I18nProvider'

interface AffiliateProduct {
  id: string
  platform: 'amazon' | 'bol'
  name: string
  name_en?: string
  name_nl?: string
  description: string
  description_en?: string
  description_nl?: string
  image: string
  url: string
  price: string
  currency: string
  badge?: string
  benefit?: string
  benefit_en?: string
  benefit_nl?: string
  category: string
  tags?: string[]
}

interface AffiliateCardProps {
  product: AffiliateProduct
  className?: string
  /** In-Feed 모드: 가격 숨기기 및 Blind UI 적용 */
  inFeedMode?: boolean
}

/**
 * 제휴 상품 비교 카드 컴포넌트
 * - RecipeCard와 동일한 크기 및 스타일 (1x1 그리드)
 * - Blind UI: 가격 숨기기로 호기심 유발
 * - 법적 준수: "Advertentie" 라벨 필수 표시
 * - 3:1 비율로 레시피 리스트에 자연스럽게 삽입
 */
export default function AffiliateCard({
  product,
  className = '',
  inFeedMode = true
}: AffiliateCardProps) {
  const { t, lang } = useI18n()
  const isAmazon = product.platform === 'amazon'
  const isBol = product.platform === 'bol'

  // 언어별 텍스트 가져오기
  const getLocalizedText = (field: 'name' | 'description' | 'benefit'): string => {
    if (lang === 'ko') {
      return product[field] || ''
    }
    if (lang === 'en') {
      const enField = `${field}_en` as keyof AffiliateProduct
      return (product[enField] as string) || product[field] || ''
    }
    if (lang === 'nl') {
      const nlField = `${field}_nl` as keyof AffiliateProduct
      return (product[nlField] as string) || product[field] || ''
    }
    return product[field] || ''
  }

  const productName = getLocalizedText('name')
  const productDescription = getLocalizedText('description')
  const productBenefit = getLocalizedText('benefit')

  // Badge 텍스트 결정 (Blind Strategy)
  const getBadge = () => {
    if (product.badge) {
      if (isBol && (product.badge.includes('내일 도착') || product.badge.includes('Morgen'))) {
        return 'Morgen in huis'
      }
      if (isAmazon && (product.badge.includes('최저가') || product.badge.includes('Best'))) {
        return 'Best Deal'
      }
      return product.badge
    }
    // 기본값
    return isBol ? 'Morgen in huis' : 'Best Deal'
  }

  // 플랫폼별 스타일 결정
  const getButtonStyles = () => {
    if (isAmazon) {
      return {
        bg: 'bg-[#FF9900]',
        hoverBg: 'hover:bg-[#FF8800]',
        textColor: 'text-black',
        badgeBg: 'bg-orange-500',
        icon: '📦',
        label: t('affiliateCard.button.amazon')
      }
    }
    if (isBol) {
      return {
        bg: 'bg-[#0000FF]',
        hoverBg: 'hover:bg-[#0000CC]',
        textColor: 'text-white',
        badgeBg: 'bg-blue-500',
        icon: '🇳🇱',
        label: t('affiliateCard.button.bol')
      }
    }
    // 기본값 (fallback)
    return {
      bg: 'bg-gray-500',
      hoverBg: 'hover:bg-gray-600',
      textColor: 'text-white',
      badgeBg: 'bg-gray-600',
      icon: '🔗',
      label: t('affiliateCard.button.link')
    }
  }

  const buttonStyles = getButtonStyles()

  return (
    <div 
      className={`
        affiliate-card 
        bg-slate-50 rounded-xl shadow-sm border border-gray-200 
        hover:shadow-md transition-shadow duration-200 
        overflow-hidden group
        ${className}
      `}
    >
      {/* 법적 준수: "Advertentie" 라벨 (우측 상단) */}
      <div className="absolute top-2 right-2 z-10 bg-white/90 text-gray-400 text-xs px-2 py-0.5 rounded shadow-sm">
        {t('ads.label')}
      </div>

      <div className="p-6">
        {/* 상품 이미지 - RecipeCard와 동일한 비율 */}
        <div className="relative w-full h-40 bg-gray-100 rounded-lg mb-4 overflow-hidden">
          {product.image ? (
            <Image
              src={product.image}
              alt={product.name}
              fill
              className="object-cover"
              sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
              loading="lazy"
              placeholder="blur"
              blurDataURL="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAAIAAoDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAhEAACAQMDBQAAAAAAAAAAAAABAgMABAUGIWGRkqGx0f/EABUBAQEAAAAAAAAAAAAAAAAAAAMF/8QAGhEAAgIDAAAAAAAAAAAAAAAAAAECEgMRkf/aAAwDAQACEQMRAD8AltJagyeH0AthI5xdrLcNM91BF5pX2HaH9bcfaSXWGaRmknyJckliyjqTzSlT54b6bk+h0R//2Q=="
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-gray-400">
              <div className="text-center">
                <div className="text-4xl mb-2">📦</div>
                <div className="text-sm">{t('affiliateCard.noImage')}</div>
              </div>
            </div>
          )}
        </div>

        {/* 상품 정보 */}
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
            {productName}
          </h3>
          {productDescription && (
            <p className="text-sm text-gray-600 line-clamp-2 mb-3">
              {productDescription}
            </p>
          )}
        </div>

        {/* Blind UI 버튼 (가격 숨김) */}
        <div className="space-y-2">
          {/* 플랫폼별 버튼 (단일 버튼) */}
          {product.url && (
            <a
              href={product.url}
              target="_blank"
              rel="nofollow sponsored noopener noreferrer"
              className={`
                relative block w-full ${buttonStyles.bg} ${buttonStyles.textColor}
                px-4 py-2.5 rounded-lg 
                font-medium text-sm
                ${buttonStyles.hoverBg}
                transition-colors duration-200
                flex items-center justify-between
                group/button
              `}
            >
              {/* 상단 뱃지 */}
              <div className={`absolute -top-2 left-3 ${buttonStyles.badgeBg} text-white text-xs font-bold px-2 py-0.5 rounded shadow-sm z-10`}>
                {getBadge()}
              </div>
              
              <div className="flex items-center gap-2">
                <span className="text-base">{buttonStyles.icon}</span>
                <span>{buttonStyles.label}</span>
              </div>
              <ExternalLink className="w-4 h-4 opacity-75 group-hover/button:opacity-100 group-hover/button:translate-x-0.5 transition-all" />
            </a>
          )}

          {/* URL이 없는 경우 */}
          {!product.url && (
            <div className="text-center py-4 text-gray-500 text-sm">
              {t('affiliateCard.noLink')}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
