#!/usr/bin/env python3
"""
Albert Heijn Bonus 스크래퍼 (Jina Reader + Gemini API)

Jina Reader API를 사용하여 AH 보너스 페이지를 마크다운으로 가져오고,
Gemini API로 상품 정보를 추출합니다.

사용법:
    python scraper/scrape_ah_jina.py
    
    # 다음 주 세일 정보
    python scraper/scrape_ah_jina.py --next-week

필요한 환경변수:
    GEMINI_API_KEY: Gemini API 키 (.env 파일 또는 환경변수)
"""

import json
import os
import sys
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

import requests
from dotenv import load_dotenv

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

# .env 파일 로드
load_dotenv(PROJECT_ROOT / ".env")

# config.py에서 API 키 가져오기 (fallback)
import sys
sys.path.insert(0, str(PROJECT_ROOT))
try:
    from config import GEMINI_API_KEY as CONFIG_API_KEY
except ImportError:
    CONFIG_API_KEY = None


class AHJinaScraper:
    """Albert Heijn 보너스 스크래퍼 (Jina + Gemini)"""
    
    # Jina Reader API URL
    JINA_BASE_URL = "https://r.jina.ai"
    
    # AH 보너스 페이지 URL
    AH_BONUS_URL = "https://www.ah.nl/bonus"
    AH_BONUS_NEXT_WEEK_URL = "https://www.ah.nl/bonus/volgende-week"
    
    def __init__(self):
        """초기화"""
        # Gemini API 키 로드
        self.gemini_api_key = os.getenv("GEMINI_API_KEY") or CONFIG_API_KEY
        
        if not self.gemini_api_key:
            raise ValueError(
                "GEMINI_API_KEY가 설정되지 않았습니다.\n"
                "다음 중 하나의 방법으로 API 키를 설정하세요:\n"
                "1. .env 파일에 GEMINI_API_KEY=your_api_key 형태로 저장\n"
                "2. config.py 파일에 GEMINI_API_KEY 변수 설정\n\n"
                "API 키 발급: https://aistudio.google.com/app/apikey"
            )
        
        # Gemini API 설정
        self.gemini_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        
    def fetch_markdown_from_jina(self, url: str) -> Optional[str]:
        """
        Jina Reader API를 통해 웹 페이지를 마크다운으로 가져옵니다.
        
        Args:
            url: 가져올 웹 페이지 URL
            
        Returns:
            마크다운 형식의 텍스트
        """
        jina_url = f"{self.JINA_BASE_URL}/{url}"
        
        print(f"📡 Jina Reader API 호출: {jina_url}")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Accept': 'text/plain',
            }
            
            response = requests.get(jina_url, headers=headers, timeout=60)
            response.raise_for_status()
            
            markdown_text = response.text
            print(f"✅ 마크다운 데이터 수신 완료 ({len(markdown_text):,} 문자)")
            
            return markdown_text
            
        except requests.RequestException as e:
            print(f"❌ Jina Reader API 오류: {e}")
            return None
    
    def extract_products_with_gemini(self, markdown_text: str) -> List[Dict[str, Any]]:
        """
        Gemini API를 사용하여 마크다운 텍스트에서 상품 정보를 추출합니다.
        
        Args:
            markdown_text: AH 보너스 페이지의 마크다운 텍스트
            
        Returns:
            추출된 상품 목록
        """
        print("🤖 Gemini API로 상품 정보 추출 중...")
        
        # 프롬프트 작성
        prompt = f"""다음은 네덜란드 Albert Heijn 슈퍼마켓의 이번 주 보너스(할인) 상품 페이지를 마크다운으로 변환한 텍스트입니다.

이 텍스트에서 할인 상품 정보를 추출하여 JSON 배열로 반환해주세요.

**추출할 필드:**
- product_name: 상품명 (네덜란드어 원문 그대로)
- discount_info: 할인 내용 (예: "1+1", "2e halve prijs", "25% korting", "2 voor €5")
- original_price: 원래 가격 (예: "€2.99", 없으면 null)
- discounted_price: 할인 가격 (예: "€1.99", 없으면 null)
- unit: 단위/용량 (예: "500g", "1L", 없으면 null)

**규칙:**
1. 실제 식품/상품만 추출하세요 (광고, 배너, 메뉴 항목 제외)
2. 중복 상품은 제외하세요
3. 가격 정보가 없어도 할인 정보(discount_info)가 있으면 포함하세요
4. JSON 배열만 출력하세요 (다른 텍스트 없이)

**마크다운 텍스트:**
```
{markdown_text[:15000]}
```

**출력 형식 (JSON 배열만):**
[
  {{
    "product_name": "AH Verse pasta",
    "discount_info": "1+1",
    "original_price": "€2.99",
    "discounted_price": "€1.50",
    "unit": "400g"
  }},
  ...
]
"""

        try:
            response = requests.post(
                f"{self.gemini_url}?key={self.gemini_api_key}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.1,
                        "topP": 0.95,
                        "maxOutputTokens": 8192,
                    }
                },
                timeout=120
            )
            
            response.raise_for_status()
            result = response.json()
            
            # 응답에서 텍스트 추출
            generated_text = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            
            # JSON 파싱
            products = self._parse_json_response(generated_text)
            
            print(f"✅ {len(products)}개 상품 추출 완료")
            return products
            
        except requests.RequestException as e:
            print(f"❌ Gemini API 오류: {e}")
            return []
        except Exception as e:
            print(f"❌ 파싱 오류: {e}")
            return []
    
    def _parse_json_response(self, text: str) -> List[Dict[str, Any]]:
        """Gemini 응답에서 JSON 배열 추출"""
        # 코드 블록 제거
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        text = text.strip()
        
        # JSON 배열 찾기
        match = re.search(r'\[[\s\S]*\]', text)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        
        # 직접 파싱 시도
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            print(f"⚠️ JSON 파싱 실패, 응답 텍스트:\n{text[:500]}")
            return []
    
    def scrape_bonus(self, week: str = 'current') -> Dict[str, Any]:
        """
        AH 보너스 상품 스크래핑
        
        Args:
            week: 'current' (이번 주) 또는 'next' (다음 주)
            
        Returns:
            스크래핑 결과 딕셔너리
        """
        print("=" * 60)
        print(f"🛒 Albert Heijn Bonus 스크래핑 시작 ({week} week)")
        print("=" * 60)
        
        # URL 선택
        if week == 'next':
            url = self.AH_BONUS_NEXT_WEEK_URL
        else:
            url = self.AH_BONUS_URL
        
        # Step 1: Jina Reader로 마크다운 가져오기
        markdown_text = self.fetch_markdown_from_jina(url)
        
        if not markdown_text:
            return self._empty_result(week)
        
        # Step 2: Gemini로 상품 정보 추출
        products = self.extract_products_with_gemini(markdown_text)
        
        if not products:
            return self._empty_result(week)
        
        # 날짜 계산
        today = datetime.now()
        if week == 'current':
            monday = today - timedelta(days=today.weekday())
        else:
            days_until_next_monday = (7 - today.weekday()) % 7
            if days_until_next_monday == 0:
                days_until_next_monday = 7
            monday = today + timedelta(days=days_until_next_monday)
        
        sunday = monday + timedelta(days=6)
        
        # 상품 데이터에 메타정보 추가
        for product in products:
            product['supermarket'] = 'Albert Heijn'
            product['store'] = 'Albert Heijn'
            product['start_date'] = monday.strftime('%Y-%m-%d')
            product['end_date'] = sunday.strftime('%Y-%m-%d')
            product['source'] = 'jina_reader'
            product['scraped_at'] = datetime.now().isoformat()
        
        # 결과 구성
        result = {
            'scraped_at': datetime.now().isoformat(),
            'week_type': week,
            'week_number': f"{monday.year}-{monday.isocalendar()[1]:02d}",
            'start_date': monday.strftime('%Y-%m-%d'),
            'end_date': sunday.strftime('%Y-%m-%d'),
            'source': 'ah.nl/bonus via Jina Reader + Gemini',
            'supermarket': 'Albert Heijn',
            'total_products': len(products),
            'products': products
        }
        
        print(f"\n🎯 총 {len(products)}개 상품 수집 완료")
        return result
    
    def _empty_result(self, week: str) -> Dict[str, Any]:
        """빈 결과 반환"""
        return {
            'scraped_at': datetime.now().isoformat(),
            'week_type': week,
            'source': 'ah.nl/bonus via Jina Reader + Gemini',
            'supermarket': 'Albert Heijn',
            'total_products': 0,
            'products': []
        }
    
    def save_results(self, result: Dict[str, Any], filename: str = None):
        """결과 저장"""
        if filename is None:
            filename = "ah_bonus_list.json"
        
        output_path = DATA_DIR / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"💾 저장 완료: {output_path}")
        return output_path


