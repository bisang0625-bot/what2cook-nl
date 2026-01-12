"""
하이브리드 크롤러 - Albert Heijn은 Reclamefolder, 나머지는 공식 사이트
"""
import os
import json
import time
import base64
import re
from pathlib import Path
from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
from typing import Optional, Tuple
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

# 7개 마트 설정 (Lidl 제외)
# 로그 분석 결과 기반 최적화:
# - Albert Heijn: Reclamefolder에서 3개도 유효하므로 최소 상품 수 조정
# - Plus, Coop: 타임아웃 빈번 → 타임아웃 시간 증가
# - 모든 마트: 스크롤 적용으로 lazy loading 콘텐츠 캡처
STORES = {
    # Albert Heijn - Reclamefolder 사용 (이전에 작동함!)
    'Albert Heijn': {
        'url': 'https://www.reclamefolder.nl/albert-heijn',
        'source': 'reclamefolder',
        'timeout': 120000,  # 90초 → 120초 (안정성 향상)
        'wait_time': 10,    # 8초 → 10초 (렌더링 대기 증가)
        'scroll': True,
        'scroll_iterations': 6  # 스크롤 횟수 증가
    },
    # 나머지 - 공식 사이트
    'Jumbo': {
        'url': 'https://www.jumbo.com/aanbiedingen',
        'source': 'official',
        'timeout': 120000,
        'wait_time': 8,
        'scroll': True,  # 스크롤 추가
        'scroll_iterations': 5
    },
    'Dirk': {
        'url': 'https://www.dirk.nl/aanbiedingen',
        'source': 'official',
        'timeout': 120000,
        'wait_time': 8,
        'scroll': True,  # 스크롤 추가
        'scroll_iterations': 5
    },
    'Aldi': {
        'url': 'https://www.aldi.nl/aanbiedingen.html',
        'source': 'official',
        'timeout': 120000,  # 90초 → 120초
        'wait_time': 8,     # 6초 → 8초
        'scroll': True,     # 스크롤 추가
        'scroll_iterations': 5
    },
    'Plus': {
        'url': 'https://www.plus.nl/aanbiedingen',
        'source': 'official',
        'timeout': 150000,  # 90초 → 150초 (타임아웃 빈번)
        'wait_time': 10,    # 6초 → 10초
        'scroll': True,     # 스크롤 추가
        'scroll_iterations': 6  # 더 많은 스크롤
    },
    'Hoogvliet': {
        'url': 'https://www.hoogvliet.com/aanbiedingen',
        'source': 'official',
        'timeout': 120000,  # 90초 → 120초
        'wait_time': 8,     # 6초 → 8초
        'scroll': True,     # 스크롤 추가
        'scroll_iterations': 5
    },
    'Coop': {
        'url': 'https://www.coop.nl/aanbiedingen',
        'source': 'official',
        'timeout': 150000,  # 120초 → 150초 (타임아웃 빈번)
        'wait_time': 10,    # 8초 → 10초
        'scroll': True,     # 스크롤 추가
        'scroll_iterations': 6  # 더 많은 스크롤
    }
}

def get_next_monday():
    today = datetime.now()
    return today if today.weekday() == 0 else today + timedelta(days=(7 - today.weekday()))

