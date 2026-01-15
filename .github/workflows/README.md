# GitHub Actions 워크플로우

## 현재 활성 워크플로우

### `smart_scraper.yml` ⭐ (권장)
- **스케줄**: 일요일/화요일 자정 (UTC 00:00)
- **기능**: 스마트 스케줄러 사용 (세일 정보 업데이트 확인 후 스크래핑)
- **실행 스크립트**: `scraper/smart_scheduler.py --wait-for-update`
- **효과**: API 사용량 최적화, 사용자 아침 확인 가능

### `daily_scrape.yml` (DEPRECATED)
- ⚠️ 더 이상 사용되지 않음
- 기존 스크래퍼 사용 (`scrapers/main_scraper.py`)
- 매일 실행으로 API 사용량 많음

## 설정 방법

### 1. GitHub Secrets 설정
Repository Settings > Secrets and variables > Actions에서 다음 Secret을 설정하세요:

- `GEMINI_API_KEY`: Gemini API 키

### 2. 워크플로우 활성화
기본적으로 워크플로우는 자동으로 활성화됩니다. 확인하려면:
- Repository > Actions 탭에서 워크플로우 목록 확인

### 3. 수동 실행
- Repository > Actions > "Smart Scraper - Weekly Sales Update" > "Run workflow"

## 스케줄 설명

### 일요일 자정 (UTC 00:00)
- 네덜란드 시간: 01:00 (CET) 또는 02:00 (CEST)
- 목적: 월요일 시작 마트들 스크래핑
- 사용자가 월요일 아침에 확인 가능

### 화요일 자정 (UTC 00:00)
- 네덜란드 시간: 01:00 (CET) 또는 02:00 (CEST)
- 목적: 수요일 시작 마트들(Jumbo, Dirk) 스크래핑
- 사용자가 수요일 아침에 확인 가능

## 문제 해결

### 워크플로우가 실행되지 않는 경우
1. Repository Settings > Actions > General에서 "Allow all actions and reusable workflows" 확인
2. Actions 탭에서 에러 로그 확인

### API 키 오류
1. Secrets에 `GEMINI_API_KEY`가 올바르게 설정되었는지 확인
2. API 키가 유효한지 확인
