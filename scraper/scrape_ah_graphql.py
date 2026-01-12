"""
Albert Heijn Bonus 페이지 GraphQL 데이터 추출
페이지에 포함된 Apollo Cache에서 프로모션 데이터를 추출합니다.
"""
import os
import json
import re
from pathlib import Path
from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta

# 브라우저 경로 설정
PROJECT_ROOT = Path(__file__).parent.parent
LOCAL_BROWSERS_PATH = PROJECT_ROOT / "pw-browsers"
if LOCAL_BROWSERS_PATH.exists():
    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(LOCAL_BROWSERS_PATH)

def scrape_ah_bonus_graphql():
    """Albert Heijn Bonus 페이지에서 GraphQL/Apollo 캐시 데이터 추출"""
    url = "https://www.ah.nl/bonus"
    products = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        
        # 네트워크 요청 캡처 설정
        api_responses = []
        
        def handle_response(response):
            """GraphQL API 응답 캡처"""
            if 'graphql' in response.url.lower() or 'api' in response.url.lower():
                try:
                    if response.status == 200 and 'json' in response.headers.get('content-type', ''):
                        data = response.json()
                        api_responses.append({
                            'url': response.url,
                            'data': data
                        })
                except:
                    pass
        
        page = context.new_page()
        page.on('response', handle_response)
        
        print(f"🔍 Albert Heijn Bonus 페이지 접속: {url}")
        page.goto(url, timeout=60000)
        page.wait_for_load_state("networkidle")
        
        # 쿠키 동의 처리
        try:
            cookie_selectors = [
                "button:has-text('Accepteren')",
                "button:has-text('Akkoord')",
                "[data-testid='accept-cookies']",
            ]
            for selector in cookie_selectors:
                try:
                    btn = page.locator(selector).first
                    if btn.is_visible(timeout=3000):
                        print("🍪 쿠키 동의 버튼 클릭")
                        btn.click()
                        import time
                        time.sleep(2)
                        break
                except:
                    continue
        except:
            pass
        
        # 페이지 스크롤 (더 많은 데이터 로딩)
        print("📜 페이지 스크롤 중...")
        for _ in range(5):
            page.evaluate("window.scrollBy(0, window.innerHeight)")
            import time
            time.sleep(1)
        
        # HTML 가져오기
        content = page.content()
        
        # Apollo Cache 데이터 추출
        print("🔎 Apollo Cache 데이터 검색 중...")
        
        # 방법 1: window.__APOLLO_STATE__ 찾기
        apollo_match = re.search(r'window\.__APOLLO_STATE__\s*=\s*(\{.*?\});', content, re.DOTALL)
        if apollo_match:
            try:
                apollo_data = json.loads(apollo_match.group(1))
                print(f"✅ Apollo State 발견! 키 수: {len(apollo_data)}")
                products = extract_products_from_apollo(apollo_data)
            except:
                pass
        
        # 방법 2: 스크립트 태그에서 JSON 데이터 추출
        if not products:
            print("📋 스크립트 태그에서 데이터 검색 중...")
            # Promotion: 패턴 찾기
            promotion_pattern = r'"Promotion:(\d+)":\s*\{[^}]*"__typename":\s*"Promotion"[^}]*\}'
            promotions = re.findall(promotion_pattern, content)
            print(f"  발견된 Promotion ID: {len(promotions)}개")
            
            # 상품 정보 추출 시도
            product_pattern = r'"title":\s*"([^"]+)".*?"price":\s*\{[^}]*"amount":\s*(\d+)'
            product_matches = re.findall(product_pattern, content)
            print(f"  발견된 상품 패턴: {len(product_matches)}개")
            
            for title, price in product_matches[:50]:
                products.append({
                    'name': title,
                    'price': f"€{int(price)/100:.2f}",
                    'supermarket': 'Albert Heijn'
                })
        
        # 방법 3: 캡처된 API 응답 분석
        if not products and api_responses:
            print(f"📡 캡처된 API 응답: {len(api_responses)}개")
            for resp in api_responses:
                if 'data' in resp and resp['data']:
                    products.extend(extract_products_from_api(resp['data']))
        
        # 방법 4: 직접 상품 카드 텍스트 추출
        if not products:
            print("🔍 페이지에서 직접 상품 정보 추출 시도...")
            # 상품 카드 선택자
            product_cards = page.locator('[data-testhook="product-card"], [data-testhook="bonus-card"], article').all()
            print(f"  상품 카드 요소: {len(product_cards)}개")
            
            for card in product_cards[:50]:
                try:
                    text = card.inner_text()
                    if text and len(text) > 5:
                        # 가격 추출
                        price_match = re.search(r'€?\s*(\d+)[,.](\d{2})', text)
                        price = f"€{price_match.group(1)}.{price_match.group(2)}" if price_match else None
                        
                        # 이름 추출 (첫 줄)
                        lines = [l.strip() for l in text.split('\n') if l.strip()]
                        name = lines[0] if lines else None
                        
                        if name and len(name) > 3:
                            products.append({
                                'name': name,
                                'price': price,
                                'supermarket': 'Albert Heijn'
                            })
                except:
                    continue
        
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
    
    # weekly_sales.json에도 저장 (크롤러 통합용)
    if products:
        today = datetime.now()
        if today.weekday() == 0:  # 월요일
            next_monday = today
        else:
            next_monday = today + timedelta(days=(7 - today.weekday()))
        next_sunday = next_monday + timedelta(days=6)
        
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
        print(f"📁 weekly_sales.json 저장 완료")
    
    return products

