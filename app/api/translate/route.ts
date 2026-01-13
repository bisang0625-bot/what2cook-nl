import { NextResponse } from 'next/server'

type TranslateRequestBody = {
  targetLang: 'en' | 'nl'
  sourceLang?: 'ko' | 'en' | 'nl' | 'auto'
  texts: string[]
}

function normalizeText(t: string) {
  return String(t || '').trim()
}

async function translateWithOpenAI(texts: string[], targetLang: 'en' | 'nl') {
  const apiKey = process.env.OPENAI_API_KEY
  if (!apiKey) {
    throw new Error('OPENAI_API_KEY is not set')
  }

  const targetName = targetLang === 'nl' ? 'Dutch (nl-NL)' : 'English (en-US)'

  const system = [
    'You are a professional localization translator for a cooking & grocery-deals app in the Netherlands.',
    `Translate user-facing recipe text into ${targetName}.`,
    'Do NOT translate store names (e.g., "Albert Heijn", "Jumbo") or brand/platform names (e.g., "Amazon", "bol.com").',
    'If a string contains product names in Dutch, keep them as-is.',
    'Keep numbers, emoji, punctuation, and parentheses structure.',
    'Prefer natural wording; do not do word-by-word translation.',
    'Return JSON only: {"translations":[...]} with the same length as input.',
  ].join(' ')

  const user = JSON.stringify({ targetLang, texts })

  const res = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify({
      model: process.env.OPENAI_TRANSLATE_MODEL || 'gpt-4o-mini',
      temperature: 0.2,
      response_format: { type: 'json_object' },
      messages: [
        { role: 'system', content: system },
        { role: 'user', content: user },
      ],
    }),
  })

  if (!res.ok) {
    const txt = await res.text().catch(() => '')
    throw new Error(`OpenAI translate failed: ${res.status} ${txt}`)
  }

  const data = await res.json()
  const content = data?.choices?.[0]?.message?.content
  const parsed = typeof content === 'string' ? JSON.parse(content) : content
  const translations = parsed?.translations
  if (!Array.isArray(translations) || translations.length !== texts.length) {
    throw new Error('Invalid translation response shape')
  }
  return translations.map((t: any) => String(t))
}

export async function POST(req: Request) {
  try {
    const body = (await req.json()) as TranslateRequestBody
    const targetLang = body?.targetLang
    const texts = Array.isArray(body?.texts) ? body.texts.map(normalizeText) : []

    if (targetLang !== 'en' && targetLang !== 'nl') {
      return NextResponse.json({ error: 'targetLang must be en|nl' }, { status: 400 })
    }
    if (texts.length === 0) {
      return NextResponse.json({ translations: [] })
    }
    if (texts.some((t) => !t)) {
      // keep alignment; translate empty as empty
      const nonEmpty = texts.filter(Boolean)
      const translatedNonEmpty =
        nonEmpty.length > 0 ? await translateWithOpenAI(nonEmpty, targetLang) : []
      let i = 0
      const translations = texts.map((t) => (t ? translatedNonEmpty[i++] : ''))
      return NextResponse.json({ translations })
    }

    const translations = await translateWithOpenAI(texts, targetLang)
    return NextResponse.json({ translations })
  } catch (e: any) {
    // If no key is configured, fall back to identity translation
    const message = String(e?.message || e)
    return NextResponse.json(
      { error: message, translations: [] },
      { status: 500 }
    )
  }
}

