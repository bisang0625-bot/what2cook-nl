"""
최종 크롤러 - Albert Heijn 특별 처리 + 7개 마트
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

# 7개 마트 (Lidl 제외)
STORES = {
    'Albert Heijn': {
        'url': 'https://www.ah.nl/bonus',
        'special_handling': True,  # 특별 처리
        'timeout': 120000,
        'wait_time': 10,  # 더 긴 대기
        'scroll': True    # 스크롤 활성화
    },
    'Jumbo': {
        'url': 'https://www.jumbo.com/aanbiedingen',
        'click_next_week': True,
        'timeout': 120000,
        'wait_time': 8
    },
    'Dirk': {
        'url': 'https://www.dirk.nl/aanbiedingen',
        'click_next_week': False,
        'timeout': 120000,
        'wait_time': 8
    },
    'Aldi': {
        'url': 'https://www.aldi.nl/aanbiedingen.html',
        'click_next_week': False,
        'timeout': 90000,
        'wait_time': 6
    },
    'Plus': {
        'url': 'https://www.plus.nl/aanbiedingen',
        'click_next_week': True,
        'timeout': 90000,
        'wait_time': 6
    },
    'Hoogvliet': {
        'url': 'https://www.hoogvliet.com/aanbiedingen',
        'click_next_week': False,
        'timeout': 90000,
        'wait_time': 6
    },
    'Coop': {
        'url': 'https://www.coop.nl/aanbiedingen',
        'click_next_week': False,
        'timeout': 120000,
        'wait_time': 8
    }
}

def get_next_monday():
    """다음 월요일"""
    today = datetime.now()
    return today if today.weekday() == 0 else today + timedelta(days=(7 - today.weekday()))

def capture_screenshot_ah_special(name, config):
    """Albert Heijn 특별 처리"""
    print(f"\n{'='*70}")
    print(f"📸 {name} 스크린샷 캡처 (특별 처리)")
    print(f"{'='*70}")
    print(f"🔗 {config['url']}")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = context.new_page()
            
            print(f"⏱️  타임아웃: {config['timeout']/1000}초")
            page.goto(config['url'], timeout=config['timeout'])
            page.wait_for_load_state("networkidle", timeout=config['timeout'])
            
            # 쿠키 동의
            try:
                for text in ['accepteren', 'accept', 'akkoord']:
                    try:
                        button = page.get_by_role("button", name=text, exact=False).first
                        if button.is_visible(timeout=2000):
                            button.click()
                            time.sleep(2)
                            print("🍪 쿠키 동의 완료")
                            break
                    except:
                        pass
            except:
                pass
            
            # 페이지가 완전히 로드될 때까지 대기
            print(f"⏳ 페이지 로딩 대기: {config['wait_time']}초")
            time.sleep(config['wait_time'])
            
            # 스크롤 다운 (Lazy loading 트리거)
            if config.get('scroll'):
                print("📜 페이지 스크롤 중...")
                for i in range(3):
                    page.evaluate("window.scrollBy(0, window.innerHeight)")
                    time.sleep(2)
                
                # 다시 맨 위로
                page.evaluate("window.scrollTo(0, 0)")
                time.sleep(2)
            
            # 상품이 로드되었는지 확인
            try:
                # AH의 일반적인 상품 요소
                selectors = [
                    'article[data-testhook="product-card"]',
                    'div[class*="product"]',
                    'article'
                ]
                
                found = False
                for selector in selectors:
                    count = page.locator(selector).count()
                    if count > 0:
                        print(f"✅ {count}개 요소 발견: {selector}")
                        found = True
                        break
                
                if not found:
                    print("⚠️ 상품 요소를 찾을 수 없습니다")
            except:
                pass
            
            # 스크린샷
            screenshot_dir = PROJECT_ROOT / "data" / "screenshots"
            screenshot_dir.mkdir(exist_ok=True)
            screenshot_path = screenshot_dir / f"{name.lower().replace(' ', '_')}_final.png"
            
            page.screenshot(path=str(screenshot_path), full_page=True)
            file_size = screenshot_path.stat().st_size / 1024
            print(f"✅ 저장 완료: {screenshot_path.name} ({file_size:.0f}KB)")
            
            browser.close()
            return screenshot_path
            
    except Exception as e:
        print(f"❌ 오류: {str(e)[:150]}")
        return None

def capture_screenshot_standard(name, config):
    """일반 마트 처리"""
    print(f"\n{'='*70}")
    print(f"📸 {name} 스크린샷 캡처")
    print(f"{'='*70}")
    print(f"🔗 {config['url']}")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = context.new_page()
            
            timeout = config.get('timeout', 90000)
            page.goto(config['url'], timeout=timeout)
            page.wait_for_load_state("networkidle", timeout=timeout)
            
            wait_time = config.get('wait_time', 6)
            time.sleep(wait_time)
            
            # 쿠키 동의
            try:
                for text in ['accepteren', 'accept', 'akkoord']:
                    try:
                        button = page.get_by_role("button", name=text, exact=False).first
                        if button.is_visible(timeout=2000):
                            button.click()
                            time.sleep(2)
                            print("🍪 쿠키 동의 완료")
                            break
                    except:
                        pass
            except:
                pass
            
            # 다음 주 버튼 클릭
            if config.get('click_next_week'):
                print("🖱️  '다음 주' 버튼 클릭 시도...")
                try:
                    for text in ['Volgende week', 'volgende week', 'Vanaf maandag']:
                        try:
                            elements = page.get_by_text(text, exact=False).all()
                            for element in elements:
                                if element.is_visible(timeout=1000):
                                    element.click()
                                    time.sleep(4)
                                    print(f"  ✅ '{text}' 클릭 성공")
                                    break
                        except:
                            pass
                except:
                    pass
            
            # 스크린샷
            screenshot_dir = PROJECT_ROOT / "data" / "screenshots"
            screenshot_dir.mkdir(exist_ok=True)
            screenshot_path = screenshot_dir / f"{name.lower().replace(' ', '_')}_final.png"
            
            page.screenshot(path=str(screenshot_path), full_page=True)
            file_size = screenshot_path.stat().st_size / 1024
            print(f"✅ 저장 완료: {screenshot_path.name} ({file_size:.0f}KB)")
            
            browser.close()
            return screenshot_path
            
    except Exception as e:
        print(f"❌ 오류: {str(e)[:150]}")
        return None

def analyze_with_ai(screenshot_path, store_name):
    """AI 분석"""
    print(f"🔍 AI 분석 중...")
    
    try:
        with open(screenshot_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        prompt = f"""이 이미지는 네덜란드 슈퍼마켓 **{store_name}**의 공식 세일 페이지입니다.

