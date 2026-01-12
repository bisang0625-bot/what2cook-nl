"""
Albert Heijn 공식 Bonus 페이지 크롤러
실제 Bonus 페이지에서 다음 주 세일 정보를 정확하게 수집
"""
import os
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta

# 환경 설정
PROJECT_ROOT = Path(__file__).parent.parent
LOCAL_BROWSERS_PATH = PROJECT_ROOT / "pw-browsers"
if LOCAL_BROWSERS_PATH.exists():
    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(LOCAL_BROWSERS_PATH)

def get_next_monday():
    """다음 월요일 날짜 계산"""
    today = datetime.now()
    if today.weekday() == 0:
        return today
    return today + timedelta(days=(7 - today.weekday()))

def scrape_ah_bonus():
    """Albert Heijn Bonus 페이지 크롤링"""
    print("\n🛒 Albert Heijn 공식 Bonus 페이지 크롤링")
    print("="*60)
    
    products = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # 디버그용 headless=False
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        
        page = context.new_page()
        
        # Albert Heijn Bonus 페이지
        url = "https://www.ah.nl/bonus"
        print(f"🔗 {url}")
        page.goto(url, timeout=60000)
        
        # 페이지 로딩 대기
        page.wait_for_load_state("networkidle")
        time.sleep(5)
        
        # 쿠키 동의
        try:
            cookie_selectors = [
                'button:has-text("Accepteren")',
                'button:has-text("Accept")',
                '[data-testid="consent-accept"]'
            ]
            for selector in cookie_selectors:
                try:
                    button = page.locator(selector).first
                    if button.is_visible():
                        button.click()
                        time.sleep(2)
                        break
                except:
                    pass
        except:
            pass
        
        print("📸 페이지 스크린샷 저장 중...")
        screenshot_dir = PROJECT_ROOT / "data" / "screenshots"
        screenshot_dir.mkdir(exist_ok=True)
        page.screenshot(path=str(screenshot_dir / "ah-bonus-debug.png"), full_page=True)
        
        print("🔍 상품 정보 추출 중...")
        
        # 여러 방법으로 시도
        try:
            # 방법 1: 상품 카드 찾기
            product_cards = page.locator('[data-testhook="product-card"], article, [class*="product"]').all()
            print(f"발견된 요소: {len(product_cards)}개")
            
            for i, card in enumerate(product_cards[:30]):  # 최대 30개
                try:
                    text = card.inner_text()
                    if len(text) > 10:  # 의미있는 텍스트
                        # 상품명 추출 (간단하게)
                        lines = [line.strip() for line in text.split('\n') if line.strip()]
                        if lines:
                            name = lines[0]
                            price = None
                            discount = None
                            
                            # 가격 찾기
                            for line in lines:
                                if '€' in line or 'euro' in line.lower():
                                    price = line
                                if '+' in line or 'korting' in line.lower() or 'gratis' in line.lower():
                                    discount = line
                            
                            if name and len(name) > 3:
                                products.append({
                                    'name': name,
                                    'price': price,
                                    'discount': discount
                                })
                                print(f"  {i+1}. {name}")
                except:
                    continue
        except Exception as e:
            print(f"⚠️ 추출 오류: {str(e)}")
        
        # HTML 저장 (디버그용)
        html_path = PROJECT_ROOT / "data" / "ah_bonus_debug.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(page.content())
        print(f"💾 HTML 저장: {html_path.name}")
        
        input("\n⏸️  브라우저를 확인하세요. 계속하려면 Enter를 누르세요...")
        
        browser.close()
    
    return products

def save_products(products):
    """상품 저장"""
    next_monday = get_next_monday()
    next_sunday = next_monday + timedelta(days=6)
    
    data = {
        'week_number': f"{next_monday.year}-{next_monday.isocalendar()[1]:02d}",
        'sale_period': f"{next_monday.strftime('%Y-%m-%d')} ~ {next_sunday.strftime('%Y-%m-%d')}",
        'scraped_at': datetime.now().isoformat(),
        'total_products': len(products),
        'supermarkets': {
            'successful': ['Albert Heijn'],
            'failed': []
        },
        'products': [
            {
                'supermarket': 'Albert Heijn',
                'product_name': p['name'],
                'price_info': p.get('price'),
                'discount_info': p.get('discount'),
                'start_date': next_monday.isoformat(),
                'end_date': next_sunday.isoformat(),
                'source': 'ah.nl/bonus (official)',
                'scraped_at': datetime.now().isoformat()
            }
            for p in products
        ]
    }
    
    output = PROJECT_ROOT / "data" / "weekly_sales.json"
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 {len(products)}개 상품 저장 완료")

if __name__ == "__main__":
    products = scrape_ah_bonus()
    
    if products:
        print(f"\n✅ {len(products)}개 상품 수집 완료")
        save_products(products)
    else:
        print("\n⚠️ 상품을 찾지 못했습니다")
        print("HTML과 스크린샷을 확인하여 페이지 구조를 분석하세요")
