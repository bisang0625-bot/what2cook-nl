'use client'

import { useI18n } from './I18nProvider'

export default function LanguageSwitcher({ className = '' }: { className?: string }) {
  const { lang, setLang, t } = useI18n()

  return (
    <div className={`inline-flex items-center gap-1 rounded-lg border border-gray-200 bg-white p-1 ${className}`}>
      <button
        type="button"
        aria-label={t('language.switcher.aria')}
        onClick={() => setLang('ko')}
        className={`px-2.5 py-1 text-xs font-semibold rounded-md transition-colors ${
          lang === 'ko' ? 'bg-orange-500 text-white' : 'text-gray-600 hover:bg-gray-50'
        }`}
      >
        KO
      </button>
      <button
        type="button"
        aria-label={t('language.switcher.aria')}
        onClick={() => setLang('en')}
        className={`px-2.5 py-1 text-xs font-semibold rounded-md transition-colors ${
          lang === 'en' ? 'bg-orange-500 text-white' : 'text-gray-600 hover:bg-gray-50'
        }`}
      >
        EN
      </button>
      <button
        type="button"
        aria-label={t('language.switcher.aria')}
        onClick={() => setLang('nl')}
        className={`px-2.5 py-1 text-xs font-semibold rounded-md transition-colors ${
          lang === 'nl' ? 'bg-orange-500 text-white' : 'text-gray-600 hover:bg-gray-50'
        }`}
      >
        NL
      </button>
    </div>
  )
}

