"""
각 슈퍼마켓 공식 사이트 조사
페이지 구조 분석 및 크롤링 가능성 평가
"""
import os
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

# 환경 설정
PROJECT_ROOT = Path(__file__).parent.parent
LOCAL_BROWSERS_PATH = PROJECT_ROOT / "pw-browsers"
if LOCAL_BROWSERS_PATH.exists():
    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(LOCAL_BROWSERS_PATH)

SUPERMARKETS = {
    'Albert Heijn': 'https://www.ah.nl/bonus',
    'Jumbo': 'https://www.jumbo.com/aanbiedingen',
    'Dirk': 'https://www.dirk.nl/aanbiedingen',
    'Lidl': 'https://www.lidl.nl/c/aanbiedingen',
    'ALDI': 'https://www.aldi.nl/aanbiedingen.html',
    'Plus': 'https://www.plus.nl/aanbiedingen',
    'Hoogvliet': 'https://www.hoogvliet.com/aanbiedingen',
    'Coop': 'https://www.coop.nl/aanbiedingen'
}

def investigate_site(name, url):
    """개별 사이트 조사"""
    print(f"\n{'='*70}")
    print(f"🔍 {name} 조사 중...")
    print(f"{'='*70}")
    print(f"🔗 URL: {url}")
    
    report = {
        'name': name,
        'url': url,
        'accessible': False,
        'page_title': '',
        'page_size_kb': 0,
        'screenshot_saved': False,
        'html_saved': False,
        'product_elements_found': 0,
        'notes': []
    }
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = context.new_page()
            
            # 페이지 로드
            print("📄 페이지 로딩 중...")
            page.goto(url, timeout=60000)
            page.wait_for_load_state("networkidle")
            time.sleep(5)
            
            report['accessible'] = True
            
            # 쿠키 동의 처리
            try:
                cookie_texts = ['accepteren', 'accept', 'akkoord', 'agree', 'toestaan']
                for text in cookie_texts:
                    try:
                        button = page.get_by_role("button", name=text, exact=False).first
                        if button.is_visible():
                            button.click()
                            time.sleep(2)
                            print("🍪 쿠키 동의 완료")
                            break
                    except:
                        pass
            except:
                pass
            
            # 페이지 정보 수집
            report['page_title'] = page.title()
            print(f"📌 페이지 제목: {report['page_title']}")
            
            # HTML 저장
            investigation_dir = PROJECT_ROOT / "data" / "investigation"
            investigation_dir.mkdir(exist_ok=True)
            
            html_path = investigation_dir / f"{name.lower().replace(' ', '_')}.html"
            html_content = page.content()
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            report['html_saved'] = True
            report['page_size_kb'] = len(html_content) / 1024
            print(f"💾 HTML 저장: {html_path.name} ({report['page_size_kb']:.1f}KB)")
            
            # 스크린샷
            screenshot_path = investigation_dir / f"{name.lower().replace(' ', '_')}.png"
            page.screenshot(path=str(screenshot_path), full_page=True)
            report['screenshot_saved'] = True
            screenshot_size = screenshot_path.stat().st_size / 1024
            print(f"📸 스크린샷 저장: {screenshot_path.name} ({screenshot_size:.0f}KB)")
            
            # 상품 요소 찾기 시도
            print("🔎 상품 요소 탐색 중...")
            
            selectors_to_try = [
                'article',
                '[data-test*="product"]',
                '[class*="product"]',
                '[class*="offer"]',
                '[class*="aanbieding"]',
                '[class*="bonus"]',
                '.product-card',
                '.offer-card',
                '[data-testid*="product"]'
            ]
            
            for selector in selectors_to_try:
                try:
                    elements = page.locator(selector).all()
                    if len(elements) > 0:
                        report['product_elements_found'] += len(elements)
                        report['notes'].append(f"Selector '{selector}': {len(elements)}개 요소 발견")
                        print(f"  ✅ {selector}: {len(elements)}개")
                except:
                    pass
            
            # 페이지 텍스트 분석
            page_text = page.inner_text('body').lower()
            keywords = ['bonus', 'aanbieding', 'korting', 'prijs', '€']
            found_keywords = [kw for kw in keywords if kw in page_text]
            if found_keywords:
                report['notes'].append(f"키워드 발견: {', '.join(found_keywords)}")
                print(f"  📝 키워드: {', '.join(found_keywords)}")
            
            browser.close()
            
    except Exception as e:
        report['notes'].append(f"오류: {str(e)}")
        print(f"❌ 오류: {str(e)}")
    
    return report

def main():
    """모든 사이트 조사"""
    print("\n" + "="*70)
    print("🔍 슈퍼마켓 사이트 조사 시작")
    print("="*70)
    
    reports = []
    
    for name, url in SUPERMARKETS.items():
        report = investigate_site(name, url)
        reports.append(report)
        
        # API 제한 방지
        print("⏳ 다음 사이트 대기 중...")
        time.sleep(5)
    
    # 결과 요약
    print("\n" + "="*70)
    print("📊 조사 결과 요약")
    print("="*70)
    
    for report in reports:
        status = "✅" if report['accessible'] else "❌"
        products = f"{report['product_elements_found']}개 요소" if report['product_elements_found'] > 0 else "요소 없음"
        print(f"{status} {report['name']}: {products}")
        if report['notes']:
            for note in report['notes'][:2]:  # 최대 2개만 표시
                print(f"   └─ {note}")
    
    # JSON 저장
    report_path = PROJECT_ROOT / "data" / "investigation" / "site_investigation_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(reports, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 상세 보고서 저장: {report_path}")
    print("\n✅ 조사 완료!")
    print("\n📁 결과 파일:")
    print(f"   - HTML 파일: data/investigation/*.html")
    print(f"   - 스크린샷: data/investigation/*.png")
    print(f"   - 보고서: data/investigation/site_investigation_report.json")

if __name__ == "__main__":
    main()
