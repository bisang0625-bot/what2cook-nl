"""
메인 크롤러
모든 슈퍼마켓을 크롤링하고 weekly_sales.json에 저장
"""
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

# 프로젝트 루트 경로 추가
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scrapers.store_config import STORES, PRIORITY_STORES, VALIDATION_CONFIG
from scrapers.base_scraper import BaseScraper


def get_next_monday():
    """다음 월요일 날짜 계산 (월요일이면 당일)"""
    today = datetime.now()
    if today.weekday() == 0:  # Monday
        return today
    return today + timedelta(days=(7 - today.weekday()))


def validate_products(products: list, store_name: str) -> list:
    """상품 데이터 검증 및 필터링"""
    validated = []
    
    for product in products:
        # 필수 필드 확인
        if not product.get('name'):
            continue
        
        # 이름 길이 체크 (너무 짧거나 긴 것 제외)
        name = product['name']
        if len(name) < 3 or len(name) > 200:
            continue
        
        # 비식품 키워드 제외 (옵션)
        name_lower = name.lower()
        non_food = ['gordijn', 'dekbed', 'ticket', 'trein', 'toiletblok', 
                   'speelgoed', 'kleding', 'vtwonen', 'home creation']
        if any(keyword in name_lower for keyword in non_food):
            print(f"  ⚠️ 비식품 제외: {name[:40]}")
            continue
        
        validated.append(product)
    
    print(f"  ✅ 검증 완료: {len(validated)}/{len(products)}개 상품")
    return validated


def save_results(all_products: list, successful_stores: list, failed_stores: list):
    """결과를 weekly_sales.json에 저장"""
    next_monday = get_next_monday()
    next_sunday = next_monday + timedelta(days=6)
    
    weekly_data = {
        'week_number': f"{next_monday.year}-{next_monday.isocalendar()[1]:02d}",
        'sale_period': f"{next_monday.strftime('%Y-%m-%d')} ~ {next_sunday.strftime('%Y-%m-%d')}",
        'scraped_at': datetime.now().isoformat(),
        'total_products': len(all_products),
        'supermarkets': {
            'successful': successful_stores,
            'failed': failed_stores
        },
        'products': [
            {
                'supermarket': p['supermarket'],
                'product_name': p['name'],
                'price_info': p.get('price'),
                'discount_info': p.get('discount'),
                'start_date': next_monday.isoformat(),
                'end_date': next_sunday.isoformat(),
                'source': 'official_website',
                'scraped_at': datetime.now().isoformat()
            }
            for p in all_products
        ]
    }
    
    output_path = PROJECT_ROOT / "data" / "weekly_sales.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(weekly_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 {output_path.name} 저장 완료")


def main(priority_only=False):
    """메인 실행 함수"""
    print("\n" + "="*70)
    print("🍳 What2Cook NL 시스템 가동")
    print("🤖 슈퍼마켓 크롤러 시작 (공식 사이트)")
    print("="*70)
    
    next_monday = get_next_monday()
    print(f"📅 대상 주차: {next_monday.year}-{next_monday.isocalendar()[1]:02d}주")
    print(f"📆 세일 기간: {next_monday.strftime('%Y-%m-%d')} (월) 시작\n")
    
    # 크롤링할 마트 선택
    if priority_only:
        stores_to_scrape = {k: v for k, v in STORES.items() if k in PRIORITY_STORES}
        print(f"🎯 우선순위 마트만 크롤링: {', '.join([v['name'] for v in stores_to_scrape.values()])}\n")
    else:
        stores_to_scrape = STORES
        print(f"🎯 전체 {len(STORES)}개 마트 크롤링\n")
    
    all_products = []
    successful_stores = []
    failed_stores = []
    
    for store_id, store_config in stores_to_scrape.items():
        try:
            # 크롤러 생성 및 실행
            scraper = BaseScraper(store_config, PROJECT_ROOT)
            products = scraper.scrape()
            
            if products:
                # 데이터 검증
                validated = validate_products(products, store_config['name'])
                
                if validated and len(validated) >= VALIDATION_CONFIG['min_products']:
                    all_products.extend(validated)
                    successful_stores.append(store_config['name'])
                else:
                    print(f"  ⚠️ 최소 상품 수({VALIDATION_CONFIG['min_products']})를 만족하지 못했습니다.")
                    failed_stores.append(store_config['name'])
            else:
                failed_stores.append(store_config['name'])
            
        except Exception as e:
            print(f"❌ {store_config['name']} 오류: {str(e)}")
            failed_stores.append(store_config['name'])
        
        # 다음 마트 대기
        import time
        print("\n⏳ 다음 마트 대기 중...\n")
        time.sleep(3)
    
    # 결과 저장
    if all_products:
        save_results(all_products, successful_stores, failed_stores)
        
        print("\n" + "="*70)
        print("📊 크롤링 완료 요약")
        print("="*70)
        print(f"✅ 성공: {len(successful_stores)}개 마트")
        
        # 마트별 상품 수
        store_counts = {}
        for p in all_products:
            store = p['supermarket']
            store_counts[store] = store_counts.get(store, 0) + 1
        
        for store in successful_stores:
            count = store_counts.get(store, 0)
            print(f"   - {store}: {count}개 상품")
        
        if failed_stores:
            print(f"\n⚠️ 실패: {len(failed_stores)}개 마트")
            for store in failed_stores:
                print(f"   - {store}")
        
        print(f"\n📦 총 {len(all_products)}개 상품 수집 완료")
        
        return True
    else:
        print("\n❌ 모든 마트에서 데이터 수집 실패")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='슈퍼마켓 세일 정보 크롤러')
    parser.add_argument(
        '--priority',
        action='store_true',
        help='우선순위 마트만 크롤링 (AH, Dirk, Aldi)'
    )
    
    args = parser.parse_args()
    
    success = main(priority_only=args.priority)
    sys.exit(0 if success else 1)
