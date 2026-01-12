"""
Reclamefolder 전단지 이미지 AI 분석 (테스트 버전 - Albert Heijn만)
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

# Genai 클라이언트 초기화
client = genai.Client(api_key=api_key)

def scrape_albert_heijn():
    """Albert Heijn만 크롤링 (테스트)"""
    print("🤖 Albert Heijn 전단지 AI 분석 시작\n")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        
        url = "https://www.reclamefolder.nl/albert-heijn"
        print(f"🔗 {url}")
        
        page = context.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_load_state("networkidle")
        time.sleep(3)
        
        # 쿠키 동의
        try:
            cookie_btn = page.get_by_role("button", name=re.compile("allow|accept|akkoord|agree", re.IGNORECASE))
            if cookie_btn.count() > 0 and cookie_btn.first.is_visible():
                cookie_btn.first.click()
                time.sleep(2)
        except:
            pass
        
        # 스크린샷 캡처
        screenshot_dir = PROJECT_ROOT / "data" / "screenshots"
        screenshot_dir.mkdir(exist_ok=True)
        screenshot_path = screenshot_dir / "albert-heijn.png"
        
        page.screenshot(path=str(screenshot_path), full_page=True)
        print(f"📸 스크린샷 저장: {screenshot_path.name}")
        
        browser.close()
    
    # AI 분석
    print("🔍 AI 이미지 분석 중...")
    products = analyze_image(screenshot_path)
    
    if products:
        print(f"✅ {len(products)}개 상품 추출 성공!\n")
        save_results(products)
        return products
    else:
        print("⚠️ 상품을 찾을 수 없습니다")
        return []

def analyze_image(image_path):
    """Gemini Vision으로 이미지 분석"""
    try:
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        prompt = """이 이미지는 네덜란드 슈퍼마켓 Albert Heijn의 세일 전단지입니다.

이미지에서 보이는 **모든 식품 세일 상품**의 정보를 추출해주세요:
- 상품명 (네덜란드어 그대로)
- 할인 가격 (€ 표시)
- 할인 조건 (1+1, 2e halve prijs, 할인율 등)

**중요**: 
- 고기, 생선, 채소, 과일, 유제품, 음료, 과자 등 모든 식품 포함
- 전단지가 길면 모든 상품을 찾아주세요
- 최소 20개 이상의 상품을 추출해주세요

JSON 배열로만 응답 (다른 텍스트 없이):
[{"name": "상품명", "price": "€X.XX", "discount": "할인조건"}]"""

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
                products.append({
                    'name': item['name'],
                    'price': item.get('price'),
                    'discount': item.get('discount'),
                    'supermarket': 'Albert Heijn'
                })
        
        return products
        
    except Exception as e:
        print(f"❌ 오류: {str(e)}")
        return []

def save_results(products):
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
        'supermarkets': {'successful': ['Albert Heijn'], 'failed': []},
        'products': [
            {
                'supermarket': 'Albert Heijn',
                'product_name': p['name'],
                'price_info': p.get('price'),
                'discount_info': p.get('discount'),
                'start_date': next_monday.isoformat(),
                'end_date': next_sunday.isoformat(),
                'source': 'reclamefolder.nl (AI)',
                'scraped_at': datetime.now().isoformat()
            }
            for p in products
        ]
    }
    
    output = PROJECT_ROOT / "data" / "weekly_sales.json"
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(weekly_data, f, ensure_ascii=False, indent=2)
    print(f"💾 weekly_sales.json 저장 완료")

if __name__ == "__main__":
    products = scrape_albert_heijn()
    
    if products:
        print("\n📋 추출된 상품 샘플 (최대 10개):")
        for i, p in enumerate(products[:10], 1):
            discount = f" ({p['discount']})" if p.get('discount') else ""
            print(f"  {i}. {p['name']} - {p.get('price', 'N/A')}{discount}")
        
        if len(products) > 10:
            print(f"  ... 외 {len(products)-10}개 더")
