# Vercel 설정 가이드

## 현재 상태

Vercel은 **정적 사이트 호스팅**만 제공합니다. Python 스크래퍼는 Vercel에서 직접 실행할 수 없습니다.

## 해결 방법

### 옵션 1: GitHub Actions 사용 (권장) ⭐

현재 설정된 방법입니다. GitHub Actions에서 스크래핑을 실행하고, 결과를 Git에 커밋하면 Vercel이 자동으로 재배포합니다.

**장점:**
- 무료 (GitHub Actions 무료 할당량 내)
- 자동 배포 연동
- 로그 확인 용이

**설정:**
- `.github/workflows/smart_scraper.yml` 파일이 이미 설정되어 있습니다.
- GitHub Secrets에 `GEMINI_API_KEY`만 설정하면 됩니다.

### 옵션 2: Vercel Cron Jobs (제한적)

Vercel Pro 플랜 이상에서만 사용 가능합니다. Serverless Functions를 사용하여 스크래핑을 실행할 수 있습니다.

**제한사항:**
- Pro 플랜 필요 (월 $20)
- 실행 시간 제한 (최대 60초)
- Python 스크래퍼 실행 어려움

### 옵션 3: 외부 서버 사용

별도의 서버(VPS, AWS EC2 등)에서 cron job을 설정하여 스크래핑을 실행하고, 결과를 Git에 푸시합니다.

**장점:**
- 완전한 제어 가능
- 제한 없음

**단점:**
- 서버 비용 발생
- 관리 필요

## 현재 권장 설정

✅ **GitHub Actions + Vercel 자동 배포**

1. GitHub Actions가 스크래핑 실행
2. 결과를 Git에 커밋
3. Vercel이 자동으로 재배포

이 방법이 가장 효율적이고 비용이 들지 않습니다.

## Vercel 환경 변수 설정

Vercel 대시보드에서 환경 변수를 설정할 수 있지만, 스크래핑은 GitHub Actions에서 실행되므로 필요하지 않습니다.

만약 Vercel에서 직접 실행하려면:
1. Vercel Dashboard > Project Settings > Environment Variables
2. `GEMINI_API_KEY` 추가

하지만 현재는 GitHub Actions를 사용하므로 불필요합니다.
