#!/usr/bin/env python3
"""
주간 크롤러 실행 스크립트

사용법:
    # 즉시 실행
    python scraper/run_weekly_scraper.py
    
    # 스케줄러 모드 실행 (매주 일요일 11:00 자동 실행)
    python scraper/run_weekly_scraper.py --schedule
"""

import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scraper.weekly_scraper import run_scraper, schedule_weekly_scraper

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--schedule':
        # 스케줄러 모드
        schedule_weekly_scraper()
    else:
        # 즉시 실행 모드
        success = run_scraper()
        sys.exit(0 if success else 1)
