'use client'

import { useRouter, useSearchParams } from 'next/navigation'
import { BillStatus, BillTopic } from '@/lib/types'

const statusOptions = [
  { value: '', label: 'All Statuses' },
  { value: BillStatus.INTRODUCED, label: 'Introduced' },
  { value: BillStatus.IN_COMMITTEE, label: 'In Committee' },
  { value: BillStatus.PASSED_HOUSE, label: 'Passed House' },
  { value: BillStatus.PASSED_SENATE, label: 'Passed Senate' },
  { value: BillStatus.SIGNED, label: 'Signed into Law' },
  { value: BillStatus.VETOED, label: 'Vetoed' },
  { value: BillStatus.FAILED, label: 'Failed' },
]

const topicOptions = [
  { value: '', label: 'All Topics' },
  { value: BillTopic.HEALTHCARE, label: 'Healthcare' },
  { value: BillTopic.DEFENSE, label: 'Defense' },
  { value: BillTopic.ECONOMY, label: 'Economy' },
  { value: BillTopic.EDUCATION, label: 'Education' },
  { value: BillTopic.ENVIRONMENT, label: 'Environment' },
  { value: BillTopic.INFRASTRUCTURE, label: 'Infrastructure' },
  { value: BillTopic.IMMIGRATION, label: 'Immigration' },
  { value: BillTopic.JUSTICE, label: 'Justice' },
  { value: BillTopic.TECHNOLOGY, label: 'Technology' },
  { value: BillTopic.FOREIGN_POLICY, label: 'Foreign Policy' },
  { value: BillTopic.AGRICULTURE, label: 'Agriculture' },
  { value: BillTopic.ENERGY, label: 'Energy' },
  { value: BillTopic.LABOR, label: 'Labor' },
  { value: BillTopic.SOCIAL_SERVICES, label: 'Social Services' },
  { value: BillTopic.OTHER, label: 'Other' },
]

const sortOptions = [
  { value: 'date-desc', label: 'Most Recent' },
  { value: 'date-asc', label: 'Oldest First' },
  { value: 'title-asc', label: 'Alphabetical (A-Z)' },
  { value: 'title-desc', label: 'Alphabetical (Z-A)' },
]

export default function BillFilters() {
  const router = useRouter()
  const searchParams = useSearchParams()

  const currentStatus = searchParams.get('status') || ''
  const currentTopic = searchParams.get('topic') || ''
  const currentSort =
    `${searchParams.get('sortBy') || 'date'}-${searchParams.get('sortOrder') || 'desc'}`

  // Count active filters
  const activeFilterCount = [
    searchParams.get('status'),
    searchParams.get('topic'),
  ].filter(Boolean).length

  const updateFilter = (key: string, value: string) => {
    const params = new URLSearchParams(searchParams.toString())

    if (value) {
      params.set(key, value)
    } else {
      params.delete(key)
    }

    // Reset to first page when filtering
    params.delete('offset')

    const newUrl = params.toString() ? `?${params.toString()}` : '/'
    router.push(newUrl, { scroll: false })
  }

  const updateSort = (value: string) => {
    const [sortBy = 'date', sortOrder = 'desc'] = value.split('-')
    const params = new URLSearchParams(searchParams.toString())

    params.set('sortBy', sortBy)
    params.set('sortOrder', sortOrder)

    const newUrl = `?${params.toString()}`
    router.push(newUrl, { scroll: false })
  }

  const clearFilters = () => {
    const params = new URLSearchParams(searchParams.toString())

    // Keep search but clear filters
    params.delete('status')
    params.delete('topic')
    params.delete('offset')

    const newUrl = params.toString() ? `?${params.toString()}` : '/'
    router.push(newUrl, { scroll: false })
  }

  return (
    <div className="bg-white border border-neutral-200 rounded-xl p-6 shadow-sm">
      <div className="flex flex-col lg:flex-row lg:items-center gap-4">
        {/* Filters Label */}
        <div className="flex items-center gap-3">
          <h2 className="text-sm font-semibold text-neutral-700 uppercase tracking-wide">
            Filters
          </h2>
          {activeFilterCount > 0 && (
            <span className="inline-flex items-center justify-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
              {activeFilterCount} active
            </span>
          )}
        </div>

        {/* Filter Dropdowns */}
        <div className="flex-1 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {/* Status Filter */}
          <div>
            <label htmlFor="status-filter" className="sr-only">
              Filter by status
            </label>
            <select
              id="status-filter"
              value={currentStatus}
              onChange={(e) => updateFilter('status', e.target.value)}
              className="w-full px-4 py-2.5 bg-white border border-neutral-300 rounded-lg text-sm
                       focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
                       transition-colors cursor-pointer"
            >
              {statusOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* Topic Filter */}
          <div>
            <label htmlFor="topic-filter" className="sr-only">
              Filter by topic
            </label>
            <select
              id="topic-filter"
              value={currentTopic}
              onChange={(e) => updateFilter('topic', e.target.value)}
              className="w-full px-4 py-2.5 bg-white border border-neutral-300 rounded-lg text-sm
                       focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
                       transition-colors cursor-pointer"
            >
              {topicOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* Sort Dropdown */}
          <div>
            <label htmlFor="sort-filter" className="sr-only">
              Sort bills
            </label>
            <select
              id="sort-filter"
              value={currentSort}
              onChange={(e) => updateSort(e.target.value)}
              className="w-full px-4 py-2.5 bg-white border border-neutral-300 rounded-lg text-sm
                       focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500
                       transition-colors cursor-pointer"
            >
              {sortOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Clear Button */}
        {activeFilterCount > 0 && (
          <button
            onClick={clearFilters}
            className="inline-flex items-center gap-2 px-4 py-2.5 text-sm font-medium text-neutral-700
                     bg-neutral-100 hover:bg-neutral-200 rounded-lg transition-colors
                     focus:outline-none focus:ring-2 focus:ring-neutral-500 focus:ring-offset-2"
            aria-label="Clear all filters"
          >
            <svg
              className="w-4 h-4"
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
            <span className="hidden sm:inline">Clear</span>
          </button>
        )}
      </div>
    </div>
  )
}
