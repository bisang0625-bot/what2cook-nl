"""
Weekly Supermarket Sale Scraper (Playwright Version)
매주 일요일 11:00에 네덜란드 슈퍼마켓 세일 정보를 크롤링합니다.

크롤링 대상:
- Reclamefolder.nl (슈퍼마켓 세일 폴더 통합 사이트)
- Albert Heijn 공식 Bonus 페이지 (보조 소스)

대상 슈퍼마켓:
Albert Heijn, Jumbo, Lidl, Dirk, ALDI, Plus, Hoogvliet, Makro, Hanos, Sligro

기술 스택:
- Playwright (동적 렌더링 및 인터랙션 처리)
- BeautifulSoup (HTML 파싱)
- Python schedule 라이브러리를 사용한 스케줄링
"""

import json
import logging
import os
import time
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from bs4 import BeautifulSoup
import schedule
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# Playwright 브라우저 경로 설정 (로컬 설치 경로 우선 사용)
PROJECT_ROOT = Path(__file__).parent.parent
LOCAL_BROWSERS_PATH = PROJECT_ROOT / "pw-browsers"
if LOCAL_BROWSERS_PATH.exists():
    os.environ['PLAYWRIGHT_BROWSERS_PATH'] = str(LOCAL_BROWSERS_PATH)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WeeklyScraper:
    """주간 슈퍼마켓 세일 정보 크롤러 (Playwright 기반)"""
    
    # 크롤링 대상 슈퍼마켓 목록
    SUPERMARKETS = [
        'Albert Heijn',
        'Jumbo',
        'Lidl',
        'Dirk',
        'ALDI',
        'Plus',
        'Hoogvliet',
        'Coop',
        'Makro',
        'Hanos',
        'Sligro'
    ]
    
    def __init__(self):
        """크롤러 초기화"""
        self.data_dir = Path(__file__).parent.parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        self.output_file = self.data_dir / "weekly_sales.json"
        
    def get_week_number(self, date: datetime = None) -> str:
        """ISO 주차 형식 (YYYY-WW) 반환 (다가오는 월요일 기준)"""
        if date is None:
            date = datetime.now()
        next_monday = self.get_next_monday(date)
        year, week, _ = next_monday.isocalendar()
        return f"{year}-{week:02d}"
    
    def get_next_monday(self, date: datetime = None) -> datetime:
        """
        기준 날짜(월요일) 반환
        
        - 오늘이 월요일인 경우: 오늘 날짜 반환 (이번 주 세일 시작)
        - 그 외 요일인 경우: 다가오는 월요일 날짜 반환
        """
        if date is None:
            date = datetime.now()
        current_weekday = date.weekday()
        if current_weekday == 0:
            days_until_monday = 0 # 오늘이 월요일이면 0일 후 (오늘)
        else:
            days_until_monday = (7 - current_weekday) % 7
            
        next_monday = date + timedelta(days=days_until_monday)
        return next_monday.replace(hour=0, minute=0, second=0, microsecond=0)
    
    def get_supermarket_url(self, supermarket: str) -> str:
        """슈퍼마켓명에 따른 Reclamefolder.nl URL 반환"""
        base_url = "https://www.reclamefolder.nl"
        slug = supermarket.lower().replace(' ', '-')
        
        # URL 매핑 (필요시 조정)
        url_mapping = {
            'albert-heijn': 'albert-heijn',
            'jumbo': 'jumbo',
            'lidl': 'lidl',
            # ... 추가 매핑 필요시 여기에
        }
        
        target_slug = url_mapping.get(slug, slug)
        return f"{base_url}/{target_slug}"

    def scrape_with_playwright(self, supermarket: str) -> List[Dict[str, Any]]:
        """Playwright를 사용하여 Reclamefolder.nl 크롤링"""
        products = []
        url = self.get_supermarket_url(supermarket)
        
        logger.info(f"[Reclamefolder] {supermarket} 크롤링 시작 (Playwright)")
        
        with sync_playwright() as p:
            # 브라우저 실행
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = context.new_page()
            
            try:
                # 1. 페이지 이동
                logger.info(f"  - URL 이동: {url}")
                page.goto(url, timeout=60000)
                page.wait_for_load_state("networkidle")
                
                # 2. 쿠키 동의 처리 (필요시)
                try:
                    cookie_btn = page.get_by_role("button", name=re.compile("allow|accept|akkoord|agree", re.IGNORECASE))
                    if cookie_btn.count() > 0 and cookie_btn.first.is_visible():
                        logger.info("  - 쿠키 동의 버튼 클릭")
                        cookie_btn.first.click()
                        time.sleep(2)
                except:
                    pass

                # 3. "Volgende week" (다음 주) 탭/버튼 찾기 및 클릭
                # Reclamefolder 구조에 따라 다름. 'Volgende week' 텍스트를 가진 요소 찾기
                next_week_clicked = False
                try:
                    # 다양한 선택자 시도
                    next_week_locators = [
                        page.get_by_text("Volgende week", exact=False),
                        page.get_by_text("Next week", exact=False),
                        page.locator("button:has-text('Volgende week')"),
                    ]
                    
                    for loc in next_week_locators:
                        if loc.count() > 0 and loc.first.is_visible():
                            logger.info("  - '다음 주' 버튼 발견 및 클릭")
                            loc.first.click()
                            page.wait_for_load_state("networkidle")
                            time.sleep(3) # 데이터 로딩 대기
                            next_week_clicked = True
                            break
                    
                    if not next_week_clicked:
                        # 오늘이 월요일이면 현재 페이지(이번 주) 데이터 사용 가능
                        if datetime.now().weekday() == 0:
                            logger.info("  ℹ️ 오늘이 월요일이므로 현재 페이지(이번 주) 데이터를 수집합니다.")
                        else:
                            logger.warning("  ⚠️ '다음 주' 버튼을 찾지 못했습니다. 데이터 수집을 건너뜁니다.")
                            return [] # 다음 주 데이터가 없으면 빈 리스트 반환

                        
                except Exception as e:
                    logger.warning(f"  - '다음 주' 버튼 처리 중 오류: {str(e)}")
                    return []

                # 4. 데이터 추출 (BeautifulSoup 활용)
                content = page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                # 상품 추출 로직 (기존과 동일하게 soup 사용)
                products = self._extract_products_from_soup(soup, supermarket, 'reclamefolder')
                
            except Exception as e:
                logger.error(f"  ❌ Playwright 크롤링 실패: {str(e)}", exc_info=True)
            finally:
                browser.close()
                
        return products

    def _extract_products_from_soup(self, soup: BeautifulSoup, supermarket: str, source: str) -> List[Dict[str, Any]]:
        """BeautifulSoup 객체에서 상품 정보 추출 (공통 로직)"""
        products = []
        next_monday = self.get_next_monday()
        next_sunday = next_monday + timedelta(days=6)
        
        # 상품 요소 찾기 (다양한 패턴)
        product_items = []
        patterns = [
            lambda x: x and ('product' in x.lower() or 'item' in x.lower()),
            lambda x: x and ('sale' in x.lower() or 'aanbieding' in x.lower()),
            # ... (기존 패턴들)
        ]
        
        # Reclamefolder 특화: article, div 등
        product_items = soup.find_all('article')
        if not product_items:
             product_items = soup.find_all('div', class_=lambda x: x and ('card' in x.lower() or 'tile' in x.lower()))
        
        # 상품이 너무 많으면 제한
        product_items = product_items[:100]
        logger.info(f"  - {len(product_items)}개의 잠재적 상품 요소 발견")

        seen_products = set()
        for item in product_items:
            try:
                product_info = self._extract_product_info(item, supermarket, source, next_monday, next_sunday)
                if product_info:
                    key = product_info['product_name']
                    if key not in seen_products:
                        seen_products.add(key)
                        products.append(product_info)
            except:
                continue
                
        return products

    def _extract_product_info(
        self, 
        element: BeautifulSoup, 
        supermarket: str, 
        source: str,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[Dict[str, Any]]:
        """HTML 요소에서 상품 정보 추출"""
        try:
            # 상품명 추출
            name = None
            # 1. 제목 태그
            for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong']:
                elem = element.find(tag)
                if elem:
                    name = elem.get_text(strip=True)
                    break
            
            # 2. 클래스명
            if not name:
                elem = element.find(class_=lambda x: x and ('title' in x.lower() or 'name' in x.lower()))
                if elem:
                    name = elem.get_text(strip=True)
            
            if not name or len(name) < 2:
                return None
                
            # 가격 추출
            price_text = None
            price_elem = element.find(class_=lambda x: x and ('price' in x.lower() or 'prijs' in x.lower() or 'euro' in x.lower()))
            if price_elem:
                price_text = price_elem.get_text(strip=True)
            
            if not price_text:
                # 텍스트에서 가격 찾기
                text = element.get_text()
                match = re.search(r'€\s*[\d,.]+', text)
                if match:
                    price_text = match.group()

            return {
                'supermarket': supermarket,
                'product_name': name,
                'price_info': price_text,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'week_number': self.get_week_number(start_date),
                'source': source,
                'scraped_at': datetime.now().isoformat()
            }
        except:
            return None

    def scrape_all(self) -> Dict[str, Any]:
        """모든 슈퍼마켓 크롤링"""
        all_products = []
        successful_supermarkets = []
        failed_supermarkets = []
        
        logger.info("=" * 60)
        logger.info("Playwright 기반 주간 세일 크롤링 시작")
        logger.info("=" * 60)
        
        for supermarket in self.SUPERMARKETS:
            try:
                products = self.scrape_with_playwright(supermarket)
                if products:
                    all_products.extend(products)
                    successful_supermarkets.append(supermarket)
                    logger.info(f"✅ {supermarket}: {len(products)}개 수집 완료")
                else:
                    failed_supermarkets.append(supermarket)
                    logger.warning(f"⚠️ {supermarket}: 데이터 없음")
            except Exception as e:
                failed_supermarkets.append(supermarket)
                logger.error(f"❌ {supermarket} 실패: {str(e)}")
                
        return {
            'week_number': self.get_week_number(),
            'scraped_at': datetime.now().isoformat(),
            'total_products': len(all_products),
            'supermarkets': {'successful': successful_supermarkets, 'failed': failed_supermarkets},
            'products': all_products
        }

    def save_data(self, data: Dict[str, Any]):
        """데이터 저장"""
        if data['total_products'] > 0:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"데이터 저장 완료: {self.output_file}")
        else:
            logger.warning("저장할 데이터가 없습니다.")

    def run(self):
        data = self.scrape_all()
        self.save_data(data)

def run_scraper():
    WeeklyScraper().run()

def schedule_weekly_scraper():
    schedule.every().sunday.at("11:00").do(run_scraper)
    logger.info("스케줄러 시작...")
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--schedule':
        schedule_weekly_scraper()
    else:
        run_scraper()
