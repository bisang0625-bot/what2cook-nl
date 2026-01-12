"""
네덜란드 주요 슈퍼마켓 설정
각 마트의 공식 세일 페이지 URL 및 크롤링 전략 정의
"""

STORES = {
    # 1. Albert Heijn (가장 중요 - 시장 점유율 35%)
    "ah": {
        "name": "Albert Heijn",
        "url": "https://www.ah.nl/bonus",
        "strategy": "click_next_week",  # 'Volgende week' 버튼 클릭 필요
        "selectors": {
            "next_week_btn": "a[href*='volgende-week'], button:has-text('Volgende week')",
            "product_card": "article[data-testhook='product-card'], div[class*='product-card']",
            "title": "strong[data-testhook='product-title'], h3[class*='title']",
            "price": "div[data-testhook='price-amount'], span[class*='price']",
            "discount": "div[class*='discount'], span[class*='bonus']"
        },
        "wait_for": "article[data-testhook='product-card']",
        "priority": 1
    },
    
    # 2. Jumbo (시장 점유율 20%)
    "jumbo": {
        "name": "Jumbo",
        "url": "https://www.jumbo.com/aanbiedingen",
        "strategy": "click_next_week",
        "selectors": {
            "next_week_btn": "button:has-text('Volgende week'), a:has-text('Volgende week')",
            "product_card": "div[class*='product-container'], article[class*='product']",
            "title": "h3[class*='title'], span[class*='name']",
            "price": "span[class*='price'], div[class*='price']",
            "discount": "span[class*='discount'], div[class*='promo']"
        },
        "wait_for": "div[class*='product']",
        "priority": 2
    },
    
    # 3. Dirk (전용 URL 존재 - 명확함)
    "dirk": {
        "name": "Dirk",
        "url": "https://www.dirk.nl/folder/volgende-week",  # 꿀팁: 다음주 전용 URL
        "strategy": "direct_url",
        "selectors": {
            "product_card": "div[class*='product-card'], article[class*='product']",
            "title": "h3[class*='title'], span[class*='name']",
            "price": "span[class*='price'], div[class*='price']",
            "discount": "span[class*='discount'], div[class*='korting']"
        },
        "wait_for": "div[class*='product']",
        "priority": 3
    },
    
    # 4. Lidl (탭 선택 방식)
    "lidl": {
        "name": "Lidl",
        "url": "https://www.lidl.nl/c/aanbiedingen",
        "strategy": "click_category",
        "selectors": {
            "category_btn": "li:has-text('Vanaf maandag'), button:has-text('Vanaf maandag')",
            "product_card": "article[class*='product'], div[class*='product-grid']",
            "title": "h3[class*='title'], span[class*='name']",
            "price": "span[class*='price']",
            "discount": "span[class*='discount'], div[class*='badge']"
        },
        "wait_for": "article[class*='product']",
        "priority": 4
    },
    
    # 5. Aldi (전용 URL 존재 - 명확함)
    "aldi": {
        "name": "Aldi",
        "url": "https://www.aldi.nl/folders/folder-van-volgende-week.html",
        "strategy": "direct_url",
        "selectors": {
            "product_card": "div[class*='mod-article-tile'], article[class*='product']",
            "title": "h3[class*='title'], span[class*='name']",
            "price": "span[class*='price'], div[class*='price']",
            "discount": "span[class*='discount'], div[class*='badge']"
        },
        "wait_for": "div[class*='article']",
        "priority": 5
    },
    
    # 6. Hoogvliet (기본 전략)
    "hoogvliet": {
        "name": "Hoogvliet",
        "url": "https://www.hoogvliet.com/aanbiedingen",
        "strategy": "default",
        "selectors": {
            "product_card": "div[class*='promotion-item'], article[class*='product']",
            "title": "h3[class*='title'], span[class*='name']",
            "price": "span[class*='price']",
            "discount": "span[class*='discount'], div[class*='korting']"
        },
        "wait_for": "div[class*='promotion']",
        "priority": 6
    },
    
    # 7. Plus (다음 주 버튼)
    "plus": {
        "name": "Plus",
        "url": "https://www.plus.nl/aanbiedingen",
        "strategy": "click_next_week",
        "selectors": {
            "next_week_btn": "button:has-text('Volgende week'), div[class*='date-selector'] button:last-child",
            "product_card": "div[class*='product'], article[class*='offer']",
            "title": "h3[class*='title'], span[class*='name']",
            "price": "span[class*='price']",
            "discount": "span[class*='discount']"
        },
        "wait_for": "div[class*='product']",
        "priority": 7
    },
    
    # 8. Coop (기본 전략)
    "coop": {
        "name": "Coop",
        "url": "https://www.coop.nl/aanbiedingen",
        "strategy": "default",
        "selectors": {
            "product_card": "div[class*='product-item'], article[class*='product']",
            "title": "h3[class*='title'], span[class*='name']",
            "price": "span[class*='price']",
            "discount": "span[class*='discount']"
        },
        "wait_for": "div[class*='product']",
        "priority": 8
    }
}

# 우선순위 높은 마트 (먼저 테스트)
PRIORITY_STORES = ["ah", "dirk", "aldi"]

# 크롤링 설정
SCRAPING_CONFIG = {
    "timeout": 60000,  # 60초
    "wait_after_load": 5,  # 페이지 로드 후 대기 (초)
    "wait_after_click": 3,  # 버튼 클릭 후 대기 (초)
    "max_retries": 3,  # 최대 재시도 횟수
    "headless": True,  # 헤드리스 모드
    "viewport": {
        "width": 1920,
        "height": 1080
    },
    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# 데이터 검증 설정
VALIDATION_CONFIG = {
    "min_products": 5,  # 최소 상품 수
    "max_products": 100,  # 최대 상품 수 (비정상 데이터 체크)
    "required_fields": ["name", "supermarket"],  # 필수 필드
    "food_keywords": [  # 식품 키워드 (비식품 필터링용)
        "vlees", "vis", "groente", "fruit", "zuivel", "brood", 
        "kip", "varken", "rund", "aardappel", "tomaat", "melk"
    ]
}
