import { BillStatus } from '@/lib/types'

interface StatusTimelineProps {
  status: BillStatus
  introducedDate: string
  lastUpdated: string
}

interface TimelineStep {
  id: string
  label: string
  icon: string
  status: 'completed' | 'current' | 'upcoming'
  date?: string
}

/**
 * Get timeline steps based on current bill status
 */
function getTimelineSteps(
  status: BillStatus,
  introducedDate: string,
  lastUpdated: string
): TimelineStep[] {
  const statusOrder = [
    BillStatus.INTRODUCED,
    BillStatus.IN_COMMITTEE,
    BillStatus.PASSED_HOUSE,
    BillStatus.PASSED_SENATE,
    BillStatus.SIGNED,
  ]

  const statusLabels: Record<BillStatus, string> = {
    [BillStatus.INTRODUCED]: 'Introduced',
    [BillStatus.IN_COMMITTEE]: 'In Committee',
    [BillStatus.PASSED_HOUSE]: 'Passed House',
    [BillStatus.PASSED_SENATE]: 'Passed Senate',
    [BillStatus.SIGNED]: 'Signed into Law',
    [BillStatus.VETOED]: 'Vetoed',
    [BillStatus.FAILED]: 'Failed',
  }

  const statusIcons: Record<BillStatus, string> = {
    [BillStatus.INTRODUCED]: '📝',
    [BillStatus.IN_COMMITTEE]: '🏛️',
    [BillStatus.PASSED_HOUSE]: '🗳️',
    [BillStatus.PASSED_SENATE]: '✅',
    [BillStatus.SIGNED]: '📜',
    [BillStatus.VETOED]: '❌',
    [BillStatus.FAILED]: '❌',
  }

  // Handle special cases (vetoed/failed)
  if (status === BillStatus.VETOED || status === BillStatus.FAILED) {
    return [
      {
        id: BillStatus.INTRODUCED,
        label: statusLabels[BillStatus.INTRODUCED],
        icon: statusIcons[BillStatus.INTRODUCED],
        status: 'completed',
        date: introducedDate,
      },
      {
        id: status,
        label: statusLabels[status],
        icon: statusIcons[status],
        status: 'current',
        date: lastUpdated,
      },
    ]
  }

  // Build normal timeline
  const currentIndex = statusOrder.indexOf(status)

  return statusOrder.map((step, index) => ({
    id: step,
    label: statusLabels[step],
    icon: statusIcons[step],
    status:
      index < currentIndex
        ? 'completed'
        : index === currentIndex
        ? 'current'
        : 'upcoming',
    date:
      index === 0
        ? introducedDate
        : index === currentIndex
        ? lastUpdated
        : undefined,
  })) as TimelineStep[]
}

/**
 * Format date to readable string
 */
function formatDate(isoDate: string): string {
  const date = new Date(isoDate)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

export default function StatusTimeline({
  status,
  introducedDate,
  lastUpdated,
}: StatusTimelineProps) {
  const steps = getTimelineSteps(status, introducedDate, lastUpdated)

  return (
    <div className="relative">
      <div className="space-y-8">
        {steps.map((step, index) => {
          const isLast = index === steps.length - 1
          const statusColors = {
            completed: 'bg-primary-600 border-primary-600 text-white',
            current: 'bg-accent-600 border-accent-600 text-white',
            upcoming: 'bg-neutral-200 border-neutral-300 text-neutral-500',
          }

          const lineColors = {
            completed: 'bg-primary-600',
            current: 'bg-accent-600',
            upcoming: 'bg-neutral-300',
          }

          return (
            <div key={step.id} className="relative flex gap-4">
              {/* Icon column */}
              <div className="relative flex flex-col items-center">
                {/* Icon circle */}
                <div
                  className={`relative z-10 flex items-center justify-center w-12 h-12 rounded-full border-2 ${statusColors[step.status]} transition-all duration-300`}
                >
                  {step.status === 'completed' ? (
                    <svg
                      className="w-6 h-6"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={3}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                  ) : step.status === 'current' ? (
                    <div className="w-3 h-3 bg-white rounded-full animate-pulse" />
                  ) : (
                    <div className="w-3 h-3 bg-neutral-400 rounded-full" />
                  )}
                </div>

                {/* Connecting line */}
                {!isLast && (
                  <div
                    className={`absolute top-12 w-0.5 h-full ${
                      lineColors[
                        step.status === 'upcoming' ? 'upcoming' : 'completed'
                      ]
                    }`}
                  />
                )}
              </div>

              {/* Content column */}
              <div className="flex-1 pb-8">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h3
                      className={`text-lg font-semibold ${
                        step.status === 'upcoming'
                          ? 'text-neutral-500'
                          : 'text-neutral-900'
                      }`}
                    >
                      {step.icon} {step.label}
                    </h3>
                    {step.date && (
                      <p className="text-sm text-neutral-600 mt-1">
                        {formatDate(step.date)}
                      </p>
                    )}
                    {step.status === 'current' && (
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 mt-2 bg-accent-100 text-accent-800 rounded-full text-xs font-medium">
                        <span className="w-2 h-2 bg-accent-600 rounded-full animate-pulse" />
                        Current Status
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Legend */}
      <div className="mt-8 pt-6 border-t border-neutral-200">
        <h4 className="text-sm font-semibold text-neutral-700 uppercase tracking-wide mb-3">
          Status Legend
        </h4>
        <div className="flex flex-wrap gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-primary-600 rounded-full" />
            <span className="text-neutral-600">Completed</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-accent-600 rounded-full" />
            <span className="text-neutral-600">Current</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-neutral-300 rounded-full" />
            <span className="text-neutral-600">Upcoming</span>
          </div>
        </div>
      </div>
    </div>
  )
}
