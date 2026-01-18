'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { ShoppingBag } from 'lucide-react'
import { useI18n } from './i18n/I18nProvider'

interface SaleProduct {
  store?: string
  supermarket?: string
  product_name?: string
  name?: string
  price?: string | null
  price_info?: string | null
  discount?: string | null
  discount_info?: string | null
  valid_from?: string
  valid_until?: string
  start_date?: string
  end_date?: string
}

interface DealsGridProps {
  products: SaleProduct[]
  category: 'main' | 'sub' | 'fruits'
  categoryLabel: string
}

// 날짜 포맷팅
const formatDate = (dateStr?: string) => {
  if (!dateStr) return ''
  try {
    const date = new Date(dateStr)
    const month = date.getMonth() + 1
    const day = date.getDate()
    return `${month}/${day}`
  } catch {
    return ''
  }
}

const formatSalePeriod = (product: SaleProduct) => {
  const startDate = product.valid_from || product.start_date
  const endDate = product.valid_until || product.end_date
  
  const start = formatDate(startDate)
  const end = formatDate(endDate)
  
  if (start && end) {
    return `${start} ~ ${end}`
  }
  return ''
}

// 마트 색상
const getStoreColors = (storeName: string) => {
  const colorMap: Record<string, { bg: string; text: string; border: string }> = {
    'Albert Heijn': { bg: 'bg-orange-100', text: 'text-orange-800', border: 'border-orange-300' },
    'Jumbo': { bg: 'bg-yellow-100', text: 'text-yellow-800', border: 'border-yellow-300' },
    'Lidl': { bg: 'bg-blue-100', text: 'text-blue-800', border: 'border-blue-300' },
    'Plus': { bg: 'bg-green-100', text: 'text-green-800', border: 'border-green-300' },
    'Hoogvliet': { bg: 'bg-red-100', text: 'text-red-800', border: 'border-red-300' },
    'Dirk': { bg: 'bg-purple-100', text: 'text-purple-800', border: 'border-purple-300' },
    'ALDI': { bg: 'bg-indigo-100', text: 'text-indigo-800', border: 'border-indigo-300' },
    'Aldi': { bg: 'bg-indigo-100', text: 'text-indigo-800', border: 'border-indigo-300' },
    'Coop': { bg: 'bg-amber-100', text: 'text-amber-800', border: 'border-amber-300' },
  }
  return colorMap[storeName] || { bg: 'bg-gray-100', text: 'text-gray-800', border: 'border-gray-300' }
}

const getStoreAbbr = (storeName: string) => {
  const abbrMap: Record<string, string> = {
    'Albert Heijn': 'AH', 'Jumbo': 'Jumbo', 'Lidl': 'Lidl', 'Plus': 'Plus',
    'Hoogvliet': 'Hoogvliet', 'Dirk': 'Dirk', 'ALDI': 'ALDI', 'Aldi': 'ALDI', 'Coop': 'Coop',
  }
  return abbrMap[storeName] || storeName.slice(0, 3).toUpperCase()
}

// 번역 캐시 (localStorage 사용)
const translationCache: Map<string, string> = new Map()

async function translateProductName(productName: string, targetLang: string): Promise<string> {
  // 한국어가 아니면 번역 불필요
  if (targetLang !== 'ko') {
    return productName
  }

  // 캐시 확인
  const cacheKey = `trans_${productName}`
  const cached = translationCache.get(cacheKey)
  if (cached) {
    return cached
  }

  // localStorage에서도 확인
  if (typeof window !== 'undefined') {
    const stored = localStorage.getItem(cacheKey)
    if (stored) {
      translationCache.set(cacheKey, stored)
      return stored
    }
  }

  try {
    const response = await fetch('/api/translate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        targetLang: 'ko',
        texts: [productName]
      })
    })

    if (response.ok) {
      const data = await response.json()
      const translated = data.translations?.[0] || productName
      
      // 캐시 저장
      translationCache.set(cacheKey, translated)
      if (typeof window !== 'undefined') {
        localStorage.setItem(cacheKey, translated)
      }
      
      return translated
    }
  } catch (error) {
    console.warn('Translation failed:', error)
  }

  return productName
}

