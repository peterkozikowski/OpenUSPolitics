import { Metadata } from 'next'
import Link from 'next/link'

/**
 * Bills index page
 *
 * This page uses client-side redirect to the home page since all bill
 * browsing and filtering happens on the homepage. Individual bills are
 * accessible at /bills/[id].
 */

export const metadata: Metadata = {
  title: 'Bills | OpenUSPolitics.org',
  description: 'Browse all congressional bills analyzed by OpenUSPolitics.org',
}

export default function BillsIndexPage() {
  return (
    <div className="min-h-screen bg-neutral-50 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-neutral-900 mb-4">
          Redirecting to Bills...
        </h1>
        <p className="text-neutral-600">
          If you are not redirected, <Link href="/" className="text-primary-700 underline">click here</Link>.
        </p>
      </div>
      <script
        dangerouslySetInnerHTML={{
          __html: `window.location.replace('/')`,
        }}
      />
    </div>
  )
}
