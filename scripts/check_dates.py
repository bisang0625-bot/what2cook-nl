"""레시피 날짜 정보 확인"""
import json
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
recipes_file = PROJECT_ROOT / "data" / "weekly_recipes.json"

with open(recipes_file, 'r', encoding='utf-8') as f:
    recipes = json.load(f)

today = datetime.now()
today = today.replace(hour=0, minute=0, second=0, microsecond=0)

print(f"📅 오늘: {today.strftime('%Y-%m-%d (%A)')}\n")

jumbo = [r for r in recipes if r.get('store') == 'Jumbo']
ah = [r for r in recipes if r.get('store') == 'Albert Heijn']

print(f"🛒 Jumbo 레시피: {len(jumbo)}개")
if jumbo:
    r = jumbo[0]
    vf = datetime.fromisoformat(r['valid_from'])
    vu = datetime.fromisoformat(r['valid_until'])
    vf = vf.replace(hour=0, minute=0, second=0, microsecond=0)
    vu = vu.replace(hour=23, minute=59, second=59)
    
    print(f"  레시피: {r['menu_name']}")
    print(f"  세일 기간: {vf.strftime('%Y-%m-%d (%A)')} ~ {vu.strftime('%Y-%m-%d (%A)')}")
    print(f"  오늘: {today.strftime('%Y-%m-%d (%A)')}")
    
    if vf <= today <= vu:
        print(f"  ✅ 분류: 지금 할인 (활성화됨)")
    elif vf > today:
        print(f"  📅 분류: 곧 시작 ({(vf - today).days}일 후)")
    else:
        print(f"  ❌ 분류: 종료됨")

print(f"\n🛒 Albert Heijn 레시피: {len(ah)}개")
if ah:
    r = ah[0]
    vf = datetime.fromisoformat(r['valid_from'])
    vu = datetime.fromisoformat(r['valid_until'])
    vf = vf.replace(hour=0, minute=0, second=0, microsecond=0)
    vu = vu.replace(hour=23, minute=59, second=59)
    
    print(f"  레시피: {r['menu_name']}")
    print(f"  세일 기간: {vf.strftime('%Y-%m-%d (%A)')} ~ {vu.strftime('%Y-%m-%d (%A)')}")
    print(f"  오늘: {today.strftime('%Y-%m-%d (%A)')}")
    
    if vf <= today <= vu:
        print(f"  ✅ 분류: 지금 할인 (활성화됨)")
    elif vf > today:
        print(f"  📅 분류: 곧 시작 ({(vf - today).days}일 후)")
    else:
        print(f"  ❌ 분류: 종료됨")
