'use client'

import { Info, ExternalLink } from 'lucide-react'
import { useState } from 'react'

interface LegalDisclosureProps {
  /** 표시 위치: 'footer' | 'sidebar' | 'inline' */
  position?: 'footer' | 'sidebar' | 'inline'
  /** 축소 가능 여부 */
  collapsible?: boolean
  /** 기본 축소 상태 */
  defaultCollapsed?: boolean
}

/**
 * 법적 준수 투명성 공지 컴포넌트
 * - 제휴 링크 수수료 발생 가능성 명시
 * - 광고 표시 안내
 * - GDPR 및 네덜란드 법률 준수
 */
export default function LegalDisclosure({
  position = 'footer',
  collapsible = true,
  defaultCollapsed = true
}: LegalDisclosureProps) {
  const [isCollapsed, setIsCollapsed] = useState(defaultCollapsed)

  const positionClasses = {
    footer: 'mt-8 pt-6 border-t border-gray-200',
    sidebar: 'sticky top-4',
    inline: 'my-6'
  }

  const content = (
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <div className="flex items-start gap-3">
        <Info className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <h4 className="font-semibold text-gray-900 mb-2">
            투명성 공지 (Transparency Disclosure)
          </h4>
          
          <div className="space-y-2 text-sm text-gray-700">
            <p>
              <strong>제휴 링크 (Affiliate Links):</strong> 본 사이트의 일부 링크는 
              제휴 프로그램을 통해 제공됩니다. 이러한 링크를 통해 구매하시면 
              저희가 소정의 수수료를 받을 수 있습니다. 이는 구매 가격에 영향을 
              주지 않으며, 서비스 운영 및 콘텐츠 제작에 도움이 됩니다.
            </p>
            
            <p>
              <strong>광고 (Advertisements):</strong> 본 사이트에는 구글 애드센스 및 
              기타 광고가 표시될 수 있습니다. 이러한 광고는 사용자의 관심사에 맞춰 
              자동으로 선택되며, 저희는 광고 내용에 대한 책임을 지지 않습니다.
            </p>
            
            <p>
              <strong>데이터 수집:</strong> 본 사이트는 쿠키를 사용하여 사용자 경험을 
              개선하고 광고를 맞춤화합니다. 자세한 내용은{' '}
              <a 
                href="/privacy" 
                className="text-blue-600 hover:underline inline-flex items-center gap-1"
              >
                개인정보처리방침
                <ExternalLink className="w-3 h-3" />
              </a>
              을 참조하세요.
            </p>
          </div>

          <div className="mt-4 pt-3 border-t border-blue-200">
            <p className="text-xs text-gray-600">
              본 공지는 네덜란드 소비자 보호법 및 GDPR을 준수합니다.
            </p>
          </div>
        </div>
      </div>
    </div>
  )

  if (!collapsible) {
    return (
      <div className={positionClasses[position]}>
        {content}
      </div>
    )
  }

  return (
    <div className={positionClasses[position]}>
      <button
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="w-full flex items-center justify-between p-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
      >
        <span className="text-sm font-medium text-gray-700 flex items-center gap-2">
          <Info className="w-4 h-4 text-blue-600" />
          투명성 공지 (Transparency Disclosure)
        </span>
        <span className="text-xs text-gray-500">
          {isCollapsed ? '펼치기' : '접기'}
        </span>
      </button>
      
      {!isCollapsed && (
        <div className="mt-2">
          {content}
        </div>
      )}
    </div>
  )
}
