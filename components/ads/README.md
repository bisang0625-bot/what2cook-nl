# AffiliateDisclosure 컴포넌트

네덜란드/EU 규정에 따른 제휴 링크 공지 컴포넌트입니다.

## 📋 개요

이 컴포넌트는 네덜란드 소비자 보호법 및 EU GDPR 규정을 준수하여 제휴 링크가 포함된 페이지에 투명성 공지를 표시합니다.

## ⚖️ 법적 준수

- **네덜란드 소비자 보호법**: 제휴 링크 수수료 발생 가능성 명시
- **EU GDPR**: 투명성 원칙 준수
- **FTC 가이드라인**: 명확한 공지 표시

## 🎯 사용 위치

다음 위치에 **항상 배치**되어야 합니다:

1. ✅ 레시피 상세 페이지 최하단
2. ✅ 상품 리스트 최하단
3. ✅ 제휴 링크가 포함된 모든 페이지

## 📦 사용법

### 기본 사용

```tsx
import AffiliateDisclosure from '@/components/ads/AffiliateDisclosure'

// 레시피 리스트 최하단
<div className="mt-8 pt-6 border-t border-gray-200">
  <AffiliateDisclosure />
</div>
```

### 옵션 사용

```tsx
// 아이콘 없이 표시
<AffiliateDisclosure showIcon={false} />

// 컴팩트 모드
<AffiliateDisclosure compact={true} />

// 커스텀 클래스
<AffiliateDisclosure className="my-custom-class" />
```

## 🎨 Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `className` | `string` | `''` | 추가 CSS 클래스명 |
| `showIcon` | `boolean` | `true` | Info 아이콘 표시 여부 |
| `compact` | `boolean` | `false` | 컴팩트 모드 (향후 구현) |

## 📝 표시되는 텍스트

**네덜란드어:**
> Op deze pagina staan affiliate links. Als u via deze links iets koopt, ontvangen wij een kleine commissie.

**한국어 (괄호 안):**
> (이 페이지는 제휴 링크를 포함하고 있으며, 구매 시 소정의 수수료를 받을 수 있습니다.)

## 🎨 스타일

- 텍스트 크기: `text-xs`
- 텍스트 색상: `text-gray-500`
- 아이콘: `Info` (lucide-react)
- 레이아웃: Flexbox (아이콘 + 텍스트)

## ✅ 통합된 위치

이 컴포넌트는 다음 위치에 자동으로 통합되어 있습니다:

1. **Dashboard 컴포넌트**
   - 레시피 그리드 최하단
   - 레시피 상세 모달 최하단

2. **AffiliateProductGrid 컴포넌트**
   - 제휴 상품 리스트 최하단

## 🔍 접근성

- `aria-hidden="true"` 속성이 아이콘에 적용되어 스크린 리더에서 제외됩니다
- 텍스트는 시맨틱 HTML (`<p>`) 태그로 마크업되어 있습니다

## 📚 참고 자료

- [네덜란드 소비자 보호법](https://www.rijksoverheid.nl/)
- [EU GDPR](https://gdpr.eu/)
- [FTC Disclosure Guidelines](https://www.ftc.gov/tips-advice/business-center/guidance/ftcs-endorsement-guides-what-people-are-asking)

---

**주의**: 이 컴포넌트는 법적 요구사항을 충족하기 위한 기본 구조를 제공하지만, 실제 운영 시에는 법률 전문가의 검토를 받는 것을 권장합니다.
