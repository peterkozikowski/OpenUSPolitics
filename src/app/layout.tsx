import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import Header from '@/components/Header'
import Footer from '@/components/Footer'
import './globals.css'

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'OpenUSPolitics.org - Congress in Plain English',
  description: 'Every major bill in Congress, explained without partisan spin or legalese. Non-partisan analysis powered by AI.',
  keywords: ['congress', 'legislation', 'bills', 'plain english', 'non-partisan', 'bill analysis', 'US politics'],
  authors: [{ name: 'OpenUSPolitics Contributors' }],
  icons: {
    icon: '/favicon.svg',
    apple: '/favicon.svg',
  },
  openGraph: {
    title: 'OpenUSPolitics.org - Congress in Plain English',
    description: 'Every major bill in Congress, explained without partisan spin or legalese.',
    type: 'website',
    siteName: 'OpenUSPolitics.org',
    url: 'https://openuspolitics.org',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'OpenUSPolitics.org - Congress in Plain English',
    description: 'Every major bill in Congress, explained without partisan spin or legalese.',
  },
  robots: {
    index: true,
    follow: true,
  },
  metadataBase: new URL('https://openuspolitics.org'),
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={inter.className}>
      <body className="min-h-screen flex flex-col bg-white">
        <Header />

        <main id="main-content" className="flex-grow">
          {children}
        </main>

        <Footer />
      </body>
    </html>
  )
}