def extract_products_from_apollo(apollo_data):
    """Apollo State에서 상품 정보 추출"""
    products = []
    for key, value in apollo_data.items():
        if key.startswith('Product:') or key.startswith('Promotion:'):
            if isinstance(value, dict):
                name = value.get('title') or value.get('name')
                price = value.get('price', {})
                if isinstance(price, dict):
                    amount = price.get('amount')
                    if amount:
                        price = f"€{amount/100:.2f}"
                    else:
                        price = None
                
                if name:
                    products.append({
                        'name': name,
                        'price': price,
                        'supermarket': 'Albert Heijn'
                    })
    return products

def extract_products_from_api(data):
    """API 응답에서 상품 정보 추출"""
    products = []
    
    def search_products(obj, depth=0):
        if depth > 10:
            return
        if isinstance(obj, dict):
            if 'title' in obj and ('price' in obj or 'products' in obj):
                name = obj.get('title')
                price = obj.get('price', {})
                if isinstance(price, dict):
                    amount = price.get('amount')
                    price = f"€{amount/100:.2f}" if amount else None
                
                if name:
                    products.append({
                        'name': name,
                        'price': price,
                        'supermarket': 'Albert Heijn'
                    })
            
            for v in obj.values():
                search_products(v, depth + 1)
        elif isinstance(obj, list):
            for item in obj:
                search_products(item, depth + 1)
    
    search_products(data)
    return products

if __name__ == "__main__":
    products = scrape_ah_bonus_graphql()
    print(f"\n🎉 크롤링 완료! {len(products)}개 상품 수집")
    
    # 상위 10개 상품 출력
    print("\n📋 상위 10개 상품:")
    for i, p in enumerate(products[:10], 1):
        print(f"  {i}. {p['name']} - {p.get('price', 'N/A')}")
    
    # Speklappen 검색
    print("\n🔎 'Speklappen' 검색:")
    speklappen = [p for p in products if 'speklap' in p['name'].lower()]
    if speklappen:
        for p in speklappen:
            print(f"  ✅ {p['name']} - {p.get('price', 'N/A')}")
    else:
        print("  ❌ 'Speklappen' 상품을 찾지 못했습니다.")
