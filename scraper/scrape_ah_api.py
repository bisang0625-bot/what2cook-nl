"""
Albert Heijn 프로모션 API 직접 호출
네트워크 요청을 분석하여 실제 API 엔드포인트를 찾습니다.
"""
import os
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta

# 브라우저 경로 설정
PROJECT_ROOT = Path(__file__).parent.parent
LOCAL_BROWSERS_PATH = PROJECT_ROOT / "pw-browsers"
if LOCAL_BROWSERS_PATH.exists():
    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(LOCAL_BROWSERS_PATH)

def scrape_ah_via_network():
    """네트워크 요청을 캡처하여 AH 프로모션 데이터 추출"""
    url = "https://www.ah.nl/bonus"
    all_products = []
    captured_requests = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        
        def capture_response(response):
            """모든 API 응답 캡처"""
            url_lower = response.url.lower()
            if any(kw in url_lower for kw in ['graphql', 'promotion', 'bonus', 'product', 'api']):
                try:
                    if response.status == 200:
                        content_type = response.headers.get('content-type', '')
                        if 'json' in content_type:
                            body = response.json()
                            captured_requests.append({
                                'url': response.url,
                                'data': body
                            })
                            print(f"  📡 API 응답 캡처: {response.url[:80]}...")
                except Exception as e:
                    pass
        
        page = context.new_page()
        page.on('response', capture_response)
        
        print(f"🔍 Albert Heijn Bonus 페이지 접속 (네트워크 모니터링): {url}")
        page.goto(url, timeout=60000)
        page.wait_for_load_state("networkidle")
        
        # 쿠키 동의
        try:
            btn = page.locator("button:has-text('Accepteren')").first
            if btn.is_visible(timeout=3000):
                print("🍪 쿠키 동의")
                btn.click()
                time.sleep(2)
        except:
            pass
        
        # 스크롤하여 더 많은 데이터 로딩
        print("📜 페이지 스크롤 중...")
        for i in range(8):
            page.evaluate("window.scrollBy(0, window.innerHeight)")
            time.sleep(1.5)
            print(f"  스크롤 {i+1}/8 완료, 캡처된 요청: {len(captured_requests)}개")
        
        # 추가 대기
        time.sleep(3)
        
        browser.close()
    
    print(f"\n📊 총 {len(captured_requests)}개의 API 응답 캡처됨")
    
    # 캡처된 데이터에서 상품 정보 추출
    for req in captured_requests:
        products = extract_products_deep(req['data'])
        if products:
            print(f"  ✅ {req['url'][:50]}... 에서 {len(products)}개 상품 추출")
            all_products.extend(products)
    
    # 중복 제거
    seen = set()
    unique_products = []
    for p in all_products:
        key = p['name']
        if key not in seen:
            seen.add(key)
            unique_products.append(p)
    
    print(f"\n🎯 총 {len(unique_products)}개의 고유 상품 추출")
    
    # 결과 저장
    if unique_products:
        save_results(unique_products)
    
    return unique_products

def extract_products_deep(data, depth=0):
    """재귀적으로 데이터 구조 탐색하여 상품 정보 추출"""
    products = []
    
    if depth > 15:
        return products
    
    if isinstance(data, dict):
        # 상품 정보가 있는지 확인
        if 'title' in data or 'name' in data:
            name = data.get('title') or data.get('name')
            if name and isinstance(name, str) and len(name) > 2:
                # 가격 정보 추출
                price = None
                price_data = data.get('price') or data.get('priceInfo') or data.get('prices')
                if isinstance(price_data, dict):
                    amount = price_data.get('amount') or price_data.get('now') or price_data.get('unitPrice')
                    if amount:
                        if isinstance(amount, (int, float)):
                            if amount > 100:  # 센트 단위
                                price = f"€{amount/100:.2f}"
                            else:
                                price = f"€{amount:.2f}"
                elif isinstance(price_data, (int, float)):
                    if price_data > 100:
                        price = f"€{price_data/100:.2f}"
                    else:
                        price = f"€{price_data:.2f}"
                
                # 할인 정보
                discount = data.get('discountLabel') or data.get('bonusLabel') or data.get('shield')
                if isinstance(discount, dict):
                    discount = discount.get('text') or discount.get('label')
                
                products.append({
                    'name': name,
                    'price': price,
                    'discount': discount,
                    'supermarket': 'Albert Heijn'
                })
        
        # 하위 데이터 탐색
        for key, value in data.items():
            if key not in ['__typename', 'id', '__ref']:
                products.extend(extract_products_deep(value, depth + 1))
    
    elif isinstance(data, list):
        for item in data:
            products.extend(extract_products_deep(item, depth + 1))
    
    return products

def save_results(products):
    """결과 저장"""
    today = datetime.now()
    if today.weekday() == 0:
        next_monday = today
    else:
        next_monday = today + timedelta(days=(7 - today.weekday()))
    next_sunday = next_monday + timedelta(days=6)
    
    # ah_bonus_products.json 저장
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
    print(f"📁 ah_bonus_products.json 저장: {len(products)}개 상품")
    
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
                'discount_info': p.get('discount'),
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
    print(f"📁 weekly_sales.json 저장 완료")

if __name__ == "__main__":
    products = scrape_ah_via_network()
    
    print(f"\n🎉 크롤링 완료! {len(products)}개 상품 수집")
    
    # 상위 15개 상품 출력
    print("\n📋 상위 15개 상품:")
    for i, p in enumerate(products[:15], 1):
        discount = f" ({p['discount']})" if p.get('discount') else ""
        print(f"  {i}. {p['name']} - {p.get('price', 'N/A')}{discount}")
    
    # 특정 키워드 검색
    keywords = ['speklap', 'kip', 'gehakt', 'kaas', 'melk']
    print("\n🔎 키워드 검색:")
    for kw in keywords:
        found = [p for p in products if kw.lower() in p['name'].lower()]
        if found:
            print(f"  ✅ '{kw}': {len(found)}개 발견")
            for p in found[:3]:
                print(f"      - {p['name']} ({p.get('price', 'N/A')})")
        else:
            print(f"  ❌ '{kw}': 없음")
