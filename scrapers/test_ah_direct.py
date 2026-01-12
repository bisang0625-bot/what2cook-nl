"""
Albert Heijn 직접 테스트 - 스크린샷 확인 및 AI 분석
"""
import os
import json
import time
import base64
import re
from pathlib import Path
from playwright.sync_api import sync_playwright
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
PROJECT_ROOT = Path(__file__).parent.parent
LOCAL_BROWSERS_PATH = PROJECT_ROOT / "pw-browsers"
if LOCAL_BROWSERS_PATH.exists():
    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(LOCAL_BROWSERS_PATH)

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

def test_reclamefolder():
    """Reclamefolder Albert Heijn 테스트"""
    print("\n" + "="*70)
    print("🔍 Albert Heijn 테스트 (Reclamefolder)")
    print("="*70)
    
    url = "https://www.reclamefolder.nl/albert-heijn"
    print(f"🔗 {url}")
    
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
            for text in ['accepteren', 'accept', 'akkoord', 'allow']:
                try:
                    button = page.get_by_role("button", name=re.compile(text, re.IGNORECASE)).first
                    if button.is_visible(timeout=2000):
                        button.click()
                        time.sleep(2)
                        print("🍪 쿠키 동의")
                        break
                except:
                    pass
        except:
            pass
        
        # 페이지 정보 출력
        print(f"\n📄 페이지 제목: {page.title()}")
        
        # 페이지 텍스트 일부 출력
        body_text = page.inner_text('body')[:500]
        print(f"\n📝 페이지 텍스트 (처음 500자):\n{body_text}")
        
        # 스크린샷
        screenshot_dir = PROJECT_ROOT / "data" / "screenshots"
        screenshot_dir.mkdir(exist_ok=True)
        screenshot_path = screenshot_dir / "ah_test.png"
        
        page.screenshot(path=str(screenshot_path), full_page=True)
        file_size = screenshot_path.stat().st_size / 1024
        print(f"\n📸 스크린샷: {screenshot_path.name} ({file_size:.0f}KB)")
        
        # HTML 저장
        html_path = PROJECT_ROOT / "data" / "ah_test.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(page.content())
        print(f"💾 HTML 저장: {html_path.name}")
        
        browser.close()
    
    # AI 분석 (다른 프롬프트로)
    print("\n🔍 AI 분석 시도...")
    
    with open(screenshot_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    # 더 간단한 프롬프트
    prompt = """이 이미지를 분석해주세요.

1. 이 이미지가 무엇인지 설명해주세요.
2. 슈퍼마켓 세일 정보가 보이면 상품 목록을 JSON으로 추출해주세요.
3. 식품이 보이지 않으면 "식품 없음"이라고 알려주세요.

만약 식품 세일 정보가 있다면 JSON 형식으로:
[{"name": "상품명", "price": "가격", "discount": "할인정보"}]"""

    try:
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
        
        print(f"\n📋 AI 응답:\n{response.text[:1000]}")
        
    except Exception as e:
        print(f"❌ AI 오류: {str(e)}")

def test_ah_bonus():
    """AH 공식 Bonus 페이지 테스트"""
    print("\n" + "="*70)
    print("🔍 Albert Heijn 테스트 (공식 Bonus 페이지)")
    print("="*70)
    
    url = "https://www.ah.nl/bonus"
    print(f"🔗 {url}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = context.new_page()
        page.goto(url, timeout=120000)
        page.wait_for_load_state("networkidle")
        
        print("⏳ 10초 대기...")
        time.sleep(10)
        
        # 쿠키 동의
        try:
            for text in ['accepteren', 'accept', 'akkoord']:
                try:
                    button = page.get_by_role("button", name=text, exact=False).first
                    if button.is_visible(timeout=2000):
                        button.click()
                        time.sleep(2)
                        print("🍪 쿠키 동의")
                        break
                except:
                    pass
        except:
            pass
        
        # 스크롤
        print("📜 페이지 스크롤...")
        for _ in range(5):
            page.evaluate("window.scrollBy(0, 500)")
            time.sleep(1)
        
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(2)
        
        # 페이지 정보
        print(f"\n📄 페이지 제목: {page.title()}")
        
        # 스크린샷
        screenshot_dir = PROJECT_ROOT / "data" / "screenshots"
        screenshot_path = screenshot_dir / "ah_bonus_test.png"
        
        page.screenshot(path=str(screenshot_path), full_page=True)
        file_size = screenshot_path.stat().st_size / 1024
        print(f"\n📸 스크린샷: {screenshot_path.name} ({file_size:.0f}KB)")
        
        browser.close()
    
    # AI 분석
    print("\n🔍 AI 분석 시도...")
    
    with open(screenshot_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    prompt = """이 이미지를 분석해주세요.

1. 이 이미지가 무엇인지 설명해주세요.
2. 슈퍼마켓 세일 정보가 보이면 상품 목록을 JSON으로 추출해주세요.

만약 식품 세일 정보가 있다면 JSON 형식으로:
[{"name": "상품명", "price": "가격", "discount": "할인정보"}]"""

    try:
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
        
        print(f"\n📋 AI 응답:\n{response.text[:1500]}")
        
    except Exception as e:
        print(f"❌ AI 오류: {str(e)}")

if __name__ == "__main__":
    test_reclamefolder()
    print("\n" + "="*70)
    test_ah_bonus()
