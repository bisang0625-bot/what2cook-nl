'use client'

import { useEffect, useMemo, useState } from 'react'
import type { AppLanguage } from './I18nProvider'

function djb2Hash(str: string) {
  let hash = 5381
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) + hash) ^ str.charCodeAt(i)
  }
  return (hash >>> 0).toString(16)
}

function cacheKey(lang: 'en' | 'nl', text: string) {
  return `w2c_tr_${lang}_${djb2Hash(text)}`
}

export function useTranslatedText(text: string, lang: AppLanguage) {
  const original = text || ''
  const shouldTranslate = lang === 'en' || lang === 'nl'
  const targetLang = (lang === 'nl' ? 'nl' : 'en') as 'en' | 'nl'

  const [translated, setTranslated] = useState<string>(original)
  const [loading, setLoading] = useState(false)

  const cacheK = useMemo(() => (shouldTranslate && original ? cacheKey(targetLang, original) : ''), [
    shouldTranslate,
    targetLang,
    original,
  ])

  useEffect(() => {
    if (!shouldTranslate) {
      setTranslated(original)
      setLoading(false)
      return
    }
    if (!original) {
      setTranslated('')
      setLoading(false)
      return
    }

    const cached = typeof window !== 'undefined' ? window.localStorage.getItem(cacheK) : null
    if (cached) {
      setTranslated(cached)
      setLoading(false)
      return
    }

    let cancelled = false
    setLoading(true)

    fetch('/api/translate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ targetLang, sourceLang: 'auto', texts: [original] }),
    })
      .then(async (res) => {
        if (!res.ok) {
          console.warn(`[useTranslatedText] API returned ${res.status} for lang=${targetLang}`)
          return original
        }
        const json = await res.json().catch(() => ({}))
        const t = json?.translations?.[0]
        // If API fails or is unconfigured, fall back to original
        if (typeof t === 'string' && t.trim()) {
          return t
        }
        console.warn(`[useTranslatedText] Empty/invalid translation for lang=${targetLang}, using original`)
        return original
      })
      .then((t) => {
        if (cancelled) return
        setTranslated(t)
        try {
          window.localStorage.setItem(cacheK, t)
        } catch {
          // ignore quota / privacy mode errors
        }
      })
      .catch((err) => {
        if (cancelled) return
        console.error(`[useTranslatedText] Fetch failed for lang=${targetLang}:`, err)
        setTranslated(original)
      })
      .finally(() => {
        if (cancelled) return
        setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [shouldTranslate, targetLang, original, cacheK])

  return { text: translated, loading }
}

