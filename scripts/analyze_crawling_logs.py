"""
크롤링 로그 종합 분석
모든 마트의 성공/실패 패턴을 분석하여 최적의 크롤링 전략 도출
"""
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent

# 분석할 로그 파일들
LOG_FILES = [
    PROJECT_ROOT / "full_scrape.log",
    PROJECT_ROOT / "test_top3.log",
    PROJECT_ROOT / "scraper_output.log",
    PROJECT_ROOT / "scraper.log",
]

def parse_log_file(file_path: Path):
    """로그 파일 파싱"""
    if not file_path.exists():
        return []
    
    events = []
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
        # 마트별 이벤트 추출
        stores = ['Albert Heijn', 'Jumbo', 'Dirk', 'Aldi', 'Plus', 'Hoogvliet', 'Coop', 'Lidl']
        
        for store in stores:
            # 성공 패턴
            success_patterns = [
                rf'{store}.*성공',
                rf'{store}.*✅',
                rf'{store}.*식품 추출.*개',
            ]
            
            # 실패 패턴
            failure_patterns = [
                rf'{store}.*실패',
                rf'{store}.*❌',
                rf'{store}.*오류',
                rf'{store}.*Timeout',
            ]
            
            # 상품 수 추출
            product_count_pattern = rf'{store}.*?(\d+)개.*?식품 추출'
            
            for pattern in success_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    # 상품 수 찾기
                    context = content[max(0, match.start()-200):match.end()+200]
                    product_match = re.search(r'(\d+)개.*?식품', context)
                    product_count = int(product_match.group(1)) if product_match else 0
                    
                    events.append({
                        'store': store,
                        'type': 'success',
                        'product_count': product_count,
                        'context': context[:100]
                    })
            
            for pattern in failure_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    events.append({
                        'store': store,
                        'type': 'failure',
                        'product_count': 0,
                        'context': content[max(0, match.start()-200):match.end()+200][:100]
                    })
    
    return events

def analyze_store_performance(events):
    """마트별 성능 분석"""
    store_stats = defaultdict(lambda: {
        'success_count': 0,
        'failure_count': 0,
        'total_products': [],
        'avg_products': 0,
        'success_rate': 0,
        'failure_reasons': []
    })
    
    for event in events:
        store = event['store']
        stats = store_stats[store]
        
        if event['type'] == 'success':
            stats['success_count'] += 1
            if event['product_count'] > 0:
                stats['total_products'].append(event['product_count'])
        else:
            stats['failure_count'] += 1
            # 실패 원인 추출
            context = event['context'].lower()
            if 'timeout' in context:
                stats['failure_reasons'].append('Timeout')
            elif 'json' in context or 'parsing' in context:
                stats['failure_reasons'].append('JSON Parsing Error')
            elif '상품 부족' in event['context']:
                stats['failure_reasons'].append('Insufficient Products')
            else:
                stats['failure_reasons'].append('Unknown')
    
    # 통계 계산
    for store, stats in store_stats.items():
        total_attempts = stats['success_count'] + stats['failure_count']
        if total_attempts > 0:
            stats['success_rate'] = stats['success_count'] / total_attempts * 100
        
        if stats['total_products']:
            stats['avg_products'] = sum(stats['total_products']) / len(stats['total_products'])
            stats['min_products'] = min(stats['total_products'])
            stats['max_products'] = max(stats['total_products'])
    
    return store_stats