def capture_screenshot(name, config, retry=0):
    """스크린샷 캡처"""
    max_retries = 2
    
    print(f"\n{'='*70}")
    print(f"📸 {name} 스크린샷 캡처" + (f" (재시도 {retry})" if retry > 0 else ""))
    print(f"{'='*70}")
    print(f"🔗 {config['url']}")
    print(f"📍 소스: {config['source']}")
    
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
            
            wait_time = config.get('wait_time', 5)
            print(f"⏳ 대기: {wait_time}초")
            time.sleep(wait_time)
            
            # 스크롤 (lazy loading 트리거)
            if config.get('scroll'):
                print("📜 페이지 스크롤...")
                scroll_iterations = config.get('scroll_iterations', 5)
                for i in range(scroll_iterations):
                    page.evaluate("window.scrollBy(0, 800)")
                    time.sleep(1.2)  # 스크롤 간 대기 시간 증가
                # 맨 아래까지 스크롤
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)
                # 다시 위로
                page.evaluate("window.scrollTo(0, 0)")
                time.sleep(2)
            
            # 쿠키 동의
            try:
                for text in ['accepteren', 'accept', 'akkoord', 'allow', 'agree']:
                    try:
                        button = page.get_by_role("button", name=re.compile(text, re.IGNORECASE)).first
                        if button.is_visible(timeout=2000):
                            button.click()
                            time.sleep(2)
                            print("🍪 쿠키 동의 완료")
                            break
                    except:
                        pass
            except:
                pass
            
            # 스크린샷
            screenshot_dir = PROJECT_ROOT / "data" / "screenshots"
            screenshot_dir.mkdir(exist_ok=True)
            screenshot_path = screenshot_dir / f"{name.lower().replace(' ', '_')}_hybrid.png"
            
            page.screenshot(path=str(screenshot_path), full_page=True)
            file_size = screenshot_path.stat().st_size / 1024
            print(f"✅ 저장: {screenshot_path.name} ({file_size:.0f}KB)")
            
            browser.close()
            return screenshot_path
            
    except Exception as e:
        print(f"❌ 오류: {str(e)[:100]}")
        
        if retry < max_retries:
            print(f"🔄 5초 후 재시도...")
            time.sleep(5)
            return capture_screenshot(name, config, retry + 1)
        
        return None