export default function DealsGrid({ products, category, categoryLabel }: DealsGridProps) {
  const { lang } = useI18n()
  const [translatedNames, setTranslatedNames] = useState<Map<string, string>>(new Map())

  useEffect(() => {
    if (lang === 'ko' && products.length > 0) {
      // 모든 상품명 번역
      const translateAll = async () => {
        const translations = new Map<string, string>()
        
        // 고유 키 생성 (상품명 + 마트명)
        const productKeys = products.map((p, idx) => {
          const name = p.product_name || p.name || ''
          const store = p.store || p.supermarket || ''
          return `${name}_${store}_${idx}`
        })
        
        // 배치로 번역 (한 번에 최대 20개)
        const batchSize = 20
        for (let i = 0; i < products.length; i += batchSize) {
          const batch = products.slice(i, i + batchSize)
          const productNames = batch.map(p => p.product_name || p.name || '')
          
          try {
            const response = await fetch('/api/translate', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                targetLang: 'ko',
                texts: productNames
              })
            })

            if (response.ok) {
              const data = await response.json()
              const translated = data.translations || []
              
              batch.forEach((product, idx) => {
                const key = productKeys[i + idx]
                const translatedName = translated[idx] || productNames[idx]
                translations.set(key, translatedName)
              })
            }
          } catch (error) {
            console.warn('Batch translation failed:', error)
          }
        }
        
        setTranslatedNames(translations)
      }
      
      translateAll()
    } else {
      setTranslatedNames(new Map())
    }
  }, [products, lang])

  if (products.length === 0) return null

  return (
    <div>
      <h3 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
        {category === 'main' && <ShoppingBag size={18} />}
        {categoryLabel}
      </h3>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
        {products.map((product, index) => {
          const storeName = product.store || product.supermarket || 'Unknown'
          const originalProductName = product.product_name || product.name || 'Unknown'
          const productKey = `${originalProductName}_${storeName}_${index}`
          const productName = lang === 'ko' && translatedNames.has(productKey) 
            ? translatedNames.get(productKey) || originalProductName
            : originalProductName
          const price = product.price || product.price_info || ''
          const discount = product.discount || product.discount_info || ''
          const salePeriod = formatSalePeriod(product)
          const colors = getStoreColors(storeName)
          const storeAbbr = getStoreAbbr(storeName)

          return (
            <Link
              key={`${storeName}-${originalProductName}-${index}`}
              href="/#recipes-section"
              className="bg-white rounded-lg border border-gray-200 hover:shadow-md hover:border-orange-300 transition-all duration-200 p-3 flex flex-col"
            >
              {/* 마트 배지 및 세일 기간 */}
              <div className="flex items-start justify-between mb-2">
                <div className={`${colors.bg} ${colors.text} ${colors.border} px-2 py-0.5 rounded-full text-xs font-bold border`}>
                  {storeAbbr}
                </div>
                {salePeriod && (
                  <span className="text-xs text-gray-500">{salePeriod}</span>
                )}
              </div>

              {/* 상품명 (2줄 제한) */}
              <h3 className="text-sm font-semibold text-gray-900 mb-2 line-clamp-2 flex-1">
                {productName}
              </h3>

              {/* 가격 및 할인 정보 */}
              <div className="flex items-center justify-between gap-2 mt-auto">
                {price && (
                  <span className="text-xs text-gray-600 truncate">{price}</span>
                )}
                {discount && (
                  <span className="text-xs font-bold text-orange-600 bg-orange-50 px-2 py-0.5 rounded whitespace-nowrap">
                    {discount}
                  </span>
                )}
              </div>
            </Link>
          )
        })}
      </div>
    </div>
  )
}
