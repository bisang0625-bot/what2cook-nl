/**
 * 모든 레시피 데이터를 EN/NL로 번역하여 JSON 파일 업데이트
 */

const fs = require('fs');
const path = require('path');

// OpenAI API 키 (환경변수에서 읽기)
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;

if (!OPENAI_API_KEY) {
  console.error('❌ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.');
  console.error('사용법: OPENAI_API_KEY=your_key node scripts/translate_recipes.js');
  process.exit(1);
}

// 번역할 파일 목록
const RECIPE_FILES = [
  'data/current_recipes.json',
  'data/weekly_recipes.json',
  'data/next_recipes.json',
];

const AFFILIATE_FILES = [
  'data/affiliate_products.json',
];

// OpenAI API로 번역
async function translateTexts(texts, targetLang) {
  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${OPENAI_API_KEY}`,
    },
    body: JSON.stringify({
      model: 'gpt-4o-mini',
      temperature: 0.2,
      response_format: { type: 'json_object' },
      messages: [
        {
          role: 'system',
          content: `You are a professional localization translator for a cooking & grocery-deals app in the Netherlands. Translate user-facing recipe text into ${targetLang === 'nl' ? 'Dutch (nl-NL)' : 'English (en-US)'}. Do NOT translate store names (e.g., "Albert Heijn", "Jumbo") or brand/platform names. Keep numbers, emoji, punctuation. Prefer natural wording. Return JSON only: {"translations":[...]} with the same length as input.`,
        },
        {
          role: 'user',
          content: JSON.stringify({ targetLang, texts }),
        },
      ],
    }),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`OpenAI API failed: ${response.status} ${text}`);
  }

  const data = await response.json();
  const content = data?.choices?.[0]?.message?.content;
  const parsed = JSON.parse(content);
  return parsed.translations;
}

// 레시피 번역 (배치 처리)
async function translateRecipe(recipe) {
  const fields = ['menu_name', 'description', 'cost_saving_tip'];
  const textsToTranslate = fields.map((f) => recipe[f] || '').filter(Boolean);

  if (textsToTranslate.length === 0) {
    return recipe; // 번역할 내용이 없음
  }

  console.log(`  - 번역 중: "${recipe.menu_name}"`);

  try {
    // EN 번역
    const translatedEN = await translateTexts(textsToTranslate, 'en');
    // NL 번역
    const translatedNL = await translateTexts(textsToTranslate, 'nl');

    let idx = 0;
    fields.forEach((field) => {
      if (recipe[field]) {
        recipe[`${field}_en`] = translatedEN[idx];
        recipe[`${field}_nl`] = translatedNL[idx];
        idx++;
      }
    });

    return recipe;
  } catch (err) {
    console.error(`    ⚠️ 번역 실패:`, err.message);
    return recipe; // 원본 반환
  }
}

// 파일별 번역 실행
async function translateFile(filePath) {
  const fullPath = path.join(__dirname, '..', filePath);

  if (!fs.existsSync(fullPath)) {
    console.log(`⏭️  건너뜀: ${filePath} (파일 없음)`);
    return;
  }

  console.log(`\n📄 ${filePath}`);
  const data = JSON.parse(fs.readFileSync(fullPath, 'utf-8'));

  if (!Array.isArray(data)) {
    console.log('  ⚠️  배열 형식이 아님, 건너뜀');
    return;
  }

  let translated = 0;
  let skipped = 0;

  for (const recipe of data) {
    // 이미 번역이 있으면 건너뜀
    if (recipe.menu_name_en && recipe.menu_name_nl) {
      skipped++;
      continue;
    }

    await translateRecipe(recipe);
    translated++;

    // API 레이트 리밋 회피 (약간의 딜레이)
    await new Promise((resolve) => setTimeout(resolve, 500));
  }

  // 파일 저장
  fs.writeFileSync(fullPath, JSON.stringify(data, null, 2), 'utf-8');
  console.log(`✅ 완료: ${translated}개 번역, ${skipped}개 건너뜀`);
}

// 광고 상품 번역
async function translateAffiliateProduct(product) {
  const fields = ['name', 'description', 'benefit'];
  const textsToTranslate = fields.map((f) => product[f] || '').filter(Boolean);

  if (textsToTranslate.length === 0) {
    return product;
  }

  console.log(`  - 번역 중: "${product.name}"`);

  try {
    const translatedEN = await translateTexts(textsToTranslate, 'en');
    const translatedNL = await translateTexts(textsToTranslate, 'nl');

    let idx = 0;
    fields.forEach((field) => {
      if (product[field]) {
        product[`${field}_en`] = translatedEN[idx];
        product[`${field}_nl`] = translatedNL[idx];
        idx++;
      }
    });

    return product;
  } catch (err) {
    console.error(`    ⚠️ 번역 실패:`, err.message);
    return product;
  }
}

// 광고 파일 번역
async function translateAffiliateFile(filePath) {
  const fullPath = path.join(__dirname, '..', filePath);

  if (!fs.existsSync(fullPath)) {
    console.log(`⏭️  건너뜀: ${filePath} (파일 없음)`);
    return;
  }

  console.log(`\n📄 ${filePath}`);
  const data = JSON.parse(fs.readFileSync(fullPath, 'utf-8'));

  if (!Array.isArray(data)) {
    console.log('  ⚠️  배열 형식이 아님, 건너뜀');
    return;
  }

  let translated = 0;
  let skipped = 0;

  for (const product of data) {
    if (product.name_en && product.name_nl) {
      skipped++;
      continue;
    }

    await translateAffiliateProduct(product);
    translated++;
    await new Promise((resolve) => setTimeout(resolve, 500));
  }

  fs.writeFileSync(fullPath, JSON.stringify(data, null, 2), 'utf-8');
  console.log(`✅ 완료: ${translated}개 번역, ${skipped}개 건너뜀`);
}

// 메인 실행
async function main() {
  console.log('🌐 레시피 & 광고 자동 번역 시작...\n');

  console.log('=== 레시피 번역 ===');
  for (const file of RECIPE_FILES) {
    await translateFile(file);
  }

  console.log('\n=== 광고 상품 번역 ===');
  for (const file of AFFILIATE_FILES) {
    await translateAffiliateFile(file);
  }

  console.log('\n✨ 모든 번역 완료!');
}

main().catch((err) => {
  console.error('❌ 오류 발생:', err);
  process.exit(1);
});
