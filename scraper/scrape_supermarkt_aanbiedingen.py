"""
Supermarkt Aanbiedingen 사이트에서 세일 정보 크롤링
https://www.supermarktaanbiedingen.com/
이 사이트는 네덜란드 슈퍼마켓 세일 정보를 통합 제공합니다.
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

SUPERMARKETS = {
    'albert-heijn': 'Albert Heijn',
    'jumbo': 'Jumbo',
    'lidl': 'Lidl',
    'aldi': 'ALDI',
    'plus': 'Plus',
    'dirk': 'Dirk',
    'hoogvliet': 'Hoogvliet',
    'coop': 'Coop'
}

def scrape_supermarkt_aanbiedingen():
    """Supermarkt Aanbiedingen에서 세일 정보 크롤링"""
    all_products = []
    successful_stores = []
    failed_stores = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        
        for slug, store_name in SUPERMARKETS.items():
            url = f"https://www.supermarktaanbiedingen.com/{slug}"
            print(f"\n🔍 {store_name} 크롤링: {url}")
            
            try:
                page = context.new_page()
                page.goto(url, timeout=60000)
                page.wait_for_load_state("networkidle")
                time.sleep(2)
                
                # 쿠키 동의
                try:
                    cookie_btn = page.locator("button:has-text('Akkoord'), button:has-text('Accept')").first
                    if cookie_btn.is_visible(timeout=2000):
                        cookie_btn.click()
                        time.sleep(1)
                except:
                    pass
                
                # 페이지 텍스트 추출
                content = page.content()
                all_text = page.evaluate("document.body.innerText")
                
                # 상품 정보 추출
                products = extract_products(all_text, store_name)
                
                if products:
                    all_products.extend(products)
                    successful_stores.append(store_name)
                    print(f"  ✅ {len(products)}개 상품 추출")
                else:
                    failed_stores.append(store_name)
                    print(f"  ⚠️ 상품 없음")
                
                page.close()
                
            except Exception as e:
                failed_stores.append(store_name)
                print(f"  ❌ 오류: {str(e)[:50]}")
        
        browser.close()
    
    # 결과 저장
    if all_products:
        save_results(all_products, successful_stores, failed_stores)
    
    return all_products, successful_stores, failed_stores

def extract_products(text, store_name):
    """텍스트에서 상품 정보 추출"""
    products = []
    lines = text.split('\n')
    
    # 가격 패턴: €X.XX 또는 X,XX
    price_pattern = r'€?\s*(\d+)[,.](\d{2})'
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        # 상품명 조건
        if 5 < len(line) < 100 and not line.isdigit():
            # 다음 줄에서 가격 찾기
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                price_match = re.search(price_pattern, next_line)
                if price_match:
                    products.append({
                        'name': line,
                        'price': f"€{price_match.group(1)}.{price_match.group(2)}",
                        'supermarket': store_name
                    })
            
            # 현재 줄에서 가격 찾기
            price_match = re.search(price_pattern, line)
            if price_match:
                # 가격 앞 텍스트를 상품명으로
                name_part = line[:price_match.start()].strip()
                if len(name_part) > 5:
                    products.append({
                        'name': name_part,
                        'price': f"€{price_match.group(1)}.{price_match.group(2)}",
                        'supermarket': store_name
                    })
    
    # 중복 제거
    seen = set()
    unique = []
    for p in products:
        key = p['name'].lower()
        if key not in seen:
            seen.add(key)
            unique.append(p)
    
    return unique[:50]  # 최대 50개

def save_results(products, successful, failed):
    """결과 저장"""
    today = datetime.now()
    if today.weekday() == 0:
        next_monday = today
    else:
        next_monday = today + timedelta(days=(7 - today.weekday()))
    next_sunday = next_monday + timedelta(days=6)
    
    weekly_data = {
        'week_number': f"{next_monday.year}-{next_monday.isocalendar()[1]:02d}",
        'scraped_at': datetime.now().isoformat(),
        'total_products': len(products),
        'supermarkets': {'successful': successful, 'failed': failed},
        'products': [
            {
                'supermarket': p['supermarket'],
                'product_name': p['name'],
                'price_info': p.get('price'),
                'start_date': next_monday.isoformat(),
                'end_date': next_sunday.isoformat(),
                'source': 'supermarktaanbiedingen.com',
                'scraped_at': datetime.now().isoformat()
            }
            for p in products
        ]
    }
    
    output = PROJECT_ROOT / "data" / "weekly_sales.json"
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(weekly_data, f, ensure_ascii=False, indent=2)
    print(f"\n📁 weekly_sales.json 저장: {len(products)}개 상품")

if __name__ == "__main__":
    products, successful, failed = scrape_supermarkt_aanbiedingen()
    
    print(f"\n{'='*60}")
    print(f"🎉 크롤링 완료!")
    print(f"  성공: {successful}")
    print(f"  실패: {failed}")
    print(f"  총 상품: {len(products)}개")
    
    # 마트별 상품 수
    print("\n📊 마트별 상품 수:")
    store_counts = {}
    for p in products:
        store = p['supermarket']
        store_counts[store] = store_counts.get(store, 0) + 1
    for store, count in store_counts.items():
        print(f"  - {store}: {count}개")
    
    # 샘플 상품
    print("\n📋 샘플 상품 (각 마트별 3개):")
    for store in successful:
        store_products = [p for p in products if p['supermarket'] == store][:3]
        print(f"\n  [{store}]")
        for p in store_products:
            print(f"    - {p['name']}: {p.get('price', 'N/A')}")
