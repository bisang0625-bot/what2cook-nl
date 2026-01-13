"""
Recipe Matcher using Google Gemini API
weekly_sales.json 데이터를 분석하여 한식 레시피를 생성하고 태그를 부여합니다.
"""

import json
import os
import uuid
from pathlib import Path
from typing import List, Dict, Any
from google import genai
from google.genai import types
from dotenv import load_dotenv

# 환경 변수 로드 (우선순위: .env 파일)
load_dotenv()

# config.py에서 API 키 가져오기 (개발자가 직접 입력)
try:
    from config import GEMINI_API_KEY as CONFIG_API_KEY
except ImportError:
    CONFIG_API_KEY = None


class RecipeMatcher:
    def __init__(self, week_type='both'):
        """
        week_type: 'current', 'next', or 'both'
        """
        self.data_dir = Path(__file__).parent / "data"
        self.week_type = week_type
        
        # 입력 파일 설정
        if week_type == 'current':
            self.input_file = self.data_dir / "current_sales.json"
            self.output_file = self.data_dir / "current_recipes.json"
        elif week_type == 'next':
            self.input_file = self.data_dir / "next_sales.json"
            self.output_file = self.data_dir / "next_recipes.json"
        else:  # both
            # 기본값 (하위 호환성)
            self.input_file = self.data_dir / "weekly_sales.json"
            self.output_file = self.data_dir / "weekly_recipes.json"
        
        # Gemini API 설정
        # 우선순위: 1) .env 파일, 2) config.py
        api_key = os.getenv("GEMINI_API_KEY") or (CONFIG_API_KEY if CONFIG_API_KEY else None)
        
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY가 설정되지 않았습니다.\n"
                "다음 중 하나의 방법으로 API 키를 설정하세요:\n"
                "1. config.py 파일의 GEMINI_API_KEY 변수에 직접 입력\n"
                "2. .env 파일에 GEMINI_API_KEY=your_api_key 형태로 저장\n\n"
                "API 키 발급: https://aistudio.google.com/app/apikey"
            )
        
        self.client = genai.Client(api_key=api_key)
        
    def load_bonus_data(self) -> Dict[str, Any]:
        """세일 데이터 파일을 읽어옵니다."""
        if not self.input_file.exists():
            raise FileNotFoundError(
                f"{self.input_file} 파일을 찾을 수 없습니다. "
                "먼저 크롤러를 실행하여 데이터를 수집해주세요."
            )
        
        with open(self.input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        print(f"[INFO] {len(data.get('products', []))}개의 세일 상품 정보를 로드했습니다.")
        return data
    
    def group_products_by_store(self, products: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """마트별로 상품을 그룹화합니다."""
        grouped = {}
        for product in products:
            # 'store' 또는 'supermarket' 필드 지원 (하위 호환성)
            store = product.get('store') or product.get('supermarket', 'Unknown')
            if store not in grouped:
                grouped[store] = []
            grouped[store].append(product)
        return grouped
    
    def categorize_ingredients(self, products: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        제품을 주재료/부재료/과일로 분류합니다.
        카테고리가 'fruits'인 품목은 자동으로 과일로 분류합니다.
        """
        # 과일 키워드 리스트 (네덜란드어)
        fruit_keywords = [
            'druiven', 'druif', 'grape', 'appel', 'apple', 'aardbei', 'strawberry',
            'banaan', 'banana', 'sinaasappel', 'orange', 'mandarijn', 'mandarin',
            'blauwe bessen', 'blueberry', 'framboos', 'raspberry', 'citroen', 'lemon',
            'kiwi', 'peer', 'pear', 'mango', 'ananas', 'pineapple', 'perzik', 'peach',
            'kersen', 'cherry', 'pruim', 'plum', 'abrikoos', 'apricot', 'fruit'
        ]
        
        main_ingredients = []
        sub_ingredients = []
        fruits = []
        
        for product in products[:30]:  # 최대 30개까지만
            name = (product.get('product_name') or product.get('name', 'Unknown')).lower()
            category = product.get('category', '').lower()
            
            # 카테고리가 'fruits'이거나 과일 키워드가 포함된 경우
            if category == 'fruits' or any(keyword in name for keyword in fruit_keywords):
                fruits.append(product)
                continue
            
            # 주재료 판단 (육류, 생선, 두부, 메인 채소 등)
            main_keywords = [
                'speklappen', 'kipfilet', 'kippendijen', 'rundvlees', 'varkensvlees',
                'gehakt', 'zalm', 'vis', 'fish', 'tofu', 'aardappelen', 'aardappel',
                'kool', 'cabbage', 'ui', 'uien', 'onion', 'wortel', 'wortelen',
                'carrot', 'paprika', 'pepper', 'tomaat', 'tomaten', 'tomato', 'champignon',
                'mushroom', 'broccoli', 'spinazie', 'spinach'
            ]
            
            # 부재료/양념 판단
            sub_keywords = [
                'knoflook', 'garlic', 'gember', 'ginger', 'soja', 'soy', 'azijn', 'vinegar',
                'olijfolie', 'olive oil', 'zout', 'salt', 'peper', 'pepper', 'suiker', 'sugar',
                'melk', 'milk', 'kaas', 'cheese', 'boter', 'butter', 'ei', 'eieren', 'egg'
            ]
            
            if any(keyword in name for keyword in main_keywords):
                main_ingredients.append(product)
            elif any(keyword in name for keyword in sub_keywords):
                sub_ingredients.append(product)
            else:
                # 판단 불가능한 경우 주재료로 분류 (메인 요리 중심)
                main_ingredients.append(product)
        
        return {
            'main': main_ingredients,
            'sub': sub_ingredients,
            'fruits': fruits
        }
    
    def create_prompt(self, store_name: str, products: List[Dict[str, Any]]) -> str:
        """마트별 레시피 생성을 위한 프롬프트를 작성합니다."""
        
        # 제품을 주재료/부재료/과일로 분류
        categorized = self.categorize_ingredients(products)
        main_products = categorized['main']
        sub_products = categorized['sub']
        fruit_products = categorized['fruits']
        
        # 상품 리스트 정리 (주재료)
        main_list = []
        for idx, p in enumerate(main_products, 1):
            name = p.get('product_name') or p.get('name', 'Unknown')
            price = p.get('price') or p.get('price_info', '')
            discount = p.get('discount') or p.get('discount_info', '')
            
            product_str = f"{idx}. {name} [주재료]"
            if price:
                product_str += f" - {price}"
            if discount:
                product_str += f" ({discount})"
            
            main_list.append(product_str)
        
        # 부재료 리스트
        sub_list = []
        for idx, p in enumerate(sub_products, 1):
            name = p.get('product_name') or p.get('name', 'Unknown')
            price = p.get('price') or p.get('price_info', '')
            discount = p.get('discount') or p.get('discount_info', '')
            
            product_str = f"{idx}. {name} [부재료/양념]"
            if price:
                product_str += f" - {price}"
            if discount:
                product_str += f" ({discount})"
            
            sub_list.append(product_str)
        
        # 과일 리스트
        fruit_list = []
        for idx, p in enumerate(fruit_products, 1):
            name = p.get('product_name') or p.get('name', 'Unknown')
            price = p.get('price') or p.get('price_info', '')
            discount = p.get('discount') or p.get('discount_info', '')
            
            product_str = f"{idx}. {name} [과일]"
            if price:
                product_str += f" - {price}"
            if discount:
                product_str += f" ({discount})"
            
            fruit_list.append(product_str)
        
        main_products_text = "\n".join(main_list) if main_list else "(없음)"
        sub_products_text = "\n".join(sub_list) if sub_list else "(없음)"
        fruit_products_text = "\n".join(fruit_list) if fruit_list else "(없음)"
        
        prompt = f"""당신은 네덜란드 마트 할인 정보를 기반으로 한국인을 위한 최적의 식단을 제안하는 **'한식 레시피 큐레이터'**입니다. 단순히 식재료 이름을 포함하는 것이 아니라, 실제로 먹었을 때 맛있고 조화로운 레시피를 추천하는 것이 목표입니다.

**{store_name} 이번 주 세일 상품 목록 (분류 완료):**

**📦 주재료 (Main Ingredients) - 레시피 제목의 중심이 되는 재료:**
{main_products_text}

**🧂 부재료/양념 (Sub Ingredients/Garnish) - 레시피의 맛을 돋우는 재료:**
{sub_products_text}

**🍎 과일 (Fruits) - 메인 요리에서 제외, 디저트/사이드 메뉴 전용:**
{fruit_products_text}

**요청사항:**
위 세일 상품 중 **한국 요리에 활용 가능한 재료를 최대한 많이 사용**하여 4인 가족(아이 포함)을 위한 한식 메뉴를 **정확히 3개** 추천해주세요.

**[매칭 원칙: 식재료 궁합]**

**1. 메인 식재료 중심:**
- 할인 품목 중 **'육류(고기), 생선, 두부, 메인 채소(감자, 양배추 등)'**를 핵심 재료로 삼아 레시피를 먼저 고르세요.
- 예: "Speklappen (삼겹살)" + "Uien (양파)" + "Knoflook (마늘)" → 제육볶음 ✅
- 예: "Rundergehakt (다진 소고기)" + "Aardappelen (감자)" → 소고기 감자조림 ✅

**2. 과일류 처리 제한 (매우 중요!):**
- 과일(포도, 사과, 딸기 등)이 할인한다고 해서 이를 **메인 요리(닭갈비, 비빔국수 등)에 강제로 넣지 마세요**.
- 과일은 오직 **디저트, 샐러드, 혹은 소스의 단맛을 내는 용도**로만 사용하세요.
- **금지 조합 예시:**
  - ❌ "포도를 넣은 닭갈비"
  - ❌ "쌈무와 청포도 쌈"
  - ❌ "사과를 넣은 제육볶음"
- **허용 조합 예시:**
  - ✅ "청포도 에이드" (음료/디저트)
  - ✅ "과일 샐러드" (샐러드)
  - ✅ "사과 소스" (소스 재료)

**3. 대체 식재료 상식:**
- 네덜란드 마트 식재료를 한식에 맞게 변형할 때는 한국인이 납득 가능한 범위를 지키세요.
- 예: Stamppot 채소 → 볶음밥용 채소나 국거리용으로 추천 ✅
- 예: 청포도 → 닭갈비에 넣기 ❌ / 청포도 에이드나 식후 과일로 추천 ✅

**4. 레시피 생성 우선순위:**
- **1순위 (정석 조합):** 할인 중인 삼겹살 + 마늘/양파 → 제육볶음
- **2순위 (현지 식재료 활용):** 할인 중인 다진 소고기 + 네덜란드 감자 → 소고기 감자조림
- **3순위 (메인 재료 부족 시):** 메인 재료가 부족하고 과일만 할인한다면, 억지로 메인 요리를 만들지 말고 **"이번 주 후식 추천"** 혹은 **"가벼운 브런치"** 카테고리로 분류하세요.

**중요 조건 (일관성 필수!):**
1. 각 메뉴는 **위 세일 상품 중 최소 2-3개**를 실제로 사용해야 합니다
2. **main_ingredients**에는 **네덜란드어 상품명과 한국어 번역을 함께** 기입하세요
   - 형식: "네덜란드어명 (한국어명)"
   - 예: "Speklappen (삼겹살)", "Kipfilet (닭가슴살)", "Witte druiven (청포도)"
   - **과일은 메인 요리가 아닌 경우에만 포함** (디저트/음료/샐러드)
3. **menu_name (제목)은 반드시 main_ingredients에 포함된 실제 재료를 반영해야 합니다**
   - **제목은 한국어만 사용** (네덜란드어 제목 금지!)
   - 예: main_ingredients에 "Kipfilet (닭가슴살)"이 있으면 → 제목은 "닭가슴살..."로 시작
   - 예: main_ingredients에 "Verse schouderkarbonade (어깨살)"이 있으면 → 제목은 "어깨살..."로 시작
   - **절대 제목과 재료가 다르면 안됩니다!**
   - **제목에 네덜란드어를 넣지 마세요!** (예: "AH Verse Pasta's를 활용한..." ❌ → "파스타를 활용한..." ✅)
4. **description (설명)도 제목과 main_ingredients와 일치해야 합니다**
   - 제목이 "고등어 구이"면 설명에도 "고등어"가 나와야 함
   - 제목이 "어깨살 구이"면 설명에도 "어깨살"이 나와야 함
5. 세일 혜택(1+1, 할인율)을 활용한 비용 절감 팁 포함
6. 다양한 카테고리: 국/찌개, 볶음, 구이, 조림 등
7. **사용자가 "이 재료로 이걸 만든다고?"라는 의문이 들지 않게 하세요**

**네덜란드어-한국어 식품 참고:**
- Speklappen = 삼겹살/돼지 뱃살
- Kipfilet/Kippendijen = 닭가슴살/닭다리살
- Rundergehakt = 소고기 다짐육
- Varkensvlees = 돼지고기
- Zalm = 연어
- Aardappelen = 감자
- Wortelen = 당근
- Uien = 양파
- Paprika = 파프리카
- Tomaten = 토마토
- Druiven = 포도
- Melk = 우유
- Kaas = 치즈
- Eieren = 계란

**JSON 형식 (다른 텍스트 없이 JSON만 출력):**
**⚠️ 필수: menu_name, description, cost_saving_tip을 반드시 한국어/영어/네덜란드어 3개 버전으로 제공하세요!**
**각 레시피 객체에 다음 필드들이 모두 포함되어야 합니다:**

- **menu_name**: 한국어 메뉴명 (예: "파스타 닭갈비")
- **menu_name_en**: 영어 메뉴명 (예: "Pasta Chicken Dak-galbi") - 필수!
- **menu_name_nl**: 네덜란드어 메뉴명 (예: "Pasta Kip Dak-galbi") - 필수!
- **description**: 한국어 설명
- **description_en**: 영어 설명 - 필수!
- **description_nl**: 네덜란드어 설명 - 필수!
- **cost_saving_tip**: 한국어 팁 (있는 경우)
- **cost_saving_tip_en**: 영어 팁 (cost_saving_tip이 있으면 필수!)
- **cost_saving_tip_nl**: 네덜란드어 팁 (cost_saving_tip이 있으면 필수!)

**번역 규칙:**
- 상점명("Albert Heijn", "Jumbo" 등)은 번역하지 마세요
- 브랜드명("Amazon", "bol.com" 등)은 번역하지 마세요
- 숫자, 이모지, 구두점은 그대로 유지하세요
- 자연스러운 표현을 사용하세요 (직역 금지)

```json
[
  {{
    "store": "{store_name}",
    "menu_name": "메뉴명 (한글, 주재료 중심)",
    "menu_name_en": "Menu name in English",
    "menu_name_nl": "Menunaam in het Nederlands",
    "main_ingredients": ["Speklappen (삼겹살)", "Kimchi (김치)", "Tofu (두부)"],
    "sale_ingredients": ["Knoflook (마늘)", "Witte druiven (청포도)"],
    "description": "요리 설명 (1-2문장, 한국어)",
    "description_en": "Recipe description in English",
    "description_nl": "Receptbeschrijving in het Nederlands",
    "tags": {{
      "is_spicy": true/false,
      "is_vegetarian": true/false,
      "is_kid_friendly": true/false,
      "is_party_food": true/false,
      "is_alcohol_snack": true/false,
      "cooking_time": "25min"
    }},
    "shopping_list": ["재료1 (한국어)", "재료2 (한국어)", ...],
    "cost_saving_tip": "세일 활용 팁 (한국어)",
    "cost_saving_tip_en": "Cost-saving tip in English",
    "cost_saving_tip_nl": "Bespaartip in het Nederlands"
  }}
]
```

**필드 설명:**
- **menu_name**: 주재료 중심의 메뉴명 (한국어만)
- **main_ingredients**: 메인 요리에 실제 사용되는 재료 (주재료 + 부재료, 네덜란드어+한국어)
- **sale_ingredients**: 세일 중인 부재료/과일 목록 (레시피 제목에는 반영되지 않지만 세일 혜택을 받는 재료)
  - 예: "Knoflook (마늘)", "Witte druiven (청포도)" 등
  - 부재료나 과일이 메인 요리에 사용되지 않더라도, 세일 중인 재료이면 여기에 포함

**태그 설명:**
- is_party_food: 손님 접대용 요리 (잡채, 불고기, 갈비찜 등)
- is_alcohol_snack: 술안주 (두부김치, 해물파전, 오징어볶음 등)
- is_kid_friendly: 아이들이 먹기 좋은 메뉴 (매운맛 X)
- is_spicy: 고추장/고춧가루 들어가면 true

**예시 (일관성 중요!):**
만약 "Speklappen €3.99 (1+1)"(주재료), "Knoflook €0.99"(부재료), "Witte druiven €1.49"(과일)이 세일 중이라면:
- menu_name: "삼겹살 김치찌개" (주재료 중심, 한국어만)
- main_ingredients: ["Speklappen (삼겹살)", "Kimchi (김치)", "Tofu (두부)", "Knoflook (마늘)"]
  - 주재료와 부재료 모두 포함 (실제 요리에 사용)
- sale_ingredients: ["Knoflook (마늘)"]
  - 부재료는 여기에 별도 표시 (레시피 제목에는 반영되지 않음)
  - 과일은 메인 요리에 사용하지 않으므로 포함하지 않음
- description: "삼겹살과 김치를 넣어 끓인 얼큰한 찌개..." (제목과 재료 일치)
- cost_saving_tip: "Speklappen(삼겹살) 1+1 기회를 활용해 김치찌개를 넉넉히 끓이세요"

**과일만 세일 중인 경우:**
- menu_name: "청포도 에이드" (디저트/음료)
- main_ingredients: ["Witte druiven (청포도)", "Suiker (설탕)", "Water (물)"]
- sale_ingredients: ["Witte druiven (청포도)"]
- description: "신선한 청포도를 활용한 상큼한 에이드..."
- tags: {{"is_kid_friendly": true, "cooking_time": "10min"}}

**잘못된 예시 (절대 하지 마세요!):**
- menu_name: "고등어 구이" 
- main_ingredients: ["Verse schouderkarbonade (어깨살)", ...]  ❌ 제목과 재료 불일치!

- menu_name: "AH Verse Pasta's를 활용한..."  ❌ 제목에 네덜란드어 포함!

- menu_name: "마늘 볶음"  ❌ 부재료를 제목에 사용!
- main_ingredients: ["Knoflook (마늘)", ...]  ❌ 주재료가 아닌 부재료 중심!

- menu_name: "포도를 넣은 닭갈비"  ❌ 과일을 메인 요리에 강제 포함!
- main_ingredients: ["Kipfilet (닭가슴살)", "Witte druiven (청포도)", ...]  ❌ 괴식 조합!

**올바른 예시:**
- menu_name: "어깨살 구이" (주재료 중심, 한국어만!)
- main_ingredients: ["Verse schouderkarbonade (어깨살)", "Knoflook (마늘)", "Uien (양파)"]  ✅ 일치!
- sale_ingredients: ["Knoflook (마늘)"]  ✅ 부재료는 별도 표시
- description: "어깨살을 구워..."  ✅ 일치!

- menu_name: "삼겹살 김치찌개" (주재료 중심!)
- main_ingredients: ["Speklappen (삼겹살)", "Kimchi (김치)", "Knoflook (마늘)"]  ✅
- sale_ingredients: ["Knoflook (마늘)"]  ✅ 부재료는 별도 표시
- description: "삼겹살과 김치를 넣어..."  ✅ 주재료 중심 설명

- menu_name: "청포도 에이드" (과일을 디저트/음료로 활용) ✅
- main_ingredients: ["Witte druiven (청포도)", "Suiker (설탕)", ...]  ✅ 적절한 활용!
- sale_ingredients: ["Witte druiven (청포도)"]  ✅ 과일은 세일 재료로 표시

- menu_name: "제육볶음" (메인 재료 중심) ✅
- main_ingredients: ["Speklappen (삼겹살)", "Knoflook (마늘)", "Uien (양파)"]  ✅ 정석 조합!
"""
        
        return prompt
    
    def parse_gemini_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Gemini API 응답을 파싱하여 레시피 리스트로 변환합니다."""
        import re
        
        # JSON 코드 블록 제거
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(1)
        elif response_text.startswith('```'):
            response_text = response_text.strip('`').strip()
            if response_text.startswith('json'):
                response_text = response_text[4:].strip()
        
        try:
            recipes_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON 파싱 실패: {str(e)}")
            print(f"응답 내용:\n{response_text[:500]}")
            return []
        
        # 데이터 검증 및 ID 추가
        recipes = []
        for recipe_data in recipes_data:
            if not isinstance(recipe_data, dict):
                continue
            
            # 필수 필드 확인
            required_fields = ['menu_name', 'main_ingredients', 'description', 'tags', 'shopping_list']
            if not all(field in recipe_data for field in required_fields):
                continue
            
            # UUID 추가
            recipe_data['id'] = str(uuid.uuid4())
            
            # 번역 필드 확인 및 로그
            has_translations = all([
                recipe_data.get('menu_name_en'),
                recipe_data.get('menu_name_nl'),
                recipe_data.get('description_en'),
                recipe_data.get('description_nl')
            ])
            if not has_translations:
                print(f"  ⚠️  번역 필드 누락: {recipe_data.get('menu_name', 'Unknown')}")
            
            # 태그 검증
            if 'tags' in recipe_data and isinstance(recipe_data['tags'], dict):
                tags = recipe_data['tags']
                # 필수 태그 기본값 설정
                tags.setdefault('is_spicy', False)
                tags.setdefault('is_vegetarian', False)
                tags.setdefault('is_kid_friendly', False)
                tags.setdefault('is_party_food', False)
                tags.setdefault('is_alcohol_snack', False)
                tags.setdefault('cooking_time', '30min')
            
            recipes.append(recipe_data)
        
        return recipes
    
    def generate_recipes_for_store(self, store_name: str, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """특정 마트의 상품을 기반으로 레시피를 생성합니다."""
        
        print(f"\n[INFO] {store_name} 레시피 생성 중... ({len(products)}개 상품)")
        prompt = self.create_prompt(store_name, products)
        
        try:
            # Gemini API 호출
            response = self.client.models.generate_content(
                model='gemini-2.0-flash-001',
                contents=prompt
            )
            response_text = response.text
            
            recipes = self.parse_gemini_response(response_text)
            
            if recipes:
                print(f"[SUCCESS] {store_name}: {len(recipes)}개 레시피 생성 완료")
            else:
                print(f"[WARNING] {store_name}: 레시피 생성 실패")
            
            return recipes
            
        except Exception as e:
            print(f"[ERROR] {store_name} API 호출 실패: {str(e)}")
            return []
    
    def save_recipes(self, recipes: List[Dict[str, Any]]):
        """레시피를 JSON 파일로 저장합니다."""
        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(recipes, f, ensure_ascii=False, indent=2)
        
        print(f"\n[SUCCESS] 총 {len(recipes)}개 레시피가 {self.output_file}에 저장되었습니다.")
    
    def run(self):
        """레시피 매칭 프로세스를 실행합니다."""
        print("=" * 50)
        print("Recipe Matcher 실행 중...")
        print("=" * 50)
        
        # 1. 세일 데이터 로드
        bonus_data = self.load_bonus_data()
        products = bonus_data.get('products', [])
        
        if not products:
            print("[ERROR] 세일 상품 데이터가 없습니다.")
            return []
        
        # 2. 마트별로 그룹화
        grouped_products = self.group_products_by_store(products)
        print(f"\n[INFO] {len(grouped_products)}개 마트의 데이터 발견")
        
        # 3. 각 마트별로 레시피 생성
        all_recipes = []
        
        # 세일 기간 정보 가져오기
        sale_period = bonus_data.get('sale_period', '')
        week_type = bonus_data.get('week_type', 'current')
        
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
        
        from datetime import datetime, timedelta
        
        def get_store_sale_dates(store_name: str, week_type: str) -> tuple:
            """마트별 세일 시작일과 종료일 계산"""
            today = datetime.now()
            days_since_monday = today.weekday()
            current_monday = today - timedelta(days=days_since_monday)
            
            start_day_of_week = STORE_SALE_START_DAY.get(store_name, 0)
            
            if week_type == 'current':
                # 현재 주의 세일 시작일
                days_to_start = (start_day_of_week - current_monday.weekday()) % 7
                if days_to_start == 0 and today.weekday() < start_day_of_week:
                    sale_start = current_monday + timedelta(days=start_day_of_week)
                else:
                    sale_start = current_monday + timedelta(days=start_day_of_week)
                    if sale_start < today:
                        sale_start = current_monday + timedelta(days=7 + start_day_of_week)
            else:  # next
                next_monday = current_monday + timedelta(days=7)
                sale_start = next_monday + timedelta(days=start_day_of_week)
            
            sale_end = sale_start + timedelta(days=6)
            return sale_start, sale_end
        
        for store_name, store_products in grouped_products.items():
            recipes = self.generate_recipes_for_store(store_name, store_products)
            
            # 각 레시피에 마트별 날짜 정보 추가
            sale_start, sale_end = get_store_sale_dates(store_name, week_type)
            
            for recipe in recipes:
                recipe['valid_from'] = sale_start.isoformat()
                recipe['valid_until'] = sale_end.isoformat()
            
            all_recipes.extend(recipes)
            
            # API 제한 방지를 위해 대기
            import time
            time.sleep(3)
        
        # 4. 레시피 저장
        if all_recipes:
            self.save_recipes(all_recipes)
        else:
            print("\n[ERROR] 생성된 레시피가 없습니다.")
        
        return all_recipes


def main(week_type='both'):
    """메인 실행 함수"""
    try:
        print("\n" + "=" * 50)
        print("🍳 What2Cook NL - Recipe Matcher 시작")
        print("=" * 50)
        
        if week_type == 'both':
            # 현재 주와 다음 주 모두 처리
            print("\n" + "=" * 50)
            print("📦 1단계: 이번 주 레시피 생성")
            print("=" * 50)
            
            try:
                matcher_current = RecipeMatcher('current')
                recipes_current = matcher_current.run()
                if recipes_current:
                    print(f"✅ 이번 주: {len(recipes_current)}개 레시피 생성")
            except FileNotFoundError:
                print("⚠️ current_sales.json이 없습니다. 이번 주 레시피를 건너뜁니다.")
            
            print("\n" + "=" * 50)
            print("📦 2단계: 다음 주 레시피 생성")
            print("=" * 50)
            
            try:
                matcher_next = RecipeMatcher('next')
                recipes_next = matcher_next.run()
                if recipes_next:
                    print(f"✅ 다음 주: {len(recipes_next)}개 레시피 생성")
            except FileNotFoundError:
                print("⚠️ next_sales.json이 없습니다. 다음 주 레시피를 건너뜁니다.")
            
            print("\n" + "=" * 50)
            print("🍳 What2Cook NL - Recipe Matcher 실행 완료!")
            print("=" * 50)
        else:
            # 단일 주차만 처리
            matcher = RecipeMatcher(week_type)
            recipes = matcher.run()
            
            if recipes:
                print("\n" + "=" * 50)
                print("✅ Recipe Matcher 실행 완료!")
                print("=" * 50)
                
                # 마트별 레시피 수 출력
                store_count = {}
                for recipe in recipes:
                    store = recipe.get('store', 'Unknown')
                    store_count[store] = store_count.get(store, 0) + 1
                
                print("\n생성된 레시피 요약:")
                for store, count in store_count.items():
                    print(f"  - {store}: {count}개")
                
                print(f"\n총 {len(recipes)}개 레시피 생성 완료!")
            
    except Exception as e:
        print(f"\n[실패] 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
