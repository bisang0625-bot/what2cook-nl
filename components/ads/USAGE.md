# 광고 및 제휴 컴포넌트 사용 가이드

## 📦 컴포넌트 목록

### 1. AdBanner (`components/ads/AdBanner.tsx`)

범용 광고 배너 컴포넌트. 구글 애드센스 또는 자체 이미지 배너를 지원합니다.

**법적 준수:**
- ✅ 우측 상단에 "Advertentie" 라벨 자동 표시 (반투명 배경)
- ✅ 자체 배너 링크에 `rel="nofollow sponsored noopener noreferrer"` 적용

**사용 예시:**

```tsx
import AdBanner from '@/components/ads/AdBanner'

// 구글 애드센스
<AdBanner
  type="adsense"
  adClient="ca-pub-XXXXXXXXXX"
  adSlot="XXXXXXXXXX"
  size="responsive"
/>

// 자체 이미지 배너
<AdBanner
  type="custom"
  imageUrl="/images/banners/custom.jpg"
  linkUrl="https://example.com"
  altText="커스텀 광고"
  size="banner"
/>
```

**Props:**
- `type`: `'adsense' | 'custom'` (필수)
- `adClient`: 애드센스 클라이언트 ID (adsense 타입)
- `adSlot`: 애드센스 슬롯 ID (adsense 타입)
- `imageUrl`: 이미지 URL (custom 타입)
- `linkUrl`: 링크 URL (custom 타입)
- `altText`: 이미지 alt 텍스트 (custom 타입)
- `size`: `'responsive' | 'banner' | 'rectangle'`
- `className`: 추가 CSS 클래스

---

### 2. AffiliateCard (`components/ads/AffiliateCard.tsx`)

제휴 상품 비교 카드. Bol.com과 Amazon.nl 가격을 비교합니다.

**법적 준수:**
- ✅ 모든 링크에 `rel="nofollow sponsored noopener noreferrer"` 필수 적용
- ✅ 최저가 뱃지 자동 표시

**사용 예시:**

```tsx
import AffiliateCard from '@/components/ads/AffiliateCard'

<AffiliateCard product={affiliateProduct} />
```

**UI 특징:**
- Bol.com 버튼: 파란색 배경 (#0000FF), 흰색 텍스트
- Amazon 버튼: 노란색 배경 (#FF9900), 검정색 텍스트
- 최저가 뱃지: "Laagste prijs (최저가)" - 녹색 배경

---

### 3. AffiliateDisclosure (`components/ads/AffiliateDisclosure.tsx`)

네덜란드/EU 규정 준수 제휴 링크 공지 컴포넌트.

**사용 예시:**

```tsx
import AffiliateDisclosure from '@/components/ads/AffiliateDisclosure'

// 페이지 최하단
<div className="mt-12 pt-8 border-t border-gray-200">
  <AffiliateDisclosure />
</div>
```

---

## 🔗 통합 페이지 예시

### `app/products/page.tsx`

```tsx
'use client'

import AdBanner from '@/components/ads/AdBanner'
import AffiliateCard from '@/components/ads/AffiliateCard'
import AffiliateDisclosure from '@/components/ads/AffiliateDisclosure'

export default function ProductsPage() {
  // ... 상품 데이터 로드

  return (
    <main>
      {/* 상단 광고 배너 */}
      <AdBanner type="custom" ... />

      {/* 제휴 상품 그리드 */}
      <div className="grid ...">
        {products.map(product => (
          <AffiliateCard key={product.id} product={product} />
        ))}
      </div>

      {/* 하단 광고 배너 */}
      <AdBanner type="adsense" ... />

      {/* 법적 공지 */}
      <AffiliateDisclosure />
    </main>
  )
}
```

---

## ⚖️ 법적 준수 체크리스트

### AdBanner
- [x] "Advertentie" 라벨 표시 (우측 상단)
- [x] 자체 배너 링크에 `rel="nofollow sponsored noopener noreferrer"`

### AffiliateCard
- [x] 모든 링크에 `rel="nofollow sponsored noopener noreferrer"`
- [x] `target="_blank"` 사용
- [x] 최저가 뱃지 표시

### AffiliateDisclosure
- [x] 네덜란드어/한국어 병기
- [x] 수수료 발생 가능성 명시
- [x] 페이지 최하단 배치

---

## 🎨 스타일 가이드

### Bol.com 버튼
- 배경색: `#0000FF` (파란색)
- 텍스트: 흰색
- 호버: `#0000CC`

### Amazon 버튼
- 배경색: `#FF9900` (노란색)
- 텍스트: 검정색
- 호버: `#FF8800`

### 최저가 뱃지
- 배경색: `bg-green-500`
- 텍스트: 흰색
- 위치: 버튼 위쪽 (-top-2)

---

## 📚 참고 자료

- [Google AdSense 정책](https://support.google.com/adsense/answer/48182)
- [네덜란드 소비자 보호법](https://www.rijksoverheid.nl/)
- [EU GDPR](https://gdpr.eu/)
- [FTC Disclosure Guidelines](https://www.ftc.gov/tips-advice/business-center/guidance/ftcs-endorsement-guides-what-people-are-asking)
