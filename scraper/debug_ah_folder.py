"""
Reclamefolder.nl에서 실제 Albert Heijn 폴더 페이지 분석
"""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re
import time
import json

# 브라우저 경로 설정
PROJECT_ROOT = Path(__file__).parent.parent
LOCAL_BROWSERS_PATH = PROJECT_ROOT / "pw-browsers"
if LOCAL_BROWSERS_PATH.exists():
    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(LOCAL_BROWSERS_PATH)

def debug_ah_folder():
    # 실제 Albert Heijn 폴더 페이지 URL
    url = "https://www.reclamefolder.nl/f/folders/68451/"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        page = context.new_page()
        
        print(f"🔍 Albert Heijn 폴더 페이지 접속: {url}")
        page.goto(url, timeout=60000)
        page.wait_for_load_state("networkidle")
        
        # 쿠키 동의
        try:
            cookie_btn = page.get_by_role("button", name=re.compile("allow|accept|akkoord|agree", re.IGNORECASE))
            if cookie_btn.count() > 0 and cookie_btn.first.is_visible():
                print("🍪 쿠키 동의")
                cookie_btn.first.click()
                time.sleep(2)
        except:
            pass
        
        # 추가 대기
        time.sleep(3)
        
        # 스크린샷 저장
        screenshot_path = PROJECT_ROOT / "data" / "ah_folder_screenshot.png"
        page.screenshot(path=str(screenshot_path), full_page=True)
        print(f"📸 스크린샷 저장: {screenshot_path}")
        
        # HTML 저장
        content = page.content()
        html_path = PROJECT_ROOT / "data" / "ah_folder_page.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"📄 HTML 저장: {html_path}")
        
        # 페이지 제목 확인
        title = page.title()
        print(f"📰 페이지 제목: {title}")
        
        # 상품 정보 검색
        soup = BeautifulSoup(content, 'html.parser')
        all_text = soup.get_text().lower()
        
        # 네덜란드 슈퍼마켓 상품명 키워드 검색
        keywords = ['speklappen', 'kip', 'varken', 'rund', 'gehakt', 'kaas', 'melk', 'brood', 
                    'pasta', 'druiven', 'vis', 'vlees', 'groente']
        print("\n🔎 키워드 검색:")
        found_keywords = []
        for kw in keywords:
            if kw.lower() in all_text:
                print(f"  ✅ '{kw}' 발견!")
                found_keywords.append(kw)
            else:
                print(f"  ❌ '{kw}' 없음")
        
        # 가격 패턴 검색
        price_pattern = re.findall(r'€\s*[\d,.]+', content)
        print(f"\n💰 발견된 가격 패턴: {len(price_pattern)}개")
        if price_pattern:
            print(f"  예시: {price_pattern[:5]}")
        
        browser.close()
        
    print("\n✅ 디버그 완료!")

if __name__ == "__main__":
    debug_ah_folder()
