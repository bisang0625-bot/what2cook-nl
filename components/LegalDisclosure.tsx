'use client'

import { Info, ExternalLink } from 'lucide-react'
import { useState } from 'react'
import { useI18n } from './i18n/I18nProvider'

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
  const { t } = useI18n()

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
            {t('legalDisclosure.title')}
          </h4>
          
          <div className="space-y-2 text-sm text-gray-700">
            <p>
              <strong>{t('legalDisclosure.section.affiliate')}:</strong> {t('legalDisclosure.body.affiliate')}
            </p>
            
            <p>
              <strong>{t('legalDisclosure.section.ads')}:</strong> {t('legalDisclosure.body.ads')}
            </p>
            
            <p>
              <strong>{t('legalDisclosure.section.data')}:</strong> {t('legalDisclosure.body.data')}{' '}
              <a 
                href="/privacy" 
                className="text-blue-600 hover:underline inline-flex items-center gap-1"
              >
                {t('legalDisclosure.privacyPolicy')}
                <ExternalLink className="w-3 h-3" />
              </a>
            </p>
          </div>

          <div className="mt-4 pt-3 border-t border-blue-200">
            <p className="text-xs text-gray-600">
              {t('legalDisclosure.footnote')}
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
          {t('legalDisclosure.title')}
        </span>
        <span className="text-xs text-gray-500">
          {isCollapsed ? t('common.expand') : t('common.collapse')}
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