def analyze_with_ai(screenshot_path, store_name, retry=0):
    """AI 분석"""
    max_retries = 2
    
    print(f"🔍 AI 분석 중..." + (f" (재시도 {retry})" if retry > 0 else ""))
    
    try:
        with open(screenshot_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        # Albert Heijn용 특별 프롬프트 (Reclamefolder 페이지 구조 고려)
        if store_name == "Albert Heijn":
            prompt = f"""이 이미지는 네덜란드 슈퍼마켓 세일 정보 페이지입니다.

**작업**: 이미지에서 보이는 **{store_name} 관련 모든 식품 세일 상품**을 추출하세요.

**참고**: 
- "Pagina niet gevonden" 메시지가 있더라도 그 아래에 세일 정보가 있습니다
- "Alle aanbiedingen" 섹션의 상품들을 추출하세요
- AH, Albert Heijn 관련 상품을 모두 포함하세요

**포함**: 파스타, 생선, 과일, 음료, 유제품 등 모든 식품
**제외**: 옷, 가구, 청소용품

**JSON 형식으로만 출력** (다른 텍스트 없이):
[
  {{"name": "Alle AH Verse pasta's", "price": "€2.39", "discount": "1+1 gratis"}},
  {{"name": "Witte druiven", "price": "€1.49", "discount": null}}
]"""
        else:
            prompt = f"""이 이미지는 네덜란드 슈퍼마켓 **{store_name}**의 세일 전단지/페이지입니다.

**작업**: 이미지에서 보이는 **모든 식품 세일 상품** 추출

**포함 (식품만)**:
- 고기 (vlees, kip, varken, rund, speklappen, gehakt)
- 생선 (vis, zalm, garnalen)
- 채소/과일 (groente, fruit, aardappelen, tomaten, druiven)
- 유제품 (zuivel, melk, kaas, yoghurt, boter)
- 음료 (frisdrank, bier, wijn, sap)
- 빵/과자 (brood, koek, chips, chocolade)
- 냉동식품 (diepvries)

**제외 (비식품)**:
- 옷, 가전, 기차표, 가구, 장난감, 화장품, 청소용품

**필수**:
- 최소 15개 이상 추출
- 상품명은 네덜란드어 원문
- 완전한 이름 사용

**JSON만 출력**:
[
  {{"name": "Speklappen", "price": "€3.99", "discount": "1+1 gratis"}},
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
        if '```json' in response_text:
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(1)
        elif '```' in response_text:
            response_text = response_text.strip('`').strip()
            if response_text.startswith('json'):
                response_text = response_text[4:].strip()
        elif '[' in response_text:
            start = response_text.index('[')
            end = response_text.rindex(']') + 1
            response_text = response_text[start:end]
        
        products_data = json.loads(response_text)
        
        products = []
        for item in products_data:
            if isinstance(item, dict) and 'name' in item:
                name = item['name']
                if 3 <= len(name) <= 150:
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
            raise ValueError("추출된 식품 없음")
        
    except json.JSONDecodeError as e:
        print(f"⚠️ JSON 오류: {str(e)[:50]}")
        # response_text가 정의되어 있는지 확인
        try:
            response_text_local = response_text
        except NameError:
            # response_text가 없으면 재시도만 수행
            if retry < max_retries:
                wait_time = 5 + (retry * 2)
                print(f"⏳ {wait_time}초 후 재시도...")
                time.sleep(wait_time)
                return analyze_with_ai(screenshot_path, store_name, retry + 1)
            return []
        
        if retry < max_retries:
            # 재시도 시 대기 시간 증가 (3초 → 5초)
            wait_time = 5 + (retry * 2)  # 재시도마다 대기 시간 증가
            print(f"⏳ {wait_time}초 후 재시도...")
            time.sleep(wait_time)
            return analyze_with_ai(screenshot_path, store_name, retry + 1)
        
        # JSON 파싱 실패 시 텍스트에서 직접 추출 시도
        print("🔄 텍스트에서 직접 추출 시도...")
        try:
            # 응답 텍스트에서 JSON 배열 찾기
            if '[' in response_text_local and ']' in response_text_local:
                start = response_text_local.index('[')
                end = response_text_local.rindex(']') + 1
                json_text = response_text_local[start:end]
                products_data = json.loads(json_text)
                # ... (기존 products 처리 로직)
                products = []
                for item in products_data:
                    if isinstance(item, dict) and 'name' in item:
                        name = item['name']
                        if 3 <= len(name) <= 150:
                            products.append({
                                'name': name,
                                'price': item.get('price'),
                                'discount': item.get('discount'),
                                'supermarket': store_name
                            })
                if products:
                    print(f"✅ {len(products)}개 식품 추출! (텍스트 파싱)")
                    return products
        except Exception as fallback_error:
            print(f"⚠️ 텍스트 파싱도 실패: {str(fallback_error)[:50]}")
        return []
        
    except Exception as e:
        print(f"❌ AI 오류: {str(e)[:100]}")
        if retry < max_retries:
            wait_time = 5 + (retry * 2)
            print(f"⏳ {wait_time}초 후 재시도...")
            time.sleep(wait_time)
            return analyze_with_ai(screenshot_path, store_name, retry + 1)
        return []

def get_current_week():
    """현재 주 월요일 계산"""
    today = datetime.now()
    days_since_monday = today.weekday()
    current_monday = today - timedelta(days=days_since_monday)
    return current_monday

# 마트별 세일 시작일 매핑 (요일: 0=월요일, 1=화요일, 2=수요일, ...)
STORE_SALE_START_DAY = {
    'Albert Heijn': 0,  # 월요일
    'Jumbo': 2,         # 수요일
    'Dirk': 2,          # 수요일
    'Aldi': 0,          # 월요일
    'Plus': 0,          # 월요일
    'Hoogvliet': 0,     # 월요일
    'Coop': 0,          # 월요일
}

def get_store_sale_dates(store_name: str, week_type: str = 'current', reference_date: Optional[datetime] = None) -> Tuple[datetime, datetime]:
    """
    마트별 세일 시작일과 종료일 계산
    
    Args:
        store_name: 마트 이름
        week_type: 'current' 또는 'next'
        reference_date: 기준 날짜 (기본값: 오늘)
    
    Returns:
        (start_date, end_date) 튜플
    """
    if reference_date is None:
        reference_date = datetime.now()
    
    # 마트별 시작 요일 (기본값: 월요일)
    start_day_of_week = STORE_SALE_START_DAY.get(store_name, 0)
    
    # 현재 주의 시작일 계산
    days_since_monday = reference_date.weekday()
    current_monday = reference_date - timedelta(days=days_since_monday)
    
    if week_type == 'current':
        # 현재 주의 세일 시작일 계산
        days_to_start = (start_day_of_week - current_monday.weekday()) % 7
        if days_to_start == 0 and reference_date.weekday() < start_day_of_week:
            # 아직 시작일이 안 지났으면 이번 주 시작일
            sale_start = current_monday + timedelta(days=start_day_of_week)
        elif days_to_start == 0:
            # 오늘이 시작일이거나 지났으면 이번 주 시작일
            sale_start = current_monday + timedelta(days=start_day_of_week)
        else:
            # 시작일이 지났으면 다음 주 시작일
            sale_start = current_monday + timedelta(days=7 + start_day_of_week)
    else:  # next
        # 다음 주의 세일 시작일
        next_monday = current_monday + timedelta(days=7)
        sale_start = next_monday + timedelta(days=start_day_of_week)
    
    # 세일 종료일 (시작일 + 6일)
    sale_end = sale_start + timedelta(days=6)
    
    return sale_start, sale_end

def save_results(all_products, successful, failed, week_type='next'):
    """결과 저장 (현재 주 또는 다음 주) - 마트별 세일 시작일 반영"""
    if week_type == 'current':
        week_monday = get_current_week()
        output_file = PROJECT_ROOT / "data" / "current_sales.json"
    else:  # next
        week_monday = get_next_monday()
        output_file = PROJECT_ROOT / "data" / "next_sales.json"
    
    week_sunday = week_monday + timedelta(days=6)
    
    # 상품별로 마트의 실제 세일 시작일 적용
    products_with_dates = []
    for p in all_products:
        store_name = p['supermarket']
        sale_start, sale_end = get_store_sale_dates(store_name, week_type)
        
        products_with_dates.append({
            'store': store_name,
            'product_name': p['name'],
            'price': p.get('price'),
            'discount': p.get('discount'),
            'valid_from': sale_start.isoformat(),
            'valid_until': sale_end.isoformat(),
            'scraped_at': datetime.now().isoformat()
        })
    
    data = {
        'week_number': f"{week_monday.year}-{week_monday.isocalendar()[1]:02d}",
        'sale_period': f"{week_monday.strftime('%Y-%m-%d')} ~ {week_sunday.strftime('%Y-%m-%d')}",
        'week_type': week_type,  # 'current' or 'next'
        'scraped_at': datetime.now().isoformat(),
        'total_products': len(all_products),
        'supermarkets': {'successful': successful, 'failed': failed},
        'products': products_with_dates
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n💾 {output_file.name} 저장 완료 ({week_type} week)")

def scrape_week(week_type='next'):
    """특정 주차 크롤링 (current 또는 next)"""
    if week_type == 'current':
        week_monday = get_current_week()
        label = "이번 주"
    else:
        week_monday = get_next_monday()
        label = "다음 주"
    
    print(f"\n📅 {label} 주차: {week_monday.year}-{week_monday.isocalendar()[1]:02d}주")
    print(f"📆 기간: {week_monday.strftime('%Y-%m-%d')} (월) 시작")
    print(f"🎯 대상: {len(STORES)}개 마트 (Lidl 제외)\n")
    
    all_products = []
    successful = []
    failed = []
    
    for name, config in STORES.items():
        screenshot = capture_screenshot(name, config)
        products = None
        
        if screenshot:
            products = analyze_with_ai(screenshot, name)
        
        # Albert Heijn 최적화:
        # - Reclamefolder에서 3개 이상이면 사용 (로그 분석 결과: 3개도 유효)
        # - 3개 미만이면 공식 사이트 시도
        if name == 'Albert Heijn':
            if products and len(products) >= 3:
                # Reclamefolder 결과가 3개 이상이면 사용
                pass
            elif not products or len(products) < 3:
                print(f"\n🔄 {name} Reclamefolder 실패 (상품 {len(products) if products else 0}개), 공식 사이트 시도...")
                official_config = {
                    'url': 'https://www.ah.nl/bonus',
                    'source': 'official',
                    'timeout': 150000,  # 120초 → 150초
                    'wait_time': 15,
                    'scroll': True,
                    'scroll_iterations': 8  # 더 많은 스크롤
                }
                screenshot2 = capture_screenshot(name, official_config)
                if screenshot2:
                    products2 = analyze_with_ai(screenshot2, name)
                    if products2 and len(products2) >= 3:
                        products = products2
                        print(f"✅ {name} 공식 사이트에서 {len(products2)}개 추출 성공!")
                    elif products and len(products) >= 3:
                        # Reclamefolder 결과 사용
                        print(f"✅ {name} Reclamefolder 결과 사용 ({len(products)}개)")
        
        # 마트별 최소 상품 수 (로그 분석 기반)
        # Albert Heijn: 3개 (Reclamefolder에서 3개도 유효)
        # 나머지: 5개 (안정적인 크롤링을 위해)
        min_products = 3 if name == 'Albert Heijn' else 5
        
        if products and len(products) >= min_products:
            all_products.extend(products)
            successful.append(name)
            print(f"  💚 {name} 성공!")
        else:
            failed.append(name)
            if not screenshot:
                print(f"  ❌ {name} 실패 (스크린샷 실패)")
            else:
                print(f"  ⚠️ {name} 실패 (상품 부족: {len(products) if products else 0}개, 최소 {min_products}개 필요)")
        
        # 마트 간 대기 시간 (서버 부하 방지)
        # 타임아웃이 발생한 마트 다음에는 더 긴 대기
        wait_between_stores = 10 if name in ['Plus', 'Coop'] else 8
        print(f"\n⏳ 다음 마트 대기... ({wait_between_stores}초)\n")
        time.sleep(wait_between_stores)
    
    # 결과 저장
    if all_products:
        save_results(all_products, successful, failed, week_type)
        
        print("\n" + "="*70)
        print(f"📊 {label} 크롤링 결과")
        print("="*70)
        print(f"✅ 성공: {len(successful)}개 마트")
        for store in successful:
            count = len([p for p in all_products if p['supermarket'] == store])
            print(f"   - {store}: {count}개 상품")
        
        if failed:
            print(f"\n⚠️ 실패: {len(failed)}개 마트")
            for store in failed:
                print(f"   - {store}")
        
        print(f"\n📦 총 {len(all_products)}개 상품")
        return True
    else:
        print(f"\n❌ {label} 모든 마트 실패")
        return False

def main(week_type='both'):
    """메인 실행"""
    print("\n" + "="*70)
    print("🍳 What2Cook NL 시스템 가동")
    print("🤖 하이브리드 크롤러 (현재 주 + 다음 주)")
    print("   - Albert Heijn: Reclamefolder (이전 작동 방식)")
    print("   - 나머지: 공식 사이트")
    print("="*70)
    
    if week_type == 'both' or week_type == 'current':
        print("\n" + "="*70)
        print("📦 1단계: 이번 주 세일 크롤링")
        print("="*70)
        scrape_week('current')
    
    if week_type == 'both' or week_type == 'next':
        print("\n" + "="*70)
        print("📦 2단계: 다음 주 세일 크롤링")
        print("="*70)
        scrape_week('next')
    
    print("\n✅ 크롤링 완료!")
    print("✅ 다음: python3 recipe_matcher.py")

if __name__ == "__main__":
    main()
