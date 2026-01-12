"""
Albert Heijn 공식 Bonus 페이지 크롤링
실제 세일 상품 정보를 추출합니다.
"""
import os
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime, timedelta

# 브라우저 경로 설정
PROJECT_ROOT = Path(__file__).parent.parent
LOCAL_BROWSERS_PATH = PROJECT_ROOT / "pw-browsers"
if LOCAL_BROWSERS_PATH.exists():
    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(LOCAL_BROWSERS_PATH)

def scrape_ah_bonus():
    """Albert Heijn Bonus 페이지에서 세일 상품 크롤링"""
    url = "https://www.ah.nl/bonus"
    products = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        
        print(f"🔍 Albert Heijn Bonus 페이지 접속: {url}")
        page.goto(url, timeout=60000)
        page.wait_for_load_state("networkidle")
        
        # 쿠키 동의 처리
        try:
            # AH 사이트의 쿠키 동의 버튼
            cookie_selectors = [
                "button:has-text('Accepteren')",
                "button:has-text('Akkoord')",
                "button:has-text('Accept')",
                "[data-testid='accept-cookies']",
                "#accept-cookies"
            ]
            for selector in cookie_selectors:
                try:
                    btn = page.locator(selector).first
                    if btn.is_visible(timeout=3000):
                        print("🍪 쿠키 동의 버튼 클릭")
                        btn.click()
                        time.sleep(2)
                        break
                except:
                    continue
        except:
            pass
        
        # 페이지 로딩 대기
        time.sleep(5)
        
        # 스크롤하여 더 많은 상품 로딩
        print("📜 페이지 스크롤 중...")
        for _ in range(3):
            page.evaluate("window.scrollBy(0, window.innerHeight)")
            time.sleep(1)
        
        # 스크린샷 저장
        screenshot_path = PROJECT_ROOT / "data" / "ah_bonus_screenshot.png"
        page.screenshot(path=str(screenshot_path), full_page=True)
        print(f"📸 스크린샷 저장: {screenshot_path}")
        
        # HTML 가져오기
        content = page.content()
        
        # HTML 저장
        html_path = PROJECT_ROOT / "data" / "ah_bonus_page.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"📄 HTML 저장: {html_path}")
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # 페이지 제목 확인
        title = page.title()
        print(f"📰 페이지 제목: {title}")
        
        # 상품 카드 찾기 - AH 사이트 구조에 맞게
        # 다양한 선택자 시도
        product_selectors = [
            '[data-testhook="product-card"]',
            '[data-testhook="bonus-card"]',
            'article[class*="product"]',
            'div[class*="product-card"]',
            'div[class*="ProductCard"]',
            'a[href*="/producten/"]',
        ]
        
        found_products = []
        for selector in product_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"✅ '{selector}' 선택자로 {len(elements)}개 요소 발견")
                found_products.extend(elements)
        
        # 중복 제거
        seen = set()
        unique_products = []
        for elem in found_products:
            elem_str = str(elem)[:200]
            if elem_str not in seen:
                seen.add(elem_str)
                unique_products.append(elem)
        
        print(f"📦 총 {len(unique_products)}개의 고유 상품 요소 발견")
        
        # 상품 정보 추출
        for elem in unique_products[:50]:  # 최대 50개
            try:
                product = extract_product_info(elem)
                if product:
                    products.append(product)
            except Exception as e:
                continue
        
        # 텍스트 기반 검색 (백업)
        if len(products) < 5:
            print("⚠️ 상품이 적게 발견됨, 텍스트 기반 검색 시도...")
            all_text = soup.get_text()
            
            # 키워드 검색
            keywords = ['speklappen', 'kip', 'varken', 'gehakt', 'kaas', 'melk', 'brood', 
                       'pasta', 'druiven', 'vis', 'vlees', 'groente', 'aardappel', 'ui', 'tomaat']
            for kw in keywords:
                if kw.lower() in all_text.lower():
                    print(f"  ✅ '{kw}' 텍스트 발견!")
        
        browser.close()
    
    # 결과 저장
    result = {
        'scraped_at': datetime.now().isoformat(),
        'source': 'ah.nl/bonus',
        'supermarket': 'Albert Heijn',
        'total_products': len(products),
        'products': products
    }
    
    output_path = PROJECT_ROOT / "data" / "ah_bonus_products.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n✅ {len(products)}개 상품 저장: {output_path}")
    
    return products

def extract_product_info(elem):
    """상품 요소에서 정보 추출"""
    try:
        # 상품명 추출
        name = None
        name_selectors = ['h3', 'h4', 'h2', '[class*="title"]', '[class*="name"]', 'strong']
        for sel in name_selectors:
            name_elem = elem.select_one(sel)
            if name_elem:
                name = name_elem.get_text(strip=True)
                if name and len(name) > 2:
                    break
        
        if not name:
            # 링크 텍스트 사용
            link = elem.select_one('a')
            if link:
                name = link.get_text(strip=True)
        
        if not name or len(name) < 3:
            return None
        
        # 가격 추출
        price = None
        price_selectors = ['[class*="price"]', '[class*="Price"]', 'span[class*="euro"]']
        for sel in price_selectors:
            price_elem = elem.select_one(sel)
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                price_match = re.search(r'[\d,.]+', price_text)
                if price_match:
                    price = price_match.group()
                    break
        
        # 할인 정보 추출
        discount = None
        discount_selectors = ['[class*="discount"]', '[class*="bonus"]', '[class*="action"]']
        for sel in discount_selectors:
            discount_elem = elem.select_one(sel)
            if discount_elem:
                discount = discount_elem.get_text(strip=True)
                break
        
        return {
            'name': name,
            'price': price,
            'discount_info': discount,
            'supermarket': 'Albert Heijn'
        }
    except:
        return None

if __name__ == "__main__":
    products = scrape_ah_bonus()
    print(f"\n🎉 크롤링 완료! {len(products)}개 상품 수집")
    
    # 상위 10개 상품 출력
    print("\n📋 상위 10개 상품:")
    for i, p in enumerate(products[:10], 1):
        print(f"  {i}. {p['name']} - {p.get('price', 'N/A')} - {p.get('discount_info', '')}")
