"""
Reclamefolder.nl HTML 구조 분석용 디버그 스크립트
"""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re
import time

# 브라우저 경로 설정
PROJECT_ROOT = Path(__file__).parent.parent
LOCAL_BROWSERS_PATH = PROJECT_ROOT / "pw-browsers"
if LOCAL_BROWSERS_PATH.exists():
    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(LOCAL_BROWSERS_PATH)

def debug_reclamefolder():
    url = "https://www.reclamefolder.nl/albert-heijn"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        page = context.new_page()
        
        print(f"🔍 페이지 접속: {url}")
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
        
        # 추가 대기 (동적 콘텐츠 로딩)
        time.sleep(3)
        
        # 스크린샷 저장
        screenshot_path = PROJECT_ROOT / "data" / "debug_screenshot.png"
        page.screenshot(path=str(screenshot_path), full_page=True)
        print(f"📸 스크린샷 저장: {screenshot_path}")
        
        # HTML 저장
        content = page.content()
        html_path = PROJECT_ROOT / "data" / "debug_page.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"📄 HTML 저장: {html_path}")
        
        # BeautifulSoup으로 구조 분석
        soup = BeautifulSoup(content, 'html.parser')
        
        print("\n" + "=" * 60)
        print("📊 HTML 구조 분석")
        print("=" * 60)
        
        # 1. 모든 article 태그
        articles = soup.find_all('article')
        print(f"\n<article> 태그: {len(articles)}개")
        
        # 2. 일반적인 상품 관련 클래스 찾기
        product_classes = ['product', 'item', 'card', 'tile', 'offer', 'aanbieding', 'bonus']
        for cls in product_classes:
            elements = soup.find_all(class_=lambda x: x and cls in x.lower())
            if elements:
                print(f"'{cls}' 포함 클래스: {len(elements)}개")
                if len(elements) > 0:
                    first_classes = elements[0].get('class', [])
                    print(f"  예시 클래스: {first_classes[:3]}")
        
        # 3. data-testid 속성 찾기
        data_testid = soup.find_all(attrs={'data-testid': True})
        print(f"\ndata-testid 속성: {len(data_testid)}개")
        if data_testid:
            testids = set([el.get('data-testid') for el in data_testid[:10]])
            print(f"  예시: {testids}")
        
        # 4. 가격 관련 요소 찾기
        price_elements = soup.find_all(class_=lambda x: x and ('price' in x.lower() or 'prijs' in x.lower()))
        print(f"\n가격 관련 요소: {len(price_elements)}개")
        
        # 5. 텍스트에서 상품명 후보 찾기
        all_text = soup.get_text()
        
        # 네덜란드 슈퍼마켓 상품명 키워드 검색
        keywords = ['speklappen', 'kip', 'varken', 'rund', 'gehakt', 'kaas', 'melk', 'brood']
        print("\n🔎 키워드 검색:")
        for kw in keywords:
            if kw.lower() in all_text.lower():
                print(f"  ✅ '{kw}' 발견!")
            else:
                print(f"  ❌ '{kw}' 없음")
        
        # 6. iframe 확인 (콘텐츠가 iframe 안에 있을 수 있음)
        iframes = soup.find_all('iframe')
        print(f"\n<iframe> 태그: {len(iframes)}개")
        
        # 7. 주요 div 구조 출력
        main_content = soup.find('main') or soup.find(id='main') or soup.find(class_='main')
        if main_content:
            print(f"\n<main> 태그 발견, 자식 요소: {len(main_content.find_all(recursive=False))}개")
        
        browser.close()
        
    print("\n✅ 디버그 완료! data/debug_screenshot.png 및 data/debug_page.html 파일을 확인하세요.")

if __name__ == "__main__":
    debug_reclamefolder()
