"""
주차 기반 분류 로직 테스트
"""
import json
from pathlib import Path
from datetime import datetime, timedelta

PROJECT_ROOT = Path(__file__).parent.parent

def test_classification():
    """현재 주 vs 다음 주 분류 로직 테스트"""
    
    # 오늘 날짜
    today = datetime.now()
    today = today.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # 이번 주 월요일과 일요일 계산
    days_since_monday = 6 if today.weekday() == 6 else today.weekday()
    this_week_monday = today - timedelta(days=days_since_monday)
    this_week_sunday = this_week_monday + timedelta(days=6)
    this_week_sunday = this_week_sunday.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    print(f"\n{'='*70}")
    print(f"📅 오늘: {today.strftime('%Y-%m-%d (%A)')}")
    print(f"📅 이번 주: {this_week_monday.strftime('%Y-%m-%d')} ~ {this_week_sunday.strftime('%Y-%m-%d')}")
    print(f"{'='*70}\n")
    
    # 레시피 로드
    current_recipes_file = PROJECT_ROOT / "data" / "current_recipes.json"
    next_recipes_file = PROJECT_ROOT / "data" / "next_recipes.json"
    
    all_recipes = []
    
    if current_recipes_file.exists():
        with open(current_recipes_file, 'r', encoding='utf-8') as f:
            current_data = json.load(f)
            all_recipes.extend(current_data)
            print(f"✅ current_recipes.json: {len(current_data)}개 레시피 로드")
    
    if next_recipes_file.exists():
        with open(next_recipes_file, 'r', encoding='utf-8') as f:
            next_data = json.load(f)
            all_recipes.extend(next_data)
            print(f"✅ next_recipes.json: {len(next_data)}개 레시피 로드")
    
    print(f"✅ 총 {len(all_recipes)}개 레시피\n")
    
    # 분류
    current_week_recipes = []
    next_week_recipes = []
    expired_recipes = []
    
    for recipe in all_recipes:
        valid_from_str = recipe.get('valid_from')
        valid_until_str = recipe.get('valid_until')
        
        if not valid_from_str or not valid_until_str:
            print(f"⚠️ 날짜 정보 없음: {recipe.get('store')} - {recipe.get('menu_name')}")
            current_week_recipes.append(recipe)  # 기본적으로 이번 주에 포함
            continue
        
        valid_from = datetime.fromisoformat(valid_from_str.replace('Z', '+00:00'))
        valid_until = datetime.fromisoformat(valid_until_str.replace('Z', '+00:00'))
        
        # 이번 주 세일: 시작일이 이번 주 내에 있거나 이미 시작했고 아직 종료하지 않음
        if valid_from <= this_week_sunday and valid_until >= this_week_monday:
            current_week_recipes.append(recipe)
        # 다음 주 세일: 시작일이 이번 주 이후
        elif valid_from > this_week_sunday:
            next_week_recipes.append(recipe)
        # 종료된 세일
        else:
            expired_recipes.append(recipe)
    
    # 결과 출력
    print(f"{'='*70}")
    print(f"📊 분류 결과")
    print(f"{'='*70}\n")
    
    print(f"✅ 이번 주: {len(current_week_recipes)}개")
    stores_current = {}
    for r in current_week_recipes:
        store = r['store']
        stores_current[store] = stores_current.get(store, 0) + 1
    for store, count in sorted(stores_current.items()):
        print(f"  - {store}: {count}개")
    
    print(f"\n✅ 다음 주: {len(next_week_recipes)}개")
    stores_next = {}
    for r in next_week_recipes:
        store = r['store']
        stores_next[store] = stores_next.get(store, 0) + 1
    for store, count in sorted(stores_next.items()):
        print(f"  - {store}: {count}개")
    
    if expired_recipes:
        print(f"\n⚠️ 종료: {len(expired_recipes)}개")
        for r in expired_recipes[:5]:
            print(f"  - {r['store']}: {r['menu_name']} ({r.get('valid_from', 'N/A')[:10]} ~ {r.get('valid_until', 'N/A')[:10]})")
    
    # Jumbo와 Dirk 상세 확인
    print(f"\n{'='*70}")
    print(f"🔍 Jumbo & Dirk 상세 확인")
    print(f"{'='*70}\n")
    
    for recipe in all_recipes:
        if recipe['store'] in ['Jumbo', 'Dirk']:
            valid_from_str = recipe.get('valid_from')
            valid_until_str = recipe.get('valid_until')
            
            if valid_from_str and valid_until_str:
                valid_from = datetime.fromisoformat(valid_from_str.replace('Z', '+00:00'))
                valid_until = datetime.fromisoformat(valid_until_str.replace('Z', '+00:00'))
                
                # 분류 결정
                if valid_from <= this_week_sunday and valid_until >= this_week_monday:
                    classification = "✅ 이번 주"
                elif valid_from > this_week_sunday:
                    classification = "📅 다음 주"
                else:
                    classification = "❌ 종료"
                
                print(f"{recipe['store']:15} | {recipe['menu_name'][:30]:30} | {classification}")
                print(f"{'':17} | 기간: {valid_from.strftime('%Y-%m-%d')} ~ {valid_until.strftime('%Y-%m-%d')}")
                print()

if __name__ == "__main__":
    test_classification()
