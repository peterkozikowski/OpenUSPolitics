'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

export default function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)

  // Handle scroll effect for sticky header
  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20)
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  // Prevent body scroll when mobile menu is open
  useEffect(() => {
    if (mobileMenuOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'unset'
    }
  }, [mobileMenuOpen])

  const navigation = [
    { name: 'Home', href: '/' },
    { name: 'Bills', href: '/' },
    { name: 'Executive Orders', href: '/executive-orders/' },
    { name: 'About', href: '/about' },
  ]

  return (
    <>
      {/* Skip to main content link for accessibility */}
      <a
        href="#main-content"
        className="skip-to-main"
      >
        Skip to main content
      </a>

      <header
        className={`sticky top-0 z-50 bg-white border-b transition-all duration-200 ${
          scrolled
            ? 'border-neutral-300 shadow-md'
            : 'border-neutral-200 shadow-sm'
        }`}
      >
        <nav className="container" aria-label="Main navigation">
          <div className="flex items-center justify-between h-16">
            {/* Logo and site name */}
            <Link
              href="/"
              className="flex items-center space-x-3 group"
              aria-label="OpenUSPolitics.org home"
            >
              <div className="w-10 h-10 bg-primary-800 rounded-lg flex items-center justify-center text-white font-bold text-lg group-hover:bg-primary-700 transition-colors">
                OP
              </div>
              <div className="hidden sm:block">
                <h1 className="text-xl font-semibold text-neutral-900 group-hover:text-primary-800 transition-colors">
                  OpenUSPolitics.org
                </h1>
                <p className="text-xs text-neutral-600">
                  Congress in Plain English
                </p>
              </div>
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-1">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  href={item.href}
                  className="px-4 py-2 text-neutral-700 hover:text-primary-800 hover:bg-neutral-50 rounded-lg font-medium transition-colors"
                >
                  {item.name}
                </Link>
              ))}

              {/* Search placeholder - Phase 2 */}
              <div className="ml-4 pl-4 border-l border-neutral-300">
                <button
                  className="text-neutral-600 hover:text-primary-800 transition-colors"
                  aria-label="Search (coming soon)"
                  disabled
                >
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                    />
                  </svg>
                </button>
              </div>
            </div>

            {/* Mobile menu button */}
            <button
              type="button"
              className="md:hidden p-2 rounded-lg text-neutral-700 hover:bg-neutral-100 hover:text-primary-800 transition-colors"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              aria-expanded={mobileMenuOpen}
              aria-label="Toggle navigation menu"
            >
              <span className="sr-only">
                {mobileMenuOpen ? 'Close menu' : 'Open menu'}
              </span>
              {mobileMenuOpen ? (
                <svg
                  className="w-6 h-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              ) : (
                <svg
                  className="w-6 h-6"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                </svg>
              )}
            </button>
          </div>

          {/* Mobile Navigation Menu */}
          {mobileMenuOpen && (
            <>
              {/* Overlay */}
              <div
                className="mobile-menu-overlay md:hidden"
                onClick={() => setMobileMenuOpen(false)}
                aria-hidden="true"
              />

              {/* Mobile menu panel */}
              <div className="md:hidden absolute top-16 left-0 right-0 bg-white border-b border-neutral-200 shadow-lg">
                <div className="container py-4 space-y-1">
                  {navigation.map((item) => (
                    <Link
                      key={item.name}
                      href={item.href}
                      className="block px-4 py-3 text-neutral-700 hover:bg-neutral-50 hover:text-primary-800 rounded-lg font-medium transition-colors"
                      onClick={() => setMobileMenuOpen(false)}
                    >
                      {item.name}
                    </Link>
                  ))}

                  {/* Mobile search placeholder */}
                  <button
                    className="w-full flex items-center space-x-3 px-4 py-3 text-neutral-600 hover:bg-neutral-50 rounded-lg transition-colors"
                    disabled
                  >
                    <svg
                      className="w-5 h-5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                      />
                    </svg>
                    <span className="text-sm">Search (coming soon)</span>
                  </button>
                </div>
              </div>
            </>
          )}
        </nav>
      </header>
    </>
  )
}
