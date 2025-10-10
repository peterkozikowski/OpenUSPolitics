import { Metadata } from 'next'
import { notFound } from 'next/navigation'
import { getBillData, getAllBills } from '@/lib/data'
import BillHeader from '@/components/BillHeader'
import BillTabs from '@/components/BillTabs'

interface BillPageProps {
  params: Promise<{
    id: string
  }>
}

/**
 * Generate static params for all bills at build time
 */
export async function generateStaticParams() {
  const metadata = await getAllBills()

  return metadata.bills.map((bill) => ({
    id: encodeURIComponent(bill.bill_number),
  }))
}

/**
 * Generate metadata for SEO
 */
export async function generateMetadata({
  params,
}: BillPageProps): Promise<Metadata> {
  try {
    const { id } = await params
    const bill = await getBillData(decodeURIComponent(id))

    return {
      title: `${bill.bill_number}: ${bill.title} | OpenUSPolitics.org`,
      description:
        bill.plain_english_summary.length > 160
          ? bill.plain_english_summary.slice(0, 157) + '...'
          : bill.plain_english_summary,
      keywords: [
        bill.bill_number,
        bill.sponsor.name,
        ...bill.topic,
        'congress',
        'legislation',
        'bill analysis',
      ],
      openGraph: {
        title: `${bill.bill_number}: ${bill.title}`,
        description: bill.plain_english_summary.slice(0, 200),
        type: 'article',
        publishedTime: bill.introduced_date,
        modifiedTime: bill.last_updated,
        authors: [bill.sponsor.name],
        siteName: 'OpenUSPolitics.org',
      },
      twitter: {
        card: 'summary_large_image',
        title: `${bill.bill_number}: ${bill.title}`,
        description: bill.plain_english_summary.slice(0, 200),
      },
    }
  } catch (error) {
    return {
      title: 'Bill Not Found | OpenUSPolitics.org',
      description: 'The requested bill could not be found.',
    }
  }
}

/**
 * Bill detail page
 */
export default async function BillPage({ params }: BillPageProps) {
  let bill

  try {
    const { id } = await params
    // Decode URL-encoded bill number (e.g., "H.R.%201234" -> "H.R. 1234")
    const billNumber = decodeURIComponent(id)
    bill = await getBillData(billNumber)
  } catch (error) {
    // If bill not found, show 404
    notFound()
  }

  return (
    <div className="min-h-screen bg-neutral-50">
      {/* Bill Header */}
      <BillHeader bill={bill} />

      {/* Bill Content Tabs */}
      <BillTabs bill={bill} />

      {/* AI Transparency Notice */}
      <section className="bg-neutral-100 border-t border-neutral-200 py-8">
        <div className="container">
          <div className="max-w-4xl mx-auto bg-white rounded-lg border border-neutral-300 p-6">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0">
                <svg
                  className="w-6 h-6 text-primary-700"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-neutral-900 mb-2">
                  About This Analysis
                </h3>
                <p className="text-neutral-700 mb-4">
                  This analysis was generated using AI (Claude) and is designed to
                  be strictly non-partisan. All analysis is based solely on the
                  official bill text from Congress.gov, with full traceability to
                  source documents.
                </p>
                <div className="flex flex-wrap gap-3">
                  <a
                    href="/methodology"
                    className="text-sm text-primary-700 hover:text-primary-800 font-medium"
                  >
                    Learn about our methodology →
                  </a>
                  <a
                    href={`https://github.com/yourusername/OpenUSPolitics/issues/new?title=Feedback on ${encodeURIComponent(
                      bill.bill_number
                    )}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-primary-700 hover:text-primary-800 font-medium"
                  >
                    Report an issue →
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
