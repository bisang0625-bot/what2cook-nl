'use client'

import { Info } from 'lucide-react'
import { useI18n } from '../i18n/I18nProvider'

interface AffiliateDisclosureProps {
  /** 추가 클래스명 */
  className?: string
  /** 아이콘 표시 여부 */
  showIcon?: boolean
  /** 컴팩트 모드 (더 작은 텍스트) */
  compact?: boolean
}

/**
 * 네덜란드/EU 규정 준수 제휴 링크 공지 컴포넌트
 * 
 * 법적 요구사항:
 * - 네덜란드 소비자 보호법 준수
 * - EU GDPR 규정 준수
 * - 제휴 링크 투명성 공지
 * 
 * 사용 위치:
 * - 레시피 상세 페이지 최하단
 * - 상품 리스트 최하단
 * - 제휴 링크가 포함된 모든 페이지
 */
export default function AffiliateDisclosure({
  className = '',
  showIcon = true,
  compact = false
}: AffiliateDisclosureProps) {
  const { t } = useI18n()

  return (
    <div className={`affiliate-disclosure ${className}`}>
      <div className={`
        flex items-start gap-2
        ${compact ? 'text-xs' : 'text-xs'}
        text-gray-500
        leading-relaxed
      `}>
        {showIcon && (
          <Info 
            className="w-4 h-4 text-gray-400 flex-shrink-0 mt-0.5" 
            aria-hidden="true"
          />
        )}
        <p className="flex-1">
          {t('affiliateDisclosure.text')}
        </p>
      </div>
    </div>
  )
}