class JumboJinaScraper:
    """Jumbo 프로모션 스크래퍼 (Jina + Gemini)"""
    
    JINA_BASE_URL = "https://r.jina.ai"
    JUMBO_PROMOTIONS_URL = "https://www.jumbo.com/aanbiedingen"
    JUMBO_PROMOTIONS_NEXT_WEEK_URL = "https://www.jumbo.com/aanbiedingen/volgende-week"
    
    def __init__(self):
        """초기화"""
        self.gemini_api_key = os.getenv("GEMINI_API_KEY") or CONFIG_API_KEY
        
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다.")
        
        self.gemini_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    
    def fetch_markdown_from_jina(self, url: str) -> Optional[str]:
        """Jina Reader API로 마크다운 가져오기"""
        jina_url = f"{self.JINA_BASE_URL}/{url}"
        
        print(f"📡 Jina Reader API 호출: {jina_url}")
        
        try:
            response = requests.get(jina_url, timeout=60)
            response.raise_for_status()
            
            markdown_text = response.text
            print(f"✅ 마크다운 데이터 수신 완료 ({len(markdown_text):,} 문자)")
            
            return markdown_text
            
        except requests.RequestException as e:
            print(f"❌ Jina Reader API 오류: {e}")
            return None
    
    def extract_products_with_gemini(self, markdown_text: str) -> List[Dict[str, Any]]:
        """Gemini API로 상품 정보 추출"""
        print("🤖 Gemini API로 상품 정보 추출 중...")
        
        prompt = f"""다음은 네덜란드 Jumbo 슈퍼마켓의 이번 주 할인 상품 페이지를 마크다운으로 변환한 텍스트입니다.

이 텍스트에서 할인 상품 정보를 추출하여 JSON 배열로 반환해주세요.

**추출할 필드:**
- product_name: 상품명 (네덜란드어 원문 그대로)
- discount_info: 할인 내용 (예: "1+1", "2e halve prijs", "25% korting")
- original_price: 원래 가격 (예: "€2.99", 없으면 null)
- discounted_price: 할인 가격 (예: "€1.99", 없으면 null)
- unit: 단위/용량 (예: "500g", "1L", 없으면 null)

**규칙:**
1. 실제 식품/상품만 추출하세요
2. 중복 상품은 제외하세요
3. JSON 배열만 출력하세요

**마크다운 텍스트:**
```
{markdown_text[:15000]}
```

**출력 형식 (JSON 배열만):**
"""

        try:
            response = requests.post(
                f"{self.gemini_url}?key={self.gemini_api_key}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {
                        "temperature": 0.1,
                        "maxOutputTokens": 8192,
                    }
                },
                timeout=120
            )
            
            response.raise_for_status()
            result = response.json()
            
            generated_text = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            
            # JSON 파싱
            text = re.sub(r'```json\s*', '', generated_text)
            text = re.sub(r'```\s*', '', text).strip()
            
            match = re.search(r'\[[\s\S]*\]', text)
            if match:
                products = json.loads(match.group())
                print(f"✅ {len(products)}개 상품 추출 완료")
                return products
            
            return []
            
        except Exception as e:
            print(f"❌ Gemini API 오류: {e}")
            return []
    
    def scrape_promotions(self, week: str = 'current') -> Dict[str, Any]:
        """Jumbo 프로모션 스크래핑"""
        print("=" * 60)
        print(f"🛒 Jumbo 프로모션 스크래핑 시작 ({week} week)")
        print("=" * 60)
        
        url = self.JUMBO_PROMOTIONS_NEXT_WEEK_URL if week == 'next' else self.JUMBO_PROMOTIONS_URL
        
        markdown_text = self.fetch_markdown_from_jina(url)
        
        if not markdown_text:
            return {'total_products': 0, 'products': []}
        
        products = self.extract_products_with_gemini(markdown_text)
        
        # 날짜 계산
        today = datetime.now()
        if week == 'current':
            monday = today - timedelta(days=today.weekday())
        else:
            days_until_next_monday = (7 - today.weekday()) % 7 or 7
            monday = today + timedelta(days=days_until_next_monday)
        
        sunday = monday + timedelta(days=6)
        
        # 메타정보 추가
        for product in products:
            product['supermarket'] = 'Jumbo'
            product['store'] = 'Jumbo'
            product['start_date'] = monday.strftime('%Y-%m-%d')
            product['end_date'] = sunday.strftime('%Y-%m-%d')
            product['source'] = 'jina_reader'
            product['scraped_at'] = datetime.now().isoformat()
        
        result = {
            'scraped_at': datetime.now().isoformat(),
            'week_type': week,
            'supermarket': 'Jumbo',
            'total_products': len(products),
            'products': products
        }
        
        print(f"\n🎯 총 {len(products)}개 상품 수집 완료")
        return result


