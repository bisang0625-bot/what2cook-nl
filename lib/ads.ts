/**
 * 광고 시스템 설정 및 유틸리티
 */

export interface AdConfig {
  /** 구글 애드센스 클라이언트 ID */
  adsenseClientId?: string
  /** 광고 타입 기본값 */
  defaultAdType: 'adsense' | 'custom'
  /** 자체 배너 활성화 여부 */
  enableCustomBanners: boolean
}

/**
 * 환경 변수에서 광고 설정 로드
 */
export function getAdConfig(): AdConfig {
  return {
    adsenseClientId: process.env.NEXT_PUBLIC_ADSENSE_CLIENT_ID,
    defaultAdType: (process.env.NEXT_PUBLIC_AD_TYPE as 'adsense' | 'custom') || 'adsense',
    enableCustomBanners: process.env.NEXT_PUBLIC_ENABLE_CUSTOM_BANNERS === 'true'
  }
}

/**
 * 광고 슬롯 ID 생성
 * @param position 광고 위치
 * @returns 슬롯 ID
 */
export function generateAdSlotId(position: string): string {
  return `ad-slot-${position}-${Date.now()}`
}
