"""
Albert Heijn Bonus Scraper
매주 일요일에 실행되어 다음 주(Volgende week) 세일 정보를 크롤링합니다.
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError


class AHScraper:
    def __init__(self):
        self.base_url = "https://www.ah.nl/bonus"
        self.data_dir = Path(__file__).parent.parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        self.output_file = self.data_dir / "next_week_bonus.json"
        
    async def scrape_next_week_bonus(self):
        """다음 주 세일 정보를 스크래핑합니다."""
        async with async_playwright() as p:
            # 브라우저 실행 (headless=False로 디버깅 가능)
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            
            try:
                print(f"[INFO] Albert Heijn 보너스 페이지 접속 중: {self.base_url}")
                await page.goto(self.base_url, wait_until="networkidle", timeout=30000)
                
                # 페이지가 완전히 로드될 때까지 대기
                await asyncio.sleep(3)
                
                # "Volgende week" 탭/버튼 찾기
                print("[INFO] 'Volgende week' 탭을 찾는 중...")
                
                # 여러 가능한 선택자 시도
                volgende_week_selectors = [
                    "button:has-text('Volgende week')",
                    "a:has-text('Volgende week')",
                    "[aria-label*='Volgende week' i]",
                    "[aria-label*='Volgende' i]",
                    "button[aria-label*='next week' i]",
                    "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'volgende week')]",
                    "//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'volgende week')]",
                    ".tab:has-text('Volgende week')",
                    "[data-testid*='volgende' i]",
                    "[data-testid*='next' i]",
                ]
                
                volgende_week_clicked = False
                for selector in volgende_week_selectors:
                    try:
                        if selector.startswith("//"):
                            # XPath 사용
                            element = page.locator(selector).first
                        else:
                            # CSS 선택자 사용
                            element = page.locator(selector).first
                        
                        if await element.is_visible(timeout=2000):
                            print(f"[INFO] 'Volgende week' 요소 발견: {selector}")
                            await element.click()
                            await asyncio.sleep(2)  # 클릭 후 페이지 로딩 대기
                            volgende_week_clicked = True
                            break
                    except (PlaywrightTimeoutError, Exception) as e:
                        continue
                
                if not volgende_week_clicked:
                    print("[WARNING] 'Volgende week' 탭을 찾을 수 없습니다. 현재 주 데이터를 가져옵니다.")
                    # 현재 주 데이터도 가져오기
                
                # 추가 대기 시간 (동적 콘텐츠 로딩)
                await asyncio.sleep(3)
                
                # 상품 정보 추출
                print("[INFO] 상품 정보 추출 중...")
                products = await self._extract_products(page)
                
                # 데이터 저장
                data = {
                    "scraped_at": datetime.now().isoformat(),
                    "week": "next_week",
                    "products": products,
                    "total_count": len(products)
                }
                
                with open(self.output_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                print(f"[SUCCESS] {len(products)}개의 상품 정보를 {self.output_file}에 저장했습니다.")
                return data
                
            except Exception as e:
                print(f"[ERROR] 스크래핑 중 오류 발생: {str(e)}")
                raise
            finally:
                await browser.close()
    
    async def _extract_products(self, page):
        """페이지에서 상품 정보를 추출합니다."""
        products = []
        
        # 여러 가능한 상품 선택자 시도
        product_selectors = [
            "[data-testid*='product' i]",
            "[data-testid*='bonus' i]",
            ".product-card",
            ".bonus-item",
            "article",
            "[class*='product' i]",
            "[class*='bonus' i]",
        ]
        
        all_elements = []
        for selector in product_selectors:
            try:
                elements = await page.locator(selector).all()
                if elements:
                    all_elements.extend(elements)
                    print(f"[INFO] {len(elements)}개의 요소를 {selector}로 찾았습니다.")
            except Exception as e:
                continue
        
        # 중복 제거 (같은 요소를 여러 선택자로 찾을 수 있음)
        seen = set()
        unique_elements = []
        for elem in all_elements:
            try:
                elem_id = await elem.get_attribute("data-testid") or await elem.get_attribute("class") or str(await elem.inner_text())[:50]
                if elem_id and elem_id not in seen:
                    seen.add(elem_id)
                    unique_elements.append(elem)
            except:
                continue
        
        print(f"[INFO] 총 {len(unique_elements)}개의 고유한 상품 요소를 찾았습니다.")
        
        # 각 상품에서 정보 추출
        for idx, elem in enumerate(unique_elements[:100]):  # 최대 100개만 처리
            try:
                product_info = await self._extract_product_info(elem, idx)
                if product_info and product_info.get("name"):
                    products.append(product_info)
            except Exception as e:
                print(f"[WARNING] 상품 {idx} 추출 중 오류: {str(e)}")
                continue
        
        return products
    
    async def _extract_product_info(self, element, index):
        """개별 상품 요소에서 정보를 추출합니다."""
        try:
            # 상품명 추출
            name_selectors = [
                "h3", "h4", "h2",
                "[class*='title' i]",
                "[class*='name' i]",
                "[data-testid*='title' i]",
                "[data-testid*='name' i]",
            ]
            
            name = None
            for selector in name_selectors:
                try:
                    name_elem = element.locator(selector).first
                    if await name_elem.count() > 0:
                        name = await name_elem.inner_text()
                        name = name.strip() if name else None
                        if name:
                            break
                except:
                    continue
            
            if not name:
                # 요소 자체의 텍스트 사용
                try:
                    text = await element.inner_text()
                    lines = [line.strip() for line in text.split("\n") if line.strip()]
                    name = lines[0] if lines else None
                except:
                    pass
            
            # 가격 추출
            price_selectors = [
                "[class*='price' i]",
                "[data-testid*='price' i]",
                "[class*='amount' i]",
            ]
            
            price = None
            original_price = None
            for selector in price_selectors:
                try:
                    price_elem = element.locator(selector).first
                    if await price_elem.count() > 0:
                        price_text = await price_elem.inner_text()
                        price = self._parse_price(price_text)
                        if price:
                            break
                except:
                    continue
            
            # 이미지 URL 추출
            image_url = None
            try:
                img_elem = element.locator("img").first
                if await img_elem.count() > 0:
                    image_url = await img_elem.get_attribute("src") or await img_elem.get_attribute("data-src")
                    if image_url and not image_url.startswith("http"):
                        image_url = "https://www.ah.nl" + image_url
            except:
                pass
            
            # 유효한 상품만 반환
            if name and len(name) > 3:  # 최소 길이 체크
                return {
                    "name": name,
                    "price": price,
                    "original_price": original_price,
                    "image_url": image_url,
                    "index": index
                }
            
        except Exception as e:
            print(f"[WARNING] 상품 정보 추출 중 오류: {str(e)}")
        
        return None
    
    def _parse_price(self, price_text):
        """가격 텍스트에서 숫자 추출"""
        if not price_text:
            return None
        
        import re
        # 유로 기호나 숫자 찾기
        price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(",", "."))
        if price_match:
            try:
                return float(price_match.group().replace(",", "."))
            except:
                pass
        return None


async def main():
    """메인 실행 함수"""
    scraper = AHScraper()
    try:
        data = await scraper.scrape_next_week_bonus()
        print(f"\n[완료] 총 {data['total_count']}개의 상품을 스크래핑했습니다.")
        return data
    except Exception as e:
        print(f"\n[실패] 스크래핑 실패: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
