'use client'

import { useEffect, useState } from 'react'
import Script from 'next/script'
import Link from 'next/link'
import Image from 'next/image'
import { useI18n } from '../i18n/I18nProvider'

interface AdBannerProps {
  /** 광고 타입: 'adsense' | 'custom' */
  type: 'adsense' | 'custom'
  /** 애드센스 클라이언트 ID (adsense 타입일 때) */
  adClient?: string
  /** 애드센스 슬롯 ID (adsense 타입일 때) */
  adSlot?: string
  /** 자체 배너 이미지 URL (custom 타입일 때) */
  imageUrl?: string
  /** 자체 배너 링크 URL (custom 타입일 때) */
  linkUrl?: string
  /** 자체 배너 alt 텍스트 (custom 타입일 때) */
  altText?: string
  /** 배너 크기 */
  size?: 'responsive' | 'banner' | 'rectangle'
  /** 추가 클래스명 */
  className?: string
}

/**
 * 범용 광고 배너 컴포넌트
 * - 구글 애드센스 또는 자체 이미지 배너 지원
 * - 법적 준수: "Advertentie" 라벨 필수 표시
 */
export default function AdBanner({
  type,
  adClient,
  adSlot,
  imageUrl,
  linkUrl,
  altText,
  size = 'responsive',
  className = ''
}: AdBannerProps) {
  const [mounted, setMounted] = useState(false)
  const [adsenseLoaded, setAdsenseLoaded] = useState(false)
  const { t } = useI18n()

  useEffect(() => {
    setMounted(true)
  }, [])

  // 크기별 스타일
  const sizeStyles = {
    responsive: 'w-full',
    banner: 'w-full h-[90px]',
    rectangle: 'w-full max-w-[300px] h-[250px]'
  }

  if (!mounted) {
    return null
  }

  return (
    <div className={`ad-banner relative ${sizeStyles[size]} ${className}`}>
      {/* 법적 준수: "Advertentie" 라벨 (우측 상단, 반투명 배경) */}
      <div className="absolute top-2 right-2 z-10 bg-black/70 text-white text-xs px-2 py-1 rounded backdrop-blur-sm">
        {t('ads.label')}
      </div>

      {type === 'adsense' ? (
        <>
          {/* 구글 애드센스 스크립트 로드 */}
          <Script
            src={`https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=${adClient || 'ca-pub-XXXXXXXXXX'}`}
            strategy="afterInteractive"
            crossOrigin="anonymous"
            onLoad={() => setAdsenseLoaded(true)}
          />
          
          {/* 애드센스 광고 단위 */}
          <ins
            className="adsbygoogle"
            style={{ display: 'block' }}
            data-ad-client={adClient || 'ca-pub-XXXXXXXXXX'}
            data-ad-slot={adSlot || 'XXXXXXXXXX'}
            data-ad-format={size === 'responsive' ? 'auto' : 'rectangle'}
            data-full-width-responsive={size === 'responsive' ? 'true' : 'false'}
          />
          
          {/* 애드센스 초기화 스크립트 */}
          {adsenseLoaded && (
            <Script id={`adsense-init-${adSlot}`} strategy="afterInteractive">
              {`
                (adsbygoogle = window.adsbygoogle || []).push({});
              `}
            </Script>
          )}
        </>
      ) : (
        /* 자체 이미지 배너 */
        <Link
          href={linkUrl || '#'}
          target="_blank"
          rel="nofollow sponsored noopener noreferrer"
          className="block w-full h-full relative"
        >
          {imageUrl ? (
            <Image
              src={imageUrl}
              alt={altText || t('ads.bannerAlt')}
              fill
              className="object-cover rounded"
              sizes="(max-width: 768px) 100vw, (max-width: 1200px) 728px, 728px"
              loading="lazy"
            />
          ) : (
            <div className="w-full h-full bg-gray-200 flex items-center justify-center text-gray-400 text-sm rounded">
              {t('ads.bannerPlaceholder')}
            </div>
          )}
        </Link>
      )}
    </div>
  )
}
