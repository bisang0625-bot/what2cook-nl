"""
공식 사이트 + Gemini Vision 크롤러
각 마트 공식 사이트의 스크린샷을 AI로 분석
"""
import os
import json
import time
import base64
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

# Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    try:
        import sys
        sys.path.insert(0, str(PROJECT_ROOT))
        import config
        api_key = config.GEMINI_API_KEY
    except:
        pass

client = genai.Client(api_key=api_key)

STORES = {
    'Albert Heijn': {
        'url': 'https://www.ah.nl/bonus',
        'click_next_week': True
    },
    'Dirk': {
        'url': 'https://www.dirk.nl/aanbiedingen',
        'click_next_week': False
    },
    'Aldi': {
        'url': 'https://www.aldi.nl/aanbiedingen.html',
        'click_next_week': False
    },
    'Jumbo': {
        'url': 'https://www.jumbo.com/aanbiedingen',
        'click_next_week': True
    },
    'Lidl': {
        'url': 'https://www.lidl.nl/c/aanbiedingen',
        'click_next_week': True
    },
    'Plus': {
        'url': 'https://www.plus.nl/aanbiedingen',
        'click_next_week': True
    },
    'Hoogvliet': {
        'url': 'https://www.hoogvliet.com/aanbiedingen',
        'click_next_week': False
    },
    'Coop': {
        'url': 'https://www.coop.nl/aanbiedingen',
        'click_next_week': False
    }
}

def get_next_monday():
    """다음 월요일"""
    today = datetime.now()
    return today if today.weekday() == 0 else today + timedelta(days=(7 - today.weekday()))

def capture_screenshot(name, url, click_next_week):
    """마트 페이지 스크린샷 캡처"""
    print(f"\n{'='*70}")
    print(f"📸 {name} 스크린샷 캡처 중...")
    print(f"{'='*70}")
    print(f"🔗 {url}")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = context.new_page()
            page.goto(url, timeout=60000)
            page.wait_for_load_state("networkidle")
            time.sleep(5)
            
            # 쿠키 동의
            try:
                for text in ['accepteren', 'accept', 'akkoord']:
                    try:
                        button = page.get_by_role("button", name=text).first
                        if button.is_visible():
                            button.click()
                            time.sleep(2)
                            print("🍪 쿠키 동의 완료")
                            break
                    except:
                        pass
            except:
                pass
            
            # '다음 주' 버튼 클릭 시도
            if click_next_week:
                print("🖱️  '다음 주' 버튼 클릭 시도...")
                try:
                    texts = ['Volgende week', 'volgende week', 'Vanaf maandag']
                    for text in texts:
                        try:
                            element = page.get_by_text(text, exact=False).first
                            if element.is_visible():
                                element.click()
                                time.sleep(3)
                                print(f"  ✅ '{text}' 클릭 성공")
                                break
                        except:
                            pass
                except:
                    print("  ⚠️ 다음 주 버튼을 찾을 수 없습니다")
            
            # 스크린샷
            screenshot_dir = PROJECT_ROOT / "data" / "screenshots"
            screenshot_dir.mkdir(exist_ok=True)
            screenshot_path = screenshot_dir / f"{name.lower().replace(' ', '_')}_ai.png"
            
            page.screenshot(path=str(screenshot_path), full_page=True)
            file_size = screenshot_path.stat().st_size / 1024
            print(f"✅ 저장 완료: {screenshot_path.name} ({file_size:.0f}KB)")
            
            browser.close()
            return screenshot_path
            
    except Exception as e:
        print(f"❌ 오류: {str(e)}")
        return None

