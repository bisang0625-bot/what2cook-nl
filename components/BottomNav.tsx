'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { ChefHat, ShoppingBag } from 'lucide-react'
import { useI18n } from './i18n/I18nProvider'

export default function BottomNav() {
  const pathname = usePathname()
  const { t } = useI18n()

  const navItems = [
    {
      label: t('nav.recipes'),
      href: '/',
      icon: ChefHat,
      active: pathname === '/',
    },
    {
      label: t('nav.deals'),
      href: '/deals',
      icon: ShoppingBag,
      active: pathname === '/deals',
    },
  ]

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-50 md:hidden">
      <div className="flex items-center justify-around h-16">
        {navItems.map((item) => {
          const Icon = item.icon
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`
                flex flex-col items-center justify-center gap-1 flex-1 h-full
                transition-colors duration-200
                ${item.active
                  ? 'text-orange-600 bg-orange-50'
                  : 'text-gray-600 hover:text-orange-600 hover:bg-gray-50'
                }
              `}
            >
              <Icon size={24} />
              <span className="text-xs font-medium">{item.label}</span>
            </Link>
          )
        })}
      </div>
    </nav>
  )
}
