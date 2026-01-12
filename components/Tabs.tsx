'use client'

import { ReactNode } from 'react'

interface TabsProps {
  tabs: {
    id: string
    label: string
    content: ReactNode
  }[]
  activeTab: string
  onTabChange: (tabId: string) => void
}

export default function Tabs({ tabs, activeTab, onTabChange }: TabsProps) {
  return (
    <div className="w-full">
      {/* Tab Headers - 버튼 스타일로 개선 */}
      <div className="flex gap-3 mb-6">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id
          return (
            <button
              key={tab.id}
              onClick={() => onTabChange(tab.id)}
              className={`
                flex-1 px-6 py-3.5 rounded-lg font-semibold text-base
                transition-all duration-200
                ${
                  isActive
                    ? 'bg-orange-500 text-white shadow-md shadow-orange-500/30'
                    : 'bg-white text-gray-700 border-2 border-gray-200 hover:border-orange-300 hover:bg-orange-50 hover:text-orange-600'
                }
              `}
            >
              {tab.label}
            </button>
          )
        })}
      </div>

      {/* Tab Content */}
      <div className="mt-4">
        {tabs.find((tab) => tab.id === activeTab)?.content}
      </div>
    </div>
  )
}
