#!/usr/bin/env python3
"""
세일 날짜 검증 스크립트 (Playwright Version)
실제 사이트에서 날짜 정보를 추출하여 '다음 주' 데이터가 맞는지 확인합니다.
"""
import sys
from pathlib import Path
import re
from datetime import datetime, timedelta
import logging
from playwright.sync_api import sync_playwright

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scraper.weekly_scraper import WeeklyScraper

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def verify_dates():
    scraper = WeeklyScraper()
    
    # 기준 날짜 계산
    today = datetime.now()
    next_monday = scraper.get_next_monday()
    next_sunday = next_monday + timedelta(days=6)
    
    logger.info("=" * 60)
    logger.info("📅 세일 날짜 검증 시작 (Playwright)")
    logger.info(f"오늘 날짜: {today.strftime('%Y-%m-%d (%A)')}")
    # 월요일인 경우 메시지 조정
    if today.weekday() == 0:
        logger.info(f"타겟 시작일(오늘): {next_monday.strftime('%Y-%m-%d')}")
    else:
        logger.info(f"타겟 시작일(다음 월요일): {next_monday.strftime('%Y-%m-%d')}")
    logger.info(f"타겟 종료일: {next_sunday.strftime('%Y-%m-%d')}")
    logger.info("=" * 60)
    
    results = {}
    
    # 주요 마트만 샘플링
    target_stores = ['Albert Heijn', 'Jumbo', 'Lidl']
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        for store in target_stores:
            logger.info(f"\n🔍 {store} 검증 중...")
            url = scraper.get_supermarket_url(store)
            
            try:
                page = context.new_page()
                logger.info(f"  - URL 이동: {url}")
                page.goto(url, timeout=60000)
                page.wait_for_load_state("networkidle")
                
                # 쿠키 동의 시도
                try:
                    cookie_btn = page.get_by_role("button", name=re.compile("allow|accept|akkoord|agree", re.IGNORECASE))
                    if cookie_btn.count() > 0 and cookie_btn.first.is_visible():
                        cookie_btn.first.click()
                        logger.info("  - 쿠키 동의 완료")
                except:
                    pass
                
                content = page.content().lower()
                
                # 1. "Volgende week" 키워드 검색
                has_next_week = 'volgende week' in content or 'next week' in content
                
                # 2. 날짜 범위 텍스트 추출
                range_matches = re.findall(r'\d{1,2}\s*[a-z]{3}\s*[-–t/m]+\s*\d{1,2}\s*[a-z]{3}', content)
                
                logger.info(f"  - 'Volgende week' 키워드: {'✅ 있음' if has_next_week else '❌ 없음'}")
                if range_matches:
                    logger.info(f"  - 발견된 날짜 범위: {range_matches[:3]}")
                
                # 3. 다음 주 버튼 존재 여부 확인
                next_week_btn = page.locator("button", has_text=re.compile("volgende week|next week", re.IGNORECASE))
                if next_week_btn.count() > 0 and next_week_btn.first.is_visible():
                    logger.info("  ✅ '다음 주' 버튼 발견됨 (클릭 가능)")
                    is_valid = True
                else:
                    logger.warning("  ⚠️ '다음 주' 버튼을 찾을 수 없음")
                    is_valid = False
                
                results[store] = is_valid
                page.close()
                
            except Exception as e:
                logger.error(f"  ❌ 오류 발생: {str(e)}")
                results[store] = False
        
        browser.close()
            
    logger.info("\n" + "=" * 60)
    logger.info("📊 검증 결과 요약")
    for store, is_valid in results.items():
        status = "✅ 확인됨" if is_valid else "⚠️ 확인 필요"
        logger.info(f"- {store}: {status}")
    logger.info("=" * 60)

if __name__ == "__main__":
    verify_dates()
