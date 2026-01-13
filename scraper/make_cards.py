import os
from PIL import Image, ImageDraw, ImageFont

# 1. Gems가 준 5개 데이터를 여기에 모두 넣었습니다.
deals_data = [
    {"store": "AH", "product": "소고기 다짐육", "deal": "1+1 혜택", "recipe": "소고기 브로콜리 덮밥", "tip": "소분 후 종이호일 보관", "cta": "프로필 링크 확인"},
    {"store": "Jumbo", "product": "브로콜리", "deal": "특가 세일", "recipe": "브로콜리 계란찜", "tip": "데친 후 물기 제거", "cta": "프로필 링크 확인"},
    {"store": "Dirk", "product": "연어 필렛", "deal": "25% OFF", "recipe": "연어 스테이크", "tip": "키친타월로 물기 제거", "cta": "프로필 링크 확인"},
    {"store": "Aldi", "product": "돼지 어깨살", "deal": "kg당 최저가", "recipe": "아이들용 간장 수육", "tip": "된장 대신 커피가루 활용", "cta": "프로필 링크 확인"},
    {"store": "Lidl", "product": "블루베리", "deal": "대용량 팩", "recipe": "블루베리 요거트", "tip": "식초물에 짧게 세척", "cta": "프로필 링크 확인"}
]

def create_card(index, data):
    width, height = 1080, 1080
    background = Image.new('RGB', (width, height), color=(26, 26, 26))
    draw = ImageDraw.Draw(background)

    # 2. 맥(Mac) 전용 한글 폰트 경로 설정
    # 맥에 기본 설치된 폰트 중 하나를 선택합니다.
    font_paths = [
        "/System/Library/Fonts/Languages/AppleSDGothicNeo.ttc", # 최신 맥 폰트
        "/Library/Fonts/AppleGothic.ttf",                      # 클래식 맥 폰트
        "/System/Library/Fonts/AppleSDGothicNeo.ttc"
    ]
    
    font_title = None
    font_content = None
    
    for path in font_paths:
        if os.path.exists(path):
            font_title = ImageFont.truetype(path, 80)
            font_content = ImageFont.truetype(path, 45)
            break

    if not font_title:
        font_title = ImageFont.load_default()
        font_content = ImageFont.load_default()

    # 텍스트 그리기
    draw.text((100, 150), f"[{data['store']}]", fill=(76, 175, 80), font=font_content)
    draw.text((100, 250), data['product'], fill=(255, 255, 255), font=font_title)
    draw.text((100, 450), f"혜택: {data['deal']}", fill=(255, 215, 0), font=font_content)
    draw.text((100, 600), f"추천 식단: {data['recipe']}", fill=(255, 255, 255), font=font_content)
    draw.text((100, 750), f"💡 Tip: {data['tip']}", fill=(200, 200, 200), font=font_content)
    draw.text((100, 950), f"NL 라이프해커 | {data['cta']}", fill=(150, 150, 150), font=font_content)

    if not os.path.exists('output'):
        os.makedirs('output')
    
    background.save(f'output/card_{index+1}.png')
    print(f"✅ {index+1}번 카드 생성 완료")

if __name__ == "__main__":
    for i, deal in enumerate(deals_data):
        create_card(i, deal)