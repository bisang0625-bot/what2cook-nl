# 주간 세일 정보 크롤러

## 개요

네덜란드 슈퍼마켓 주간 세일 정보를 정기적으로 크롤링하는 스크립트입니다.

## 기술 스택

- **Python requests**: HTTP 요청
- **BeautifulSoup4**: HTML 파싱
- **Python schedule**: 주간 스케줄링
- **Selenium/Playwright 미사용**: 정적 HTML만 파싱

## 크롤링 대상

1. **Reclamefolder.nl**: 슈퍼마켓 세일 폴더 통합 사이트
2. **Albert Heijn Bonus**: Albert Heijn 공식 Bonus 페이지 (보조 소스)

## 대상 슈퍼마켓

Albert Heijn, Jumbo, Lidl, Dirk, ALDI, Plus, Hoogvliet, Makro, Hanos, Sligro

## 실행 방법

### 즉시 실행 (테스트용)

```bash
python scraper/run_weekly_scraper.py
```

### 스케줄러 모드 (매주 일요일 11:00 자동 실행)

```bash
python scraper/run_weekly_scraper.py --schedule
```

## 스케줄 설정

- **실행 주기**: 매주 일요일 11:00 (로컬 타임존 기준)
- **스케줄 방식**: Python `schedule` 라이브러리 사용
- **운영 환경 권장**: `systemd`, `supervisor` 등과 함께 사용

### systemd 서비스 예시 (선택사항)

`/etc/systemd/system/weekly-scraper.service`:

```ini
[Unit]
Description=Weekly Supermarket Sale Scraper
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/K-receipe
ExecStart=/usr/bin/python3 /path/to/K-receipe/scraper/run_weekly_scraper.py --schedule
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 데이터 형식

크롤링된 데이터는 `data/weekly_sales.json`에 저장됩니다:

```json
{
  "week_number": "2024-01",
  "scraped_at": "2024-01-07T11:00:00",
  "total_products": 150,
  "supermarkets": {
    "successful": ["Albert Heijn", "Jumbo", "Lidl"],
    "failed": ["Dirk"]
  },
  "products": [
    {
      "supermarket": "Albert Heijn",
      "product_name": "Speklappen",
      "price_info": "€2.99",
      "sale_period": "7 jan - 13 jan 2024",
      "start_date": "2024-01-07T00:00:00",
      "end_date": "2024-01-13T23:59:59",
      "week_number": "2024-01",
      "source": "reclamefolder",
      "scraped_at": "2024-01-07T11:00:00"
    }
  ]
}
```

## 안정성

1. **개별 실패 처리**: 하나의 슈퍼마켓 크롤링 실패 시 다른 슈퍼마켓은 계속 실행
2. **데이터 보존**: 크롤링 실패 시 기존 데이터는 유지
3. **로깅**: 모든 단계에서 상세한 로그 기록 (`scraper.log`)
4. **백업**: 새 데이터 저장 전 기존 데이터 자동 백업

## 중요: HTML 구조 확인 필요

현재 코드는 일반적인 HTML 구조를 가정하고 작성되었습니다. 실제 사이트의 HTML 구조를 확인하여 선택자를 조정해야 합니다.

### 확인 및 수정 방법

1. **브라우저 개발자 도구 사용**:
   - Reclamefolder.nl 접속
   - 원하는 슈퍼마켓 페이지 열기
   - 개발자 도구 (F12)로 HTML 구조 확인
   - 상품 카드/리스트의 실제 클래스명 및 구조 확인

2. **코드 수정**:
   - `scrape_reclamefolder()` 메서드의 선택자 수정
   - `_extract_product_info()` 메서드의 상품 정보 추출 로직 수정

3. **테스트**:
   - 수정 후 즉시 실행 모드로 테스트
   - 로그 확인하여 데이터 추출 성공 여부 확인

## 로그

실행 로그는 `scraper.log` 파일에 저장됩니다:
- INFO: 일반 정보
- WARNING: 경고 (데이터 없음 등)
- ERROR: 에러 (크롤링 실패 등)

## 주의사항

1. **robots.txt 확인**: 크롤링 전 각 사이트의 robots.txt 확인 권장
2. **요청 간격**: 과도한 요청 방지를 위해 요청 간 적절한 딜레이 추가 권장
3. **HTML 변경**: 사이트 HTML 구조 변경 시 선택자 업데이트 필요
