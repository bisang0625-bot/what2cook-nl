#!/usr/bin/env python3
"""
🛒 네덜란드 마트 통합 할인 정보 스크래퍼
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Jina Reader + Gemini API를 사용하여 네덜란드 주요 마트들의
할인 정보를 한 번에 수집합니다.

🚀 실행 방법:
    python3 scraper/scrape_all_stores.py

📁 출력 파일:
    data/all_stores_sales.json  - 모든 마트 통합 데이터
    data/current_sales.json     - 앱에서 사용하는 형식
    data/weekly_sales.json      - 기존 호환 형식

⚙️ 필요 설정:
    config.py에 GEMINI_API_KEY 설정 필요

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import asyncio
import aiohttp
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

# config.py에서 API 키 가져오기
sys.path.insert(0, str(PROJECT_ROOT))
try:
    from config import GEMINI_API_KEY
except ImportError:
    GEMINI_API_KEY = None

# 환경변수에서도 확인
if not GEMINI_API_KEY:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ 오류: GEMINI_API_KEY가 설정되지 않았습니다.")
    print("   config.py 파일에 GEMINI_API_KEY를 설정해주세요.")
    print("   API 키 발급: https://aistudio.google.com/app/apikey")
    sys.exit(1)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📋 타겟 마트 설정
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STORES: Dict[str, str] = {
    "Albert Heijn": "https://www.ah.nl/bonus",
    "Dirk": "https://www.dirk.nl/aanbiedingen",
    "Lidl": "https://www.lidl.nl/c/aanbiedingen/a10008785",
    "ALDI": "https://www.aldi.nl/aanbiedingen.html",
    "Plus": "https://www.plus.nl/aanbiedingen",
    "Coop": "https://www.coop.nl/aanbiedingen",
    "Hoogvliet": "https://www.hoogvliet.com/aanbiedingen",
}

# Jina Reader API 기본 URL
JINA_BASE_URL = "https://r.jina.ai"

# Gemini API 설정
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📦 데이터 클래스
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class Product:
    """상품 정보"""
    product_name: str
    price: Optional[str] = None
    original_price: Optional[str] = None
    discount_label: Optional[str] = None
    valid_date: Optional[str] = None
    unit: Optional[str] = None
    store: str = ""
    category: str = "main"  # main, sub, fruits
    scraped_at: str = ""


@dataclass
class StoreResult:
    """마트별 스크래핑 결과"""
    store: str
    success: bool
    products: List[Dict[str, Any]]
    error: Optional[str] = None
    scraped_at: str = ""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔧 유틸리티 함수
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_week_dates() -> Tuple[str, str]:
    """이번 주 월요일~일요일 날짜 반환"""
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)
    return monday.strftime('%Y-%m-%d'), sunday.strftime('%Y-%m-%d')


def get_next_week_dates() -> Tuple[str, str]:
    """다음 주 월요일~일요일 날짜 반환"""
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    next_monday = monday + timedelta(days=7)
    next_sunday = next_monday + timedelta(days=6)
    return next_monday.strftime('%Y-%m-%d'), next_sunday.strftime('%Y-%m-%d')


def categorize_product(product_name: str) -> str:
    """상품을 카테고리로 분류 (main/sub/fruits)"""
    name_lower = product_name.lower()
    
    # 과일 키워드
    fruit_keywords = [
        'appel', 'peer', 'druif', 'druiven', 'banaan', 'sinaasappel', 'mandarijn',
        'aardbei', 'framboos', 'blauwe bessen', 'kiwi', 'mango', 'ananas', 'citroen',
        'limoen', 'meloen', 'watermeloen', 'perzik', 'pruim', 'kers', 'fruit'
    ]
    
    # 주재료 키워드 (육류, 생선, 주요 채소)
    main_keywords = [
        'kip', 'varken', 'rund', 'gehakt', 'speklap', 'karbonade', 'worst', 'bacon',
        'zalm', 'vis', 'garnaal', 'tonijn', 'makreel', 'haring',
        'aardappel', 'ui', 'tomaat', 'paprika', 'broccoli', 'bloemkool', 'sla',
        'komkommer', 'wortel', 'champignon', 'spinazie', 'boerenkool', 'andijvie'
    ]
    
    # 분류
    if any(kw in name_lower for kw in fruit_keywords):
        return 'fruits'
    elif any(kw in name_lower for kw in main_keywords):
        return 'main'
    else:
        return 'sub'


def print_progress(message: str, emoji: str = "📌"):
    """진행 상황 출력"""
    print(f"{emoji} {message}")


def print_error(store: str, error: str):
    """에러 출력"""
    print(f"❌ Error: [{store}] 실패 - {error}")


def print_success(store: str, count: int):
    """성공 출력"""
    print(f"✅ [{store}] {count}개 상품 추출 완료")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🌐 Jina Reader API 호출 (비동기)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def fetch_markdown_from_jina(
    session: aiohttp.ClientSession, 
    store: str, 
    url: str
) -> Tuple[str, Optional[str], Optional[str]]:
    """
    Jina Reader API를 통해 마크다운 텍스트 가져오기 (비동기)
    
    Returns:
        (store, markdown_text, error)
    """
    # URL 인코딩 (특수문자 처리)
    encoded_url = url
    jina_url = f"{JINA_BASE_URL}/{encoded_url}"
    
    try:
        print_progress(f"[{store}] Jina Reader 요청 중... URL: {url}", "📡")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/plain',
        }
        
        async with session.get(jina_url, headers=headers, timeout=aiohttp.ClientTimeout(total=90)) as response:
            if response.status == 200:
                markdown_text = await response.text()
                # 다음 주 페이지인지 확인 (키워드 체크)
                if 'volgende-week' in url.lower() or 'next week' in url.lower():
                    if 'volgende week' in markdown_text.lower() or 'next week' in markdown_text.lower():
                        print_progress(f"[{store}] 다음 주 세일 정보 확인됨", "✅")
                    else:
                        print_progress(f"[{store}] 다음 주 세일 정보가 마크다운에 없을 수 있음", "⚠️")
                
                print_progress(f"[{store}] 마크다운 수신 ({len(markdown_text):,}자)", "📥")
                return store, markdown_text, None
            else:
                error = f"HTTP {response.status}"
                print_error(store, f"{error} - URL: {url}")
                return store, None, error
                
    except asyncio.TimeoutError:
        error = "요청 시간 초과 (90초)"
        print_error(store, f"{error} - URL: {url}")
        return store, None, error
    except Exception as e:
        error = str(e)
        print_error(store, f"{error} - URL: {url}")
        return store, None, error


async def fetch_all_stores_markdown(stores: Dict[str, str]) -> Dict[str, Tuple[Optional[str], Optional[str]]]:
    """
    모든 마트의 마크다운을 비동기로 동시에 가져오기
    
    Returns:
        {store: (markdown_text, error)}
    """
    print("\n" + "=" * 60)
    print("📡 Step 1: Jina Reader API로 모든 마트 데이터 동시 수집")
    print("=" * 60 + "\n")
    
    results = {}
    
    connector = aiohttp.TCPConnector(limit=5)  # 동시 연결 수 제한
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [
            fetch_markdown_from_jina(session, store, url)
            for store, url in stores.items()
        ]
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        for response in responses:
            if isinstance(response, Exception):
                continue
            store, markdown, error = response
            results[store] = (markdown, error)
    
    # 결과 요약
    success_count = sum(1 for _, (md, _) in results.items() if md)
    print(f"\n📊 Jina Reader 결과: {success_count}/{len(stores)} 마트 성공")
    
    return results


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🤖 Gemini API로 상품 정보 추출
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def parse_products_with_gemini(
    session: aiohttp.ClientSession,
    store: str,
    markdown_text: str
) -> Tuple[str, List[Dict[str, Any]], Optional[str]]:
    """
    Gemini API로 마크다운에서 상품 정보 추출 (비동기)
    
    Returns:
        (store, products, error)
    """
    print_progress(f"[{store}] Gemini API로 파싱 중...", "🤖")
    
    # 텍스트가 너무 길면 자르기 (토큰 제한)
    max_length = 20000
    if len(markdown_text) > max_length:
        markdown_text = markdown_text[:max_length]
    
    # System Prompt
    prompt = f"""너는 네덜란드 마트 할인 정보를 정리하는 전문가야.

