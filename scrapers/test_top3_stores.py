"""
Albert Heijn, Jumbo, Dirk 세 마트만 테스트
현재 주와 다음 주 모두 크롤링
"""
import sys
from pathlib import Path

# 상위 디렉토리를 경로에 추가
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scrapers.hybrid_scraper import (
    STORES, capture_screenshot, analyze_with_ai,
    get_store_sale_dates, save_results,
    get_current_week, get_next_monday
)
from datetime import datetime, timedelta
import json
import time

# 세 마트만 선택
TOP3_STORES = {
    'Albert Heijn': STORES['Albert Heijn'],
    'Jumbo': STORES['Jumbo'],
    'Dirk': STORES['Dirk']
}

def test_store(store_name: str, config: dict, week_type: str = 'current'):
    """단일 마트 테스트"""
    print(f"\n{'='*70}")
    print(f"🧪 테스트: {store_name} ({week_type} week)")
    print(f"{'='*70}")
    
    # 스크린샷 캡처
    screenshot = capture_screenshot(store_name, config)
    
    if not screenshot:
        print(f"❌ {store_name}: 스크린샷 실패")
        return None
    
    # AI 분석
    products = analyze_with_ai(screenshot, store_name)
    
    # Albert Heijn은 최소 4개, 나머지는 5개
    min_products = 4 if store_name == 'Albert Heijn' else 5
    
    # Albert Heijn이 Reclamefolder에서 4개 이상 추출되면 바로 사용
    if store_name == 'Albert Heijn' and products and len(products) >= 4:
        print(f"✅ {store_name}: Reclamefolder 성공! ({len(products)}개)")
    elif not products or len(products) < min_products:
        print(f"⚠️ {store_name}: 상품 부족 ({len(products) if products else 0}개)")
        
        # Albert Heijn은 공식 사이트도 시도
        if store_name == 'Albert Heijn':
            print(f"\n🔄 {store_name} 공식 사이트 시도...")
            official_config = {
                'url': 'https://www.ah.nl/bonus',
                'source': 'official',
                'timeout': 120000,
                'wait_time': 15,
                'scroll': True
            }
            screenshot2 = capture_screenshot(store_name, official_config)
            if screenshot2:
                products2 = analyze_with_ai(screenshot2, store_name)
                if products2 and len(products2) >= 4:
                    products = products2
                    print(f"✅ {store_name}: 공식 사이트 성공! ({len(products)}개)")
                elif products and len(products) >= 4:
                    # Reclamefolder 결과 사용
                    print(f"✅ {store_name}: Reclamefolder 결과 사용 ({len(products)}개)")
                else:
                    print(f"❌ {store_name}: 모든 소스 실패")
                    return None
            elif products and len(products) >= 4:
                # Reclamefolder 결과 사용
                print(f"✅ {store_name}: Reclamefolder 결과 사용 ({len(products)}개)")
            else:
                print(f"❌ {store_name}: 모든 소스 실패")
                return None
        else:
            return None
    else:
        print(f"✅ {store_name}: 성공! ({len(products)}개)")
    
    # 날짜 정보 추가
    sale_start, sale_end = get_store_sale_dates(store_name, week_type)
    
    products_with_dates = []
    for p in products:
        products_with_dates.append({
            'store': store_name,
            'product_name': p['name'],
            'price': p.get('price'),
            'discount': p.get('discount'),
            'valid_from': sale_start.isoformat(),
            'valid_until': sale_end.isoformat(),
            'scraped_at': datetime.now().isoformat()
        })
    
    return products_with_dates

def main():
    """세 마트 테스트 실행"""
    print("\n" + "="*70)
    print("🧪 TOP 3 마트 크롤링 테스트")
    print("   - Albert Heijn")
    print("   - Jumbo")
    print("   - Dirk")
    print("="*70)
    
    # 현재 주와 다음 주 모두 테스트
    results = {
        'current': {'products': [], 'successful': [], 'failed': []},
        'next': {'products': [], 'successful': [], 'failed': []}
    }
    
    for week_type in ['current', 'next']:
        print(f"\n{'='*70}")
        print(f"📦 {week_type.upper()} WEEK 크롤링")
        print(f"{'='*70}")
        
        for store_name, config in TOP3_STORES.items():
            products = test_store(store_name, config, week_type)
            
            # Albert Heijn은 최소 4개, 나머지는 5개
            min_products = 4 if store_name == 'Albert Heijn' else 5
            
            if products and len(products) >= min_products:
                results[week_type]['products'].extend(products)
                results[week_type]['successful'].append(store_name)
            else:
                results[week_type]['failed'].append(store_name)
            
            print("\n⏳ 다음 마트 대기...\n")
            time.sleep(5)
    
    # 결과 저장
    for week_type in ['current', 'next']:
        if results[week_type]['products']:
            if week_type == 'current':
                week_monday = get_current_week()
                output_file = PROJECT_ROOT / "data" / "current_sales.json"
            else:
                week_monday = get_next_monday()
                output_file = PROJECT_ROOT / "data" / "next_sales.json"
            
            week_sunday = week_monday + timedelta(days=6)
            
            data = {
                'week_number': f"{week_monday.year}-{week_monday.isocalendar()[1]:02d}",
                'sale_period': f"{week_monday.strftime('%Y-%m-%d')} ~ {week_sunday.strftime('%Y-%m-%d')}",
                'week_type': week_type,
                'scraped_at': datetime.now().isoformat(),
                'total_products': len(results[week_type]['products']),
                'supermarkets': {
                    'successful': results[week_type]['successful'],
                    'failed': results[week_type]['failed']
                },
                'products': results[week_type]['products']
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"\n💾 {output_file.name} 저장 완료")
            print(f"   - 성공: {len(results[week_type]['successful'])}개 마트")
            print(f"   - 실패: {len(results[week_type]['failed'])}개 마트")
            print(f"   - 상품: {len(results[week_type]['products'])}개")
    
    # 최종 요약
    print("\n" + "="*70)
    print("📊 최종 결과")
    print("="*70)
    
    for week_type in ['current', 'next']:
        print(f"\n{week_type.upper()} WEEK:")
        print(f"  ✅ 성공: {results[week_type]['successful']}")
        if results[week_type]['failed']:
            print(f"  ❌ 실패: {results[week_type]['failed']}")
        print(f"  📦 상품: {len(results[week_type]['products'])}개")
    
    # 모든 마트 성공 여부 확인
    all_success = all(
        store in results['current']['successful'] and 
        store in results['next']['successful']
        for store in TOP3_STORES.keys()
    )
    
    if all_success:
        print("\n✅ 모든 마트 크롤링 성공!")
    else:
        print("\n⚠️ 일부 마트 크롤링 실패")

if __name__ == "__main__":
    main()
