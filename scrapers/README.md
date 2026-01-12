# 🛒 슈퍼마켓 크롤러 시스템

네덜란드 주요 8개 슈퍼마켓의 공식 세일 정보를 크롤링하는 시스템

---

## 📁 파일 구조

```
scrapers/
├── __init__.py              # 패키지 초기화
├── store_config.py          # 마트별 설정 (URL, 전략, 셀렉터)
├── base_scraper.py          # 기본 크롤러 클래스
├── main_scraper.py          # 메인 실행 스크립트
└── README.md                # 이 파일
```

---

## 🎯 지원 마트

| 마트 | Strategy | 상태 |
|------|----------|------|
| **Albert Heijn** | `click_next_week` | ✅ 우선순위 |
| **Dirk** | `direct_url` | ✅ 우선순위 |
| **Aldi** | `direct_url` | ✅ 우선순위 |
| Jumbo | `click_next_week` | ⏳ 테스트 필요 |
| Lidl | `click_category` | ⏳ 테스트 필요 |
| Plus | `click_next_week` | ⏳ 테스트 필요 |
| Hoogvliet | `default` | ⏳ 테스트 필요 |
| Coop | `default` | ⏳ 테스트 필요 |

---

## 🚀 사용법

### 1. 우선순위 마트만 크롤링 (권장)
```bash
python3 scrapers/main_scraper.py --priority
```
AH, Dirk, Aldi 3개 마트만 크롤링 (빠른 테스트)

### 2. 전체 마트 크롤링
```bash
python3 scrapers/main_scraper.py
```
8개 마트 모두 크롤링 (시간 소요)

### 3. 결과 확인
```bash
cat data/weekly_sales.json
```

---

## 🔧 크롤링 전략 설명

### `direct_url`
- **사용 마트**: Dirk, Aldi
- **방식**: URL이 직접 "다음 주" 페이지를 가리킴
- **예시**: `https://www.dirk.nl/folder/volgende-week`
- **장점**: 가장 안정적, 버튼 클릭 불필요

### `click_next_week`
- **사용 마트**: Albert Heijn, Jumbo, Plus
- **방식**: "Volgende week" 버튼 클릭 필요
- **장점**: 공식 UI 사용, 정확도 높음
- **주의**: 버튼 셀렉터가 변경될 수 있음

### `click_category`
- **사용 마트**: Lidl
- **방식**: "Vanaf maandag" 카테고리 탭 클릭
- **특징**: Lidl 특유의 UI 구조

### `default`
- **사용 마트**: Hoogvliet, Coop
- **방식**: 한 페이지에 모든 세일 정보 표시
- **장점**: 간단함

---

## ⚙️ 설정 수정

### 마트 URL 변경
`scrapers/store_config.py` 파일에서 수정:

```python
STORES = {
    "ah": {
        "url": "https://www.ah.nl/bonus",  # ← 여기 수정
        ...
    }
}
```

### 셀렉터 변경
페이지 구조가 변경되면 셀렉터 업데이트:

```python
"selectors": {
    "product_card": "article[data-testhook='product-card']",  # ← 여기 수정
    "title": "strong[data-testhook='product-title']",
    ...
}
```

### 크롤링 설정
`scrapers/store_config.py`의 `SCRAPING_CONFIG`:

```python
SCRAPING_CONFIG = {
    "headless": True,        # False로 하면 브라우저 보임 (디버그용)
    "timeout": 60000,        # 타임아웃 (밀리초)
    "wait_after_load": 5,    # 페이지 로드 후 대기 시간 (초)
}
```

---

## 🐛 디버깅

### 1. 헤드리스 모드 끄기
`store_config.py`에서:
```python
"headless": False  # 브라우저가 보임
```

### 2. 스크린샷 확인
`data/screenshots/` 폴더에 각 마트의 스크린샷 저장됨

### 3. 셀렉터 확인
브라우저 개발자 도구(F12)에서 실제 HTML 구조 확인

---

## 📊 출력 형식

`data/weekly_sales.json`:

```json
{
  "week_number": "2026-03",
  "sale_period": "2026-01-12 ~ 2026-01-18",
  "total_products": 120,
  "supermarkets": {
    "successful": ["Albert Heijn", "Dirk", "Aldi"],
    "failed": []
  },
  "products": [
    {
      "supermarket": "Albert Heijn",
      "product_name": "Verse kipfilet",
      "price_info": "€5.49",
      "discount_info": "25% korting",
      "start_date": "2026-01-12T00:00:00",
      "source": "official_website"
    }
  ]
}
```

---

## 🔄 다음 단계

크롤링 성공 후:

```bash
# 레시피 생성
python3 recipe_matcher.py

# 웹사이트 확인
npm run dev
```

---

## ⚠️ 주의사항

1. **Rate Limiting**: 각 마트 사이에 3초 대기
2. **쿠키 동의**: 자동으로 처리되지만, 가끔 수동 필요
3. **페이지 구조 변경**: 마트 사이트가 업데이트되면 셀렉터 수정 필요
4. **Playwright 브라우저**: 처음 실행 시 자동 다운로드

---

## 💡 팁

- 우선 `--priority` 옵션으로 3개 마트만 테스트
- 에러 발생 시 `headless=False`로 브라우저 확인
- 셀렉터가 작동하지 않으면 여러 개 설정 (`, `로 구분)
