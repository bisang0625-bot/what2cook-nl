"""
기존 레시피에 마트별 세일 시작일 정보 추가
"""
import json
from pathlib import Path
from datetime import datetime, timedelta

PROJECT_ROOT = Path(__file__).parent.parent

# 마트별 세일 시작일 매핑
STORE_SALE_START_DAY = {
    'Albert Heijn': 0,  # 월요일
    'Jumbo': 2,         # 수요일
    'Dirk': 2,          # 수요일
    'Aldi': 0,          # 월요일
    'Plus': 0,          # 월요일
    'Hoogvliet': 0,     # 월요일
    'Coop': 0,          # 월요일
}

def get_store_sale_dates(store_name: str, week_type: str = 'current') -> tuple:
    """마트별 세일 시작일과 종료일 계산"""
    today = datetime.now()
    days_since_monday = today.weekday()
    current_monday = today - timedelta(days=days_since_monday)
    
    start_day_of_week = STORE_SALE_START_DAY.get(store_name, 0)
    
    if week_type == 'current':
        # 현재 주의 세일 시작일
        days_to_start = (start_day_of_week - current_monday.weekday() + 7) % 7
        sale_start = current_monday + timedelta(days=days_to_start)
        
        # 시작일이 지났으면 다음 주
        if sale_start < today:
            sale_start = current_monday + timedelta(days=7 + start_day_of_week)
    else:  # next
        next_monday = current_monday + timedelta(days=7)
        sale_start = next_monday + timedelta(days=start_day_of_week)
    
    sale_end = sale_start + timedelta(days=6)
    return sale_start, sale_end

def main():
    """기존 레시피에 날짜 정보 추가"""
    recipes_file = PROJECT_ROOT / "data" / "weekly_recipes.json"
    
    if not recipes_file.exists():
        print(f"❌ {recipes_file} 파일이 없습니다.")
        return
    
    with open(recipes_file, 'r', encoding='utf-8') as f:
        recipes = json.load(f)
    
    print(f"📝 {len(recipes)}개 레시피에 날짜 정보 추가 중...")
    
    updated_count = 0
    for recipe in recipes:
        store_name = recipe.get('store', 'Unknown')
        
        # 이미 날짜 정보가 있으면 스킵
        if recipe.get('valid_from') and recipe.get('valid_until'):
            continue
        
        # 마트별 세일 시작일 계산
        sale_start, sale_end = get_store_sale_dates(store_name, 'current')
        
        recipe['valid_from'] = sale_start.isoformat()
        recipe['valid_until'] = sale_end.isoformat()
        updated_count += 1
        
        print(f"  ✅ {store_name}: {sale_start.strftime('%Y-%m-%d')} ~ {sale_end.strftime('%Y-%m-%d')}")
    
    # 저장
    with open(recipes_file, 'w', encoding='utf-8') as f:
        json.dump(recipes, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 {updated_count}개 레시피 업데이트 완료!")
    print(f"📁 파일: {recipes_file}")

if __name__ == "__main__":
    main()
