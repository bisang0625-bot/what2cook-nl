'use client'

import { useState, useEffect } from 'react'
import { useI18n } from './i18n/I18nProvider'

interface AdSlotProps {
  /** 광고 슬롯 ID (고유 식별자) */
  slotId: string
  /** 광고 타입: 'adsense' | 'custom' */
  adType?: 'adsense' | 'custom'
  /** 자체 배너 이미지 URL (custom 타입일 때) */
  customImageUrl?: string
  /** 자체 배너 링크 (custom 타입일 때) */
  customLinkUrl?: string
  /** 광고 크기 (기본값: 'responsive') */
  size?: 'responsive' | 'rectangle' | 'banner'
  /** 클래스명 */
  className?: string
}

/**
 * 하이브리드 광고 슬롯 컴포넌트
 * - 구글 애드센스와 자체 배너를 전환 가능
 * - 법적 준수: '광고(Advertentie)' 라벨링 포함
 */
export default function AdSlot({
  slotId,
  adType = 'adsense',
  customImageUrl,
  customLinkUrl,
  size = 'responsive',
  className = ''
}: AdSlotProps) {
  const [mounted, setMounted] = useState(false)
  const [adSenseLoaded, setAdSenseLoaded] = useState(false)
  const { t } = useI18n()

  useEffect(() => {
    setMounted(true)
    
    // 구글 애드센스 스크립트 로드
    if (adType === 'adsense') {
      const script = document.createElement('script')
      script.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXX'
      script.async = true
      script.crossOrigin = 'anonymous'
      script.onload = () => setAdSenseLoaded(true)
      document.head.appendChild(script)

      return () => {
        // Cleanup
        const existingScript = document.querySelector('script[src*="adsbygoogle"]')
        if (existingScript) {
          existingScript.remove()
        }
      }
    }
  }, [adType])

  useEffect(() => {
    // 애드센스 광고 초기화
    if (adType === 'adsense' && adSenseLoaded && mounted) {
      try {
        ((window as any).adsbygoogle = (window as any).adsbygoogle || []).push({})
      } catch (e) {
        console.error('AdSense initialization error:', e)
      }
    }
  }, [adType, adSenseLoaded, mounted])

  if (!mounted) {
    return null
  }

  const sizeClasses = {
    responsive: 'w-full',
    rectangle: 'w-full max-w-[300px] h-[250px]',
    banner: 'w-full h-[90px]'
  }

  return (
    <div className={`ad-slot ${className}`}>
      {/* 법적 준수: 광고 라벨 */}
      <div className="text-xs text-gray-500 mb-1 flex items-center gap-1">
        <span className="bg-gray-100 px-2 py-0.5 rounded">{t('ads.label')}</span>
      </div>

      {/* 광고 컨텐츠 */}
      <div className={`${sizeClasses[size]} bg-gray-50 border border-gray-200 rounded-lg overflow-hidden`}>
        {adType === 'adsense' ? (
          <ins
            className="adsbygoogle"
            style={{ display: 'block' }}
            data-ad-client="ca-pub-XXXXXXXXXX"
            data-ad-slot={slotId}
            data-ad-format={size === 'responsive' ? 'auto' : 'rectangle'}
            data-full-width-responsive={size === 'responsive' ? 'true' : 'false'}
          />
        ) : (
          <a
            href={customLinkUrl || '#'}
            target="_blank"
            rel="nofollow sponsored"
            className="block w-full h-full"
          >
            {customImageUrl ? (
              <img
                src={customImageUrl}
                alt={t('ads.bannerAlt')}
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-gray-400 text-sm">
                {t('ads.bannerPlaceholder')}
              </div>
            )}
          </a>
        )}
      </div>
    </div>
  )
}
