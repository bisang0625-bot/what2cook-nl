#!/usr/bin/env python3
"""
🧠 스마트 스크래핑 스케줄러
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

마트별 세일 업데이트 요일을 분석하여 최적의 스크래핑 시점을 결정합니다.
Gemini API 사용량을 최소화하기 위해 불필요한 스크래핑을 방지합니다.

📅 마트별 세일 시작일:
- 월요일 시작: Albert Heijn, ALDI, Plus, Hoogvliet, Coop
- 수요일 시작: Jumbo, Dirk

🎯 최적 스크래핑 전략:
1. 월요일 시작 마트: 일요일 22:00 또는 월요일 06:00
2. 수요일 시작 마트: 화요일 22:00 또는 수요일 06:00
3. 통합 스크래핑: 일요일 22:00 (대부분의 마트를 한 번에)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import json
import sys
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📋 마트별 세일 시작일 설정
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STORE_SALE_START_DAY: Dict[str, int] = {
    'Albert Heijn': 0,  # 월요일 (0 = Monday)
    'ALDI': 0,          # 월요일
    'Plus': 0,          # 월요일
    'Hoogvliet': 0,     # 월요일
    'Coop': 0,          # 월요일
    'Jumbo': 2,         # 수요일 (2 = Wednesday)
    'Dirk': 2,          # 수요일
    'Lidl': 0,          # 월요일 (추정)
}

# 요일 이름 매핑
WEEKDAY_NAMES = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']

# 마트별 URL (세일 정보 확인용)
STORE_URLS: Dict[str, str] = {
    'Albert Heijn': 'https://www.ah.nl/bonus',
    'ALDI': 'https://www.aldi.nl/aanbiedingen.html',
    'Plus': 'https://www.plus.nl/aanbiedingen',
    'Hoogvliet': 'https://www.hoogvliet.com/aanbiedingen',
    'Coop': 'https://www.coop.nl/aanbiedingen',
    'Jumbo': 'https://www.jumbo.com/aanbiedingen',
    'Dirk': 'https://www.dirk.nl/aanbiedingen',
    'Lidl': 'https://www.lidl.nl/c/aanbiedingen',
}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔍 세일 정보 업데이트 확인
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def check_sale_info_updated(store_name: str, week_type: str = 'current', max_retries: int = 3) -> Tuple[bool, str]:
    """
    세일 정보가 웹사이트에 업데이트되었는지 확인
    
    Args:
        store_name: 마트 이름
        week_type: 'current' 또는 'next'
        max_retries: 최대 재시도 횟수
    
    Returns:
        (is_updated, message)
    """
    if store_name not in STORE_URLS:
        return True, "URL 정보 없음 (스킵)"
    
    url = STORE_URLS[store_name]
    
    # 다음 주 확인을 위한 URL 변환
    if week_type == 'next':
        if store_name == 'Albert Heijn':
            url = 'https://www.ah.nl/bonus/volgende-week'
        elif 'aanbiedingen' in url:
            url = url.rstrip('/') + '/volgende-week'
    
    # Jina Reader로 간단히 확인
    jina_url = f"https://r.jina.ai/{url}"
    
    for attempt in range(max_retries):
        try:
            response = requests.get(jina_url, timeout=15)
            if response.status_code == 200:
                content = response.text.lower()
                
                # 세일 정보가 있는지 확인 (날짜, 상품명 등)
                today = datetime.now()
                if week_type == 'next':
                    # 다음 주 세일 확인
                    next_monday = today - timedelta(days=today.weekday()) + timedelta(days=7)
                    next_date_str = next_monday.strftime('%d %b').lower()  # 예: "19 jan"
                    
                    # 다음 주 관련 키워드 확인
                    has_next_week = (
                        'volgende week' in content or
                        'next week' in content or
                        next_date_str in content or
                        len(content) > 1000  # 충분한 콘텐츠가 있으면 업데이트된 것으로 간주
                    )
                    
                    if has_next_week:
                        return True, f"다음 주 세일 정보 확인됨 (시도 {attempt + 1}/{max_retries})"
                else:
                    # 이번 주 세일 확인
                    current_monday = today - timedelta(days=today.weekday())
                    current_date_str = current_monday.strftime('%d %b').lower()
                    
                    # 충분한 콘텐츠가 있으면 업데이트된 것으로 간주
                    if len(content) > 1000:
                        return True, f"세일 정보 확인됨 (시도 {attempt + 1}/{max_retries})"
                
                if attempt < max_retries - 1:
                    time.sleep(10)  # 10초 대기 후 재시도
                    continue
                else:
                    return False, f"세일 정보 미확인 (시도 {max_retries}회 실패)"
            
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(10)
                continue
            else:
                return False, f"확인 실패: {str(e)}"
    
    return False, "최대 재시도 횟수 초과"


def wait_for_sale_update(store_name: str, week_type: str = 'current', max_wait_minutes: int = 60, check_interval_minutes: int = 5) -> Tuple[bool, str]:
    """
    세일 정보가 업데이트될 때까지 대기
    
    Args:
        store_name: 마트 이름
        week_type: 'current' 또는 'next'
        max_wait_minutes: 최대 대기 시간 (분)
        check_interval_minutes: 확인 간격 (분)
    
    Returns:
        (is_updated, message)
    """
    print(f"\n⏳ [{store_name}] 세일 정보 업데이트 대기 중...")
    print(f"   최대 대기 시간: {max_wait_minutes}분, 확인 간격: {check_interval_minutes}분")
    
    start_time = datetime.now()
    check_count = 0
    
    while True:
        elapsed = (datetime.now() - start_time).total_seconds() / 60
        
        if elapsed > max_wait_minutes:
            return False, f"최대 대기 시간({max_wait_minutes}분) 초과"
        
        check_count += 1
        is_updated, message = check_sale_info_updated(store_name, week_type, max_retries=1)
        
        print(f"   [{check_count}회 확인] {message}")
        
        if is_updated:
            elapsed_str = f"{elapsed:.1f}분"
            return True, f"세일 정보 업데이트 확인됨 (대기 시간: {elapsed_str})"
        
        # 다음 확인까지 대기
        if elapsed + check_interval_minutes <= max_wait_minutes:
            print(f"   {check_interval_minutes}분 후 재확인...")
            time.sleep(check_interval_minutes * 60)
        else:
            break
    
    return False, "대기 시간 초과"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔍 스크래핑 필요 여부 확인
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_store_sale_start_day(store_name: str) -> int:
    """마트의 세일 시작일 반환 (0=월요일, 2=수요일)"""
    return STORE_SALE_START_DAY.get(store_name, 0)


def get_current_week_sale_start(store_name: str) -> datetime:
    """현재 주의 세일 시작일 계산"""
    today = datetime.now()
    days_since_monday = today.weekday()
    current_monday = today - timedelta(days=days_since_monday)
    
    sale_start_day = get_store_sale_start_day(store_name)
    sale_start = current_monday + timedelta(days=sale_start_day)
    
    # 시작일이 지났으면 다음 주
    if sale_start < today.replace(hour=0, minute=0, second=0):
        sale_start = current_monday + timedelta(days=7 + sale_start_day)
    
    return sale_start


def get_next_week_sale_start(store_name: str) -> datetime:
    """다음 주의 세일 시작일 계산"""
    today = datetime.now()
    days_since_monday = today.weekday()
    current_monday = today - timedelta(days=days_since_monday)
    next_monday = current_monday + timedelta(days=7)
    
    sale_start_day = get_store_sale_start_day(store_name)
    sale_start = next_monday + timedelta(days=sale_start_day)
    
    return sale_start


def check_if_scraping_needed(store_name: str, week_type: str = 'current') -> Tuple[bool, str]:
    """
    스크래핑이 필요한지 확인
    
    Returns:
        (needed, reason)
    """
    today = datetime.now()
    
    if week_type == 'current':
        sale_start = get_current_week_sale_start(store_name)
        sale_end = sale_start + timedelta(days=6)
        
        # 세일이 이미 시작되었고 아직 진행 중
        if sale_start <= today <= sale_end:
            # 데이터 파일 확인
            data_file = DATA_DIR / "current_sales.json"
            if data_file.exists():
                try:
                    with open(data_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # 해당 마트의 데이터가 있는지 확인
                    products = data.get('products', [])
                    store_products = [p for p in products if p.get('supermarket') == store_name or p.get('store') == store_name]
                    
                    if store_products:
                        # 데이터가 최신인지 확인 (세일 시작일 이후에 스크래핑되었는지)
                        scraped_at = data.get('scraped_at', '')
                        if scraped_at:
                            try:
                                scraped_date = datetime.fromisoformat(scraped_at.replace('Z', '+00:00'))
                                # 세일 시작일 이후에 스크래핑되었으면 OK
                                if scraped_date >= sale_start:
                                    return False, f"이미 최신 데이터 있음 (스크래핑: {scraped_date.strftime('%Y-%m-%d %H:%M')})"
                            except:
                                pass
                        
                        return True, f"데이터가 있지만 세일 시작일({sale_start.strftime('%Y-%m-%d')}) 이후 업데이트 필요"
                    
                    return True, f"데이터 없음"
                except:
                    return True, f"데이터 파일 확인 실패"
            
            return True, f"데이터 파일 없음"
        
        # 세일이 아직 시작되지 않음
        elif today < sale_start:
            days_until = (sale_start - today).days
            if days_until > 2:
                return False, f"세일 시작까지 {days_until}일 남음 ({sale_start.strftime('%Y-%m-%d')})"
            else:
                return True, f"세일 시작 임박 ({sale_start.strftime('%Y-%m-%d')})"
        
        # 세일이 이미 종료됨
        else:
            return False, f"세일 종료됨 ({sale_end.strftime('%Y-%m-%d')})"
    
    else:  # next week
        sale_start = get_next_week_sale_start(store_name)
        sale_end = sale_start + timedelta(days=6)
        
        # 다음 주 세일이 아직 멀리 있으면 스크래핑 불필요
        days_until = (sale_start - today).days
        if days_until > 5:
            return False, f"다음 주 세일까지 {days_until}일 남음"
        
        # 데이터 파일 확인
        data_file = DATA_DIR / "next_sales.json"
        if data_file.exists():
            try:
                with open(data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                products = data.get('products', [])
                store_products = [p for p in products if p.get('supermarket') == store_name or p.get('store') == store_name]
                
                if store_products:
                    scraped_at = data.get('scraped_at', '')
                    if scraped_at:
                        try:
                            scraped_date = datetime.fromisoformat(scraped_at.replace('Z', '+00:00'))
                            # 최근 3일 이내 스크래핑되었으면 OK
                            if (today - scraped_date).days < 3:
                                return False, f"최근 스크래핑됨 ({scraped_date.strftime('%Y-%m-%d %H:%M')})"
                        except:
                            pass
            except:
                pass
        
        return True, f"다음 주 세일 준비 필요 ({sale_start.strftime('%Y-%m-%d')})"


def get_optimal_scraping_time() -> Dict[str, any]:
    """
    최적의 스크래핑 시점 계산 (더 일찍 실행)
    
    Returns:
        {
            'recommended_time': datetime,
            'stores_to_scrape': List[str],
            'reason': str
        }
    """
    today = datetime.now()
    weekday = today.weekday()
    hour = today.hour
    
    # 월요일 시작 마트들
    monday_stores = [s for s, day in STORE_SALE_START_DAY.items() if day == 0]
    # 수요일 시작 마트들
    wednesday_stores = [s for s, day in STORE_SALE_START_DAY.items() if day == 2]
    
    # 현재 요일과 시간에 따른 추천 (더 일찍 실행)
    if weekday == 6:  # 일요일
        # 일요일 자정 (00:00)에 실행하여 사용자가 월요일 아침에 확인 가능
        return {
            'recommended_time': today.replace(hour=0, minute=0, second=0),
            'stores_to_scrape': monday_stores + wednesday_stores,  # 모두
            'reason': '일요일 자정 - 월요일/수요일 시작 마트 모두 준비 (사용자 미리 확인 가능)'
        }
    
    elif weekday == 0:  # 월요일
        if hour < 6:  # 월요일 새벽 6시 이전
            return {
                'recommended_time': today.replace(hour=0, minute=0, second=0),
                'stores_to_scrape': monday_stores,
                'reason': '월요일 새벽 - 월요일 시작 마트 (사용자 아침 확인 가능)'
            }
        else:
            return {
                'recommended_time': None,
                'stores_to_scrape': [],
                'reason': '월요일 오전 - 이미 스크래핑 완료 예상'
            }
    
    elif weekday == 1:  # 화요일
        # 화요일 자정 (00:00)에 실행하여 사용자가 수요일 아침에 확인 가능
        if hour < 6:
            return {
                'recommended_time': today.replace(hour=0, minute=0, second=0),
                'stores_to_scrape': wednesday_stores,
                'reason': '화요일 자정 - 수요일 시작 마트 준비 (사용자 아침 확인 가능)'
            }
        else:
            return {
                'recommended_time': None,
                'stores_to_scrape': [],
                'reason': '화요일 - 스크래핑 불필요'
            }
    
    elif weekday == 2:  # 수요일
        if hour < 6:  # 수요일 새벽 6시 이전
            return {
                'recommended_time': today.replace(hour=0, minute=0, second=0),
                'stores_to_scrape': wednesday_stores,
                'reason': '수요일 새벽 - 수요일 시작 마트 (사용자 아침 확인 가능)'
            }
        else:
            return {
                'recommended_time': None,
                'stores_to_scrape': [],
                'reason': '수요일 오전 - 이미 스크래핑 완료 예상'
            }
    
    else:  # 목요일~토요일
        return {
            'recommended_time': None,
            'stores_to_scrape': [],
            'reason': f'{WEEKDAY_NAMES[weekday]} - 스크래핑 불필요 (주말)'
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📊 스크래핑 필요성 분석
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def analyze_scraping_needs() -> Dict[str, any]:
    """모든 마트의 스크래핑 필요성 분석"""
    today = datetime.now()
    
    print("\n" + "=" * 70)
    print("🧠 스마트 스크래핑 필요성 분석")
    print("=" * 70)
    print(f"📅 분석 시점: {today.strftime('%Y-%m-%d %H:%M:%S')} ({WEEKDAY_NAMES[today.weekday()]})")
    print("=" * 70 + "\n")
    
    results = {
        'current_week': {},
        'next_week': {},
        'summary': {
            'current_needed': [],
            'current_not_needed': [],
            'next_needed': [],
            'next_not_needed': []
        }
    }
    
    # 이번 주 분석
    print("📅 이번 주 세일 데이터 분석")
    print("-" * 70)
    for store in STORE_SALE_START_DAY.keys():
        needed, reason = check_if_scraping_needed(store, 'current')
        sale_start = get_current_week_sale_start(store)
        
        results['current_week'][store] = {
            'needed': needed,
            'reason': reason,
            'sale_start': sale_start.strftime('%Y-%m-%d'),
            'sale_start_day': WEEKDAY_NAMES[sale_start.weekday()]
        }
        
        status = "✅ 필요" if needed else "⏭️ 불필요"
        print(f"{status} [{store}]")
        print(f"  세일 시작: {sale_start.strftime('%Y-%m-%d')} ({WEEKDAY_NAMES[sale_start.weekday()]})")
        print(f"  사유: {reason}")
        print()
        
        if needed:
            results['summary']['current_needed'].append(store)
        else:
            results['summary']['current_not_needed'].append(store)
    
    # 다음 주 분석
    print("\n📅 다음 주 세일 데이터 분석")
    print("-" * 70)
    for store in STORE_SALE_START_DAY.keys():
        needed, reason = check_if_scraping_needed(store, 'next')
        sale_start = get_next_week_sale_start(store)
        
        results['next_week'][store] = {
            'needed': needed,
            'reason': reason,
            'sale_start': sale_start.strftime('%Y-%m-%d'),
            'sale_start_day': WEEKDAY_NAMES[sale_start.weekday()]
        }
        
        status = "✅ 필요" if needed else "⏭️ 불필요"
        print(f"{status} [{store}]")
        print(f"  세일 시작: {sale_start.strftime('%Y-%m-%d')} ({WEEKDAY_NAMES[sale_start.weekday()]})")
        print(f"  사유: {reason}")
        print()
        
        if needed:
            results['summary']['next_needed'].append(store)
        else:
            results['summary']['next_not_needed'].append(store)
    
    # 최적 스크래핑 시점
    optimal = get_optimal_scraping_time()
    
    print("\n" + "=" * 70)
    print("🎯 최적 스크래핑 시점 추천")
    print("=" * 70)
    if optimal['recommended_time']:
        print(f"⏰ 추천 시간: {optimal['recommended_time'].strftime('%Y-%m-%d %H:%M')}")
        print(f"🏪 스크래핑 대상: {', '.join(optimal['stores_to_scrape'])}")
        print(f"📝 사유: {optimal['reason']}")
    else:
        print(f"⏸️ 현재는 스크래핑 불필요")
        print(f"📝 사유: {optimal['reason']}")
    print("=" * 70)
    
    # 요약
    print("\n📊 요약")
    print("-" * 70)
    print(f"이번 주 스크래핑 필요: {len(results['summary']['current_needed'])}개 마트")
    if results['summary']['current_needed']:
        print(f"  - {', '.join(results['summary']['current_needed'])}")
    print(f"다음 주 스크래핑 필요: {len(results['summary']['next_needed'])}개 마트")
    if results['summary']['next_needed']:
        print(f"  - {', '.join(results['summary']['next_needed'])}")
    print("-" * 70)
    
    return results


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🚀 스마트 스크래핑 실행
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def should_run_scraping(check_update: bool = True) -> Tuple[bool, str, List[str]]:
    """
    현재 시점에 스크래핑을 실행해야 하는지 판단
    
    Args:
        check_update: 세일 정보 업데이트 확인 여부
    
    Returns:
        (should_run, reason, stores_to_scrape)
    """
    analysis = analyze_scraping_needs()
    
    current_needed = analysis['summary']['current_needed']
    next_needed = analysis['summary']['next_needed']
    
    all_needed = list(set(current_needed + next_needed))
    
    if not all_needed:
        return False, "모든 마트 데이터가 최신 상태", []
    
    # 세일 정보 업데이트 확인
    if check_update:
        print("\n" + "=" * 70)
        print("🔍 세일 정보 업데이트 확인")
        print("=" * 70)
        
        updated_stores = []
        not_updated_stores = []
        
        for store in all_needed:
            # 이번 주 또는 다음 주 확인
            week_type = 'current' if store in current_needed else 'next'
            is_updated, message = check_sale_info_updated(store, week_type, max_retries=2)
            
            if is_updated:
                updated_stores.append(store)
                print(f"✅ [{store}] {message}")
            else:
                not_updated_stores.append(store)
                print(f"⏳ [{store}] {message}")
        
        if updated_stores:
            return True, f"{len(updated_stores)}개 마트 세일 정보 업데이트 확인됨", updated_stores
        elif not_updated_stores:
            return False, f"{len(not_updated_stores)}개 마트 세일 정보 아직 미업데이트", not_updated_stores
        else:
            return False, "세일 정보 확인 실패", []
    
    return True, f"{len(all_needed)}개 마트 스크래핑 필요", all_needed


def main():
    """메인 실행 함수"""
    import argparse
    import subprocess
    
    parser = argparse.ArgumentParser(description='스마트 스크래핑 스케줄러')
    parser.add_argument('--analyze', action='store_true', help='스크래핑 필요성만 분석 (실행 안 함)')
    parser.add_argument('--force', action='store_true', help='강제 실행 (분석 및 업데이트 확인 무시)')
    parser.add_argument('--wait-for-update', action='store_true', help='세일 정보 업데이트까지 대기')
    parser.add_argument('--no-check-update', action='store_true', help='세일 정보 업데이트 확인 건너뛰기')
    args = parser.parse_args()
    
    if args.analyze:
        # 분석만 수행
        analyze_scraping_needs()
        return
    
    # 스크래핑 필요성 확인
    if not args.force:
        check_update = not args.no_check_update
        should_run, reason, stores = should_run_scraping(check_update=check_update)
        
        if not should_run:
            # 업데이트 대기 옵션이 있으면 대기
            if args.wait_for_update and stores:
                print(f"\n⏳ 세일 정보 업데이트 대기 중...")
                for store in stores:
                    week_type = 'current'  # 기본값
                    is_updated, message = wait_for_sale_update(store, week_type, max_wait_minutes=60, check_interval_minutes=5)
                    if is_updated:
                        print(f"✅ [{store}] {message}")
                    else:
                        print(f"⚠️ [{store}] {message}")
                
                # 다시 확인
                should_run, reason, stores = should_run_scraping(check_update=True)
                if not should_run:
                    print(f"\n⏸️ 스크래핑 불필요: {reason}")
                    print("   --force 옵션으로 강제 실행 가능")
                    return
            else:
                print(f"\n⏸️ 스크래핑 불필요: {reason}")
                print("   --force 옵션으로 강제 실행 가능")
                print("   --wait-for-update 옵션으로 업데이트 대기 가능")
                return
    
    # 스크래핑 실행
    print("\n🚀 스크래핑 실행...")
    
    try:
        # scrape_all_stores.py를 직접 import하여 실행
        sys.path.insert(0, str(PROJECT_ROOT))
        import asyncio
        
        # scrape_all_stores.py의 run 함수 실행 (동기 래퍼)
        from scraper.scrape_all_stores import run as scrape_run
        print("📡 scrape_all_stores.py 모듈 로드 완료")
        
        # 동기 함수 실행
        result = scrape_run()
        print("\n✅ 스크래핑 완료")
        
        # 레시피 생성
        print("\n🍳 레시피 생성...")
        from recipe_matcher import main as recipe_main
        recipes = recipe_main('both')
        
        if recipes:
            print("\n✅ 레시피 생성 완료")
        else:
            print("\n⚠️ 레시피 생성 실패 또는 레시피 없음")
            
    except ImportError as e:
        print(f"\n❌ 모듈 import 실패: {e}")
        print("📋 subprocess로 대체 실행 시도...")
        # Fallback: subprocess 사용
        result = subprocess.run(
            ["python3", "scraper/scrape_all_stores.py"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print("에러:", result.stderr)
        
        if result.returncode == 0:
            print("\n✅ 스크래핑 완료 (subprocess)")
            result2 = subprocess.run(
                ["python3", "recipe_matcher.py"],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True
            )
            print(result2.stdout)
            if result2.stderr:
                print("에러:", result2.stderr)
        else:
            print("\n❌ 스크래핑 실패")
            raise
    except Exception as e:
        print(f"\n❌ 스크래핑 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