def generate_recommendations(store_stats):
    """최적화 권장사항 생성"""
    recommendations = {}
    
    for store, stats in store_stats.items():
        rec = {
            'current_strategy': 'unknown',
            'recommended_strategy': 'unknown',
            'optimizations': []
        }
        
        # 성공률 기반 권장사항
        if stats['success_rate'] >= 90:
            rec['recommended_strategy'] = 'keep_current'
            rec['optimizations'].append('현재 전략 유지')
        elif stats['success_rate'] >= 70:
            rec['recommended_strategy'] = 'improve_retry'
            rec['optimizations'].append('재시도 로직 강화')
            rec['optimizations'].append('타임아웃 증가')
        else:
            rec['recommended_strategy'] = 'alternative_source'
            rec['optimizations'].append('대체 소스 고려')
            rec['optimizations'].append('크롤링 방식 변경')
        
        # 실패 원인 기반 권장사항
        failure_reasons = stats['failure_reasons']
        if 'Timeout' in failure_reasons:
            rec['optimizations'].append('타임아웃 시간 증가 (현재 120초 → 180초)')
            rec['optimizations'].append('렌더링 대기 시간 증가 (현재 8초 → 12초)')
        
        if 'JSON Parsing Error' in failure_reasons:
            rec['optimizations'].append('AI 응답 파싱 재시도 로직 강화')
            rec['optimizations'].append('JSON 파싱 에러 핸들링 개선')
        
        if 'Insufficient Products' in failure_reasons:
            rec['optimizations'].append('최소 상품 수 기준 조정')
            rec['optimizations'].append('스크롤 범위 확대')
        
        # 평균 상품 수 기반 권장사항
        if stats['avg_products'] > 0:
            if stats['avg_products'] < 5:
                rec['optimizations'].append('스크린샷 범위 확대')
                rec['optimizations'].append('페이지 스크롤 강화')
            elif stats['avg_products'] > 50:
                rec['optimizations'].append('크롤링 효율 최적화 (너무 많은 상품)')
        
        recommendations[store] = rec
    
    return recommendations

def main():
    """메인 분석 함수"""
    print("\n" + "="*70)
    print("📊 크롤링 로그 종합 분석")
    print("="*70 + "\n")
    
    # 모든 로그 파일에서 이벤트 수집
    all_events = []
    for log_file in LOG_FILES:
        if log_file.exists():
            events = parse_log_file(log_file)
            all_events.extend(events)
            print(f"✅ {log_file.name}: {len(events)}개 이벤트 발견")
        else:
            print(f"⚠️ {log_file.name}: 파일 없음")
    
    print(f"\n총 {len(all_events)}개 이벤트 수집\n")
    
    # 마트별 성능 분석
    store_stats = analyze_store_performance(all_events)
    
    # 결과 출력
    print("="*70)
    print("📈 마트별 성능 통계")
    print("="*70 + "\n")
    
    for store in sorted(store_stats.keys()):
        stats = store_stats[store]
        total = stats['success_count'] + stats['failure_count']
        
        if total == 0:
            continue
        
        print(f"🏪 {store}")
        print(f"   시도: {total}회")
        print(f"   성공: {stats['success_count']}회 ({stats['success_rate']:.1f}%)")
        print(f"   실패: {stats['failure_count']}회")
        
        if stats['total_products']:
            print(f"   평균 상품 수: {stats['avg_products']:.1f}개")
            print(f"   범위: {stats['min_products']}~{stats['max_products']}개")
        
        if stats['failure_reasons']:
            reason_counts = {}
            for reason in stats['failure_reasons']:
                reason_counts[reason] = reason_counts.get(reason, 0) + 1
            print(f"   실패 원인: {dict(reason_counts)}")
        
        print()
    
    # 권장사항 생성
    recommendations = generate_recommendations(store_stats)
    
    print("="*70)
    print("💡 최적화 권장사항")
    print("="*70 + "\n")
    
    for store in sorted(recommendations.keys()):
        rec = recommendations[store]
        print(f"🏪 {store}")
        print(f"   전략: {rec['recommended_strategy']}")
        if rec['optimizations']:
            for opt in rec['optimizations']:
                print(f"   - {opt}")
        print()
    
    # 최종 요약
    print("="*70)
    print("📋 최종 요약")
    print("="*70 + "\n")
    
    high_performance = [s for s, stats in store_stats.items() if stats['success_rate'] >= 90]
    medium_performance = [s for s, stats in store_stats.items() if 70 <= stats['success_rate'] < 90]
    low_performance = [s for s, stats in store_stats.items() if stats['success_rate'] < 70 and stats['success_count'] + stats['failure_count'] > 0]
    
    print(f"✅ 고성능 (90% 이상): {', '.join(high_performance) if high_performance else '없음'}")
    print(f"⚠️ 중간 성능 (70-90%): {', '.join(medium_performance) if medium_performance else '없음'}")
    print(f"❌ 저성능 (70% 미만): {', '.join(low_performance) if low_performance else '없음'}")
    print()
    
    return store_stats, recommendations

if __name__ == "__main__":
    store_stats, recommendations = main()