def analyze_with_ai(screenshot_path, store_name):
    """Gemini Vision으로 스크린샷 분석"""
    print(f"🔍 AI 분석 중...")
    
    try:
        with open(screenshot_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        prompt = f"""이 이미지는 네덜란드 슈퍼마켓 **{store_name}**의 공식 세일 페이지입니다.

**작업**: 이미지에서 보이는 **모든 식품 세일 상품**을 추출하세요.

**중요**:
1. **식품만** 추출 (고기, 생선, 채소, 과일, 유제품, 음료, 빵, 과자 등)
2. 비식품 제외 (옷, 가전, 기차표, 가구 등)
3. 상품명은 네덜란드어 원문 그대로
4. 최소 20개 이상 추출

**추출 정보**:
- 상품명 (완전한 이름)
- 가격 (€ 표시)
- 할인 정보 (1+1, korting, 할인율 등)

**JSON 형식만 출력 (다른 텍스트 없이)**:
```json
[
  {{"name": "Verse kipfilet", "price": "€5.49", "discount": "25% korting"}},
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
        import re
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
                name_lower = item['name'].lower()
                # 비식품 필터링
                non_food = ['gordijn', 'dekbed', 'ticket', 'trein', 'toiletblok', 'speelgoed']
                if not any(kw in name_lower for kw in non_food):
                    products.append({
                        'name': item['name'],
                        'price': item.get('price'),
                        'discount': item.get('discount'),
                        'supermarket': store_name
                    })
        
        print(f"✅ {len(products)}개 상품 추출!")
        return products
        
    except Exception as e:
        print(f"❌ AI 분석 오류: {str(e)}")
        return []

def save_results(all_products, successful, failed):
    """결과 저장"""
    next_monday = get_next_monday()
    next_sunday = next_monday + timedelta(days=6)
    
    data = {
        'week_number': f"{next_monday.year}-{next_monday.isocalendar()[1]:02d}",
        'sale_period': f"{next_monday.strftime('%Y-%m-%d')} ~ {next_sunday.strftime('%Y-%m-%d')}",
        'scraped_at': datetime.now().isoformat(),
        'total_products': len(all_products),
        'supermarkets': {'successful': successful, 'failed': failed},
        'products': [
            {
                'supermarket': p['supermarket'],
                'product_name': p['name'],
                'price_info': p.get('price'),
                'discount_info': p.get('discount'),
                'start_date': next_monday.isoformat(),
                'end_date': next_sunday.isoformat(),
                'source': 'official_website_ai',
                'scraped_at': datetime.now().isoformat()
            }
            for p in all_products
        ]
    }
    
    output = PROJECT_ROOT / "data" / "weekly_sales.json"
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n💾 {output.name} 저장 완료")

def main():
    """메인 실행"""
    print("\n" + "="*70)
    print("🤖 공식 사이트 + AI Vision 크롤러")
    print("="*70)
    
    next_monday = get_next_monday()
    print(f"📅 주차: {next_monday.year}-{next_monday.isocalendar()[1]:02d}주")
    print(f"📆 기간: {next_monday.strftime('%Y-%m-%d')} (월) 시작\n")
    
    all_products = []
    successful = []
    failed = []
    
    for name, info in STORES.items():
        # 1. 스크린샷 캡처
        screenshot = capture_screenshot(name, info['url'], info['click_next_week'])
        
        if screenshot:
            # 2. AI 분석
            products = analyze_with_ai(screenshot, name)
            
            if products and len(products) >= 5:
                all_products.extend(products)
                successful.append(name)
            else:
                failed.append(name)
        else:
            failed.append(name)
        
        # 대기
        print("\n⏳ 다음 마트 대기...\n")
        time.sleep(5)
    
    # 결과
    if all_products:
        save_results(all_products, successful, failed)
        
        print("\n" + "="*70)
        print("📊 결과 요약")
        print("="*70)
        print(f"✅ 성공: {len(successful)}개")
        for store in successful:
            count = len([p for p in all_products if p['supermarket'] == store])
            print(f"   - {store}: {count}개")
        
        if failed:
            print(f"\n⚠️ 실패: {len(failed)}개")
            for store in failed:
                print(f"   - {store}")
        
        print(f"\n📦 총 {len(all_products)}개 상품")

if __name__ == "__main__":
    main()
