"""
Albert Heijn Bonus 페이지에서 시각적으로 보이는 상품 정보 추출
Playwright의 locator를 사용하여 실제 렌더링된 요소에서 데이터를 가져옵니다.
"""
import os
import json
import time
import re
from pathlib import Path
from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta

# 브라우저 경로 설정
PROJECT_ROOT = Path(__file__).parent.parent
LOCAL_BROWSERS_PATH = PROJECT_ROOT / "pw-browsers"
if LOCAL_BROWSERS_PATH.exists():
    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(LOCAL_BROWSERS_PATH)

def scrape_ah_visual():
    """시각적으로 렌더링된 AH Bonus 상품 정보 추출"""
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
        
        # 페이지 완전 로딩 대기
        page.wait_for_load_state("networkidle")
        time.sleep(3)
        
        # 쿠키 동의
        try:
            btn = page.locator("button:has-text('Accepteren')").first
            if btn.is_visible(timeout=5000):
                print("🍪 쿠키 동의")
                btn.click()
                time.sleep(2)
        except:
            pass
        
        # JavaScript 렌더링 완료 대기
        page.wait_for_load_state("domcontentloaded")
        time.sleep(5)
        
        # 스크롤하여 모든 상품 로딩
        print("📜 페이지 스크롤 중...")
        last_height = page.evaluate("document.body.scrollHeight")
        for i in range(10):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)
            new_height = page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            print(f"  스크롤 {i+1} 완료")
        
        # 맨 위로 돌아가기
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(2)
        
        # 스크린샷 저장
        screenshot_path = PROJECT_ROOT / "data" / "ah_visual_screenshot.png"
        page.screenshot(path=str(screenshot_path), full_page=True)
        print(f"📸 스크린샷 저장: {screenshot_path}")
        
        # 다양한 선택자로 상품 카드 찾기
        print("\n🔎 상품 카드 검색 중...")
        
        selectors_to_try = [
            # AH 사이트 특화 선택자
            '[data-testhook*="product"]',
            '[data-testhook*="promotion"]',
            '[data-testhook*="bonus"]',
            '[class*="product-card"]',
            '[class*="ProductCard"]',
            '[class*="promotion-card"]',
            '[class*="PromotionCard"]',
            '[class*="bonus-card"]',
            '[class*="BonusCard"]',
            # 일반적인 선택자
            'article',
            '[role="article"]',
            '[class*="Card"]',
            '[class*="card"]',
            'a[href*="/producten/"]',
            'a[href*="/bonus/"]',
        ]
        
        found_elements = []
        for selector in selectors_to_try:
            try:
                elements = page.locator(selector).all()
                if elements and len(elements) > 0:
                    print(f"  ✅ '{selector}': {len(elements)}개 요소")
                    for elem in elements[:5]:  # 처음 5개만 샘플
                        try:
                            text = elem.inner_text(timeout=1000)
                            if text and len(text) > 10:
                                found_elements.append({
                                    'selector': selector,
                                    'text': text[:200]
                                })
                        except:
                            pass
            except Exception as e:
                pass
        
        print(f"\n📦 발견된 요소 샘플:")
        for i, elem in enumerate(found_elements[:10]):
            print(f"  {i+1}. [{elem['selector']}] {elem['text'][:100]}...")
        
        # 페이지의 모든 텍스트에서 상품 정보 패턴 찾기
        print("\n🔍 페이지 텍스트에서 상품 정보 추출...")
        all_text = page.evaluate("document.body.innerText")
        
        # 가격 패턴 주변 텍스트 추출
        price_pattern = r'([\w\s\-\']+)\s*€\s*(\d+)[,.](\d{2})'
        matches = re.findall(price_pattern, all_text)
        print(f"  가격 패턴 매칭: {len(matches)}개")
        
        for name, euros, cents in matches[:30]:
            name = name.strip()
            if len(name) > 3 and len(name) < 100:
                products.append({
                    'name': name,
                    'price': f"€{euros}.{cents}",
                    'supermarket': 'Albert Heijn'
                })
        
        # 할인 패턴 (1+1, 2e halve prijs 등)
        discount_pattern = r'(\d+\+\d+|2e halve prijs|[0-9]+% korting)'
        discounts = re.findall(discount_pattern, all_text, re.IGNORECASE)
        print(f"  할인 패턴 발견: {len(discounts)}개 - {set(discounts)}")
        
        # 텍스트 라인별 분석
        lines = all_text.split('\n')
        print(f"  총 텍스트 라인: {len(lines)}개")
        
        # 상품명으로 보이는 라인 추출
        product_lines = []
        for i, line in enumerate(lines):
            line = line.strip()
            # 상품명 조건: 적당한 길이, 숫자로만 되어있지 않음
            if 10 < len(line) < 80 and not line.isdigit():
                # 가격이 바로 다음 줄에 있는지 확인
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if re.match(r'€?\s*\d+[,.]?\d*', next_line):
                        product_lines.append({
                            'name': line,
                            'price': next_line
                        })
        
        print(f"  상품-가격 쌍 발견: {len(product_lines)}개")
        for item in product_lines[:10]:
            print(f"    - {item['name']}: {item['price']}")
            products.append({
                'name': item['name'],
                'price': item['price'],
                'supermarket': 'Albert Heijn'
            })
        
        browser.close()
    
    # 중복 제거
    seen = set()
    unique_products = []
    for p in products:
        key = p['name'].lower()
        if key not in seen:
            seen.add(key)
            unique_products.append(p)
    
    print(f"\n🎯 총 {len(unique_products)}개의 고유 상품 추출")
    
    # 결과 저장
    if unique_products:
        save_results(unique_products)
    
    return unique_products