입력된 텍스트는 '{store}' 마트의 할인 페이지를 마크다운으로 변환한 것이야.

이 텍스트에서 할인 상품 정보를 추출해서 JSON 배열로 반환해줘.

**추출할 필드:**
- product_name: 상품명 (네덜란드어 원문 그대로, 필수)
- price: 할인가격 (예: "€2.99", 없으면 null)
- original_price: 원래 가격 (예: "€3.99", 없으면 null)
- discount_label: 할인 내용 (예: "1+1", "2e halve prijs", "25% korting", "2 voor €5")
- valid_date: 유효기간 (찾을 수 있다면, 예: "13 jan - 19 jan", 없으면 null)
- unit: 단위/용량 (예: "500g", "1L", 없으면 null)

**규칙:**
1. 실제 식품/상품만 추출해 (광고, 배너, 메뉴 항목 제외)
2. 중복 상품은 제외해
3. 최소 product_name과 discount_label 중 하나는 있어야 해
4. JSON 배열만 출력해 (다른 텍스트 없이)
5. 최대 100개까지만 추출해

**입력 텍스트:**
```
{markdown_text}
```

**출력 (JSON 배열만):**"""

    try:
        async with session.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.1,
                    "topP": 0.95,
                    "maxOutputTokens": 8192,
                }
            },
            timeout=aiohttp.ClientTimeout(total=120)
        ) as response:
            if response.status != 200:
                error = f"Gemini API HTTP {response.status}"
                print_error(store, error)
                return store, [], error
            
            result = await response.json()
            
            # 응답에서 텍스트 추출
            generated_text = (
                result.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
            )
            
            # JSON 파싱
            products = parse_json_response(generated_text)
            
            if products:
                print_success(store, len(products))
            else:
                print_progress(f"[{store}] 추출된 상품 없음", "⚠️")
            
            return store, products, None
            
    except asyncio.TimeoutError:
        error = "Gemini API 시간 초과 (120초)"
        print_error(store, error)
        return store, [], error
    except Exception as e:
        error = str(e)
        print_error(store, error)
        return store, [], error


def parse_json_response(text: str) -> List[Dict[str, Any]]:
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
        return []


async def parse_all_stores_with_gemini(
    markdown_results: Dict[str, Tuple[Optional[str], Optional[str]]]
) -> Dict[str, StoreResult]:
    """
    모든 마트의 마크다운을 Gemini로 파싱 (비동기)
    """
    print("\n" + "=" * 60)
    print("🤖 Step 2: Gemini API로 상품 정보 추출")
    print("=" * 60 + "\n")
    
    results = {}
    
    # 마크다운이 있는 마트만 처리
    stores_with_data = {
        store: markdown 
        for store, (markdown, error) in markdown_results.items() 
        if markdown
    }
    
    if not stores_with_data:
        print("⚠️ 파싱할 데이터가 없습니다.")
        return results
    
    connector = aiohttp.TCPConnector(limit=3)  # Gemini API 동시 호출 제한
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [
            parse_products_with_gemini(session, store, markdown)
            for store, markdown in stores_with_data.items()
        ]
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        for response in responses:
            if isinstance(response, Exception):
                continue
            store, products, error = response
            results[store] = StoreResult(
                store=store,
                success=len(products) > 0,
                products=products,
                error=error,
                scraped_at=datetime.now().isoformat()
            )
    
    # 실패한 마트 결과 추가
    for store, (markdown, error) in markdown_results.items():
        if store not in results:
            results[store] = StoreResult(
                store=store,
                success=False,
                products=[],
                error=error or "Jina Reader 실패",
                scraped_at=datetime.now().isoformat()
            )
    
    return results


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📁 결과 저장
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def save_results(store_results: Dict[str, StoreResult], week_type: str = 'current') -> Dict[str, Any]:
    """
    결과를 JSON 파일로 저장
    
    Args:
        store_results: 마트별 스크래핑 결과
        week_type: 'current' (이번 주) 또는 'next' (다음 주)
    """
    print("\n" + "=" * 60)
    print(f"💾 Step 3: 결과 저장 ({week_type} week)")
    print("=" * 60 + "\n")
    
    if week_type == 'next':
        start_date, end_date = get_next_week_dates()
    else:
        start_date, end_date = get_week_dates()
    
    today = datetime.now()
    
    # 모든 상품 수집
    all_products = []
    successful_stores = []
    failed_stores = []
    
    for store, result in store_results.items():
        if result.success and result.products:
            successful_stores.append(store)
            
            for product in result.products:
                # 카테고리 분류
                category = categorize_product(product.get('product_name', ''))
                
                # 표준화된 상품 데이터
                standardized_product = {
                    'supermarket': store,
                    'store': store,
                    'product_name': product.get('product_name', ''),
                    'price_info': product.get('price'),
                    'original_price': product.get('original_price'),
                    'discount_info': product.get('discount_label'),
                    'unit': product.get('unit'),
                    'valid_date': product.get('valid_date'),
                    'category': category,
                    'start_date': start_date,
                    'end_date': end_date,
                    'source': 'jina_reader',
                    'scraped_at': datetime.now().isoformat()
                }
                all_products.append(standardized_product)
        else:
            failed_stores.append(store)
    
    # 통합 결과
    if week_type == 'next':
        # 다음 주의 주차 계산
        next_monday = datetime.strptime(start_date, '%Y-%m-%d')
        week_number = f"{next_monday.year}-{next_monday.isocalendar()[1]:02d}"
    else:
        week_number = f"{today.year}-{today.isocalendar()[1]:02d}"
    
    combined_result = {
        'scraped_at': datetime.now().isoformat(),
        'week_type': week_type,
        'week_number': week_number,
        'start_date': start_date,
        'end_date': end_date,
        'total_products': len(all_products),
        'supermarkets': {
            'successful': successful_stores,
            'failed': failed_stores
        },
        'products': all_products
    }
    
    # 상세 결과 (마트별)
    detailed_result = {
        'scraped_at': datetime.now().isoformat(),
        'stores': {
            store: {
                'success': result.success,
                'product_count': len(result.products),
                'error': result.error,
                'products': result.products
            }
            for store, result in store_results.items()
        }
    }
    
    # 파일 저장
    if week_type == 'next':
        # 다음 주 데이터 저장
        next_sales_path = DATA_DIR / "next_sales.json"
        with open(next_sales_path, 'w', encoding='utf-8') as f:
            json.dump(combined_result, f, ensure_ascii=False, indent=2)
        print(f"📁 저장 완료: {next_sales_path}")
    else:
        # 이번 주 데이터 저장
        # 1. 상세 결과
        all_stores_path = DATA_DIR / "all_stores_sales.json"
        with open(all_stores_path, 'w', encoding='utf-8') as f:
            json.dump(detailed_result, f, ensure_ascii=False, indent=2)
        print(f"📁 저장 완료: {all_stores_path}")
        
        # 2. 앱용 통합 결과 (current_sales.json)
        current_sales_path = DATA_DIR / "current_sales.json"
        with open(current_sales_path, 'w', encoding='utf-8') as f:
            json.dump(combined_result, f, ensure_ascii=False, indent=2)
        print(f"📁 저장 완료: {current_sales_path}")
        
        # 3. 기존 호환용 (weekly_sales.json)
        weekly_sales_path = DATA_DIR / "weekly_sales.json"
        with open(weekly_sales_path, 'w', encoding='utf-8') as f:
            json.dump(combined_result, f, ensure_ascii=False, indent=2)
        print(f"📁 저장 완료: {weekly_sales_path}")
    
    return combined_result


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🚀 메인 실행
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def scrape_week(week_type: str = 'current') -> Dict[str, Any]:
    """
    특정 주차의 세일 데이터 스크래핑
    
    Args:
        week_type: 'current' (이번 주) 또는 'next' (다음 주)
    """
    start_time = time.time()
    
    print("\n" + "=" * 60)
    print(f"🛒 네덜란드 마트 통합 할인 정보 스크래퍼 ({week_type} week)")
    print("=" * 60)
    print(f"📅 실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🏪 타겟 마트: {', '.join(STORES.keys())}")
    print("=" * 60)
    
    # 다음 주 URL 변환 (일부 마트는 다음 주 URL이 다를 수 있음)
    stores_to_scrape = STORES.copy()
    if week_type == 'next':
        # 다음 주 URL로 변환 (가능한 경우)
        next_week_urls = {}
        for store, url in STORES.items():
            # AH는 다음 주 URL이 다름 (명시적으로 설정)
            if store == "Albert Heijn":
                next_week_urls[store] = "https://www.ah.nl/bonus/volgende-week"
                print_progress(f"[{store}] 다음 주 URL: {next_week_urls[store]}", "🔗")
            # 다른 마트는 URL에 "volgende-week" 추가 시도
            elif "aanbiedingen" in url:
                # URL 끝에 /volgende-week 추가
                next_week_urls[store] = url.rstrip('/') + "/volgende-week"
                print_progress(f"[{store}] 다음 주 URL: {next_week_urls[store]}", "🔗")
            else:
                # 기본 URL 유지
                next_week_urls[store] = url
        stores_to_scrape = next_week_urls
        print(f"\n📋 다음 주 크롤링 대상 URL:")
        for store, url in stores_to_scrape.items():
            print(f"   - {store}: {url}")
    
    # Step 1: Jina Reader로 마크다운 가져오기 (비동기)
    markdown_results = await fetch_all_stores_markdown(stores_to_scrape)
    
    # Step 2: Gemini로 파싱 (비동기)
    store_results = await parse_all_stores_with_gemini(markdown_results)
    
    # Step 3: 결과 저장
    final_result = save_results(store_results, week_type)
    
    # 최종 요약
    elapsed_time = time.time() - start_time
    
    print("\n" + "=" * 60)
    print(f"📊 {week_type} week 결과 요약")
    print("=" * 60)
    print(f"✅ 성공: {', '.join(final_result['supermarkets']['successful']) or '없음'}")
    print(f"❌ 실패: {', '.join(final_result['supermarkets']['failed']) or '없음'}")
    print(f"📦 총 상품: {final_result['total_products']}개")
    print(f"⏱️ 소요 시간: {elapsed_time:.1f}초")
    print("=" * 60)
    
    return final_result


async def main():
    """메인 비동기 실행 함수 (이번 주 + 다음 주 모두)"""
    total_start_time = time.time()
    
    print("\n" + "=" * 70)
    print("🛒 네덜란드 마트 통합 할인 정보 스크래퍼")
    print("=" * 70)
    print(f"📅 실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🏪 타겟 마트: {', '.join(STORES.keys())}")
    print("=" * 70)
    
    # 이번 주 스크래핑
    current_result = await scrape_week('current')
    
    # 다음 주 스크래핑
    next_result = await scrape_week('next')
    
    # 전체 요약
    total_elapsed = time.time() - total_start_time
    
    print("\n" + "=" * 70)
    print("📊 전체 결과 요약")
    print("=" * 70)
    print(f"✅ 이번 주: {current_result['total_products']}개 상품")
    print(f"✅ 다음 주: {next_result['total_products']}개 상품")
    print(f"📦 총 상품: {current_result['total_products'] + next_result['total_products']}개")
    print(f"⏱️ 총 소요 시간: {total_elapsed:.1f}초")
    print("=" * 70)
    
    return {
        'current': current_result,
        'next': next_result
    }


def run():
    """동기 실행 래퍼 (비개발자용)"""
    return asyncio.run(main())


if __name__ == "__main__":
    run()
