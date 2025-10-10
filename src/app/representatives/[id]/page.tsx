import { Metadata } from 'next'
import { notFound } from 'next/navigation'
import { getAllBills, getBillData } from '@/lib/data'
import { Party, Office } from '@/lib/types'
import RepresentativeHeader from '@/components/RepresentativeHeader'
import SponsoredBills from '@/components/SponsoredBills'
import VotingRecord from '@/components/VotingRecord'

interface RepresentativePageProps {
  params: Promise<{
    id: string
  }>
}

/**
 * Generate metadata for SEO
 */
export async function generateMetadata({
  params,
}: RepresentativePageProps): Promise<Metadata> {
  try {
    const { id } = await params
    const metadata = await getAllBills()

    // Find bills by this representative (match by id)
    const sponsoredBills = metadata.bills.filter((bill) => {
      return bill.sponsor_name.toLowerCase().includes(id.toLowerCase())
    })

    if (sponsoredBills.length > 0) {
      // Get full bill data to access sponsor info
      const firstBill = await getBillData(sponsoredBills[0]!.bill_number)
      const rep = firstBill.sponsor

      return {
        title: `${rep.name} - Representative Profile | OpenUSPolitics.org`,
        description: `View ${rep.name}'s sponsored legislation and legislative activity in the ${rep.office}.`,
        keywords: [
          rep.name,
          rep.state,
          rep.office,
          'representative',
          'congress',
          'legislation',
        ],
      }
    }

    return {
      title: 'Representative Not Found | OpenUSPolitics.org',
      description: 'Representative profile not found.',
    }
  } catch (error) {
    return {
      title: 'Representative Not Found | OpenUSPolitics.org',
      description: 'Representative profile not found.',
    }
  }
}

/**
 * Representative profile page
 */
export default async function RepresentativePage({
  params,
}: RepresentativePageProps) {
  try {
    const { id } = await params
    const metadata = await getAllBills()

    // Find bills sponsored by this representative
    // Note: In production, we'd use bioguide_id or a more robust matching system
    const sponsoredBills = metadata.bills.filter((bill) => {
      return bill.sponsor_name.toLowerCase().includes(id.toLowerCase())
    })

    if (sponsoredBills.length === 0) {
      notFound()
    }

    // Get representative info from first sponsored bill
    const firstBill = await getBillData(sponsoredBills[0]!.bill_number)
    const representative = firstBill.sponsor

    /**
     * Get party full name
     */
    function getPartyName(party: Party): string {
      switch (party) {
        case Party.DEMOCRAT:
          return 'Democrat'
        case Party.REPUBLICAN:
          return 'Republican'
        case Party.INDEPENDENT:
          return 'Independent'
        default:
          return party
      }
    }

    return (
      <div className="min-h-screen bg-neutral-50">
        {/* Representative Header */}
        <RepresentativeHeader representative={representative} />

        {/* Main Content */}
        <div className="container py-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Main content */}
            <div className="lg:col-span-2 space-y-8">
              <SponsoredBills bills={sponsoredBills} />
              <VotingRecord />
            </div>

            {/* Sidebar */}
            <div className="lg:col-span-1">
              <div className="sticky top-8 space-y-6">
                {/* Quick Facts */}
                <div className="bg-white rounded-lg border border-neutral-200 p-6">
                  <h3 className="text-lg font-semibold text-neutral-900 mb-4">
                    Quick Facts
                  </h3>
                  <dl className="space-y-4">
                    <div>
                      <dt className="text-sm text-neutral-600 mb-1">Party</dt>
                      <dd className="text-sm font-semibold text-neutral-900">
                        {getPartyName(representative.party)}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm text-neutral-600 mb-1">State</dt>
                      <dd className="text-sm font-semibold text-neutral-900">
                        {representative.state}
                      </dd>
                    </div>
                    {representative.district !== null && (
                      <div>
                        <dt className="text-sm text-neutral-600 mb-1">District</dt>
                        <dd className="text-sm font-semibold text-neutral-900">
                          {representative.district}
                        </dd>
                      </div>
                    )}
                    <div>
                      <dt className="text-sm text-neutral-600 mb-1">Office</dt>
                      <dd className="text-sm font-semibold text-neutral-900">
                        {representative.office === Office.HOUSE
                          ? 'House of Representatives'
                          : 'Senate'}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm text-neutral-600 mb-1">
                        Bills Sponsored
                      </dt>
                      <dd className="text-sm font-semibold text-neutral-900">
                        {sponsoredBills.length}
                      </dd>
                    </div>
                  </dl>
                </div>

                {/* External Links */}
                <div className="bg-white rounded-lg border border-neutral-200 p-6">
                  <h3 className="text-lg font-semibold text-neutral-900 mb-4">
                    External Links
                  </h3>
                  <div className="space-y-3">
                    <a
                      href={representative.congress_gov_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 text-sm text-primary-700 hover:text-primary-800"
                    >
                      <svg
                        className="w-4 h-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                        />
                      </svg>
                      Congress.gov Profile
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  } catch (error) {
    notFound()
  }
}