def save_results(products):
    """결과 저장"""
    today = datetime.now()
    if today.weekday() == 0:
        next_monday = today
    else:
        next_monday = today + timedelta(days=(7 - today.weekday()))
    next_sunday = next_monday + timedelta(days=6)
    
    # weekly_sales.json 저장
    weekly_data = {
        'week_number': f"{next_monday.year}-{next_monday.isocalendar()[1]:02d}",
        'scraped_at': datetime.now().isoformat(),
        'total_products': len(products),
        'supermarkets': {'successful': ['Albert Heijn'], 'failed': []},
        'products': [
            {
                'supermarket': 'Albert Heijn',
                'product_name': p['name'],
                'price_info': p.get('price'),
                'start_date': next_monday.isoformat(),
                'end_date': next_sunday.isoformat(),
                'source': 'ah.nl/bonus',
                'scraped_at': datetime.now().isoformat()
            }
            for p in products
        ]
    }
    
    weekly_output = PROJECT_ROOT / "data" / "weekly_sales.json"
    with open(weekly_output, 'w', encoding='utf-8') as f:
        json.dump(weekly_data, f, ensure_ascii=False, indent=2)
    print(f"📁 weekly_sales.json 저장 완료: {len(products)}개 상품")

if __name__ == "__main__":
    products = scrape_ah_visual()
    
    print(f"\n🎉 크롤링 완료! {len(products)}개 상품 수집")
    
    # 상위 15개 상품 출력
    print("\n📋 상위 15개 상품:")
    for i, p in enumerate(products[:15], 1):
        print(f"  {i}. {p['name']} - {p.get('price', 'N/A')}")
    
    # 특정 키워드 검색
    keywords = ['speklap', 'kip', 'gehakt', 'kaas', 'melk', 'brood', 'pasta']
    print("\n🔎 키워드 검색:")
    for kw in keywords:
        found = [p for p in products if kw.lower() in p['name'].lower()]
        if found:
            print(f"  ✅ '{kw}': {len(found)}개 발견")
            for p in found[:2]:
                print(f"      - {p['name']} ({p.get('price', 'N/A')})")
        else:
            print(f"  ❌ '{kw}': 없음")
