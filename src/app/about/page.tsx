import { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'About & Methodology | OpenUSPolitics.org',
  description:
    'Learn how OpenUSPolitics.org uses AI and open-source technology to provide non-partisan analysis of congressional legislation.',
  keywords: [
    'about',
    'methodology',
    'AI analysis',
    'non-partisan',
    'open source',
    'transparency',
  ],
}

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-neutral-50">
      {/* Hero */}
      <section className="bg-gradient-to-br from-primary-800 to-primary-900 text-white py-16">
        <div className="container">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-4xl md:text-5xl font-bold mb-6">
              About OpenUSPolitics.org
            </h1>
            <p className="text-xl text-primary-100">
              Making congressional legislation accessible to everyone through AI-powered
              analysis and radical transparency.
            </p>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <article className="container py-12">
        <div className="max-w-4xl mx-auto">
          {/* Mission Statement */}
          <section id="mission" className="mb-16">
            <h2 className="text-3xl font-bold text-neutral-900 mb-6">Our Mission</h2>
            <div className="prose prose-lg max-w-none">
              <p className="text-lg text-neutral-700 leading-relaxed mb-4">
                Congressional legislation affects every American, yet most bills are
                written in dense legal language that&apos;s nearly impossible for ordinary
                citizens to understand. OpenUSPolitics.org solves this problem by
                translating every major bill into plain English—with complete
                transparency and zero political bias.
              </p>
              <div className="bg-primary-50 border-l-4 border-primary-600 p-6 my-6">
                <p className="text-primary-900 font-semibold mb-2">
                  We believe that:
                </p>
                <ul className="space-y-2 text-primary-800">
                  <li>• Every citizen deserves to understand what Congress is doing</li>
                  <li>• Political information should be free from partisan spin</li>
                  <li>• Technology should empower, not manipulate</li>
                  <li>• Transparency builds trust in democratic institutions</li>
                </ul>
              </div>
            </div>
          </section>

          {/* How It Works */}
          <section id="how-it-works" className="mb-16">
            <h2 className="text-3xl font-bold text-neutral-900 mb-6">How It Works</h2>
            <div className="space-y-6">
              <div className="bg-white rounded-lg border border-neutral-200 p-6">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center text-2xl">
                    1️⃣
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold text-neutral-900 mb-2">
                      Data Collection
                    </h3>
                    <p className="text-neutral-700">
                      We fetch bill text directly from the official Congress.gov API
                      daily, ensuring our analysis is based on the authoritative source.
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg border border-neutral-200 p-6">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center text-2xl">
                    2️⃣
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold text-neutral-900 mb-2">
                      Document Processing
                    </h3>
                    <p className="text-neutral-700">
                      Bills are parsed, chunked into manageable sections, and converted
                      into vector embeddings for efficient retrieval.
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg border border-neutral-200 p-6">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center text-2xl">
                    3️⃣
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold text-neutral-900 mb-2">
                      AI Analysis
                    </h3>
                    <p className="text-neutral-700">
                      Claude 3.5 Sonnet analyzes the bill using carefully engineered
                      prompts designed to eliminate bias and maintain strict objectivity.
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg border border-neutral-200 p-6">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center text-2xl">
                    4️⃣
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold text-neutral-900 mb-2">
                      Traceability
                    </h3>
                    <p className="text-neutral-700">
                      Every phrase in our analysis is linked to the exact source passage,
                      making it 100% verifiable and eliminating AI hallucinations.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* Methodology */}
          <section id="methodology" className="mb-16">
            <h2 className="text-3xl font-bold text-neutral-900 mb-6">Methodology</h2>
            <div className="prose prose-lg max-w-none">
              <h3 className="text-2xl font-semibold text-neutral-900 mb-4">
                Data Source
              </h3>
              <p className="text-neutral-700 mb-6">
                All bill text comes from the official{' '}
                <a
                  href="https://api.congress.gov"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-primary-700 hover:text-primary-800 font-medium"
                >
                  Congress.gov API
                </a>
                . We do not modify, interpret, or editorialize the source text in any
                way.
              </p>

              <h3 className="text-2xl font-semibold text-neutral-900 mb-4">
                AI Model
              </h3>
              <p className="text-neutral-700 mb-6">
                We use Anthropic&apos;s Claude 3.5 Sonnet (claude-sonnet-4-5-20250929), a
                state-of-the-art language model known for its accuracy and reasoning
                capabilities. The model is instructed to act as a non-partisan
                Congressional Research Service analyst.
              </p>

              <h3 className="text-2xl font-semibold text-neutral-900 mb-4">
                RAG (Retrieval-Augmented Generation)
              </h3>
              <p className="text-neutral-700 mb-6">
                We use a hybrid RAG system combining vector similarity search
                (sentence-transformers) and BM25 keyword matching. This ensures the AI
                only analyzes text actually present in the bill, preventing
                hallucinations.
              </p>

              <h3 className="text-2xl font-semibold text-neutral-900 mb-4">
                Prompt Engineering
              </h3>
              <p className="text-neutral-700 mb-4">
                Our prompts explicitly forbid:
              </p>
              <ul className="list-disc ml-6 mb-6 space-y-2 text-neutral-700">
                <li>Political opinions or editorializing</li>
                <li>Loaded language or partisan framing</li>
                <li>Speculation beyond the bill text</li>
                <li>References to current events not in the bill</li>
                <li>Predictions about political feasibility</li>
              </ul>

              <details className="bg-neutral-100 rounded-lg p-6 mb-6">
                <summary className="cursor-pointer font-semibold text-neutral-900">
                  View Technical Stack Details
                </summary>
                <div className="mt-4 space-y-2 text-sm text-neutral-700">
                  <p>
                    <strong>Frontend:</strong> Next.js 14, React, TypeScript, Tailwind
                    CSS
                  </p>
                  <p>
                    <strong>Backend:</strong> Python 3.11, FastAPI
                  </p>
                  <p>
                    <strong>AI:</strong> Anthropic Claude API, sentence-transformers
                  </p>
                  <p>
                    <strong>Vector DB:</strong> ChromaDB with persistent storage
                  </p>
                  <p>
                    <strong>Hosting:</strong> Cloudflare Pages (frontend), Railway
                    (backend)
                  </p>
                  <p>
                    <strong>Data:</strong> Congress.gov API v3
                  </p>
                </div>
              </details>
            </div>
          </section>

          {/* Limitations */}
          <section id="limitations" className="mb-16">
            <h2 className="text-3xl font-bold text-neutral-900 mb-6">Limitations</h2>
            <div className="bg-yellow-50 border-2 border-yellow-300 rounded-lg p-6">
              <h3 className="text-xl font-semibold text-yellow-900 mb-4">
                Important Disclaimers
              </h3>
              <ul className="space-y-3 text-yellow-900">
                <li className="flex items-start gap-2">
                  <svg
                    className="w-5 h-5 mt-0.5 flex-shrink-0"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                    />
                  </svg>
                  <span>
                    <strong>Not Legal Advice:</strong> Our analysis is educational only.
                    For legal questions, consult an attorney.
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <svg
                    className="w-5 h-5 mt-0.5 flex-shrink-0"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                    />
                  </svg>
                  <span>
                    <strong>AI-Generated:</strong> While we use best practices, AI can
                    make mistakes. Always verify important details.
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <svg
                    className="w-5 h-5 mt-0.5 flex-shrink-0"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                    />
                  </svg>
                  <span>
                    <strong>Coverage:</strong> We focus on major legislation. Not all
                    bills are analyzed.
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <svg
                    className="w-5 h-5 mt-0.5 flex-shrink-0"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                    />
                  </svg>
                  <span>
                    <strong>Report Issues:</strong> Found an error?{' '}
                    <a
                      href="https://github.com/yourusername/OpenUSPolitics/issues"
                      className="underline font-semibold"
                    >
                      Please report it
                    </a>
                    .
                  </span>
                </li>
              </ul>
            </div>
          </section>

          {/* Transparency */}
          <section id="transparency" className="mb-16">
            <h2 className="text-3xl font-bold text-neutral-900 mb-6">
              Open Source & Transparency
            </h2>
            <div className="prose prose-lg max-w-none">
              <p className="text-neutral-700 mb-6">
                OpenUSPolitics.org is 100% open source. Every line of code, every
                prompt, and every analysis methodology is public and auditable.
              </p>
              <div className="grid md:grid-cols-2 gap-6 mb-6">
                <a
                  href="https://github.com/yourusername/OpenUSPolitics"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-3 p-6 bg-white border-2 border-neutral-300 rounded-lg hover:border-primary-600 transition-colors"
                >
                  <svg
                    className="w-8 h-8"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
                  </svg>
                  <div className="flex-1">
                    <div className="font-semibold text-neutral-900">
                      View Source Code
                    </div>
                    <div className="text-sm text-neutral-600">
                      Complete codebase on GitHub
                    </div>
                  </div>
                </a>
                <a
                  href="https://github.com/yourusername/OpenUSPolitics/blob/main/CONTRIBUTING.md"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-3 p-6 bg-white border-2 border-neutral-300 rounded-lg hover:border-primary-600 transition-colors"
                >
                  <svg
                    className="w-8 h-8 text-accent-600"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 4v16m8-8H4"
                    />
                  </svg>
                  <div className="flex-1">
                    <div className="font-semibold text-neutral-900">
                      Contribute
                    </div>
                    <div className="text-sm text-neutral-600">
                      Help improve the project
                    </div>
                  </div>
                </a>
              </div>
            </div>
          </section>

          {/* Privacy */}
          <section id="privacy" className="mb-16">
            <h2 className="text-3xl font-bold text-neutral-900 mb-6">Privacy</h2>
            <div className="prose prose-lg max-w-none">
              <p className="text-neutral-700 mb-4">
                We respect your privacy and don&apos;t track or collect personal data:
              </p>
              <ul className="space-y-2 text-neutral-700 mb-6">
                <li className="flex items-start gap-2">
                  <span className="text-accent-600 mt-1">✓</span>
                  <span>No cookies or tracking scripts</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-accent-600 mt-1">✓</span>
                  <span>No user accounts or login required</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-accent-600 mt-1">✓</span>
                  <span>No personal data collection</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-accent-600 mt-1">✓</span>
                  <span>Privacy-focused analytics (aggregate only)</span>
                </li>
              </ul>
            </div>
          </section>

          {/* Contact */}
          <section id="contact" className="mb-16">
            <h2 className="text-3xl font-bold text-neutral-900 mb-6">Contact</h2>
            <div className="prose prose-lg max-w-none">
              <p className="text-neutral-700 mb-6">
                Have questions, found an issue, or want to contribute?
              </p>
              <div className="space-y-4">
                <a
                  href="https://github.com/yourusername/OpenUSPolitics/issues"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-3 p-4 bg-white border border-neutral-300 rounded-lg hover:border-primary-600 transition-colors"
                >
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
                      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                    />
                  </svg>
                  <div className="flex-1">
                    <div className="font-semibold text-neutral-900">
                      Report an Issue
                    </div>
                    <div className="text-sm text-neutral-600">
                      File a bug report or content issue on GitHub
                    </div>
                  </div>
                </a>
              </div>
            </div>
          </section>

          {/* CTA */}
          <section className="bg-gradient-to-br from-primary-800 to-primary-900 rounded-2xl p-8 md:p-12 text-center text-white">
            <h2 className="text-3xl font-bold mb-4">Ready to Get Started?</h2>
            <p className="text-primary-100 text-lg mb-8">
              Browse the latest congressional bills, explained in plain English.
            </p>
            <Link href="/" className="btn-primary bg-white text-primary-800 hover:bg-primary-50">
              Browse Bills
            </Link>
          </section>
        </div>
      </article>
    </div>
  )
}
