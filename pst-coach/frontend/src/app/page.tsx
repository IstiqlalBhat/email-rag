import Link from 'next/link'

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="max-w-5xl w-full text-center">
        <h1 className="text-6xl font-bold mb-8">
          PST Coach
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-300 mb-12">
          Transform your email history into actionable insights about communication, workload, and habits
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <div className="p-6 border rounded-lg">
            <h3 className="text-lg font-semibold mb-2">Ask My Inbox</h3>
            <p className="text-sm text-gray-600">RAG-powered search over your email history with source citations</p>
          </div>
          <div className="p-6 border rounded-lg">
            <h3 className="text-lg font-semibold mb-2">Coach Me</h3>
            <p className="text-sm text-gray-600">AI insights about your communication patterns and work habits</p>
          </div>
          <div className="p-6 border rounded-lg">
            <h3 className="text-lg font-semibold mb-2">Privacy First</h3>
            <p className="text-sm text-gray-600">Redaction by default, one-click deletion, full data control</p>
          </div>
        </div>

        <div className="flex gap-4 justify-center">
          <Link
            href="/upload"
            className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
          >
            Get Started
          </Link>
          <Link
            href="/dashboard"
            className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
          >
            Dashboard
          </Link>
        </div>
      </div>
    </div>
  )
}
