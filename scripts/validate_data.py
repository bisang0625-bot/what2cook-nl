"""
데이터 검증 스크립트
배포 전 데이터 품질 확인
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

PROJECT_ROOT = Path(__file__).parent.parent

def validate_sales_data(file_path: Path, week_type: str) -> Dict[str, Any]:
    """세일 데이터 검증"""
    print(f"\n{'='*70}")
    print(f"📊 {week_type.upper()} WEEK 세일 데이터 검증")
    print(f"{'='*70}")
    
    if not file_path.exists():
        return {
            'valid': False,
            'error': f'파일이 없습니다: {file_path}',
            'stores': {},
            'total_products': 0
        }
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 필수 필드 확인
    required_fields = ['week_type', 'scraped_at', 'products', 'supermarkets']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return {
            'valid': False,
            'error': f'필수 필드 누락: {missing_fields}',
            'stores': {},
            'total_products': 0
        }
    
    # 마트별 상품 수 집계
    stores = {}
    for product in data.get('products', []):
        store = product.get('store', 'Unknown')
        if store not in stores:
            stores[store] = 0
        stores[store] += 1
        
        # 필수 필드 확인
        if not product.get('product_name'):
            print(f"⚠️ 상품명 없음: {product}")
        if not product.get('valid_from') or not product.get('valid_until'):
            print(f"⚠️ 날짜 정보 없음: {product.get('product_name', 'Unknown')}")
    
    total_products = len(data.get('products', []))
    successful_stores = data.get('supermarkets', {}).get('successful', [])
    failed_stores = data.get('supermarkets', {}).get('failed', [])
    
    print(f"✅ 총 상품 수: {total_products}개")
    print(f"✅ 성공한 마트: {len(successful_stores)}개 - {successful_stores}")
    if failed_stores:
        print(f"⚠️ 실패한 마트: {len(failed_stores)}개 - {failed_stores}")
    print(f"\n마트별 상품 수:")
    for store, count in sorted(stores.items()):
        print(f"  - {store}: {count}개")
    
    return {
        'valid': True,
        'total_products': total_products,
        'stores': stores,
        'successful_stores': successful_stores,
        'failed_stores': failed_stores,
        'scraped_at': data.get('scraped_at'),
        'week_type': data.get('week_type')
    }

def validate_recipes(file_path: Path, week_type: str) -> Dict[str, Any]:
    """레시피 데이터 검증"""
    print(f"\n{'='*70}")
    print(f"🍳 {week_type.upper()} WEEK 레시피 데이터 검증")
    print(f"{'='*70}")
    
    if not file_path.exists():
        return {
            'valid': False,
            'error': f'파일이 없습니다: {file_path}',
            'recipes': [],
            'stores': {}
        }
    
    with open(file_path, 'r', encoding='utf-8') as f:
        recipes = json.load(f)
    
    if not isinstance(recipes, list):
        return {
            'valid': False,
            'error': '레시피 데이터가 리스트 형식이 아닙니다',
            'recipes': [],
            'stores': {}
        }
    
    # 필수 필드 확인
    required_fields = ['id', 'store', 'menu_name', 'main_ingredients', 'description', 'tags', 'shopping_list']
    valid_recipes = []
    invalid_recipes = []
    
    for recipe in recipes:
        missing_fields = [field for field in required_fields if field not in recipe]
        if missing_fields:
            invalid_recipes.append({
                'recipe': recipe.get('menu_name', 'Unknown'),
                'missing': missing_fields
            })
        else:
            valid_recipes.append(recipe)
    
    # 마트별 레시피 수 집계
    stores = {}
    for recipe in valid_recipes:
        store = recipe.get('store', 'Unknown')
        if store not in stores:
            stores[store] = 0
        stores[store] += 1
        
        # 날짜 정보 확인
        if not recipe.get('valid_from') or not recipe.get('valid_until'):
            print(f"⚠️ 날짜 정보 없음: {recipe.get('menu_name', 'Unknown')} ({store})")
    
    print(f"✅ 총 레시피 수: {len(valid_recipes)}개")
    if invalid_recipes:
        print(f"⚠️ 유효하지 않은 레시피: {len(invalid_recipes)}개")
        for invalid in invalid_recipes:
            print(f"  - {invalid['recipe']}: 누락 필드 {invalid['missing']}")
    
    print(f"\n마트별 레시피 수:")
    for store, count in sorted(stores.items()):
        print(f"  - {store}: {count}개")
    
    return {
        'valid': len(invalid_recipes) == 0,
        'total_recipes': len(valid_recipes),
        'invalid_recipes': len(invalid_recipes),
        'recipes': valid_recipes,
        'stores': stores
    }

def main():
    """메인 검증 함수"""
    print("\n" + "="*70)
    print("🔍 데이터 검증 시작")
    print("="*70)
    
    results = {
        'current_sales': None,
        'next_sales': None,
        'current_recipes': None,
        'next_recipes': None
    }
    
    # 세일 데이터 검증
    results['current_sales'] = validate_sales_data(
        PROJECT_ROOT / "data" / "current_sales.json",
        "current"
    )
    
    results['next_sales'] = validate_sales_data(
        PROJECT_ROOT / "data" / "next_sales.json",
        "next"
    )
    
    # 레시피 데이터 검증
    results['current_recipes'] = validate_recipes(
        PROJECT_ROOT / "data" / "current_recipes.json",
        "current"
    )
    
    results['next_recipes'] = validate_recipes(
        PROJECT_ROOT / "data" / "next_recipes.json",
        "next"
    )
    
    # 최종 요약
    print("\n" + "="*70)
    print("📋 최종 검증 결과")
    print("="*70)
    
    all_valid = True
    
    # 세일 데이터
    print("\n📦 세일 데이터:")
    for week_type in ['current', 'next']:
        key = f'{week_type}_sales'
        result = results[key]
        if result and result.get('valid'):
            print(f"  ✅ {week_type.upper()}: {result['total_products']}개 상품, {len(result['successful_stores'])}개 마트 성공")
            if result.get('failed_stores'):
                print(f"     ⚠️ 실패: {result['failed_stores']}")
        else:
            print(f"  ❌ {week_type.upper()}: {result.get('error', '검증 실패')}")
            all_valid = False
    
    # 레시피 데이터
    print("\n🍳 레시피 데이터:")
    for week_type in ['current', 'next']:
        key = f'{week_type}_recipes'
        result = results[key]
        if result and result.get('valid'):
            print(f"  ✅ {week_type.upper()}: {result['total_recipes']}개 레시피")
        else:
            print(f"  ❌ {week_type.upper()}: {result.get('error', '검증 실패')}")
            all_valid = False
    
    # 배포 가능 여부
    print("\n" + "="*70)
    if all_valid:
        print("✅ 배포 가능: 모든 데이터가 유효합니다!")
        
        # 최소 요구사항 확인
        current_products = results['current_sales'].get('total_products', 0) if results['current_sales'] else 0
        next_products = results['next_sales'].get('total_products', 0) if results['next_sales'] else 0
        current_recipes_count = results['current_recipes'].get('total_recipes', 0) if results['current_recipes'] else 0
        next_recipes_count = results['next_recipes'].get('total_recipes', 0) if results['next_recipes'] else 0
        
        if current_products >= 50 and next_products >= 50:
            print(f"✅ 상품 수 충분: 현재 주 {current_products}개, 다음 주 {next_products}개")
        else:
            print(f"⚠️ 상품 수 부족: 현재 주 {current_products}개, 다음 주 {next_products}개 (권장: 각 50개 이상)")
        
        if current_recipes_count >= 15 and next_recipes_count >= 15:
            print(f"✅ 레시피 수 충분: 현재 주 {current_recipes_count}개, 다음 주 {next_recipes_count}개")
        else:
            print(f"⚠️ 레시피 수 부족: 현재 주 {current_recipes_count}개, 다음 주 {next_recipes_count}개 (권장: 각 15개 이상)")
    else:
        print("❌ 배포 불가: 일부 데이터가 유효하지 않습니다.")
        print("   위의 오류를 수정한 후 다시 검증해주세요.")
    print("="*70)

if __name__ == "__main__":
    main()
