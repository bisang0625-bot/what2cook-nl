'use client'

import React, { createContext, useContext, useEffect, useMemo, useState } from 'react'

export type AppLanguage = 'ko' | 'en' | 'nl'

type MessageKey = keyof typeof MESSAGES.en

type I18nContextValue = {
  lang: AppLanguage
  setLang: (lang: AppLanguage) => void
  t: (key: MessageKey, vars?: Record<string, string | number>) => string
}

const MESSAGES = {
  ko: {
    'language.english': '영어',
    'language.dutch': '네덜란드어',
    'language.switcher.aria': '언어',

    'nav.recipes': '레시피',
    'nav.deals': '세일',

    'common.all': '전체',
    'common.loading': '로딩 중…',
    'common.expand': '펼치기',
    'common.collapse': '접기',

    'home.title': 'What2Cook NL',
    'home.subtitle': '네덜란드 마트 세일로 고르는 오늘의 한식 메뉴',
    'home.cta.deals': '세일 보기',
    'home.error.generic': '데이터를 불러오는 중 문제가 발생했습니다.',
    'home.loading.recipes': '레시피 로딩 중…',
    'home.error.title': '오류',
    'home.empty.title': '레시피가 없습니다',
    'home.empty.subtitle': '먼저 스크래퍼/크롤러를 실행해 주세요.',
    'home.section.mealIdeas.title': '추천식단',
    'home.section.mealIdeas.subtitle': '네덜란드 마트 세일 품목으로 추천하는 한식 레시피',

    'deals.title': '세일',
    'deals.subtitle': '한식에 잘 어울리는 추천 세일 품목만 모았습니다',
    'deals.backToRecipes': '레시피',
    'deals.tab.thisWeek': '이번 주',
    'deals.tab.nextWeek': '다음 주',
    'deals.nextWeek.empty': '다음 주 세일 정보 준비 중입니다.',
    'deals.category.main': '🥩 주재료',
    'deals.category.sub': '🧂 부재료/양념',
    'deals.category.fruits': '🍎 과일/디저트',

    'recipes.tab.thisWeek': '이번 주',
    'recipes.tab.nextWeek': '다음 주',
    'recipes.thisWeek.description':
      '이번 주(월–일) 진행되는 세일 기반 레시피입니다. 수요일 시작 마트(Jumbo, Dirk)도 포함됩니다.',
    'recipes.nextWeek.description': '다음 주 시작 세일 기반 레시피입니다. 미리 준비하세요!',
    'recipes.thisWeek.empty.title': '이번 주 세일이 없습니다',
    'recipes.thisWeek.empty.subtitle': '다음 주를 확인해 보세요.',
    'recipes.nextWeek.empty.title': '아직 공개된 다음 주 세일이 없어요!',
    'recipes.nextWeek.empty.subtitle': '주말에 다시 와주세요. 보통 토–일에 다음 주 세일이 공개됩니다.',
    'recipes.updateSchedule.title': '📅 업데이트 일정',
    'recipes.updateSchedule.thisWeek': '이번 주 목록: 매주 일요일 새벽 1-2시 업데이트 (월요일 시작 마트: Albert Heijn, ALDI, Plus, Hoogvliet, Coop, Lidl)',
    'recipes.updateSchedule.nextWeek': '다음 주 목록: 매주 일요일 새벽 1-2시 업데이트 (월요일 시작 마트) + 화요일 새벽 1-2시 업데이트 (수요일 시작 마트: Jumbo, Dirk)',
    'recipes.updateSchedule.note': '모든 시간은 네덜란드 시간 기준입니다.',

    'products.loading': '상품 로딩 중…',
    'products.error.generic': '상품을 불러올 수 없습니다.',
    'products.title': '추천 상품',
    'products.subtitle': '한식 요리에 도움이 되는 상품을 비교해보세요',
    'products.viewMode.smart': '지능형 비교',
    'products.viewMode.cards': '카드',
    'products.bannerAlt.custom': '커스텀 광고 배너',
    'products.section.smart.title': '지능형 가격 비교',
    'products.section.smart.subtitle': '가격/배송/신뢰도를 종합 비교합니다. 버튼 위치는 랜덤입니다.',
    'products.section.cards.title': '상품 카드',
    'products.empty.title': '추천 상품이 없습니다',
    'products.empty.subtitle': '곧 추가될 예정입니다.',

    'storeFilter.title': '마트 필터',
    'storeFilter.all': '전체',

    'ads.label': '광고',
    'ads.bannerAlt': '광고 배너',
    'ads.bannerPlaceholder': '광고 배너',

    'affiliateDisclosure.text':
      '이 페이지에는 제휴 링크가 포함되어 있습니다. 링크를 통해 구매하시면 추가 비용 없이 소정의 수수료를 받을 수 있습니다.',

    'legalDisclosure.title': '투명성 공지',
    'legalDisclosure.section.affiliate': '제휴 링크',
    'legalDisclosure.section.ads': '광고',
    'legalDisclosure.section.data': '데이터/쿠키',
    'legalDisclosure.privacyPolicy': '개인정보처리방침',
    'legalDisclosure.footnote': '본 공지는 네덜란드 소비자 보호법 및 GDPR 준수를 위해 제공됩니다.',
    'legalDisclosure.body.affiliate':
      '본 사이트의 일부 링크는 제휴 링크입니다. 해당 링크로 구매 시 소정의 수수료를 받을 수 있으며, 구매 가격은 변동되지 않습니다. 서비스 운영에 도움이 됩니다.',
    'legalDisclosure.body.ads':
      '구글 애드센스 및 기타 광고가 표시될 수 있습니다. 광고는 사용자 관심사에 따라 자동 선택될 수 있으며, 광고 내용에 대한 책임은 제3자에게 있습니다.',
    'legalDisclosure.body.data':
      '사용자 경험 개선 및 광고 개인화를 위해 쿠키를 사용할 수 있습니다. 자세한 내용은 개인정보처리방침을 확인해 주세요.',

    'dashboard.tagline': '이번 주 마트 세일로 차리는 알뜰 밥상',
    'dashboard.count.filtered': '{filtered}개의 레시피 (전체 {total}개 중)',
    'dashboard.count.total': '{total}개의 레시피',
    'dashboard.storeSelect.label': '마트 선택 (여러 개 선택 가능)',
    'dashboard.storeSelect.all': '전체 ({count})',
    'dashboard.storeSelect.selectedCount': '{count}개 마트 선택됨',
    'dashboard.noDeals.title': '현재 등록된 세일 정보가 없습니다.',
    'dashboard.noDeals.subtitle': '매주 일요일 업데이트됩니다.',
    'dashboard.filters.label': '필터',
    'dashboard.filters.group.recommended': '추천:',
    'dashboard.filters.group.features': '특징:',
    'dashboard.filter.kidFriendly': '아이 식단',
    'dashboard.filter.vegetarian': '채식',
    'dashboard.filter.partyFood': '파티/손님초대',
    'dashboard.filter.alcoholSnack': '술안주',
    'dashboard.filter.spicy': '매운맛',
    'dashboard.filter.quickMeal': '30분 이내',
    'dashboard.filter.bestDeal': '1+1 / 파격할인',
    'dashboard.noMatch': '필터 조건에 맞는 레시피가 없습니다.',
    'dashboard.resetFilters': '필터 초기화',
    'dashboard.tag.kidFriendly': '아이식단',
    'dashboard.tag.spicy': '매운맛',
    'dashboard.tag.vegetarian': '채식',
    'dashboard.tag.party': '파티',
    'dashboard.tag.alcoholSnack': '안주',
    'dashboard.modal.saleIngredients': '세일 식재료',
    'dashboard.modal.shoppingList': '쇼핑 리스트',
    'dashboard.modal.savingTip': '절약 팁',
    'dashboard.modal.cookingTime': '조리 시간: {time}',
    'dashboard.dateBadge.until': '🔥 D-{days} ({date}까지)',
    'dashboard.dateBadge.starts': '📅 {date} ({weekday}) 오픈',

    'affiliateCard.button.amazon': 'Amazon 확인',
    'affiliateCard.button.bol': 'Bol.com 확인',
    'affiliateCard.button.link': '링크 확인',
    'affiliateCard.noImage': '이미지 없음',
    'affiliateCard.noLink': '제휴 링크 정보가 없습니다.',

    'sales.weekly.title': '마트별 주간 세일 리스트',
    'sales.weekly.subtitle': '이번 주 장볼 거리를 미리 확인하고 추천 레시피를 확인하세요!',
    'sales.cta.recipesForIngredient': '이 재료로 추천하는 레시피 보기',

    'affiliateComparison.bestPrice': '최저가',
    'affiliateComparison.noLinks': '제휴 링크 정보가 없습니다.',
    'affiliateComparison.noticeTitle': '투명성 공지:',
    'affiliateComparison.noticeText':
      '위 링크를 통해 구매하시면 소정의 수수료를 받을 수 있습니다. 이는 서비스 운영에 도움이 되며, 구매 가격에는 영향을 주지 않습니다.',

    'affiliateBalancer.microcopy.bol.nextDay': '내일 받고 싶다면',
    'affiliateBalancer.microcopy.bol.pickup': '매장에서 직접 픽업',
    'affiliateBalancer.microcopy.bol.check': '가격 및 재고 확인',
    'affiliateBalancer.microcopy.amazon.bestPrice': '최저가로 구매하기',
    'affiliateBalancer.microcopy.amazon.prime': 'Prime 무료 배송 혜택',
    'affiliateBalancer.microcopy.amazon.reviews': '리뷰 확인 후 구매',
    'affiliateBalancer.button.viewBol': 'Bol.com에서 보기',
    'affiliateBalancer.button.viewAmazon': 'Amazon에서 보기',
    'affiliateBalancer.prompt': '가격은 아마존이 싼데, 배송은 bol.com이 빠르네? 어디서 살까?',
    'affiliateBalancer.compareHint': '두 플랫폼의 가격과 배송 옵션을 비교해보세요',
  },
  en: {
    'language.english': 'English',
    'language.dutch': 'Dutch',
    'language.switcher.aria': 'Language',

    'nav.recipes': 'Recipes',
    'nav.deals': 'Deals',

    'common.all': 'All',
    'common.loading': 'Loading…',
    'common.expand': 'Show details',
    'common.collapse': 'Hide details',

    'home.title': 'What2Cook NL',
    'home.subtitle': 'Korean-friendly recipes based on Dutch supermarket deals',
    'home.cta.deals': 'View deals',
    'home.error.generic': 'Something went wrong while loading data.',
    'home.loading.recipes': 'Loading recipes…',
    'home.error.title': 'Error',
    'home.empty.title': 'No recipes yet',
    'home.empty.subtitle': 'Run the scraper first.',
    'home.section.mealIdeas.title': 'Meal ideas',
    'home.section.mealIdeas.subtitle': 'Korean-friendly recipes based on Dutch supermarket deals',

    'deals.title': 'Deals',
    'deals.subtitle': 'Curated deal picks that work well for Korean cooking',
    'deals.backToRecipes': 'Recipes',
    'deals.tab.thisWeek': 'This week',
    'deals.tab.nextWeek': 'Next week',
    'deals.nextWeek.empty': "Next week's deals aren't available yet.",
    'deals.category.main': '🥩 Main ingredients',
    'deals.category.sub': '🧂 Seasonings & extras',
    'deals.category.fruits': '🍎 Fruit & dessert',

    'recipes.tab.thisWeek': 'This week',
    'recipes.tab.nextWeek': 'Next week',
    'recipes.thisWeek.description':
      'Recipes and deal items active this week (Mon–Sun). Includes stores that start on Wednesday (Jumbo, Dirk).',
    'recipes.nextWeek.description': 'Recipes for deals starting next week. Plan ahead!',
    'recipes.thisWeek.empty.title': 'No deals this week',
    'recipes.thisWeek.empty.subtitle': 'Check next week.',
    'recipes.nextWeek.empty.title': "Next week's deals aren't available yet.",
    'recipes.nextWeek.empty.subtitle':
      "Come back over the weekend — most stores publish next week's deals on Sat–Sun.",
    'recipes.updateSchedule.title': '📅 Update Schedule',
    'recipes.updateSchedule.thisWeek': 'This week: Updated every Sunday at 1-2 AM (Monday-start stores: Albert Heijn, ALDI, Plus, Hoogvliet, Coop, Lidl)',
    'recipes.updateSchedule.nextWeek': 'Next week: Updated every Sunday at 1-2 AM (Monday-start stores) + Tuesday at 1-2 AM (Wednesday-start stores: Jumbo, Dirk)',
    'recipes.updateSchedule.note': 'All times are in Netherlands time (CET/CEST).',

    'products.loading': 'Loading products…',
    'products.error.generic': "Couldn't load products.",
    'products.title': 'Recommended products',
    'products.subtitle': 'Compare products that help with Korean cooking',
    'products.viewMode.smart': 'Smart comparison',
    'products.viewMode.cards': 'Cards',
    'products.bannerAlt.custom': 'Custom ad banner',
    'products.section.smart.title': 'Smart price comparison',
    'products.section.smart.subtitle': 'Compare price, delivery, and trust. Button position is randomized.',
    'products.section.cards.title': 'Product cards',
    'products.empty.title': 'No recommendations yet',
    'products.empty.subtitle': 'More coming soon.',

    'dashboard.tagline': "Budget-friendly meals with this week's supermarket deals",
    'dashboard.count.filtered': '{filtered} recipes (out of {total})',
    'dashboard.count.total': '{total} recipes',
    'dashboard.storeSelect.label': 'Stores (multi-select)',
    'dashboard.storeSelect.all': 'All ({count})',
    'dashboard.storeSelect.selectedCount': '{count} stores selected',
    'dashboard.noDeals.title': 'No deal data available yet.',
    'dashboard.noDeals.subtitle': 'Updated every Sunday.',
    'dashboard.filters.label': 'Filters',
    'dashboard.filters.group.recommended': 'Suggested:',
    'dashboard.filters.group.features': 'Features:',
    'dashboard.filter.kidFriendly': 'Kid-friendly',
    'dashboard.filter.vegetarian': 'Vegetarian',
    'dashboard.filter.partyFood': 'Party / guests',
    'dashboard.filter.alcoholSnack': 'With drinks',
    'dashboard.filter.spicy': 'Spicy',
    'dashboard.filter.quickMeal': 'Under 30 min',
    'dashboard.filter.bestDeal': 'Best deal (1+1, etc.)',
    'dashboard.noMatch': 'No recipes match your filters.',
    'dashboard.resetFilters': 'Reset filters',
    'dashboard.tag.kidFriendly': 'Kid-friendly',
    'dashboard.tag.spicy': 'Spicy',
    'dashboard.tag.vegetarian': 'Vegetarian',
    'dashboard.tag.party': 'Party',
    'dashboard.tag.alcoholSnack': 'With drinks',
    'dashboard.modal.saleIngredients': 'On-sale ingredients',
    'dashboard.modal.shoppingList': 'Shopping list',
    'dashboard.modal.savingTip': 'Money-saving tip',
    'dashboard.modal.cookingTime': 'Cooking time: {time}',
    'dashboard.dateBadge.until': '🔥 D-{days} (until {date})',
    'dashboard.dateBadge.starts': '📅 Starts {date} ({weekday})',

    'affiliateCard.button.amazon': 'View on Amazon',
    'affiliateCard.button.bol': 'View on bol.com',
    'affiliateCard.button.link': 'View link',
    'affiliateCard.noImage': 'No image',
    'affiliateCard.noLink': 'No affiliate link available.',

    'affiliateBalancer.microcopy.bol.nextDay': 'Want it tomorrow?',
    'affiliateBalancer.microcopy.bol.pickup': 'Pick up in store',
    'affiliateBalancer.microcopy.bol.check': 'Check price & stock',
    'affiliateBalancer.microcopy.amazon.bestPrice': 'Grab the best price',
    'affiliateBalancer.microcopy.amazon.prime': 'Prime delivery perks',
    'affiliateBalancer.microcopy.amazon.reviews': 'Check reviews before you buy',
    'affiliateBalancer.button.viewBol': 'View on bol.com',
    'affiliateBalancer.button.viewAmazon': 'View on Amazon',
    'affiliateBalancer.prompt': 'Amazon is cheaper, but bol.com delivers faster — where should you buy?',
    'affiliateBalancer.compareHint': 'Compare price and delivery options across both platforms.',

    'sales.weekly.title': 'Weekly deals by store',
    'sales.weekly.subtitle': "Plan your shop and jump to recipe ideas for what's on sale.",
    'sales.cta.recipesForIngredient': 'See recipes with this ingredient',

    'affiliateComparison.bestPrice': 'Best price',
    'affiliateComparison.noLinks': 'No affiliate links available.',
    'affiliateComparison.noticeTitle': 'Transparency:',
    'affiliateComparison.noticeText':
      'If you buy through the links above, we may earn a small commission at no extra cost to you. This helps support the service and does not affect the price you pay.',

    'storeFilter.title': 'Store filter',
    'storeFilter.all': 'All',

    'ads.label': 'Ad',
    'ads.bannerAlt': 'Ad banner',
    'ads.bannerPlaceholder': 'Ad banner',

    'affiliateDisclosure.text':
      'This page contains affiliate links. If you buy through these links, we may earn a small commission at no extra cost to you.',

    'legalDisclosure.title': 'Transparency notice',
    'legalDisclosure.section.affiliate': 'Affiliate links',
    'legalDisclosure.section.ads': 'Advertisements',
    'legalDisclosure.section.data': 'Data & cookies',
    'legalDisclosure.privacyPolicy': 'Privacy policy',
    'legalDisclosure.footnote': 'This notice is provided to comply with Dutch consumer law and the GDPR.',
    'legalDisclosure.body.affiliate':
      'Some links on this site are affiliate links. If you purchase through them, we may receive a small commission. This does not change the price you pay and helps keep the service running.',
    'legalDisclosure.body.ads':
      'We may display Google AdSense and other ads. Ads can be selected automatically based on your interests. We are not responsible for the content of third‑party ads.',
    'legalDisclosure.body.data':
      'We use cookies to improve the user experience and personalize ads. For details, please see our privacy policy.',
  },
  nl: {
    'language.english': 'Engels',
    'language.dutch': 'Nederlands',
    'language.switcher.aria': 'Taal',

    'nav.recipes': 'Recepten',
    'nav.deals': 'Aanbiedingen',

    'common.all': 'Alles',
    'common.loading': 'Laden…',
    'common.expand': 'Details tonen',
    'common.collapse': 'Details verbergen',

    'home.title': 'What2Cook NL',
    'home.subtitle': 'Koreaanse recepten geïnspireerd op aanbiedingen van Nederlandse supermarkten',
    'home.cta.deals': 'Bekijk aanbiedingen',
    'home.error.generic': 'Er ging iets mis bij het laden van de gegevens.',
    'home.loading.recipes': 'Recepten laden…',
    'home.error.title': 'Fout',
    'home.empty.title': 'Nog geen recepten',
    'home.empty.subtitle': 'Start eerst de scraper.',
    'home.section.mealIdeas.title': 'Maaltijdideeën',
    'home.section.mealIdeas.subtitle': 'Koreaanse recepten op basis van aanbiedingen bij Nederlandse supermarkten',

    'deals.title': 'Aanbiedingen',
    'deals.subtitle': 'Samengestelde aanbiedingen die goed passen bij Koreaanse gerechten',
    'deals.backToRecipes': 'Recepten',
    'deals.tab.thisWeek': 'Deze week',
    'deals.tab.nextWeek': 'Volgende week',
    'deals.nextWeek.empty': 'Aanbiedingen voor volgende week zijn nog niet beschikbaar.',
    'deals.category.main': '🥩 Hoofdingrediënten',
    'deals.category.sub': '🧂 Kruiden & extra’s',
    'deals.category.fruits': '🍎 Fruit & dessert',

    'recipes.tab.thisWeek': 'Deze week',
    'recipes.tab.nextWeek': 'Volgende week',
    'recipes.thisWeek.description':
      'Recepten en aanbiedingen die deze week actief zijn (ma–zo). Inclusief winkels die op woensdag starten (Jumbo, Dirk).',
    'recipes.nextWeek.description': 'Recepten voor aanbiedingen die volgende week starten. Plan vooruit!',
    'recipes.thisWeek.empty.title': 'Geen aanbiedingen deze week',
    'recipes.thisWeek.empty.subtitle': 'Bekijk volgende week.',
    'recipes.nextWeek.empty.title': 'Aanbiedingen voor volgende week zijn nog niet beschikbaar.',
    'recipes.nextWeek.empty.subtitle':
      'Kom in het weekend terug — de meeste winkels publiceren volgende week op za–zo.',
    'recipes.updateSchedule.title': '📅 Updateschema',
    'recipes.updateSchedule.thisWeek': 'Deze week: Elke zondag om 1-2 uur bijgewerkt (maandag-start winkels: Albert Heijn, ALDI, Plus, Hoogvliet, Coop, Lidl)',
    'recipes.updateSchedule.nextWeek': 'Volgende week: Elke zondag om 1-2 uur bijgewerkt (maandag-start winkels) + dinsdag om 1-2 uur (woensdag-start winkels: Jumbo, Dirk)',
    'recipes.updateSchedule.note': 'Alle tijden zijn in Nederlandse tijd (CET/CEST).',

    'products.loading': 'Producten laden…',
    'products.error.generic': 'Kan producten niet laden.',
    'products.title': 'Aanbevolen producten',
    'products.subtitle': 'Vergelijk producten die helpen bij Koreaanse gerechten',
    'products.viewMode.smart': 'Slim vergelijken',
    'products.viewMode.cards': 'Kaarten',
    'products.bannerAlt.custom': 'Custom advertentiebanner',
    'products.section.smart.title': 'Slimme prijsvergelijking',
    'products.section.smart.subtitle': 'Vergelijk prijs, bezorging en betrouwbaarheid. De knoppositie is willekeurig.',
    'products.section.cards.title': 'Productkaarten',
    'products.empty.title': 'Nog geen aanbevelingen',
    'products.empty.subtitle': 'Binnenkort meer.',

    'dashboard.tagline': 'Betaalbaar koken met aanbiedingen van deze week',
    'dashboard.count.filtered': '{filtered} recepten (van {total})',
    'dashboard.count.total': '{total} recepten',
    'dashboard.storeSelect.label': 'Winkels (meerdere selecties)',
    'dashboard.storeSelect.all': 'Alles ({count})',
    'dashboard.storeSelect.selectedCount': '{count} winkels geselecteerd',
    'dashboard.noDeals.title': 'Nog geen aanbiedingsdata beschikbaar.',
    'dashboard.noDeals.subtitle': 'Elke zondag bijgewerkt.',
    'dashboard.filters.label': 'Filters',
    'dashboard.filters.group.recommended': 'Aanbevolen:',
    'dashboard.filters.group.features': 'Kenmerken:',
    'dashboard.filter.kidFriendly': 'Kindvriendelijk',
    'dashboard.filter.vegetarian': 'Vegetarisch',
    'dashboard.filter.partyFood': 'Feest / gasten',
    'dashboard.filter.alcoholSnack': 'Bij drank',
    'dashboard.filter.spicy': 'Pittig',
    'dashboard.filter.quickMeal': 'Binnen 30 min',
    'dashboard.filter.bestDeal': 'Topdeal (1+1, etc.)',
    'dashboard.noMatch': 'Geen recepten die bij je filters passen.',
    'dashboard.resetFilters': 'Filters resetten',
    'dashboard.tag.kidFriendly': 'Kindvriendelijk',
    'dashboard.tag.spicy': 'Pittig',
    'dashboard.tag.vegetarian': 'Vegetarisch',
    'dashboard.tag.party': 'Feest',
    'dashboard.tag.alcoholSnack': 'Bij drank',
    'dashboard.modal.saleIngredients': 'Aanbiedingsingrediënten',
    'dashboard.modal.shoppingList': 'Boodschappenlijst',
    'dashboard.modal.savingTip': 'Bespaartip',
    'dashboard.modal.cookingTime': 'Bereidingstijd: {time}',
    'dashboard.dateBadge.until': '🔥 D-{days} (t/m {date})',
    'dashboard.dateBadge.starts': '📅 Start {date} ({weekday})',

    'affiliateCard.button.amazon': 'Bekijk op Amazon',
    'affiliateCard.button.bol': 'Bekijk op bol.com',
    'affiliateCard.button.link': 'Bekijk link',
    'affiliateCard.noImage': 'Geen afbeelding',
    'affiliateCard.noLink': 'Geen affiliate link beschikbaar.',

    'affiliateBalancer.microcopy.bol.nextDay': 'Morgen in huis?',
    'affiliateBalancer.microcopy.bol.pickup': 'Afhalen in de winkel',
    'affiliateBalancer.microcopy.bol.check': 'Prijs & voorraad checken',
    'affiliateBalancer.microcopy.amazon.bestPrice': 'Pak de beste prijs',
    'affiliateBalancer.microcopy.amazon.prime': 'Prime bezorgvoordeel',
    'affiliateBalancer.microcopy.amazon.reviews': 'Bekijk reviews voor je koopt',
    'affiliateBalancer.button.viewBol': 'Bekijk op bol.com',
    'affiliateBalancer.button.viewAmazon': 'Bekijk op Amazon',
    'affiliateBalancer.prompt': 'Amazon is goedkoper, maar bol.com levert sneller — waar koop je?',
    'affiliateBalancer.compareHint': 'Vergelijk prijs en bezorgopties van beide platforms.',

    'sales.weekly.title': 'Wekelijkse aanbiedingen per winkel',
    'sales.weekly.subtitle': 'Plan je boodschappen en ga direct naar receptideeën voor wat in de aanbieding is.',
    'sales.cta.recipesForIngredient': 'Bekijk recepten met dit ingrediënt',

    'affiliateComparison.bestPrice': 'Beste prijs',
    'affiliateComparison.noLinks': 'Geen affiliate links beschikbaar.',
    'affiliateComparison.noticeTitle': 'Transparantie:',
    'affiliateComparison.noticeText':
      'Als je via de links hierboven iets koopt, kunnen wij een kleine commissie ontvangen — zonder extra kosten voor jou. Dit helpt de service te onderhouden en heeft geen invloed op de prijs.',

    'storeFilter.title': 'Winkelfilter',
    'storeFilter.all': 'Alles',

    'ads.label': 'Advertentie',
    'ads.bannerAlt': 'Advertentiebanner',
    'ads.bannerPlaceholder': 'Advertentiebanner',

    'affiliateDisclosure.text':
      'Deze pagina bevat affiliate links. Als je via deze links iets koopt, ontvangen wij mogelijk een kleine commissie — zonder extra kosten voor jou.',

    'legalDisclosure.title': 'Transparantieverklaring',
    'legalDisclosure.section.affiliate': 'Affiliate links',
    'legalDisclosure.section.ads': 'Advertenties',
    'legalDisclosure.section.data': 'Gegevens & cookies',
    'legalDisclosure.privacyPolicy': 'Privacyverklaring',
    'legalDisclosure.footnote': 'Deze verklaring is bedoeld om te voldoen aan de Nederlandse consumentenwetgeving en de GDPR.',
    'legalDisclosure.body.affiliate':
      'Sommige links op deze site zijn affiliate links. Als je via die links iets koopt, kunnen wij een kleine commissie ontvangen. Dit verandert niets aan de prijs die jij betaalt en helpt de service te onderhouden.',
    'legalDisclosure.body.ads':
      'We kunnen Google AdSense en andere advertenties tonen. Advertenties kunnen automatisch worden geselecteerd op basis van je interesses. Wij zijn niet verantwoordelijk voor de inhoud van advertenties van derden.',
    'legalDisclosure.body.data':
      'We gebruiken cookies om de gebruikerservaring te verbeteren en advertenties te personaliseren. Bekijk voor meer informatie onze privacyverklaring.',
  },
} as const

