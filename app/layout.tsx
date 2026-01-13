import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import I18nProvider from '../components/i18n/I18nProvider'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL || 'https://what2cook.nl'),
  title: {
    default: 'What2Cook NL — Deals & Korean recipe ideas',
    template: '%s | What2Cook NL'
  },
  description:
    'Discover curated Dutch supermarket deals (AH, Jumbo, Dirk) and Korean-friendly recipe ideas. Ontdek samengestelde aanbiedingen en Koreaanse recepten.',
  keywords: [
    'What2Cook',
    'What2Cook NL',
    'Korean recipes',
    'Korean cooking',
    'Dutch supermarket deals',
    'Albert Heijn',
    'Jumbo',
    'Lidl',
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
    locale: 'en_US',
    alternateLocale: ['nl_NL'],
    url: '/',
    siteName: 'What2Cook NL',
    title: 'What2Cook NL — Deals & Korean recipe ideas',
    description:
      'Discover curated Dutch supermarket deals and Korean-friendly recipe ideas. Ontdek samengestelde aanbiedingen en Koreaanse recepten.',
    images: [
      {
        url: '/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'What2Cook NL — Deals & Korean recipe ideas',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'What2Cook NL — Deals & Korean recipe ideas',
    description:
      'Discover curated Dutch supermarket deals and Korean-friendly recipe ideas. Ontdek samengestelde aanbiedingen en Koreaanse recepten.',
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
    <html lang="en">
      <body className={inter.className}>
        <I18nProvider>{children}</I18nProvider>
      </body>
    </html>
  )
}
