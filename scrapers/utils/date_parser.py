"""
네덜란드어 날짜 파싱 유틸리티
세일 기간 텍스트를 ISO 형식 날짜로 변환
"""
import re
from datetime import datetime, timedelta
from typing import Optional, Tuple

# 네덜란드어 월 이름 매핑
DUTCH_MONTHS = {
    'januari': 1, 'jan': 1,
    'februari': 2, 'feb': 2,
    'maart': 3, 'mrt': 3,
    'april': 4, 'apr': 4,
    'mei': 5,
    'juni': 6, 'jun': 6,
    'juli': 7, 'jul': 7,
    'augustus': 8, 'aug': 8,
    'september': 9, 'sep': 9,
    'oktober': 10, 'okt': 10,
    'november': 11, 'nov': 11,
    'december': 12, 'dec': 12
}

# 네덜란드어 요일 약어
DUTCH_DAYS = {
    'ma': 'monday', 'maandag': 'monday',
    'di': 'tuesday', 'dinsdag': 'tuesday',
    'wo': 'wednesday', 'woensdag': 'wednesday',
    'do': 'thursday', 'donderdag': 'thursday',
    'vr': 'friday', 'vrijdag': 'friday',
    'za': 'saturday', 'zaterdag': 'saturday',
    'zo': 'sunday', 'zondag': 'sunday'
}

def parse_dutch_date(date_text: str, reference_date: Optional[datetime] = None) -> Optional[datetime]:
    """
    네덜란드어 날짜 텍스트를 datetime으로 파싱
    
    예시:
    - "18 januari" -> 2026-01-18
    - "ma 13 t/m zo 19 jan" -> 시작일: 2026-01-13, 종료일: 2026-01-19
    - "t/m 18 januari" -> 종료일만 있음
    """
    if not date_text:
        return None
    
    if reference_date is None:
        reference_date = datetime.now()
    
    date_text = date_text.lower().strip()
    
    # 패턴 1: "18 januari" 또는 "18 jan"
    pattern1 = r'(\d{1,2})\s+(' + '|'.join(DUTCH_MONTHS.keys()) + r')'
    match = re.search(pattern1, date_text)
    if match:
        day = int(match.group(1))
        month_name = match.group(2)
        month = DUTCH_MONTHS[month_name]
        year = reference_date.year
        
        # 월이 지나갔으면 다음 해
        if month < reference_date.month or (month == reference_date.month and day < reference_date.day):
            year += 1
        
        try:
            return datetime(year, month, day)
        except ValueError:
            return None
    
    # 패턴 2: "ma 13" (요일 + 일)
    pattern2 = r'(' + '|'.join(DUTCH_DAYS.keys()) + r')\s+(\d{1,2})'
    match = re.search(pattern2, date_text)
    if match:
        day = int(match.group(2))
        # 요일로부터 날짜 계산 (복잡하므로 간단히 월만 추정)
        # 실제로는 더 정교한 로직 필요
        month = reference_date.month
        year = reference_date.year
        
        try:
            return datetime(year, month, day)
        except ValueError:
            return None
    
    return None

