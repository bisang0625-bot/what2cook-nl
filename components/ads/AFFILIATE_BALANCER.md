# AffiliateBalancer 컴포넌트 가이드

## 📋 개요

지능형 제휴 마케팅 위젯으로, Bol.com과 Amazon.nl로의 트래픽을 전략적으로 분배하고 전체 CTR(클릭률)을 높이기 위해 설계되었습니다.

## 🎯 핵심 전략

### 1. 위치 편향 제거
- **랜덤 버튼 배치**: 페이지 로드 시 `Math.random()`으로 버튼 순서를 50% 확률로 변경
- **동일한 시각적 무게감**: 두 버튼의 크기와 디자인을 동일하게 유지

### 2. 가격 외 구매 결정 요소 시각화
- **USP 아이콘**: 각 플랫폼의 강점을 아이콘으로 표시
  - 빠른 배송: 🚚 Truck
  - 가격 경쟁력: ⭐ Star
  - 신뢰도: 🛡️ Shield
- **뱃지 시스템**: 
  - 최저가: 녹색
  - 내일 도착: 파란색
  - Prime: 주황색
- **혜택 텍스트**: 배송 옵션, 픽업 가능 여부 등

### 3. 매력적인 마이크로 카피
- **고민 유도 문구**: "가격은 아마존이 싼데, 배송은 볼닷컴이 빠르네? 어디서 살까?"
- **상황별 카피**:
  - Bol.com: "내일 받고 싶다면", "매장에서 직접 픽업", "가격 및 재고 확인"
  - Amazon: "최저가로 구매하기", "Prime 무료 배송 혜택", "리뷰 확인 후 구매"

## 📊 데이터 구조

### 새로운 스키마 (`platforms`)

```json
{
  "id": "cuckoo-6p",
  "name": "쿠쿠 6인용 압력밥솥",
  "platforms": {
    "bol": {
      "url": "...",
      "price": "€120.00",
      "currency": "EUR",
      "badge": "내일 도착",
      "benefit": "AH 매장 픽업 가능",
      "usp": "빠른 배송"
    },
    "amazon": {
      "url": "...",
      "price": "€118.00",
      "currency": "EUR",
      "badge": "최저가",
      "benefit": "Prime 무료 배송",
      "usp": "가격 경쟁력"
    }
  }
}
```

### 필드 설명

- `badge`: 눈에 띄는 뱃지 텍스트 (예: "내일 도착", "최저가", "Prime")
- `benefit`: 추가 혜택 설명 (예: "AH 매장 픽업 가능", "Prime 무료 배송")
- `usp`: 플랫폼의 고유 강점 (예: "빠른 배송", "가격 경쟁력", "신뢰도")

## 🎨 UI 디자인

### 버튼 스타일

**Bol.com 버튼:**
- 배경색: `#0000FF` (파란색)
- 텍스트: 흰색
- 호버: `#0000CC`
- 그림자 효과 및 호버 스케일 애니메이션

**Amazon 버튼:**
- 배경색: `#FF9900` (노란색)
- 텍스트: 검정색
- 호버: `#FF8800`
- 그림자 효과 및 호버 스케일 애니메이션

### 뱃지 색상

- **최저가**: 녹색 (`bg-green-500`)
- **내일 도착**: 파란색 (`bg-blue-500`)
- **Prime**: 주황색 (`bg-orange-500`)
- **기본**: 회색 (`bg-gray-600`)

## 🔍 클릭 트래킹

### 콘솔 로그
```javascript
console.log(`[Affiliate Click] Platform: ${platform}, Product: ${productId}`)
```

### Google Analytics 연동 (선택사항)
```javascript
gtag('event', 'affiliate_click', {
  platform: 'bol' | 'amazon',
  product_id: string,
  product_name: string
})
```

## ⚖️ 법적 준수

- ✅ 모든 링크에 `rel="nofollow sponsored noopener noreferrer"` 적용
- ✅ `target="_blank"` 사용
- ✅ 클릭 트래킹 로그 기록

## 📦 사용 예시

```tsx
import AffiliateBalancer from '@/components/ads/AffiliateBalancer'

<AffiliateBalancer product={affiliateProduct} />
```

## 🎯 예상 효과

1. **위치 편향 제거**: 랜덤 배치로 양쪽 버튼 클릭률 균형
2. **CTR 향상**: 가격 외 요소 시각화로 클릭 유도
3. **전환율 향상**: 매력적인 마이크로 카피로 구매 결정 촉진
4. **트래픽 분산**: Bol.com과 Amazon.nl로 균형잡힌 트래픽 분배

## 🔧 커스터마이징

### USP 아이콘 추가
`getUSPIcon` 함수에 새로운 케이스 추가:
```tsx
case '새로운 USP':
  return <NewIcon className="w-4 h-4" />
```

### 마이크로 카피 수정
`getMicroCopy` 함수에서 상황별 카피 조정

### 뱃지 색상 변경
`getBadgeColor` 함수에서 색상 매핑 수정

---

**결론**: 이 컴포넌트는 사용자가 "가격은 아마존이 싼데, 배송은 볼닷컴이 빠르네? 어디서 살까?"라고 고민하며 두 버튼 중 하나는 반드시 누르게 만드는 UI를 구현합니다.
