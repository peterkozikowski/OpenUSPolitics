import Image from 'next/image'
import { Representative, Party, Office } from '@/lib/types'

interface RepresentativeHeaderProps {
  representative: Representative
}

/**
 * Get party color for gradients
 */
function getPartyGradient(party: Party): string {
  switch (party) {
    case Party.DEMOCRAT:
      return 'from-blue-800 to-blue-900'
    case Party.REPUBLICAN:
      return 'from-red-800 to-red-900'
    case Party.INDEPENDENT:
      return 'from-purple-800 to-purple-900'
    default:
      return 'from-neutral-800 to-neutral-900'
  }
}

/**
 * Get party badge color
 */
function getPartyBadgeColor(party: Party): string {
  switch (party) {
    case Party.DEMOCRAT:
      return 'bg-blue-100 text-blue-800 border-blue-300'
    case Party.REPUBLICAN:
      return 'bg-red-100 text-red-800 border-red-300'
    case Party.INDEPENDENT:
      return 'bg-purple-100 text-purple-800 border-purple-300'
    default:
      return 'bg-neutral-100 text-neutral-800 border-neutral-300'
  }
}

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

/**
 * Get office icon
 */
function getOfficeIcon(office: Office): string {
  return office === Office.HOUSE ? '🏛️' : '🏛️'
}

export default function RepresentativeHeader({
  representative,
}: RepresentativeHeaderProps) {
  const partyGradient = getPartyGradient(representative.party)
  const partyBadgeColor = getPartyBadgeColor(representative.party)

  return (
    <header className={`bg-gradient-to-br ${partyGradient} text-white`}>
      <div className="container py-12 md:py-16">
        <div className="flex flex-col md:flex-row items-center md:items-start gap-6 md:gap-8">
          {/* Profile Photo */}
          <div className="flex-shrink-0">
            <div className="w-32 h-32 md:w-40 md:h-40 rounded-full bg-white/20 backdrop-blur-sm border-4 border-white/30 overflow-hidden shadow-xl">
              {representative.photo_url ? (
                <Image
                  src={representative.photo_url}
                  alt={representative.name}
                  width={160}
                  height={160}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-6xl font-bold text-white/50">
                  {representative.name.charAt(0)}
                </div>
              )}
            </div>
          </div>

          {/* Info */}
          <div className="flex-1 text-center md:text-left">
            {/* Name */}
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              {representative.name}
            </h1>

            {/* Party, State, District */}
            <div className="flex flex-wrap items-center justify-center md:justify-start gap-3 mb-4">
              <span
                className={`inline-flex items-center px-4 py-2 rounded-lg text-sm font-semibold border-2 ${partyBadgeColor}`}
              >
                {getPartyName(representative.party)}
              </span>

              <span className="text-lg text-white/90">
                {representative.state}
                {representative.district !== null && ` - District ${representative.district}`}
              </span>
            </div>

            {/* Office */}
            <div className="flex items-center justify-center md:justify-start gap-2 text-lg mb-6">
              <span className="text-2xl" aria-hidden="true">
                {getOfficeIcon(representative.office)}
              </span>
              <span className="text-white/90">
                {representative.office === Office.HOUSE
                  ? 'U.S. House of Representatives'
                  : 'U.S. Senate'}
              </span>
            </div>

            {/* External Link */}
            <a
              href={representative.congress_gov_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-white text-primary-800 rounded-lg font-semibold hover:bg-white/90 transition-colors focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-2 focus:ring-offset-blue-800"
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
                  d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                />
              </svg>
              View on Congress.gov
            </a>
          </div>
        </div>
      </div>
    </header>
  )
}
