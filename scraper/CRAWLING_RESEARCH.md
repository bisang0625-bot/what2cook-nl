# 🔍 네덜란드 슈퍼마켓 크롤링 방법 조사

## 📋 목표 마트 리스트

| 마트 | 공식 세일 페이지 | 상태 |
|------|-----------------|------|
| Albert Heijn | https://www.ah.nl/bonus | ✅ 확인 필요 |
| Jumbo | https://www.jumbo.com/aanbiedingen | ✅ 확인 필요 |
| Dirk | https://www.dirk.nl/aanbiedingen | ✅ 확인 필요 |
| Lidl | https://www.lidl.nl/c/aanbiedingen | ✅ 확인 필요 |
| ALDI | https://www.aldi.nl/aanbiedingen.html | ✅ 확인 필요 |
| Plus | https://www.plus.nl/aanbiedingen | ✅ 확인 필요 |
| Hoogvliet | https://www.hoogvliet.com/aanbiedingen | ✅ 확인 필요 |
| Coop | https://www.coop.nl/aanbiedingen | ✅ 확인 필요 |

---

## 🎯 접근 방법

### **방법 1: 각 마트 공식 사이트 직접 크롤링** ⭐ (권장)

**장점:**
- ✅ 가장 정확한 데이터
- ✅ 실시간 업데이트
- ✅ 마트별 독립적 처리 (한 곳 실패해도 다른 곳 영향 없음)
- ✅ 브랜드 매칭 오류 없음

**단점:**
- ⚠️ 각 마트마다 다른 페이지 구조
- ⚠️ 개별 크롤러 필요
- ⚠️ 유지보수 필요

**구현 계획:**
1. Playwright로 각 페이지 방문
2. 페이지 구조 분석 (HTML 저장)
3. 상품 요소 찾기 (CSS selector)
4. 데이터 추출 및 저장

---

### **방법 2: Reclamefolder.nl 대안 접근**

**시도할 방법들:**

#### 2-1. 검색 기능 사용
```
https://www.reclamefolder.nl/search?q=[마트명]
```

#### 2-2. 폴더 ID 직접 접근
```
https://www.reclamefolder.nl/f/folders/[ID]/
```
- 각 마트의 최신 폴더 ID를 찾아서 직접 접근

#### 2-3. API 엔드포인트 찾기
- 브라우저 개발자 도구로 Network 탭 확인
- JSON API가 있는지 조사

**현재 문제:**
- ❌ 직접 URL 접근 시 404 또는 빈 페이지
- ❌ 이미지 기반 PDF 뷰어 (텍스트 추출 불가)

---

### **방법 3: Gemini Vision AI로 공식 사이트 스크린샷 분석** ⭐

**장점:**
- ✅ 페이지 구조 파악 불필요
- ✅ 모든 마트에 동일한 로직 적용
- ✅ 빠른 구현

**단점:**
- ⚠️ API 비용 발생
- ⚠️ 정확도 90-95% (완벽하지 않음)

**프로세스:**
1. Playwright로 각 마트 공식 세일 페이지 스크린샷
2. Gemini Vision으로 이미지 분석
3. 상품명, 가격, 할인 정보 추출

---

### **방법 4: 하이브리드 접근** 🎯 (최적)

**전략:**
```
1. Albert Heijn, Jumbo: HTML 파싱 (큰 마트, 정확도 최우선)
2. Lidl, ALDI, Dirk: Gemini Vision (중간 마트)
3. Plus, Hoogvliet, Coop: Gemini Vision 또는 스킵
```

**이유:**
- AH와 Jumbo가 네덜란드 시장 60% 점유
- 한인들이 가장 많이 사용
- 리소스 효율적 배분

---

## 🔧 구현 우선순위

### Phase 1: 핵심 마트 (1-2주)
1. ✅ Albert Heijn - 공식 사이트 HTML 파싱
2. ✅ Jumbo - 공식 사이트 HTML 파싱

### Phase 2: 주요 마트 (2-3주)
3. Lidl - Gemini Vision
4. ALDI - Gemini Vision
5. Dirk - Gemini Vision

### Phase 3: 추가 마트 (필요시)
6. Plus - Gemini Vision
7. Hoogvliet - Gemini Vision
8. Coop - Gemini Vision

---

## 📊 예상 데이터 품질

| 방법 | 정확도 | 속도 | 비용 | 유지보수 |
|------|--------|------|------|---------|
| HTML 파싱 | 98% | 빠름 | 무료 | 높음 |
| Gemini Vision | 90% | 중간 | 낮음 | 낮음 |
| Reclamefolder | 80% | 느림 | 무료 | 높음 |

---

## 💡 최종 권장 사항

**단계별 구현:**

1. **지금 당장** (30분)
   - 사용자가 제공한 URL로 각 마트 페이지 방문
   - HTML 구조 분석 및 저장
   - 스크린샷 캡처

2. **오늘 중** (2-3시간)
   - Albert Heijn 공식 크롤러 완성
   - Jumbo 공식 크롤러 완성
   - 테스트 및 검증

3. **내일** (3-4시간)
   - 나머지 6개 마트 Gemini Vision 크롤러
   - 전체 통합 테스트
   - 레시피 생성 및 프론트엔드 연동

**예상 결과:**
- ✅ 8개 마트 모두 크롤링 성공
- ✅ 마트별 정확한 상품 매칭
- ✅ 주간 자동 업데이트 가능