**작업**: 이미지에서 보이는 **모든 식품 세일 상품** 추출

**포함**: 고기, 생선, 채소, 과일, 유제품, 음료, 빵, 과자, 냉동식품
**제외**: 비식품 (옷, 가전, 기차표, 가구, 장난감, 화장품)

**필수 조건**:
- 최소 15개 이상 식품
- 상품명은 네덜란드어 원문
- 완전한 이름 (약어 금지)

**JSON만 출력**:
[
  {{"name": "Verse kipfilet", "price": "€5.49", "discount": "25% korting"}},
  {{"name": "Hollandse aardappelen", "price": "€1.99", "discount": null}}
]"""

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
            ],
            config=types.GenerateContentConfig(temperature=0.3, max_output_tokens=8000)
        )
        
        response_text = response.text.strip()
        
        # JSON 추출
        import re
        if '```json' in response_text:
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(1)
        elif '[' in response_text:
            start = response_text.index('[')
            end = response_text.rindex(']') + 1
            response_text = response_text[start:end]
        
        products_data = json.loads(response_text)
        
        products = []
        for item in products_data:
            if isinstance(item, dict) and 'name' in item:
                name = item['name']
                if len(name) >= 3 and len(name) <= 150:
                    products.append({
                        'name': name,
                        'price': item.get('price'),
                        'discount': item.get('discount'),
                        'supermarket': store_name
                    })
        
        if products:
            print(f"✅ {len(products)}개 식품 추출!")
            return products
        else:
            print("⚠️ 추출된 식품이 없습니다")
            return []
        
    except Exception as e:
        print(f"❌ AI 분석 오류: {str(e)[:150]}")
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
                'source': 'official_website_final',
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
    print("🤖 최종 크롤러 - 7개 마트 (Albert Heijn 특별 처리)")
    print("="*70)
    print("📝 참고: Lidl은 제외되었습니다 (추후 추가 가능)\n")
    
    next_monday = get_next_monday()
    print(f"📅 주차: {next_monday.year}-{next_monday.isocalendar()[1]:02d}주")
    print(f"📆 기간: {next_monday.strftime('%Y-%m-%d')} (월) 시작\n")
    
    all_products = []
    successful = []
    failed = []
    
    for name, config in STORES.items():
        # Albert Heijn은 특별 처리
        if config.get('special_handling'):
            screenshot = capture_screenshot_ah_special(name, config)
        else:
            screenshot = capture_screenshot_standard(name, config)
        
        if screenshot:
            products = analyze_with_ai(screenshot, name)
            
            if products and len(products) >= 5:
                all_products.extend(products)
                successful.append(name)
                print(f"  💚 {name} 성공!")
            else:
                failed.append(name)
                print(f"  ⚠️ {name} 실패")
        else:
            failed.append(name)
        
        print("\n⏳ 다음 마트 대기...\n")
        time.sleep(8)
    
    # 결과
    if all_products:
        save_results(all_products, successful, failed)
        
        print("\n" + "="*70)
        print("📊 최종 결과")
        print("="*70)
        print(f"✅ 성공: {len(successful)}개 마트")
        for store in successful:
            count = len([p for p in all_products if p['supermarket'] == store])
            print(f"   - {store}: {count}개 상품")
        
        if failed:
            print(f"\n⚠️ 실패: {len(failed)}개 마트")
            for store in failed:
                print(f"   - {store}")
        
        print(f"\n📦 총 {len(all_products)}개 상품 수집")
        print("\n✅ 다음 단계: python3 recipe_matcher.py")
        return True
    else:
        print("\n❌ 모든 마트 실패")
        return False

if __name__ == "__main__":
    main()
