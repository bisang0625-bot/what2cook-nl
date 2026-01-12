# 뭐해먹지 NL | What2Cook NL

네덜란드 거주 한인들을 위한 슈퍼마켓 세일 정보 기반 한식 레시피 추천 서비스

**What2Cook NL** helps Korean residents in the Netherlands cook delicious meals using discounted ingredients from local supermarkets.

## 프로젝트 구조

```
.
├── app/                    # Next.js App Router
│   ├── layout.tsx         # 루트 레이아웃
│   ├── page.tsx           # 메인 페이지
│   └── globals.css        # 글로벌 스타일
├── components/
│   └── Dashboard.tsx      # 메인 대시보드 컴포넌트
├── scraper/
│   ├── __init__.py
│   └── ah_scraper.py      # Albert Heijn 세일 정보 크롤러
├── data/
│   └── weekly_recipes.json  # 레시피 데이터 (자동 생성)
├── recipe_matcher.py      # Gemini API 레시피 생성
├── requirements.txt       # Python 의존성
├── package.json           # Node.js 의존성
└── README.md
```

## 설치 및 실행

### 1. Python 의존성 설치

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Gemini API 키 설정

API 키를 설정하는 방법은 두 가지가 있습니다:

#### 방법 1: config.py 파일에 직접 입력 (권장)

`config.py` 파일을 열어서 `GEMINI_API_KEY` 변수에 직접 API 키를 입력하세요:

```python
# config.py
GEMINI_API_KEY = "AIzaSyBxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # 여기에 API 키 입력
```

#### 방법 2: .env 파일 사용

```bash
# .env.example을 .env로 복사
cp .env.example .env

# .env 파일을 열어서 API 키 입력
# GEMINI_API_KEY=your_gemini_api_key_here
```

**API 키 발급 방법:**
1. https://aistudio.google.com/app/apikey 접속
2. "Create API Key" 클릭
3. 발급받은 API 키를 `config.py` 또는 `.env` 파일에 입력

**우선순위:** .env 파일 > config.py 파일

### 3. 스크래퍼 실행 (Step 1)

```bash
python scraper/ah_scraper.py
```

실행하면 `data/next_week_bonus.json` 파일에 다음 주 세일 정보가 저장됩니다.

### 4. 레시피 생성 (Step 2)

```bash
python recipe_matcher.py
```

실행하면 `data/weekly_recipes.json` 파일에 한식 레시피가 생성됩니다.

### 5. 프론트엔드 실행 (Step 3)

```bash
# Node.js 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

브라우저에서 http://localhost:3000 접속하여 대시보드를 확인할 수 있습니다.

### 6. 주간 세일 정보 크롤러 실행

```bash
# 즉시 실행 (테스트용)
python scraper/run_weekly_scraper.py

# 스케줄러 모드 실행 (매주 일요일 11:00 자동 실행)
python scraper/run_weekly_scraper.py --schedule
```

**스케줄러 모드:**
- Python `schedule` 라이브러리를 사용하여 매주 일요일 11:00에 자동 실행
- 프로세스가 계속 실행되어야 하므로, 운영 환경에서는 `systemd`, `supervisor` 등과 함께 사용 권장
- 실행 로그는 `scraper.log` 파일에 저장됩니다

**크롤링 결과:**
- `data/weekly_sales.json` 파일에 저장
- 기존 데이터는 자동 백업 (weekly_sales_backup_*.json)
- 데이터가 없는 경우 기존 데이터는 유지됩니다

## 주요 기능

### Step 1: Smart Scraper (완료)
- Playwright를 사용하여 Albert Heijn 보너스 페이지 크롤링
- "Volgende week" (다음 주) 탭 자동 탐지 및 클릭
- 상품명, 가격, 이미지 정보 추출
- JSON 형식으로 데이터 저장

### Step 2: AI Recipe Matcher (완료)
- Google Gemini API (gemini-1.5-flash)를 사용한 레시피 생성
- 세일 상품 기반 한식 메뉴 추천
- 필터링용 태그 시스템 (매운맛, 채식, 아이식단, 조리시간)
- 확장 가능한 구조 (다른 마트 추가 가능)

### Step 3: Frontend Dashboard (완료)
- Next.js 14 (App Router) 기반 반응형 웹 대시보드
- Tailwind CSS를 사용한 모던한 UI
- 필터링 시스템:
  - 마트 선택 (Albert Heijn, Jumbo, Lidl)
  - 태그 필터 (아이 식단, 매콤한 맛, 채식)
- 레시피 카드 그리드 및 상세 모달
- 네덜란드 오렌지 컬러 테마

### 주간 세일 정보 크롤러 (추가)
- requests + BeautifulSoup 기반 크롤러 (Selenium/Playwright 미사용)
- Reclamefolder.nl 및 Albert Heijn Bonus 페이지 크롤링
- 10개 슈퍼마켓 지원: Albert Heijn, Jumbo, Lidl, Dirk, ALDI, Plus, Hoogvliet, Makro, Hanos, Sligro
- 매주 일요일 11:00 자동 실행 (Python schedule 라이브러리)
- 안정성 강화: 에러 처리, 로깅, 개별 실패 처리
- 데이터 형식: 슈퍼마켓명, 세일 주차 (YYYY-WW), 상품명, 할인 정보, 세일 기간, 크롤링 시각
