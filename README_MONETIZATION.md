# 수익화 시스템 가이드

K-Bonus 프로젝트의 하이브리드 수익화 시스템 사용 가이드입니다.

## 📋 개요

본 프로젝트는 다음 수익화 방식을 지원합니다:

1. **구글 애드센스 (Google AdSense)**: 자동 광고 배치
2. **제휴 링크 (Affiliate Links)**: Bol.com, Amazon.nl 제휴 프로그램
3. **자체 배너 (Custom Banners)**: 직접 광고 배너

## 🔧 설정 방법

### 1. 환경 변수 설정

`.env.local` 파일을 생성하고 다음 변수를 설정하세요:

```bash
# Google AdSense
NEXT_PUBLIC_ADSENSE_CLIENT_ID=ca-pub-XXXXXXXXXX

# 광고 타입
NEXT_PUBLIC_AD_TYPE=adsense  # 또는 'custom'

# 자체 배너 활성화
NEXT_PUBLIC_ENABLE_CUSTOM_BANNERS=false
```

### 2. 구글 애드센스 설정

1. [Google AdSense](https://www.google.com/adsense/)에 가입
2. 사이트 승인 대기
3. 광고 단위 생성
4. `NEXT_PUBLIC_ADSENSE_CLIENT_ID`에 클라이언트 ID 입력
5. `components/AdSlot.tsx`의 `data-ad-slot` 값 업데이트

### 3. 제휴 상품 추가

`data/affiliate_products.json` 파일에 제휴 상품을 추가하세요:

```json
{
  "id": "product-id",
  "name": "상품명",
  "description": "상품 설명",
  "image": "/images/products/image.jpg",
  "affiliate_links": {
    "bol": {
      "url": "https://partner.bol.com/...",
      "price": "€120.00",
      "currency": "EUR"
    },
    "amazon": {
      "url": "https://amazon.nl/dp/...?tag=kbonus-21",
      "price": "€115.99",
      "currency": "EUR"
    }
  },
  "category": "kitchen",
  "tags": ["한식", "필수템"]
}
```

## 📦 컴포넌트 사용법

### AdSlot (광고 슬롯)

```tsx
import AdSlot from '@/components/AdSlot'

// 구글 애드센스
<AdSlot 
  slotId="header-banner"
  adType="adsense"
  size="banner"
/>

// 자체 배너
<AdSlot 
  slotId="custom-banner"
  adType="custom"
  customImageUrl="/images/banners/custom.jpg"
  customLinkUrl="https://example.com"
  size="rectangle"
/>
```

### AffiliateComparison (제휴 링크 비교)

```tsx
import AffiliateComparison from '@/components/AffiliateComparison'

<AffiliateComparison 
  product={affiliateProduct}
/>
```

### AffiliateProductGrid (제휴 상품 그리드)

```tsx
import AffiliateProductGrid from '@/components/AffiliateProductGrid'

<AffiliateProductGrid 
  products={affiliateProducts}
  title="추천 상품"
/>
```

### LegalDisclosure (법적 공지)

```tsx
import LegalDisclosure from '@/components/LegalDisclosure'

<LegalDisclosure 
  position="footer"
  collapsible={true}
  defaultCollapsed={true}
/>
```

## ⚖️ 법적 준수 사항

### 자동 적용되는 법적 준수 기능

1. **제휴 링크 속성**
   - 모든 제휴 링크에 `rel="nofollow sponsored"` 자동 적용
   - SEO 및 검색 엔진 정책 준수

2. **광고 라벨링**
   - 모든 광고 영역에 "광고 (Advertentie)" 라벨 표시
   - 사용자에게 명확한 광고 표시

3. **투명성 공지**
   - 제휴 링크 수수료 발생 가능성 명시
   - GDPR 및 네덜란드 법률 준수

### 수동 확인 사항

1. **개인정보처리방침**
   - `/privacy` 페이지 생성 필요
   - 쿠키 사용 및 데이터 수집 정책 명시

2. **이용약관**
   - `/terms` 페이지 생성 권장
   - 제휴 링크 및 광고 관련 약관 포함

3. **제휴 프로그램 약관**
   - Bol.com, Amazon.nl 제휴 프로그램 약관 준수
   - 각 플랫폼의 요구사항 확인

## 📊 모니터링

### 제휴 링크 클릭 추적

제휴 링크 클릭을 추적하려면 `components/AffiliateComparison.tsx`에 분석 코드를 추가하세요:

```tsx
const handleAffiliateClick = (store: string, productId: string) => {
  // Google Analytics 또는 기타 분석 도구
  gtag('event', 'affiliate_click', {
    store: store,
    product_id: productId
  })
}
```

### 광고 성과 추적

구글 애드센스 대시보드에서 다음 지표를 확인하세요:
- 페이지뷰당 수익 (RPM)
- 클릭률 (CTR)
- 수익

## 🔒 보안 고려사항

1. **환경 변수 보호**
   - `.env.local`은 Git에 커밋하지 마세요
   - `.gitignore`에 포함되어 있는지 확인

2. **제휴 링크 검증**
   - `lib/affiliate.ts`의 `isValidAffiliateLink()` 함수 사용
   - 유효하지 않은 링크는 표시하지 않음

3. **XSS 방지**
   - 사용자 입력은 항상 sanitize
   - React의 기본 XSS 방지 기능 활용

## 🚀 배포 전 체크리스트

- [ ] `.env.local` 파일 설정 완료
- [ ] 구글 애드센스 승인 완료
- [ ] 제휴 프로그램 가입 완료 (Bol.com, Amazon.nl)
- [ ] 제휴 상품 데이터 추가 완료
- [ ] 개인정보처리방침 페이지 생성
- [ ] 법적 공지가 모든 페이지에 표시되는지 확인
- [ ] 모바일 반응형 테스트 완료
- [ ] 광고 및 제휴 링크가 정상 작동하는지 확인

## 📚 참고 자료

- [Google AdSense 정책](https://support.google.com/adsense/answer/48182)
- [Bol.com 파트너 프로그램](https://partnerprogramma.bol.com/)
- [Amazon Associates](https://affiliate-program.amazon.nl/)
- [GDPR 가이드](https://gdpr.eu/)
- [네덜란드 소비자 보호법](https://www.rijksoverheid.nl/)

---

**주의**: 본 시스템은 법적 준수를 위한 기본 구조를 제공하지만, 실제 운영 시에는 법률 전문가의 검토를 받는 것을 권장합니다.