function interpolate(template: string, vars?: Record<string, string | number>) {
  if (!vars) return template
  return template.replace(/\{(\w+)\}/g, (_, k: string) => String(vars[k] ?? `{${k}}`))
}

function detectInitialLanguage(): AppLanguage {
  if (typeof window === 'undefined') return 'en'
  const saved = window.localStorage.getItem('w2c_lang')
  if (saved === 'ko' || saved === 'en' || saved === 'nl') return saved
  const navLang = window.navigator.language?.toLowerCase() || ''
  if (navLang.startsWith('ko')) return 'ko'
  if (navLang.startsWith('nl')) return 'nl'
  return 'en'
}

const I18nContext = createContext<I18nContextValue | null>(null)

export default function I18nProvider({ children }: { children: React.ReactNode }) {
  const [lang, setLangState] = useState<AppLanguage>('en')

  useEffect(() => {
    setLangState(detectInitialLanguage())
  }, [])

  const setLang = (nextLang: AppLanguage) => {
    setLangState(nextLang)
    if (typeof window !== 'undefined') {
      window.localStorage.setItem('w2c_lang', nextLang)
    }
  }

  useEffect(() => {
    if (typeof document !== 'undefined') {
      document.documentElement.lang = lang
    }
  }, [lang])

  const value = useMemo<I18nContextValue>(() => {
    const t = (key: MessageKey, vars?: Record<string, string | number>) => {
      const msg = (MESSAGES[lang] as any)[key] ?? (MESSAGES.en as any)[key] ?? String(key)
      return interpolate(String(msg), vars)
    }
    return { lang, setLang, t }
  }, [lang])

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>
}

export function useI18n() {
  const ctx = useContext(I18nContext)
  if (!ctx) throw new Error('useI18n must be used within I18nProvider')
  return ctx
}

