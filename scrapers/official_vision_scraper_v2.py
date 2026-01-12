"""
공식 사이트 + Gemini Vision 크롤러 (개선 버전)
실패한 마트 재시도, 에러 핸들링 강화
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
        'click_next_week': True,
        'timeout': 120000,  # 2분
        'wait_time': 8
    },
    'Dirk': {
        'url': 'https://www.dirk.nl/aanbiedingen',
        'click_next_week': False,
        'timeout': 120000,
        'wait_time': 8
    },
    'Jumbo': {
        'url': 'https://www.jumbo.com/aanbiedingen',
        'click_next_week': True,
        'timeout': 120000,
        'wait_time': 8
    },
    'Lidl': {
        'url': 'https://www.lidl.nl/c/aanbiedingen',
        'click_next_week': True,
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

def capture_screenshot(name, config, retry=0):
    """마트 페이지 스크린샷 캡처 (재시도 로직)"""
    max_retries = 2
    
    print(f"\n{'='*70}")
    print(f"📸 {name} 스크린샷 캡처 중..." + (f" (재시도 {retry}/{max_retries})" if retry > 0 else ""))
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
            
            # 타임아웃 설정
            timeout = config.get('timeout', 90000)
            print(f"⏱️  타임아웃: {timeout/1000}초")
            
            page.goto(config['url'], timeout=timeout)
            page.wait_for_load_state("networkidle", timeout=timeout)
            
            wait_time = config.get('wait_time', 6)
            print(f"⏳ 페이지 렌더링 대기: {wait_time}초")
            time.sleep(wait_time)
            
            # 쿠키 동의
            try:
                for text in ['accepteren', 'accept', 'akkoord', 'toestaan', 'alle cookies']:
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
            
            # '다음 주' 버튼 클릭 시도
            if config.get('click_next_week'):
                print("🖱️  '다음 주' 버튼 클릭 시도...")
                clicked = False
                
                # 여러 방법으로 시도
                try:
                    # 방법 1: 텍스트로 찾기
                    for text in ['Volgende week', 'volgende week', 'Vanaf maandag', 'vanaf maandag']:
                        try:
                            elements = page.get_by_text(text, exact=False).all()
                            for element in elements:
                                if element.is_visible(timeout=1000):
                                    element.click()
                                    time.sleep(4)
                                    print(f"  ✅ '{text}' 클릭 성공")
                                    clicked = True
                                    break
                        except:
                            pass
                        if clicked:
                            break
                    
                    # 방법 2: href로 찾기
                    if not clicked:
                        try:
                            link = page.locator("a[href*='volgende']").first
                            if link.is_visible(timeout=1000):
                                link.click()
                                time.sleep(4)
                                print("  ✅ 'volgende' 링크 클릭 성공")
                                clicked = True
                        except:
                            pass
                    
                except:
                    pass
                
                if not clicked:
                    print("  ⚠️ 다음 주 버튼을 찾을 수 없습니다 (현재 페이지 사용)")
            
            # 스크린샷
            screenshot_dir = PROJECT_ROOT / "data" / "screenshots"
            screenshot_dir.mkdir(exist_ok=True)
            screenshot_path = screenshot_dir / f"{name.lower().replace(' ', '_')}_v2.png"
            
            page.screenshot(path=str(screenshot_path), full_page=True)
            file_size = screenshot_path.stat().st_size / 1024
            print(f"✅ 저장 완료: {screenshot_path.name} ({file_size:.0f}KB)")
            
            browser.close()
            return screenshot_path
            
    except Exception as e:
        print(f"❌ 오류: {str(e)[:100]}")
        
        # 재시도
        if retry < max_retries:
            print(f"🔄 {5}초 후 재시도...")
            time.sleep(5)
            return capture_screenshot(name, config, retry + 1)
        
        return None

def analyze_with_ai(screenshot_path, store_name, retry=0):
    """Gemini Vision으로 스크린샷 분석 (재시도 로직)"""
    max_retries = 2
    
    print(f"🔍 AI 분석 중..." + (f" (재시도 {retry}/{max_retries})" if retry > 0 else ""))
    
    try:
        with open(screenshot_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        prompt = f"""이 이미지는 네덜란드 슈퍼마켓 **{store_name}**의 공식 세일 페이지 스크린샷입니다.

**중요 작업**:
1. 이미지에서 보이는 **모든 식품 세일 상품**을 추출하세요
2. **식품만** 포함 (고기, 생선, 채소, 과일, 유제품, 음료, 빵, 과자, 냉동식품 등)
3. 비식품은 **절대 제외** (옷, 가전, 기차표, 가구, 장난감, 화장품 등)

**추출 정보**:
- 상품명: 네덜란드어 원문 그대로, 완전한 이름
- 가격: € 기호 포함
- 할인: 1+1, korting, halve prijs 등

**필수 조건**:
- 최소 15개 이상 식품 추출
- 상품명은 약어 사용 금지
- 이미지 전체를 꼼꼼히 스캔

