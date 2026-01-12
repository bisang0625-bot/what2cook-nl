/**
 * 제휴 링크 유틸리티 함수
 * - 법적 준수 속성 자동 적용
 * - 링크 검증
 */

/**
 * 제휴 링크에 법적 준수 속성 추가
 * @param url 원본 URL
 * @returns 안전한 제휴 링크 속성 객체
 */
export function getAffiliateLinkProps(url: string) {
  return {
    href: url,
    target: '_blank',
    rel: 'nofollow sponsored', // SEO 및 법적 준수
    'aria-label': '제휴 링크 (새 창에서 열림)'
  }
}

/**
 * 제휴 링크가 유효한지 검증
 * @param url URL 문자열
 * @returns 유효성 여부
 */
export function isValidAffiliateLink(url: string | undefined): boolean {
  if (!url) return false
  
  try {
    const urlObj = new URL(url)
    // Bol.com 또는 Amazon.nl 도메인 확인
    return (
      urlObj.hostname.includes('bol.com') ||
      urlObj.hostname.includes('amazon.nl') ||
      urlObj.hostname.includes('partner.bol.com')
    )
  } catch {
    return false
  }
}

/**
 * 가격 문자열을 숫자로 변환
 * @param priceString 가격 문자열 (예: "€120.00")
 * @returns 숫자 값
 */
export function parsePrice(priceString: string): number {
  return parseFloat(priceString.replace(/[€,\s]/g, '')) || 0
}

/**
 * 두 가격 비교하여 더 저렴한 곳 반환
 * @param price1 첫 번째 가격
 * @param price2 두 번째 가격
 * @returns '1' | '2' | null (같으면 null)
 */
export function getCheaperPrice(
  price1: string | undefined,
  price2: string | undefined
): '1' | '2' | null {
  if (!price1 || !price2) return null
  
  const num1 = parsePrice(price1)
  const num2 = parsePrice(price2)
  
  if (num1 < num2) return '1'
  if (num2 < num1) return '2'
  return null
}
