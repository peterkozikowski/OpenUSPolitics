'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'

interface SearchBarProps {
  placeholder?: string
  autoFocus?: boolean
}

export default function SearchBar({
  placeholder = 'Search bills by title or number...',
  autoFocus = false,
}: SearchBarProps) {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [query, setQuery] = useState(searchParams.get('search') || '')
  const [isFocused, setIsFocused] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)
  const debounceTimer = useRef<NodeJS.Timeout | undefined>(undefined)

  // Keyboard shortcut (Cmd+K or Ctrl+K)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        inputRef.current?.focus()
      }

      // Escape to clear
      if (e.key === 'Escape' && document.activeElement === inputRef.current) {
        handleClear()
        inputRef.current?.blur()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  // Debounced search
  useEffect(() => {
    if (debounceTimer.current) {
      clearTimeout(debounceTimer.current)
    }

    debounceTimer.current = setTimeout(() => {
      const params = new URLSearchParams(searchParams.toString())

      if (query.trim()) {
        params.set('search', query.trim())
      } else {
        params.delete('search')
      }

      // Reset to first page when searching
      params.delete('offset')

      const newUrl = params.toString() ? `?${params.toString()}` : '/'
      router.push(newUrl, { scroll: false })
    }, 300)

    return () => {
      if (debounceTimer.current) {
        clearTimeout(debounceTimer.current)
      }
    }
  }, [query, router, searchParams])

  const handleClear = () => {
    setQuery('')
    inputRef.current?.focus()
  }

  return (
    <div className="w-full">
      <div
        className={`relative flex items-center transition-all duration-200 ${
          isFocused ? 'scale-[1.01]' : ''
        }`}
      >
        {/* Search Icon */}
        <div className="absolute left-4 pointer-events-none">
          <svg
            className="w-5 h-5 text-neutral-400"
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
        </div>

        {/* Input Field */}
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder={placeholder}
          autoFocus={autoFocus}
          className={`w-full pl-12 pr-24 py-4 text-lg bg-white border-2 rounded-xl
                     transition-all duration-200
                     placeholder:text-neutral-400
                     focus:outline-none focus:border-primary-600 focus:ring-4 focus:ring-primary-100
                     ${
                       isFocused
                         ? 'border-primary-600 shadow-lg'
                         : 'border-neutral-200 shadow-md'
                     }`}
          aria-label="Search bills"
          aria-describedby="search-hint"
        />

        {/* Right side controls */}
        <div className="absolute right-4 flex items-center gap-2">
          {/* Clear Button */}
          {query && (
            <button
              onClick={handleClear}
              className="p-1.5 text-neutral-400 hover:text-neutral-700 hover:bg-neutral-100 rounded-md transition-colors"
              aria-label="Clear search"
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
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          )}

          {/* Keyboard Shortcut Hint */}
          <div className="hidden sm:flex items-center gap-1 px-2 py-1 bg-neutral-100 rounded-md text-xs text-neutral-500 font-medium">
            <kbd className="font-mono">⌘</kbd>
            <span>K</span>
          </div>
        </div>
      </div>

      {/* Search Hint */}
      <p id="search-hint" className="sr-only">
        Search bills by title, number, or keywords. Press Cmd+K or Ctrl+K to focus.
      </p>
    </div>
  )
}