**JSON 형식만 출력** (마크다운, 설명 없이 순수 JSON만):
[
  {{"name": "Verse kipfilet", "price": "€5.49", "discount": "25% korting"}},
  {{"name": "Hollandse aardappelen 2kg", "price": "€1.99", "discount": null}},
  {{"name": "Verse tomaten", "price": "€2.49", "discount": "1+1 gratis"}}
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
            config=types.GenerateContentConfig(
                temperature=0.3,  # 더 일관된 출력
                max_output_tokens=8000
            )
        )
        
        response_text = response.text.strip()
        
        # JSON 추출 (여러 방법 시도)
        import re
        
        # 방법 1: ```json 코드 블록
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(1)
        # 방법 2: ``` 코드 블록
        elif '```' in response_text:
            response_text = response_text.strip('`').strip()
            if response_text.startswith('json'):
                response_text = response_text[4:].strip()
        # 방법 3: [ 로 시작하는 부분 찾기
        elif '[' in response_text:
            start = response_text.index('[')
            end = response_text.rindex(']') + 1
            response_text = response_text[start:end]
        
        # JSON 파싱
        products_data = json.loads(response_text)
        
        if not isinstance(products_data, list):
            raise ValueError("JSON은 배열이어야 합니다")
        
        products = []
        for item in products_data:
            if isinstance(item, dict) and 'name' in item:
                name = item['name']
                name_lower = name.lower()
                
                # 비식품 필터링 (강화)
                non_food = [
                    'gordijn', 'dekbed', 'ticket', 'trein', 'toiletblok', 
                    'speelgoed', 'kleding', 'jurk', 'broek', 'shirt',
                    'vtwonen', 'home creation', 'servies', 'handdoek',
                    'lamp', 'stoel', 'tafel', 'kussen'
                ]
                
                if any(kw in name_lower for kw in non_food):
                    continue
                
                # 이름 길이 체크
                if len(name) < 3 or len(name) > 150:
                    continue
                
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
            raise ValueError("추출된 식품이 없습니다")
        
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON 파싱 오류: {str(e)[:100]}")
        print(f"  응답 시작: {response_text[:200] if 'response_text' in locals() else 'N/A'}")
        
        # 재시도
        if retry < max_retries:
            print(f"🔄 {3}초 후 AI 재분석...")
            time.sleep(3)
            return analyze_with_ai(screenshot_path, store_name, retry + 1)
        
        return []
        
    except Exception as e:
        print(f"❌ AI 분석 오류: {str(e)[:100]}")
        
        if retry < max_retries:
            print(f"🔄 {3}초 후 AI 재분석...")
            time.sleep(3)
            return analyze_with_ai(screenshot_path, store_name, retry + 1)
        
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
                'source': 'official_website_ai_v2',
                'scraped_at': datetime.now().isoformat()
            }
            for p in all_products
        ]
    }
    
    output = PROJECT_ROOT / "data" / "weekly_sales.json"
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n💾 {output.name} 저장 완료")

def main(only_failed=False):
    """메인 실행"""
    print("\n" + "="*70)
    print("🤖 공식 사이트 + AI Vision 크롤러 V2 (개선 버전)")
    print("="*70)
    
    next_monday = get_next_monday()
    print(f"📅 주차: {next_monday.year}-{next_monday.isocalendar()[1]:02d}주")
    print(f"📆 기간: {next_monday.strftime('%Y-%m-%d')} (월) 시작\n")
    
    # 이전 실패 마트 목록
    failed_stores = ['Albert Heijn', 'Dirk', 'Jumbo', 'Lidl', 'Coop']
    
    if only_failed:
        stores_to_scrape = {k: v for k, v in STORES.items() if k in failed_stores}
        print(f"🎯 실패한 마트만 재크롤링: {', '.join(stores_to_scrape.keys())}\n")
    else:
        stores_to_scrape = STORES
        print(f"🎯 전체 {len(STORES)}개 마트 크롤링\n")
    
    all_products = []
    successful = []
    failed = []
    
    for name, config in stores_to_scrape.items():
        # 1. 스크린샷 캡처
        screenshot = capture_screenshot(name, config)
        
        if screenshot:
            # 2. AI 분석
            products = analyze_with_ai(screenshot, name)
            
            if products and len(products) >= 5:
                all_products.extend(products)
                successful.append(name)
                print(f"  💚 {name} 성공!")
            else:
                failed.append(name)
                print(f"  ⚠️ {name} 실패 (상품 수 부족)")
        else:
            failed.append(name)
            print(f"  ❌ {name} 실패 (스크린샷 실패)")
        
        # 대기
        print("\n⏳ 다음 마트 대기 (API 제한 방지)...\n")
        time.sleep(8)
    
    # 결과
    if all_products:
        save_results(all_products, successful, failed)
        
        print("\n" + "="*70)
        print("📊 크롤링 결과 요약")
        print("="*70)
        print(f"✅ 성공: {len(successful)}개 마트")
        for store in successful:
            count = len([p for p in all_products if p['supermarket'] == store])
            print(f"   - {store}: {count}개 상품")
        
        if failed:
            print(f"\n⚠️ 실패: {len(failed)}개 마트")
            for store in failed:
                print(f"   - {store}")
        
        print(f"\n📦 총 {len(all_products)}개 상품 수집 완료")
        return True
    else:
        print("\n❌ 모든 마트 실패")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='슈퍼마켓 AI 크롤러 V2')
    parser.add_argument(
        '--failed-only',
        action='store_true',
        help='실패한 마트만 재크롤링'
    )
    
    args = parser.parse_args()
    
    success = main(only_failed=args.failed_only)
    
    if success:
        print("\n✅ 다음 단계: python3 recipe_matcher.py")
