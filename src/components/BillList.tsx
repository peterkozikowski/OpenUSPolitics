'use client'

import { useState, useEffect, useMemo } from 'react'
import { useSearchParams } from 'next/navigation'
import { Bill, BillStatus, BillTopic } from '@/lib/types'
import BillCard from './BillCard'

interface BillListProps {
  bills: Bill[]
}

export default function BillList({ bills }: BillListProps) {
  const searchParams = useSearchParams()
  const [currentPage, setCurrentPage] = useState(0)
  const ITEMS_PER_PAGE = 20

  // Reset page when filters change
  useEffect(() => {
    setCurrentPage(0)
  }, [searchParams])

  // Filter and sort bills
  const filteredBills = useMemo(() => {
    let result = [...bills]

    // Apply status filter
    const statusFilter = searchParams.get('status') as BillStatus | null
    if (statusFilter) {
      result = result.filter((bill) => bill.status === statusFilter)
    }

    // Apply topic filter
    const topicFilter = searchParams.get('topic') as BillTopic | null
    if (topicFilter) {
      result = result.filter((bill) => bill.topic.includes(topicFilter))
    }

    // Apply search filter
    const searchQuery = searchParams.get('search')
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      result = result.filter(
        (bill) =>
          bill.title.toLowerCase().includes(query) ||
          bill.bill_number.toLowerCase().includes(query) ||
          bill.plain_english_summary.toLowerCase().includes(query)
      )
    }

    // Apply sorting
    const sortBy = searchParams.get('sortBy') || 'date'
    const sortOrder = searchParams.get('sortOrder') || 'desc'

    result.sort((a, b) => {
      let comparison = 0

      switch (sortBy) {
        case 'title':
          comparison = a.title.localeCompare(b.title)
          break
        case 'status':
          comparison = a.status.localeCompare(b.status)
          break
        case 'date':
        default:
          comparison =
            new Date(a.introduced_date).getTime() -
            new Date(b.introduced_date).getTime()
          break
      }

      return sortOrder === 'asc' ? comparison : -comparison
    })

    return result
  }, [bills, searchParams])

  // Pagination
  const totalPages = Math.ceil(filteredBills.length / ITEMS_PER_PAGE)
  const offset = currentPage * ITEMS_PER_PAGE
  const paginatedBills = filteredBills.slice(offset, offset + ITEMS_PER_PAGE)
  const hasMore = currentPage < totalPages - 1
  const hasPrevious = currentPage > 0

  const billSummaries = paginatedBills.map((bill) => ({
    bill_number: bill.bill_number,
    title: bill.title,
    status: bill.status,
    topic: bill.topic,
    introduced_date: bill.introduced_date,
    sponsor_name: bill.sponsor.name,
    sponsor_party: bill.sponsor.party,
  }))

  const handlePrevious = () => {
    setCurrentPage((prev) => Math.max(0, prev - 1))
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const handleNext = () => {
    setCurrentPage((prev) => Math.min(totalPages - 1, prev + 1))
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <>
      {/* Results Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <div>
          <h2 className="text-2xl font-bold text-neutral-900">
            {searchParams.get('search') ? 'Search Results' : 'Recent Bills'}
          </h2>
          <p className="text-neutral-600 mt-1">
            {filteredBills.length === 0 ? (
              'No bills found'
            ) : (
              <>
                Showing {offset + 1}-
                {Math.min(offset + ITEMS_PER_PAGE, filteredBills.length)} of{' '}
                {filteredBills.length}{' '}
                {filteredBills.length === 1 ? 'bill' : 'bills'}
              </>
            )}
          </p>
        </div>

        {searchParams.get('search') && (
          <div className="text-sm text-neutral-600">
            Searching for: <strong>{searchParams.get('search')}</strong>
          </div>
        )}
      </div>

      {/* Bill Grid */}
      {billSummaries.length === 0 ? (
        <div className="text-center py-16">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-neutral-100 rounded-full mb-4">
            <svg
              className="w-8 h-8 text-neutral-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-neutral-900 mb-2">
            No bills found
          </h3>
          <p className="text-neutral-600 mb-6">
            Try adjusting your filters or search terms
          </p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {billSummaries.map((bill) => (
              <BillCard key={bill.bill_number} bill={bill} />
            ))}
          </div>

          {/* Pagination */}
          {(hasPrevious || hasMore) && (
            <div className="mt-12 flex justify-center gap-4">
              {hasPrevious && (
                <button
                  onClick={handlePrevious}
                  className="btn-secondary"
                  aria-label="Previous page"
                >
                  ← Previous
                </button>
              )}

              {hasMore && (
                <button
                  onClick={handleNext}
                  className="btn-primary"
                  aria-label="Next page"
                >
                  Next →
                </button>
              )}
            </div>
          )}
        </>
      )}
    </>
  )
}
