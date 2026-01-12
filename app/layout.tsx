import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || 'https://what2cook.nl'),
  title: {
    default: '뭐해먹지 NL | What2Cook NL - 네덜란드 마트 세일 및 한식 레시피 추천',
    template: '%s | 뭐해먹지 NL'
  },
  description: 'AH, Jumbo, Dirk 등 네덜란드 마트의 이번 주 세일 품목을 분석하여 최적의 한식 메뉴와 레시피를 제안합니다. 알뜰하게 장보고 맛있게 요리하세요!',
  keywords: [
    '뭐해먹지',
    'What2Cook',
    'What2Cook NL',
    '한식 레시피',
    '네덜란드 마트 세일',
    'Albert Heijn',
    'Jumbo',
    'Lidl',
    '한인 요리',
    '할인 레시피',
    'Korean recipes',
    'Netherlands supermarket',
    'Nederlandse supermarkt',
    'Koreaanse recepten'
  ],
  authors: [{ name: 'What2Cook NL Team' }],
  creator: 'What2Cook NL',
  publisher: 'What2Cook NL',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  openGraph: {
    type: 'website',
    locale: 'ko_KR',
    alternateLocale: ['nl_NL', 'en_US'],
    url: '/',
    siteName: '뭐해먹지 NL | What2Cook NL',
    title: '뭐해먹지 NL | What2Cook NL - 네덜란드 마트 세일 및 한식 레시피 추천',
    description: 'AH, Jumbo, Dirk 등 네덜란드 마트의 이번 주 세일 품목을 분석하여 최적의 한식 메뉴와 레시피를 제안합니다. 알뜰하게 장보고 맛있게 요리하세요!',
    images: [
      {
        url: '/og-image.jpg',
        width: 1200,
        height: 630,
        alt: '뭐해먹지 NL | What2Cook NL - 네덜란드 마트 세일 및 한식 레시피 추천',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: '뭐해먹지 NL | What2Cook NL - 네덜란드 마트 세일 및 한식 레시피 추천',
    description: 'AH, Jumbo, Dirk 등 네덜란드 마트의 이번 주 세일 품목을 분석하여 최적의 한식 메뉴와 레시피를 제안합니다. 알뜰하게 장보고 맛있게 요리하세요!',
    images: ['/og-image.jpg'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  alternates: {
    canonical: '/',
    languages: {
      'ko-KR': '/',
      'nl-NL': '/nl',
      'en-US': '/en',
    },
  },
  verification: {
    // Google Search Console verification (필요시 추가)
    // google: 'your-google-verification-code',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ko">
      <body className={inter.className}>{children}</body>
    </html>
  )
}