def parse_sale_period(text: str, reference_date: Optional[datetime] = None) -> Tuple[Optional[datetime], Optional[datetime]]:
    """
    세일 기간 텍스트를 파싱하여 시작일과 종료일 반환
    
    예시:
    - "ma 13 t/m zo 19 jan" -> (2026-01-13, 2026-01-19)
    - "t/m 18 januari" -> (None, 2026-01-18)
    - "van 12 tot 18 januari" -> (2026-01-12, 2026-01-18)
    """
    if not text:
        return None, None
    
    if reference_date is None:
        reference_date = datetime.now()
    
    text = text.lower().strip()
    
    # 패턴 1: "ma 13 t/m zo 19 jan" 또는 "13 t/m 19 januari"
    pattern1 = r'(\d{1,2})\s+t/m\s+(\d{1,2})\s+(' + '|'.join(DUTCH_MONTHS.keys()) + r')'
    match = re.search(pattern1, text)
    if match:
        start_day = int(match.group(1))
        end_day = int(match.group(2))
        month_name = match.group(3)
        month = DUTCH_MONTHS[month_name]
        year = reference_date.year
        
        # 월이 지나갔으면 다음 해
        if month < reference_date.month:
            year += 1
        
        try:
            start_date = datetime(year, month, start_day)
            end_date = datetime(year, month, end_day)
            return start_date, end_date
        except ValueError:
            pass
    
    # 패턴 2: "t/m 18 januari" (종료일만)
    pattern2 = r't/m\s+(\d{1,2})\s+(' + '|'.join(DUTCH_MONTHS.keys()) + r')'
    match = re.search(pattern2, text)
    if match:
        end_day = int(match.group(1))
        month_name = match.group(2)
        month = DUTCH_MONTHS[month_name]
        year = reference_date.year
        
        if month < reference_date.month:
            year += 1
        
        try:
            end_date = datetime(year, month, end_day)
            return None, end_date
        except ValueError:
            pass
    
    # 패턴 3: "van ... tot ..." 또는 "van ... t/m ..."
    pattern3 = r'van\s+(\d{1,2})\s+(?:tot|t/m)\s+(\d{1,2})\s+(' + '|'.join(DUTCH_MONTHS.keys()) + r')'
    match = re.search(pattern3, text)
    if match:
        start_day = int(match.group(1))
        end_day = int(match.group(2))
        month_name = match.group(3)
        month = DUTCH_MONTHS[month_name]
        year = reference_date.year
        
        if month < reference_date.month:
            year += 1
        
        try:
            start_date = datetime(year, month, start_day)
            end_date = datetime(year, month, end_day)
            return start_date, end_date
        except ValueError:
            pass
    
    return None, None

def get_current_week_range(reference_date: Optional[datetime] = None) -> Tuple[datetime, datetime]:
    """현재 주의 월요일과 일요일 반환"""
    if reference_date is None:
        reference_date = datetime.now()
    
    days_since_monday = reference_date.weekday()
    monday = reference_date - timedelta(days=days_since_monday)
    sunday = monday + timedelta(days=6)
    
    return monday, sunday

def get_next_week_range(reference_date: Optional[datetime] = None) -> Tuple[datetime, datetime]:
    """다음 주의 월요일과 일요일 반환"""
    if reference_date is None:
        reference_date = datetime.now()
    
    days_since_monday = reference_date.weekday()
    current_monday = reference_date - timedelta(days=days_since_monday)
    next_monday = current_monday + timedelta(days=7)
    next_sunday = next_monday + timedelta(days=6)
    
    return next_monday, next_sunday

def fallback_dates(week_type: str = 'current', reference_date: Optional[datetime] = None) -> Tuple[datetime, datetime]:
    """
    날짜 파싱 실패 시 fallback 날짜 반환
    
    Args:
        week_type: 'current' 또는 'next'
        reference_date: 기준 날짜 (기본값: 오늘)
    
    Returns:
        (start_date, end_date) 튜플
    """
    if reference_date is None:
        reference_date = datetime.now()
    
    if week_type == 'current':
        return get_current_week_range(reference_date)
    else:  # next
        return get_next_week_range(reference_date)

def format_date_badge(start_date: Optional[datetime], end_date: Optional[datetime], today: Optional[datetime] = None) -> dict:
    """
    날짜 뱃지 정보 생성
    
    Returns:
        {
            'type': 'active' | 'upcoming',
            'text': 'D-3 (1/15까지)' 또는 '1/13(월) 오픈',
            'days_left': 남은 일수 (active인 경우)
        }
    """
    if today is None:
        today = datetime.now()
    
    if start_date and end_date:
        if start_date <= today <= end_date:
            # 현재 활성화된 세일
            days_left = (end_date - today).days
            return {
                'type': 'active',
                'text': f'🔥 D-{days_left} ({end_date.strftime("%m/%d")}까지)',
                'days_left': days_left
            }
        elif start_date > today:
            # 곧 시작될 세일
            days_until = (start_date - today).days
            weekday_kr = ['월', '화', '수', '목', '금', '토', '일'][start_date.weekday()]
            return {
                'type': 'upcoming',
                'text': f'📅 {start_date.strftime("%m/%d")}({weekday_kr}) 오픈',
                'days_until': days_until
            }
    
    # 날짜 정보가 불완전한 경우
    if end_date and end_date >= today:
        days_left = (end_date - today).days
        return {
            'type': 'active',
            'text': f'🔥 D-{days_left} ({end_date.strftime("%m/%d")}까지)',
            'days_left': days_left
        }
    
    return {
        'type': 'unknown',
        'text': '날짜 정보 없음',
        'days_left': None
    }
