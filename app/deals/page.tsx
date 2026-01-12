'use client'

import { useEffect, useState, useMemo } from 'react'
import Link from 'next/link'
import { ShoppingBag, ChefHat } from 'lucide-react'
// 컴포넌트 경로가 @/ 로 안될 경우를 대비해 상대 경로로 작성 (필요시 조정 가능)
import Tabs from '../../components/Tabs'
import DealsGrid from '../../components/DealsGrid'
import BottomNav from '../../components/BottomNav'
import StoreFilter from '../../components/StoreFilter'

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

interface WeeklySalesData {
  products: SaleProduct[]
  week_type?: 'current' | 'next'
}

export default function DealsPage() {
  const [currentSales, setCurrentSales] = useState<WeeklySalesData | undefined>(undefined)
  const [nextSales, setNextSales] = useState<WeeklySalesData | undefined>(undefined)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'current' | 'next'>('current')
  
  // 마트 필터 상태
  const [selectedStores, setSelectedStores] = useState<Set<string>>(new Set())
  const [selectAll, setSelectAll] = useState<boolean>(true)

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        // [수정] Vercel 빌드 에러 방지를 위해 상대 경로(../../) 사용
        try {
          // current_sales.json 시도
          const currentSalesModule = await import('../../data/current_sales.json')
          setCurrentSales({ products: currentSalesModule.default.products || currentSalesModule.default, week_type: 'current' })
        } catch (err) {
          console.warn('[What2Cook NL] current_sales.json 로드 실패, weekly_sales.json 시도');
          try {
            const weeklyModule = await import('../../data/weekly_sales.json')
            const products = Array.isArray(weeklyModule.default) ? weeklyModule.default : (weeklyModule.default.products || []);