'use client'

/**
 * Voting record component (Phase 1 - Placeholder)
 *
 * This component will display the representative's voting record
 * once voting data is integrated in Phase 2.
 */
export default function VotingRecord() {
  // Placeholder data structure for demonstration
  const placeholderVotes = [
    {
      id: '1',
      billNumber: 'H.R. 1234',
      title: 'Infrastructure Investment Act',
      vote: 'Yes',
      date: '2025-01-15',
      result: 'Passed',
    },
    {
      id: '2',
      billNumber: 'S. 5678',
      title: 'Education Funding Bill',
      vote: 'No',
      date: '2025-01-10',
      result: 'Failed',
    },
  ]

  /**
   * Get vote badge color
   */
  function getVoteBadgeColor(vote: string): string {
    switch (vote.toLowerCase()) {
      case 'yes':
      case 'aye':
        return 'bg-green-100 text-green-800 border-green-300'
      case 'no':
      case 'nay':
        return 'bg-red-100 text-red-800 border-red-300'
      case 'present':
        return 'bg-neutral-200 text-neutral-700 border-neutral-400'
      case 'not voting':
        return 'bg-neutral-100 text-neutral-600 border-neutral-300'
      default:
        return 'bg-neutral-100 text-neutral-600 border-neutral-300'
    }
  }

  /**
   * Get result badge color
   */
  function getResultBadgeColor(result: string): string {
    return result.toLowerCase() === 'passed'
      ? 'bg-green-50 text-green-700'
      : 'bg-red-50 text-red-700'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-neutral-900">Voting Record</h2>
      </div>

      {/* Phase 1 Notice */}
      <div className="bg-primary-50 border-2 border-primary-200 rounded-lg p-6">
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
          <div>
            <h3 className="text-lg font-semibold text-primary-900 mb-2">
              Coming Soon
            </h3>
            <p className="text-primary-800 mb-3">
              Detailed voting records will be available in Phase 2. We&apos;re working on
              integrating comprehensive voting data from Congress.gov.
            </p>
            <div className="text-sm text-primary-700">
              <strong>What&apos;s coming:</strong>
              <ul className="list-disc ml-5 mt-2 space-y-1">
                <li>Complete voting history</li>
                <li>Vote explanations and statements</li>
                <li>Voting patterns and statistics</li>
                <li>Party-line vote analysis</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Example Table Structure (Desktop) */}
      <div className="hidden md:block bg-white rounded-lg border border-neutral-200 overflow-hidden">
        <table className="min-w-full divide-y divide-neutral-200">
          <thead className="bg-neutral-50">
            <tr>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-semibold text-neutral-700 uppercase tracking-wider"
              >
                Bill
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-semibold text-neutral-700 uppercase tracking-wider"
              >
                Title
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-center text-xs font-semibold text-neutral-700 uppercase tracking-wider"
              >
                Vote
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-center text-xs font-semibold text-neutral-700 uppercase tracking-wider"
              >
                Date
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-center text-xs font-semibold text-neutral-700 uppercase tracking-wider"
              >
                Result
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-neutral-200 opacity-50">
            {placeholderVotes.map((vote) => (
              <tr key={vote.id} className="hover:bg-neutral-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-primary-700">
                  {vote.billNumber}
                </td>
                <td className="px-6 py-4 text-sm text-neutral-900">
                  {vote.title}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span
                    className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border ${getVoteBadgeColor(
                      vote.vote
                    )}`}
                  >
                    {vote.vote}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-600 text-center">
                  {new Date(vote.date).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric',
                  })}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span
                    className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${getResultBadgeColor(
                      vote.result
                    )}`}
                  >
                    {vote.result}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Example Cards (Mobile) */}
      <div className="md:hidden space-y-4 opacity-50">
        {placeholderVotes.map((vote) => (
          <div
            key={vote.id}
            className="bg-white rounded-lg border border-neutral-200 p-4"
          >
            <div className="flex items-start justify-between mb-3">
              <div>
                <div className="text-sm font-semibold text-primary-700 mb-1">
                  {vote.billNumber}
                </div>
                <div className="text-sm text-neutral-900">{vote.title}</div>
              </div>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <span
                className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border ${getVoteBadgeColor(
                  vote.vote
                )}`}
              >
                {vote.vote}
              </span>
              <span
                className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${getResultBadgeColor(
                  vote.result
                )}`}
              >
                {vote.result}
              </span>
              <span className="text-xs text-neutral-600">
                {new Date(vote.date).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'short',
                  day: 'numeric',
                })}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
