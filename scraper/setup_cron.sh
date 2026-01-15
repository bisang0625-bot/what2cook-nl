#!/bin/bash
#
# 🕐 스마트 스크래핑 Cron Job 설정
# 
# 이 스크립트는 최적의 시점에 자동으로 스크래핑을 실행하도록 cron job을 설정합니다.
#
# 실행 시점:
# - 일요일 22:00: 월요일 시작 마트들 (대부분)
# - 화요일 22:00: 수요일 시작 마트들 (Jumbo, Dirk)
#
# 사용법:
#   bash scraper/setup_cron.sh
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON_PATH=$(which python3)

echo "🕐 스마트 스크래핑 Cron Job 설정"
echo "=================================="
echo ""
echo "프로젝트 경로: $PROJECT_ROOT"
echo "Python 경로: $PYTHON_PATH"
echo ""

# Cron job 명령어 생성 (더 일찍 실행: 일요일/화요일 자정)
# --wait-for-update: 세일 정보가 업데이트될 때까지 대기
CRON_CMD_SUNDAY="0 0 * * 0 cd $PROJECT_ROOT && $PYTHON_PATH scraper/smart_scheduler.py --wait-for-update >> logs/cron_scraper.log 2>&1"
CRON_CMD_TUESDAY="0 0 * * 2 cd $PROJECT_ROOT && $PYTHON_PATH scraper/smart_scheduler.py --wait-for-update >> logs/cron_scraper.log 2>&1"

# 로그 디렉토리 생성
mkdir -p "$PROJECT_ROOT/logs"

# 기존 cron job 제거 (중복 방지)
(crontab -l 2>/dev/null | grep -v "smart_scheduler.py" | grep -v "scrape_all_stores.py") | crontab -

# 새 cron job 추가
(crontab -l 2>/dev/null; echo ""; echo "# What2Cook NL - Smart Scraping Scheduler"; echo "# 일요일 22:00 - 월요일 시작 마트들"; echo "$CRON_CMD_SUNDAY"; echo "# 화요일 22:00 - 수요일 시작 마트들"; echo "$CRON_CMD_TUESDAY") | crontab -

echo "✅ Cron job 설정 완료!"
echo ""
echo "설정된 스케줄:"
echo "  - 일요일 00:00: 월요일 시작 마트 스크래핑 (세일 정보 업데이트 확인 후 실행)"
echo "  - 화요일 00:00: 수요일 시작 마트 스크래핑 (세일 정보 업데이트 확인 후 실행)"
echo ""
echo "현재 cron job 목록:"
crontab -l | grep -A 2 "smart_scheduler"
echo ""
echo "로그 파일: $PROJECT_ROOT/logs/cron_scraper.log"
echo ""
echo "Cron job 제거 방법:"
echo "  crontab -e"
echo "  (smart_scheduler.py 관련 라인 삭제)"
