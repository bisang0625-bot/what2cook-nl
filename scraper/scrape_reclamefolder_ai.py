"""
Reclamefolder AI 크롤러 - 전체 마트 대상 (개선 버전)
전단지 이미지를 Gemini Vision으로 분석하여 세일 정보 추출
"""
import os
import json
import time
import base64
import re
from pathlib import Path
from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
from google import genai
from google.genai import types
from dotenv import load_dotenv

# 환경 설정
load_dotenv()
PROJECT_ROOT = Path(__file__).parent.parent
LOCAL_BROWSERS_PATH = PROJECT_ROOT / "pw-browsers"
if LOCAL_BROWSERS_PATH.exists():
    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(LOCAL_BROWSERS_PATH)

# Gemini API 설정
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    try:
        import sys
        sys.path.insert(0, str(PROJECT_ROOT))
        import config
        api_key = config.GEMINI_API_KEY
    except:
        pass

if not api_key:
    raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")

client = genai.Client(api_key=api_key)

# 대상 마트
SUPERMARKETS = {
    'Albert Heijn': 'albert-heijn',
    'Jumbo': 'jumbo',
    'Lidl': 'lidl',
    'Dirk': 'dirk',
    'ALDI': 'aldi',
    'Plus': 'plus',
    'Hoogvliet': 'hoogvliet',
    'Coop': 'coop'
}

def get_next_monday():
    """다음 월요일 날짜 계산 (월요일이면 당일)"""
    today = datetime.now()
    if today.weekday() == 0:
        return today
    return today + timedelta(days=(7 - today.weekday()))

def scrape_supermarket(name, slug):
    """개별 마트 크롤링 (개선 버전)"""
    print(f"\n{'='*60}")
    print(f"🛒 {name} 크롤링 시작")
    print(f"{'='*60}")
    
    try:
        # 각 마트마다 새로운 브라우저 인스턴스 생성
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            
            url = f"https://www.reclamefolder.nl/{slug}"
            print(f"🔗 {url}")
            
            page = context.new_page()
            
            # 페이지 로드
            page.goto(url, timeout=60000)
            page.wait_for_load_state("networkidle")
            time.sleep(5)  # 충분한 대기 시간
            
            # 쿠키 동의
            try:
                cookie_btn = page.get_by_role("button", name=re.compile("allow|accept|akkoord|agree", re.IGNORECASE))
                if cookie_btn.count() > 0 and cookie_btn.first.is_visible():
                    cookie_btn.first.click()
                    time.sleep(2)
            except:
                pass
            
            # 페이지 제목 확인 (검증용)
            page_title = page.title()
            print(f"📄 페이지 제목: {page_title}")
            
            # 마트 이름이 페이지에 있는지 확인
            page_text = page.inner_text('body').lower()
            if slug not in page_text and name.lower() not in page_text:
                print(f"⚠️ 경고: 페이지에 '{name}' 정보가 없을 수 있습니다")
            
            # 스크린샷 캡처
            screenshot_dir = PROJECT_ROOT / "data" / "screenshots"
            screenshot_dir.mkdir(exist_ok=True)
            screenshot_path = screenshot_dir / f"{slug}.png"
            
            page.screenshot(path=str(screenshot_path), full_page=True)
            file_size = screenshot_path.stat().st_size / 1024  # KB
            print(f"📸 스크린샷 저장: {screenshot_path.name} ({file_size:.0f}KB)")
            
            browser.close()
        
        # AI 분석
        print("🔍 AI 이미지 분석 중...")
        products = analyze_image(screenshot_path, name, slug)
        
        if products:
            # 상품 검증: 다른 마트 브랜드 제외
            validated_products = validate_products(products, name)
            if validated_products:
                print(f"✅ {len(validated_products)}개 상품 추출 성공!")
                return validated_products
            else:
                print(f"⚠️ {name}: 검증된 상품이 없습니다")
                return []
        else:
            print(f"⚠️ {name}에서 상품을 찾을 수 없습니다")
            return []
            
    except Exception as e:
        print(f"❌ {name} 크롤링 실패: {str(e)}")
        return []

def validate_products(products, supermarket_name):
    """상품 검증: 다른 마트의 자체 브랜드 제외"""
    # 마트별 브랜드 키워드
    brand_keywords = {
        'Albert Heijn': ['ah ', 'ah-', 'albert heijn'],
        'Jumbo': ['jumbo '],
        'Lidl': ['lidl', 'freeway'],
        'ALDI': ['aldi'],
        'Plus': ['plus '],
        'Hoogvliet': ['hoogvliet'],
        'Coop': ['coop '],
        'Dirk': ['dirk']
    }
    
    validated = []
    for product in products:
        product_name = product['name'].lower()
        
        # 다른 마트의 브랜드 상품인지 확인
        is_other_brand = False
        for market, keywords in brand_keywords.items():
            if market != supermarket_name:
                for keyword in keywords:
                    if keyword in product_name:
                        is_other_brand = True
                        print(f"  ⚠️ 제외: '{product['name']}' (다른 마트 브랜드)")
                        break
                if is_other_brand:
                    break
        
        if not is_other_brand:
            validated.append(product)
    
    return validated

