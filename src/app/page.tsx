import { filterBills } from '@/lib/data'
import { BillStatus, BillTopic } from '@/lib/types'
import BillCard from '@/components/BillCard'
import BillFilters from '@/components/BillFilters'
import SearchBar from '@/components/SearchBar'

interface HomePageProps {
  searchParams: Promise<{
    status?: string
    topic?: string
    search?: string
    sortBy?: string
    sortOrder?: string
    offset?: string
  }>
}

export default async function HomePage({ searchParams }: HomePageProps) {
  const params = await searchParams
  // Parse filters from URL params
  const filters = {
    status: params.status as BillStatus | undefined,
    topic: params.topic as BillTopic | undefined,
    search: params.search,
    sortBy: (params.sortBy as 'date' | 'title' | 'status') || 'date',
    sortOrder: (params.sortOrder as 'asc' | 'desc') || 'desc',
    limit: 20,
    offset: parseInt(params.offset || '0', 10),
  }

  // Fetch filtered bills
  const { bills, total, hasMore, offset } = await filterBills(filters)

  // Extract summaries for display
  const billSummaries = bills.map((bill) => ({
    bill_number: bill.bill_number,
    title: bill.title,
    status: bill.status,
    topic: bill.topic,
    introduced_date: bill.introduced_date,
    sponsor_name: bill.sponsor.name,
    sponsor_party: bill.sponsor.party,
  }))

  return (
    <div className="min-h-screen bg-neutral-50">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-primary-800 to-primary-900 text-white py-16 md:py-24">
        <div className="container">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6 text-balance">
              Congress in Plain English
            </h1>
            <p className="text-xl md:text-2xl text-primary-100 mb-8 text-balance">
              Every major bill explained without partisan spin or legalese.
              Updated daily with AI-powered analysis.
            </p>

            {/* Search Bar */}
            <div className="max-w-2xl mx-auto">
              <SearchBar />
            </div>

            {/* Stats */}
            <div className="mt-12 flex flex-wrap justify-center gap-8 text-center">
              <div>
                <div className="text-3xl md:text-4xl font-bold text-white">
                  {total}
                </div>
                <div className="text-sm text-primary-200 mt-1">
                  Bills Analyzed
                </div>
              </div>
              <div>
                <div className="text-3xl md:text-4xl font-bold text-white">
                  100%
                </div>
                <div className="text-sm text-primary-200 mt-1">
                  Non-Partisan
                </div>
              </div>
              <div>
                <div className="text-3xl md:text-4xl font-bold text-white">
                  Free
                </div>
                <div className="text-sm text-primary-200 mt-1">
                  & Open Source
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <section className="container py-8 md:py-12">
        {/* Filters */}
        <div className="mb-8">
          <BillFilters />
        </div>

        {/* Results Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div>
            <h2 className="text-2xl font-bold text-neutral-900">
              {params.search ? 'Search Results' : 'Recent Bills'}
            </h2>
            <p className="text-neutral-600 mt-1">
              {total === 0 ? (
                'No bills found'
              ) : (
                <>
                  Showing {offset + 1}-{Math.min(offset + 20, total)} of {total}{' '}
                  {total === 1 ? 'bill' : 'bills'}
                </>
              )}
            </p>
          </div>

          {params.search && (
            <div className="text-sm text-neutral-600">
              Searching for: <strong>{params.search}</strong>
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
            {(offset > 0 || hasMore) && (
              <div className="mt-12 flex justify-center gap-4">
                {offset > 0 && (
                  <a
                    href={`?${new URLSearchParams({
                      ...params,
                      offset: String(Math.max(0, offset - 20)),
                    }).toString()}`}
                    className="btn-secondary"
                  >
                    ← Previous
                  </a>
                )}

                {hasMore && (
                  <a
                    href={`?${new URLSearchParams({
                      ...params,
                      offset: String(offset + 20),
                    }).toString()}`}
                    className="btn-primary"
                  >
                    Next →
                  </a>
                )}
              </div>
            )}
          </>
        )}
      </section>

      {/* Value Proposition */}
      <section className="bg-white border-t border-neutral-200 py-16">
        <div className="container">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl font-bold text-center text-neutral-900 mb-12">
              Why OpenUSPolitics.org?
            </h2>

            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-12 h-12 bg-primary-100 rounded-lg mb-4">
                  <svg
                    className="w-6 h-6 text-primary-800"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-neutral-900 mb-2">
                  100% Non-Partisan
                </h3>
                <p className="text-neutral-600">
                  Strictly objective analysis with no political bias or editorial spin
                </p>
              </div>

              <div className="text-center">
                <div className="inline-flex items-center justify-center w-12 h-12 bg-accent-100 rounded-lg mb-4">
                  <svg
                    className="w-6 h-6 text-accent-800"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M13 10V3L4 14h7v7l9-11h-7z"
                    />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-neutral-900 mb-2">
                  AI-Powered Analysis
                </h3>
                <p className="text-neutral-600">
                  Advanced AI translates complex legislation into plain English
                </p>
              </div>

              <div className="text-center">
                <div className="inline-flex items-center justify-center w-12 h-12 bg-neutral-100 rounded-lg mb-4">
                  <svg
                    className="w-6 h-6 text-neutral-800"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"
                    />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-neutral-900 mb-2">
                  Fully Transparent
                </h3>
                <p className="text-neutral-600">
                  Open source code and full traceability to original bill text
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