def scrape_all_supermarkets(week: str = 'current') -> Dict[str, Any]:
    """모든 슈퍼마켓 스크래핑 (AH + Jumbo)"""
    all_products = []
    successful = []
    failed = []
    
    print("\n" + "=" * 70)
    print(f"🚀 Jina Reader + Gemini 통합 스크래퍼 시작 ({week} week)")
    print("=" * 70)
    
    # Albert Heijn
    try:
        ah_scraper = AHJinaScraper()
        ah_result = ah_scraper.scrape_bonus(week)
        
        if ah_result['products']:
            all_products.extend(ah_result['products'])
            successful.append('Albert Heijn')
        else:
            failed.append('Albert Heijn')
    except Exception as e:
        print(f"❌ Albert Heijn 실패: {e}")
        failed.append('Albert Heijn')
    
    # Jumbo
    try:
        jumbo_scraper = JumboJinaScraper()
        jumbo_result = jumbo_scraper.scrape_promotions(week)
        
        if jumbo_result['products']:
            all_products.extend(jumbo_result['products'])
            successful.append('Jumbo')
        else:
            failed.append('Jumbo')
    except Exception as e:
        print(f"❌ Jumbo 실패: {e}")
        failed.append('Jumbo')
    
    # 날짜 계산
    today = datetime.now()
    if week == 'current':
        monday = today - timedelta(days=today.weekday())
    else:
        days_until_next_monday = (7 - today.weekday()) % 7 or 7
        monday = today + timedelta(days=days_until_next_monday)
    
    result = {
        'week_number': f"{monday.year}-{monday.isocalendar()[1]:02d}",
        'week_type': week,
        'scraped_at': datetime.now().isoformat(),
        'total_products': len(all_products),
        'supermarkets': {
            'successful': successful,
            'failed': failed
        },
        'products': all_products
    }
    
    print("\n" + "=" * 70)
    print(f"📊 최종 결과")
    print(f"  - 총 상품: {len(all_products)}개")
    print(f"  - 성공: {', '.join(successful) or '없음'}")
    print(f"  - 실패: {', '.join(failed) or '없음'}")
    print("=" * 70)
    
    return result


