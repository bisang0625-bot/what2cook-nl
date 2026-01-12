"""
기본 크롤러 클래스
각 마트의 strategy에 따라 다른 방식으로 크롤링
"""
import os
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, Page
from datetime import datetime, timedelta
from .store_config import SCRAPING_CONFIG

class BaseScraper:
    """슈퍼마켓 크롤러 기본 클래스"""
    
    def __init__(self, store_config: dict, project_root: Path):
        self.config = store_config
        self.name = store_config['name']
        self.url = store_config['url']
        self.strategy = store_config['strategy']
        self.selectors = store_config['selectors']
        self.project_root = project_root
        
        # Playwright 브라우저 경로 설정
        local_browsers = project_root / "pw-browsers"
        if local_browsers.exists():
            os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(local_browsers)
    
    def scrape(self) -> list:
        """메인 크롤링 메서드"""
        print(f"\n{'='*70}")
        print(f"🛒 {self.name} 크롤링 시작")
        print(f"{'='*70}")
        print(f"🔗 URL: {self.url}")
        print(f"📋 Strategy: {self.strategy}")
        
        products = []
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=SCRAPING_CONFIG['headless']
                )
                context = browser.new_context(
                    user_agent=SCRAPING_CONFIG['user_agent'],
                    viewport=SCRAPING_CONFIG['viewport']
                )
                
                page = context.new_page()
                
                # 1. 페이지 로드
                print("📄 페이지 로딩 중...")
                page.goto(self.url, timeout=SCRAPING_CONFIG['timeout'])
                page.wait_for_load_state("networkidle")
                time.sleep(SCRAPING_CONFIG['wait_after_load'])
                
                # 2. 쿠키 동의 처리
                self._handle_cookie_consent(page)
                
                # 3. Strategy별 처리
                if self.strategy == "direct_url":
                    print("✅ Direct URL - 바로 데이터 수집")
                    products = self._scrape_direct(page)
                    
                elif self.strategy == "click_next_week":
                    print("🖱️  'Volgende week' 버튼 클릭 시도...")
                    if self._click_next_week_button(page):
                        products = self._scrape_direct(page)
                    else:
                        print("⚠️ 다음 주 버튼을 찾을 수 없습니다. 현재 페이지 데이터 수집...")
                        products = self._scrape_direct(page)
                        
                elif self.strategy == "click_category":
                    print("🖱️  카테고리 버튼 클릭 시도...")
                    if self._click_category_button(page):
                        products = self._scrape_direct(page)
                    else:
                        print("⚠️ 카테고리 버튼을 찾을 수 없습니다.")
                        products = self._scrape_direct(page)
                        
                elif self.strategy == "default":
                    print("✅ Default - 바로 데이터 수집")
                    products = self._scrape_direct(page)
                
                # 4. 스크린샷 저장 (디버그용)
                self._save_screenshot(page)
                
                browser.close()
                
        except Exception as e:
            print(f"❌ 크롤링 실패: {str(e)}")
            return []
        
        if products:
            print(f"✅ {len(products)}개 상품 수집 완료!")
        else:
            print(f"⚠️ 상품을 찾지 못했습니다.")
        
        return products
    
    def _handle_cookie_consent(self, page: Page):
        """쿠키 동의 처리"""
        try:
            cookie_texts = [
                'accepteren', 'accept', 'akkoord', 'agree', 
                'toestaan', 'alle cookies'
            ]
            
            for text in cookie_texts:
                try:
                    buttons = page.get_by_role("button", name=text).all()
                    for button in buttons:
                        if button.is_visible():
                            button.click()
                            time.sleep(2)
                            print("🍪 쿠키 동의 완료")
                            return
                except:
                    pass
        except:
            pass
    
    def _click_next_week_button(self, page: Page) -> bool:
        """'다음 주' 버튼 클릭"""
        selectors = self.selectors.get('next_week_btn', '').split(', ')
        
        for selector in selectors:
            try:
                # CSS selector 시도
                element = page.locator(selector).first
                if element.count() > 0 and element.is_visible():
                    element.click()
                    time.sleep(SCRAPING_CONFIG['wait_after_click'])
                    print(f"  ✅ 버튼 클릭 성공: {selector}")
                    return True
            except:
                pass
        
        # 텍스트로 직접 찾기
        try:
            texts = ['Volgende week', 'volgende week', 'Volgende']
            for text in texts:
                element = page.get_by_text(text, exact=False).first
                if element.count() > 0 and element.is_visible():
                    element.click()
                    time.sleep(SCRAPING_CONFIG['wait_after_click'])
                    print(f"  ✅ 버튼 클릭 성공: '{text}'")
                    return True
        except:
            pass
        
        return False
    
    def _click_category_button(self, page: Page) -> bool:
        """카테고리 버튼 클릭 (Lidl 등)"""
        selectors = self.selectors.get('category_btn', '').split(', ')
        
        for selector in selectors:
            try:
                element = page.locator(selector).first
                if element.count() > 0 and element.is_visible():
                    element.click()
                    time.sleep(SCRAPING_CONFIG['wait_after_click'])
                    print(f"  ✅ 카테고리 클릭 성공: {selector}")
                    return True
            except:
                pass
        
        return False
    
    def _scrape_direct(self, page: Page) -> list:
        """실제 상품 데이터 수집"""
        products = []
        
        # 대기할 요소가 있으면 대기
        if 'wait_for' in self.config:
            try:
                page.wait_for_selector(
                    self.config['wait_for'], 
                    timeout=10000
                )
            except:
                print("  ⚠️ 대기 요소를 찾을 수 없습니다.")
        
        # 상품 카드 찾기
        product_selectors = self.selectors.get('product_card', '').split(', ')
        product_cards = []
        
        for selector in product_selectors:
            try:
                cards = page.locator(selector).all()
                if len(cards) > 0:
                    product_cards = cards
                    print(f"  📦 {len(cards)}개 상품 카드 발견: {selector}")
                    break
            except:
                pass
        
        if not product_cards:
            print("  ⚠️ 상품 카드를 찾을 수 없습니다.")
            return []
        
        # 각 상품 카드에서 정보 추출
        for i, card in enumerate(product_cards[:50], 1):  # 최대 50개
            try:
                product = self._extract_product_info(card)
                if product and product.get('name'):
                    product['supermarket'] = self.name
                    products.append(product)
                    print(f"  {i}. {product['name'][:50]}")
            except Exception as e:
                continue
        
        return products
    
    def _extract_product_info(self, card) -> dict:
        """개별 상품 카드에서 정보 추출"""
        product = {
            'name': None,
            'price': None,
            'discount': None
        }
        
        # 상품명 추출
        title_selectors = self.selectors.get('title', '').split(', ')
        for selector in title_selectors:
            try:
                element = card.locator(selector).first
                if element.count() > 0:
                    product['name'] = element.inner_text().strip()
                    break
            except:
                pass
        
        # 상품명을 못 찾으면 카드 전체 텍스트에서 첫 줄 사용
        if not product['name']:
            try:
                text = card.inner_text().strip()
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                if lines:
                    product['name'] = lines[0]
            except:
                pass
        
        # 가격 추출
        price_selectors = self.selectors.get('price', '').split(', ')
        for selector in price_selectors:
            try:
                element = card.locator(selector).first
                if element.count() > 0:
                    product['price'] = element.inner_text().strip()
                    break
            except:
                pass
        
        # 할인 정보 추출
        discount_selectors = self.selectors.get('discount', '').split(', ')
        for selector in discount_selectors:
            try:
                element = card.locator(selector).first
                if element.count() > 0:
                    product['discount'] = element.inner_text().strip()
                    break
            except:
                pass
        
        return product
    
    def _save_screenshot(self, page: Page):
        """스크린샷 저장 (디버그용)"""
        try:
            screenshot_dir = self.project_root / "data" / "screenshots"
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"{self.name.lower().replace(' ', '_')}_official.png"
            page.screenshot(path=str(screenshot_dir / filename), full_page=True)
            print(f"📸 스크린샷 저장: {filename}")
        except:
            pass
