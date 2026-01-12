"""
네덜란드 슈퍼마켓 세일 시작일 분석
실제 각 마트의 세일 시작 요일 확인
"""
from datetime import datetime, timedelta

# 현재 알려진 세일 시작일
KNOWN_SCHEDULES = {
    'Albert Heijn': {
        'start_day': 0,  # 월요일
        'note': 'AH는 월요일부터 일요일까지 주간 세일',
        'source': '공식 사이트 확인'
    },
    'Jumbo': {
        'start_day': 2,  # 수요일
        'note': 'Jumbo는 수요일부터 화요일까지 주간 세일',
        'source': '공식 사이트 확인'
    },
    'Dirk': {
        'start_day': 2,  # 수요일
        'note': 'Dirk는 수요일부터 화요일까지 주간 세일',
        'source': '공식 사이트 확인'
    },
    'Aldi': {
        'start_day': 0,  # 월요일
        'note': 'Aldi는 월요일부터 일요일까지 주간 세일',
        'source': '공식 사이트 확인'
    },
    'Plus': {
        'start_day': 0,  # 월요일
        'note': 'Plus는 월요일부터 일요일까지 주간 세일',
        'source': '공식 사이트 확인'
    },
    'Hoogvliet': {
        'start_day': 0,  # 월요일
        'note': 'Hoogvliet는 월요일부터 일요일까지 주간 세일',
        'source': '공식 사이트 확인'
    },
    'Coop': {
        'start_day': 0,  # 월요일
        'note': 'Coop는 월요일부터 일요일까지 주간 세일',
        'source': '공식 사이트 확인'
    }
}

def analyze_current_week():
    """현재 주 기준 각 마트 세일 상태 분석"""
    today = datetime.now()
    today_name = ['월', '화', '수', '목', '금', '토', '일'][today.weekday()]
    
    print(f"\n{'='*70}")
    print(f"📅 오늘: {today.strftime('%Y-%m-%d')} ({today_name}요일)")
    print(f"{'='*70}\n")
    
    days_since_monday = today.weekday()
    current_monday = today - timedelta(days=days_since_monday)
    
    print("각 마트의 세일 상태:\n")
    
    for store, info in KNOWN_SCHEDULES.items():
        start_day = info['start_day']
        start_day_name = ['월', '화', '수', '목', '금', '토', '일'][start_day]
        
        # 이번 주 세일 시작일
        this_week_start = current_monday + timedelta(days=start_day)
        this_week_end = this_week_start + timedelta(days=6)
        
        # 상태 확인
        if this_week_start <= today <= this_week_end:
            status = "🟢 활성화됨 (지금 할인)"
            days_left = (this_week_end - today).days
            detail = f"D-{days_left} ({this_week_end.strftime('%m/%d')}까지)"
        elif this_week_start > today:
            status = "🔵 곧 시작 (다음 주 미리보기)"
            days_until = (this_week_start - today).days
            detail = f"{days_until}일 후 시작 ({this_week_start.strftime('%m/%d')} {start_day_name}요일)"
        else:
            status = "⚪ 종료됨"
            detail = f"종료: {this_week_end.strftime('%m/%d')}"
        
        print(f"{store:15} | 시작: {start_day_name}요일 | {status}")
        print(f"{'':17} | {detail}")
        print(f"{'':17} | 기간: {this_week_start.strftime('%m/%d')} ~ {this_week_end.strftime('%m/%d')}")
        print()

def recommendation():
    """크롤링 전략 권장사항"""
    print(f"\n{'='*70}")
    print("💡 크롤링 전략 권장사항")
    print(f"{'='*70}\n")
    
    today = datetime.now()
    today_weekday = today.weekday()
    
    if today_weekday == 0:  # 월요일
        print("오늘은 월요일입니다:")
        print("  - 월요일 시작 마트 (AH, Aldi, Plus, Hoogvliet, Coop): '이번 주' 세일 크롤링")
        print("  - 수요일 시작 마트 (Jumbo, Dirk): '다음 주' 세일 크롤링")
        print()
        print("권장 로직:")
        print("  1. current_sales.json: 월요일 시작 마트만 포함")
        print("  2. next_sales.json: 수요일 시작 마트 포함")
        print("  3. 또는 모든 마트를 current_sales.json에 포함하되, 날짜를 정확히 설정")
    elif today_weekday == 2:  # 수요일
        print("오늘은 수요일입니다:")
        print("  - 모든 마트의 세일이 활성화됨")
        print("  - current_sales.json: 모든 마트 포함 가능")
    else:
        print(f"오늘은 {['월', '화', '수', '목', '금', '토', '일'][today_weekday]}요일입니다:")
        print("  - 현재 활성화된 세일을 크롤링하여 current_sales.json에 저장")
        print("  - 다음 주 세일을 크롤링하여 next_sales.json에 저장")

if __name__ == "__main__":
    analyze_current_week()
    recommendation()
