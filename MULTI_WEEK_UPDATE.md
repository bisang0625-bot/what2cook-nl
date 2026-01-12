# 📅 Multi-Week Update: 현재 주 + 다음 주 세일 정보

## ✅ 구현 완료

### 1. 프론트엔드 탭 UI
- **`components/Tabs.tsx`**: 재사용 가능한 탭 컴포넌트
- **`app/page.tsx`**: 
  - "이번 주 세일" 탭
  - "다음 주 미리보기" 탭
  - 각 탭에서 해당 주차의 레시피 표시

### 2. 데이터 구조
- **현재 주**: `data/current_sales.json` → `data/current_recipes.json`
- **다음 주**: `data/next_sales.json` → `data/next_recipes.json`

### 3. 통일된 데이터 스키마
```json
{
  "store": "Albert Heijn",
  "product_name": "Speklappen",
  "price": "€3.99",
  "discount": "1+1 gratis",
  "valid_from": "2026-01-12T00:00:00",
  "valid_until": "2026-01-18T00:00:00",
  "scraped_at": "2026-01-12T13:00:00"
}
```

### 4. 크롤러 업데이트
- **`scrapers/hybrid_scraper.py`**:
  - `scrape_week(week_type)`: 'current' 또는 'next' 크롤링
  - `save_results()`: week_type에 따라 파일 분리 저장
  - `main(week_type='both')`: 두 주차 모두 크롤링

### 5. 레시피 생성기 업데이트
- **`recipe_matcher.py`**:
  - `RecipeMatcher(week_type)`: 'current', 'next', 'both' 지원
  - 각 주차별로 레시피 파일 분리 저장

---

## 🚀 사용 방법

### 크롤링 실행
```bash
# 현재 주 + 다음 주 모두 크롤링
python3 scrapers/hybrid_scraper.py

# 현재 주만
python3 scrapers/hybrid_scraper.py current

# 다음 주만
python3 scrapers/hybrid_scraper.py next
```

### 레시피 생성
```bash
# 현재 주 + 다음 주 모두 생성
python3 recipe_matcher.py

# 현재 주만
python3 recipe_matcher.py current

# 다음 주만
python3 recipe_matcher.py next
```

### 웹사이트 확인
```bash
npm run dev
# http://localhost:3000 접속
# 상단 탭으로 "이번 주 세일" / "다음 주 미리보기" 전환
```

---

## 📁 파일 구조

```
data/
├── current_sales.json      # 이번 주 세일 상품
├── current_recipes.json    # 이번 주 레시피
├── next_sales.json         # 다음 주 세일 상품
└── next_recipes.json       # 다음 주 레시피
```

---

## 🔄 다음 단계

1. **크롤러 실행**: `python3 scrapers/hybrid_scraper.py`
2. **레시피 생성**: `python3 recipe_matcher.py`
3. **웹사이트 확인**: 브라우저에서 탭 전환 테스트

---

## ⚠️ 참고사항

- 현재는 `weekly_recipes.json`을 `current_recipes.json`으로 복사하여 테스트 중
- 실제 크롤러 실행 시 `current_sales.json`과 `next_sales.json`이 생성됨
- 각 마트마다 "현재 주"와 "다음 주" 버튼이 있는지 확인 필요 (추후 개선)