def main():
    """메인 실행 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AH/Jumbo 세일 정보 스크래퍼 (Jina + Gemini)')
    parser.add_argument('--next-week', action='store_true', help='다음 주 세일 정보 가져오기')
    parser.add_argument('--all', action='store_true', help='모든 슈퍼마켓 스크래핑 (AH + Jumbo)')
    parser.add_argument('--jumbo', action='store_true', help='Jumbo만 스크래핑')
    args = parser.parse_args()
    
    week = 'next' if args.next_week else 'current'
    
    if args.all:
        # 모든 슈퍼마켓
        result = scrape_all_supermarkets(week)
        
        # 저장
        if week == 'current':
            filename = 'current_sales.json'
        else:
            filename = 'next_sales.json'
        
        output_path = DATA_DIR / filename
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n💾 저장 완료: {output_path}")
        
        # weekly_sales.json도 업데이트
        with open(DATA_DIR / 'weekly_sales.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"💾 저장 완료: {DATA_DIR / 'weekly_sales.json'}")
        
    elif args.jumbo:
        # Jumbo만
        scraper = JumboJinaScraper()
        result = scraper.scrape_promotions(week)
        
        output_path = DATA_DIR / 'jumbo_promotions.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n💾 저장 완료: {output_path}")
        
    else:
        # Albert Heijn만 (기본)
        scraper = AHJinaScraper()
        result = scraper.scrape_bonus(week)
        scraper.save_results(result, 'ah_bonus_list.json')
    
    return result


if __name__ == "__main__":
    main()
