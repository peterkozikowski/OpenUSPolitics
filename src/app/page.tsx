import { Suspense } from 'react'
import { getAllBillsFull } from '@/lib/data'
import BillFilters from '@/components/BillFilters'
import SearchBar from '@/components/SearchBar'
import BillList from '@/components/BillList'

export default async function HomePage() {
  // Fetch all bills at build time for static export
  const bills = await getAllBillsFull()

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
              <Suspense fallback={<div className="h-16 bg-white/10 rounded-xl animate-pulse" />}>
                <SearchBar />
              </Suspense>
            </div>

            {/* Stats */}
            <div className="mt-12 flex flex-wrap justify-center gap-8 text-center">
              <div>
                <div className="text-3xl md:text-4xl font-bold text-white">
                  {bills.length}
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
          <Suspense fallback={<div className="h-20 bg-white rounded-xl border border-neutral-200 animate-pulse" />}>
            <BillFilters />
          </Suspense>
        </div>

        {/* Bill List with client-side filtering */}
        <Suspense fallback={<div className="h-96 bg-white rounded-xl border border-neutral-200 animate-pulse" />}>
          <BillList bills={bills} />
        </Suspense>
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
