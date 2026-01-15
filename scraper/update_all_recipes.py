#!/usr/bin/env python3
"""
🔄 레시피 전체 업데이트 스크립트 (스마트 스케줄러 통합)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

스마트 스케줄러를 사용하여 필요한 경우에만 스크래핑을 실행합니다.
Gemini API 사용량을 최소화합니다.

🚀 실행 방법:
    python3 scraper/update_all_recipes.py          # 스마트 모드 (권장)
    python3 scraper/update_all_recipes.py --force  # 강제 실행

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import sys
import subprocess
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
SCRAPER_DIR = PROJECT_ROOT / "scraper"


def run_command(cmd, description):
    """명령어 실행"""
    print("\n" + "=" * 60)
    print(f"📋 {description}")
    print("=" * 60)
    
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=PROJECT_ROOT,
        capture_output=False,
        text=True
    )
    
    if result.returncode != 0:
        print(f"❌ 오류 발생: {description}")
        return False
    
    print(f"✅ 완료: {description}")
    return True


def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='레시피 전체 업데이트 (스마트 스케줄러 통합)')
    parser.add_argument('--force', action='store_true', help='강제 실행 (스마트 스케줄러 무시)')
    args = parser.parse_args()
    
    print("\n" + "=" * 70)
    print("🔄 레시피 전체 업데이트 시작")
    print("=" * 70)
    
    if args.force:
        print("\n⚠️ 강제 실행 모드: 스마트 스케줄러를 건너뜁니다")
        # Step 1: 이번 주 + 다음 주 세일 데이터 스크래핑 (통합)
        print("\n📅 Step 1: 이번 주 + 다음 주 세일 데이터 스크래핑")
        success1 = run_command(
            "python3 scraper/scrape_all_stores.py",
            "이번 주 + 다음 주 세일 데이터 스크래핑"
        )
    else:
        print("\n🧠 스마트 스케줄러 모드: 필요한 경우에만 스크래핑합니다")
        # Step 1: 스마트 스크래핑 실행
        print("\n📅 Step 1: 스마트 스크래핑 실행")
        success1 = run_command(
            "python3 scraper/smart_scheduler.py",
            "스마트 스크래핑 (필요한 경우에만 실행)"
        )
    
    if not success1:
        print("⚠️ 세일 데이터 스크래핑 실패, 계속 진행합니다...")
    
    # Step 2: 레시피 생성
    print("\n🍳 Step 2: 레시피 생성")
    success2 = run_command(
        "python3 recipe_matcher.py",
        "이번 주 + 다음 주 레시피 생성"
    )
    
    # 최종 요약
    print("\n" + "=" * 70)
    print("📊 업데이트 완료 요약")
    print("=" * 70)
    print(f"✅ 세일 데이터 스크래핑: {'성공' if success1 else '실패'}")
    print(f"✅ 레시피 생성: {'성공' if success2 else '실패'}")
    print("=" * 70)
    
    if success2:
        print("\n✨ 모든 레시피가 업데이트되었습니다!")
        print("   브라우저를 새로고침하면 새로운 레시피를 확인할 수 있습니다.")
    else:
        print("\n⚠️ 일부 단계에서 오류가 발생했습니다.")
        print("   로그를 확인하여 문제를 해결해주세요.")


if __name__ == "__main__":
    main()