def analyze_image(image_path, supermarket_name, slug):
    """Gemini Vision으로 이미지 분석 (개선 버전)"""
    try:
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        prompt = f"""이 이미지는 네덜란드 슈퍼마켓 **{supermarket_name}**의 세일 전단지입니다.

**중요**: 이 전단지는 반드시 **{supermarket_name}** 마트의 것이어야 합니다. 다른 마트의 상품이 아닙니다.

**추출 작업:**
1. 전단지의 마트 이름이 **{supermarket_name}**인지 먼저 확인하세요
2. 전단지 전체에서 **식품** 세일 상품만 추출하세요 (의류, 가전, 기차표 제외)
3. 고기, 생선, 채소, 과일, 유제품, 음료, 빵 등 요리 재료만 포함

**추출 정보:**
- 상품명 (네덜란드어 원문, 완전한 이름)
- 가격 (€ 표시)
- 할인 조건 (1+1, korting 등)

**필수 조건:**
- **{supermarket_name} 자체 브랜드 우선** 추출
- 다른 슈퍼마켓 브랜드(AH, Jumbo 등)가 보이면 무시
- 최소 15개 이상 식품 추출
- 비식품(옷, 가전, 티켓) 제외

**JSON 형식만 출력 (다른 텍스트 없이):**
```json
[
  {{"name": "Verse kip filet", "price": "€5.49", "discount": "25% korting"}},
  {{"name": "Aardappelen", "price": "€1.99", "discount": null}}
]
```"""

        response = client.models.generate_content(
            model='gemini-2.0-flash-001',
            contents=[
                types.Content(
                    role='user',
                    parts=[
                        types.Part(text=prompt),
                        types.Part(inline_data=types.Blob(mime_type='image/png', data=image_data))
                    ]
                )
            ]
        )
        
        response_text = response.text.strip()
        
        # JSON 추출
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(1)
        elif response_text.startswith('```'):
            response_text = response_text.strip('`').strip()
            if response_text.startswith('json'):
                response_text = response_text[4:].strip()
        
        products_data = json.loads(response_text)
        
        products = []
        for item in products_data:
            if isinstance(item, dict) and 'name' in item:
                # 비식품 필터링
                name_lower = item['name'].lower()
                non_food_keywords = ['gordijn', 'dekbed', 'ticket', 'trein', 'toiletblok', 'vtwonen', 'home creation']
                if not any(keyword in name_lower for keyword in non_food_keywords):
                    products.append({
                        'name': item['name'],
                        'price': item.get('price'),
                        'discount': item.get('discount'),
                        'supermarket': supermarket_name
                    })
        
        return products
        
    except Exception as e:
        print(f"  ⚠️ AI 분석 오류: {str(e)}")
        return []

def save_results(all_products, successful_markets, failed_markets):
    """결과를 weekly_sales.json에 저장"""
    next_monday = get_next_monday()
    next_sunday = next_monday + timedelta(days=6)
    
    weekly_data = {
        'week_number': f"{next_monday.year}-{next_monday.isocalendar()[1]:02d}",
        'sale_period': f"{next_monday.strftime('%Y-%m-%d')} ~ {next_sunday.strftime('%Y-%m-%d')}",
        'scraped_at': datetime.now().isoformat(),
        'total_products': len(all_products),
        'supermarkets': {
            'successful': successful_markets,
            'failed': failed_markets
        },
        'products': [
            {
                'supermarket': p['supermarket'],
                'product_name': p['name'],
                'price_info': p.get('price'),
                'discount_info': p.get('discount'),
                'start_date': next_monday.isoformat(),
                'end_date': next_sunday.isoformat(),
                'source': 'reclamefolder.nl (AI Vision)',
                'scraped_at': datetime.now().isoformat()
            }
            for p in all_products
        ]
    }
    
    output = PROJECT_ROOT / "data" / "weekly_sales.json"
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(weekly_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 {output.name} 저장 완료")

def main():
    """메인 크롤링 실행"""
    print("\n" + "="*60)
    print("🤖 AI 크롤러 시작 - Reclamefolder.nl (개선 버전)")
    print("="*60)
    
    next_monday = get_next_monday()
    print(f"📅 대상 주차: {next_monday.year}-{next_monday.isocalendar()[1]:02d}주")
    print(f"📆 세일 기간: {next_monday.strftime('%Y-%m-%d')} (월) 시작\n")
    
    all_products = []
    successful_markets = []
    failed_markets = []
    
    for name, slug in SUPERMARKETS.items():
        products = scrape_supermarket(name, slug)
        
        if products:
            all_products.extend(products)
            successful_markets.append(name)
        else:
            failed_markets.append(name)
        
        # API 제한 방지를 위해 대기 (중요!)
        print("⏳ 다음 마트 대기 중...")
        time.sleep(8)  # 더 긴 대기 시간
    
    # 결과 저장
    if all_products:
        save_results(all_products, successful_markets, failed_markets)
        
        print("\n" + "="*60)
        print("📊 크롤링 완료 요약")
        print("="*60)
        print(f"✅ 성공: {len(successful_markets)}개 마트")
        for market in successful_markets:
            count = len([p for p in all_products if p['supermarket'] == market])
            print(f"   - {market}: {count}개 상품")
        
        if failed_markets:
            print(f"\n⚠️ 실패: {len(failed_markets)}개 마트")
            for market in failed_markets:
                print(f"   - {market}")
        
        print(f"\n📦 총 {len(all_products)}개 상품 수집 완료")
    else:
        print("\n❌ 모든 마트에서 데이터 수집 실패")

if __name__ == "__main__":
    main()
