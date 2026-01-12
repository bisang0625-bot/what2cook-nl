'use client'

import { useState, useEffect } from 'react'
import { ExternalLink, Truck, Shield, Star, Clock, CheckCircle } from 'lucide-react'
import Image from 'next/image'

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
  platforms: {
    bol?: PlatformData
    amazon?: PlatformData
  }
  category: string
  tags?: string[]
}

interface AffiliateBalancerProps {
  product: AffiliateProduct
  className?: string
}

/**
 * 지능형 제휴 마케팅 위젯
 * 
 * 전략:
 * 1. 버튼 위치 랜덤화로 위치 편향 제거
 * 2. 가격 외 구매 결정 요소 시각화 (배송, 신뢰도)
 * 3. 매력적인 마이크로 카피로 클릭 유도
 * 4. 사용자 고민을 유도하여 반드시 클릭하게 만드는 UI
 */
export default function AffiliateBalancer({
  product,
  className = ''
}: AffiliateBalancerProps) {
  const [buttonOrder, setButtonOrder] = useState<'bol-first' | 'amazon-first'>('bol-first')
  const [mounted, setMounted] = useState(false)

  const { bol, amazon } = product.platforms

  // 페이지 로드 시 버튼 순서 랜덤화
  useEffect(() => {
    setMounted(true)
    // 50% 확률로 순서 변경
    const random = Math.random()
    setButtonOrder(random < 0.5 ? 'bol-first' : 'amazon-first')
  }, [])

  // 클릭 트래킹 함수
  const trackClick = (platform: 'bol' | 'amazon', productId: string) => {
    console.log(`[Affiliate Click] Platform: ${platform}, Product: ${productId}`)
    
    // 추후 분석 도구 연동 가능
    if (typeof window !== 'undefined' && (window as any).gtag) {
      (window as any).gtag('event', 'affiliate_click', {
        platform: platform,
        product_id: productId,
        product_name: product.name
      })
    }
  }

  // USP 아이콘 매핑
  const getUSPIcon = (usp: string) => {
    switch (usp.toLowerCase()) {
      case '빠른 배송':
      case 'fast delivery':
        return <Truck className="w-4 h-4" />
      case '가격 경쟁력':
      case 'price':
        return <Star className="w-4 h-4" />
      case '신뢰도':
      case 'trust':
        return <Shield className="w-4 h-4" />
      default:
        return <CheckCircle className="w-4 h-4" />
    }
  }

  // 뱃지 색상 결정
  const getBadgeColor = (badge: string) => {
    if (badge.includes('최저가') || badge.includes('Laagste')) {
      return 'bg-green-500 text-white'
    }
    if (badge.includes('도착') || badge.includes('Morgen')) {
      return 'bg-blue-500 text-white'
    }
    if (badge.includes('Prime')) {
      return 'bg-orange-500 text-white'
    }
    return 'bg-gray-600 text-white'
  }

  // 마이크로 카피 생성
  const getMicroCopy = (platform: 'bol' | 'amazon', data: PlatformData) => {
    if (platform === 'bol') {
      if (data.badge.includes('내일 도착')) {
        return '내일 받고 싶다면'
      }
      if (data.benefit.includes('픽업')) {
        return '매장에서 직접 픽업'
      }
      return '가격 및 재고 확인'
    } else {
      if (data.badge.includes('최저가')) {
        return '최저가로 구매하기'
      }
      if (data.benefit.includes('Prime')) {
        return 'Prime 무료 배송 혜택'
      }
      return '리뷰 확인 후 구매'
    }
  }

  if (!mounted || (!bol && !amazon)) {
    return null
  }

  // 버튼 컴포넌트
  const BolButton = bol ? (
    <a
      href={bol.url}
      target="_blank"
      rel="nofollow sponsored noopener noreferrer"
      onClick={() => trackClick('bol', product.id)}
      className="
        relative flex-1
        bg-[#0000FF] text-white
        rounded-xl p-5
        hover:bg-[#0000CC]
        transition-all duration-200
        shadow-lg hover:shadow-xl
        transform hover:scale-[1.02]
        group
      "
    >
      {/* 뱃지 */}
      <div className={`absolute -top-2 left-4 ${getBadgeColor(bol.badge)} text-xs font-bold px-3 py-1 rounded-full shadow-md z-10`}>
        {bol.badge}
      </div>

      {/* 메인 콘텐츠 */}
      <div className="flex flex-col items-center text-center space-y-3 pt-2">
        {/* USP 아이콘 */}
        <div className="flex items-center gap-2 text-sm opacity-90">
          {getUSPIcon(bol.usp)}
          <span className="font-medium">{bol.usp}</span>
        </div>

        {/* 가격 */}
        <div className="text-2xl font-bold">{bol.price}</div>

        {/* 마이크로 카피 */}
        <div className="text-sm font-medium opacity-95 group-hover:opacity-100">
          {getMicroCopy('bol', bol)}
        </div>

        {/* 혜택 */}
        <div className="text-xs opacity-75 flex items-center gap-1">
          <Clock className="w-3 h-3" />
          <span>{bol.benefit}</span>
        </div>

        {/* 버튼 텍스트 */}
        <div className="mt-2 text-sm font-semibold border-t border-white/20 pt-3 w-full">
          Bol.com에서 보기
          <ExternalLink className="w-3 h-3 inline-block ml-1" />
        </div>
      </div>
    </a>
  ) : null

  const AmazonButton = amazon ? (
    <a
      href={amazon.url}
      target="_blank"
      rel="nofollow sponsored noopener noreferrer"
      onClick={() => trackClick('amazon', product.id)}
      className="
        relative flex-1
        bg-[#FF9900] text-black
        rounded-xl p-5
        hover:bg-[#FF8800]
        transition-all duration-200
        shadow-lg hover:shadow-xl
        transform hover:scale-[1.02]
        group
      "
    >
      {/* 뱃지 */}
      <div className={`absolute -top-2 left-4 ${getBadgeColor(amazon.badge)} text-xs font-bold px-3 py-1 rounded-full shadow-md z-10`}>
        {amazon.badge}
      </div>

      {/* 메인 콘텐츠 */}
      <div className="flex flex-col items-center text-center space-y-3 pt-2">
        {/* USP 아이콘 */}
        <div className="flex items-center gap-2 text-sm opacity-90">
          {getUSPIcon(amazon.usp)}
          <span className="font-medium">{amazon.usp}</span>
        </div>

        {/* 가격 */}
        <div className="text-2xl font-bold">{amazon.price}</div>

        {/* 마이크로 카피 */}
        <div className="text-sm font-medium opacity-95 group-hover:opacity-100">
          {getMicroCopy('amazon', amazon)}
        </div>

        {/* 혜택 */}
        <div className="text-xs opacity-75 flex items-center gap-1">
          <Shield className="w-3 h-3" />
          <span>{amazon.benefit}</span>
        </div>

        {/* 버튼 텍스트 */}
        <div className="mt-2 text-sm font-semibold border-t border-black/20 pt-3 w-full">
          Amazon에서 보기
          <ExternalLink className="w-3 h-3 inline-block ml-1" />
        </div>
      </div>
    </a>
  ) : null

  return (
    <div className={`affiliate-balancer bg-white rounded-2xl border-2 border-gray-200 overflow-hidden shadow-lg hover:shadow-xl transition-shadow ${className}`}>
      {/* 상품 이미지 */}
      <div className="relative w-full h-56 bg-gradient-to-br from-gray-100 to-gray-200">
        {product.image ? (
          <Image
            src={product.image}
            alt={product.name}
            fill
            className="object-cover"
            sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400">
            <div className="text-center">
              <div className="text-4xl mb-2">📦</div>
              <div className="text-sm">이미지 없음</div>
            </div>
          </div>
        )}
      </div>

      {/* 상품 정보 */}
      <div className="p-5">
        <h3 className="text-xl font-bold text-gray-900 mb-2 line-clamp-2">
          {product.name}
        </h3>
        {product.description && (
          <p className="text-sm text-gray-600 mb-5 line-clamp-2">
            {product.description}
          </p>
        )}

        {/* 고민 유도 문구 */}
        <div className="mb-5 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm text-blue-900 text-center font-medium">
            💭 가격은 아마존이 싼데, 배송은 볼닷컴이 빠르네? 어디서 살까?
          </p>
        </div>

        {/* 버튼 영역 (랜덤 순서) */}
        <div className="flex gap-3">
          {buttonOrder === 'bol-first' ? (
            <>
              {BolButton}
              {AmazonButton}
            </>
          ) : (
            <>
              {AmazonButton}
              {BolButton}
            </>
          )}
        </div>

        {/* 비교 안내 */}
        <div className="mt-4 text-center">
          <p className="text-xs text-gray-500">
            두 플랫폼의 가격과 배송 옵션을 비교해보세요
          </p>
        </div>
      </div>
    </div>
  )
}
