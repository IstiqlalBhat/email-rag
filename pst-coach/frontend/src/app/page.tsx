import Link from 'next/link'
import LiquidCard from '@/components/ui/LiquidCard'
import LiquidButton from '@/components/ui/LiquidButton'
import dynamic from 'next/dynamic'

const BackgroundScene = dynamic(() => import('@/components/scene/BackgroundScene'), { ssr: false })

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-6 lg:p-24 relative overflow-hidden">
      <BackgroundScene />

      {/* Main Container - Z-index ensure it sits above shader */}
      <div className="relative z-10 w-full max-w-7xl flex flex-col items-center gap-16 md:gap-24">

        {/* Header - Centered & Authoritative */}
        <header className="text-center space-y-6 max-w-4xl mx-auto">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-terra-100 border border-terra-200 text-terra-900 mb-6">
            <span className="w-2 h-2 rounded-full bg-terra-500 animate-pulse"></span>
            <span className="text-xs font-bold tracking-widest uppercase">Email Intelligence</span>
          </div>

          <h1 className="text-7xl md:text-9xl display-text leading-[0.9]">
            PST <span className="text-terra-600 italic">Coach</span>
          </h1>

          <p className="text-xl md:text-2xl text-mineral-600 dark:text-mineral-300 font-light leading-relaxed max-w-2xl mx-auto">
            Discover the hidden patterns in your communication.
            <br className="hidden md:block" />
            Turn raw data into <span className="font-medium text-terra-600">organic wisdom</span>.
          </p>
        </header>

        {/* Feature Grid - Rigorous Alignment */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 w-full max-w-6xl px-4">

          {/* Card 1 */}
          <LiquidCard className="bg-white/70 dark:bg-mineral-900/40 relative group overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-terra-200/50 rounded-full blur-3xl -mr-10 -mt-10 transition-all group-hover:bg-terra-300/60"></div>
            <div className="relative z-10 space-y-4">
              <div className="w-14 h-14 rounded-2xl bg-terra-100 text-terra-700 flex items-center justify-center text-2xl shadow-sm">
                🔍
              </div>
              <h3 className="text-2xl font-serif font-bold text-mineral-900 dark:text-white">Ask My Inbox</h3>
              <p className="text-mineral-600 dark:text-mineral-300 leading-relaxed">
                Retrieve memories instantly with RAG-powered semantic search. It's not just a keyword match; it's true understanding.
              </p>
            </div>
          </LiquidCard>

          {/* Card 2 - Elevated */}
          <LiquidCard className="bg-white/80 dark:bg-mineral-900/50 md:-translate-y-4 shadow-xl border-terra-200/50 relative group overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-terra-400 to-terra-600"></div>
            <div className="relative z-10 space-y-4">
              <div className="w-14 h-14 rounded-2xl bg-mineral-100 text-mineral-700 flex items-center justify-center text-2xl shadow-sm">
                📈
              </div>
              <h3 className="text-2xl font-serif font-bold text-mineral-900 dark:text-white">Coach Me</h3>
              <p className="text-mineral-600 dark:text-mineral-300 leading-relaxed">
                Gain deep insights into your work habits. Identify burnout risks and communication bottlenecks before they happen.
              </p>
            </div>
          </LiquidCard>

          {/* Card 3 */}
          <LiquidCard className="bg-white/70 dark:bg-mineral-900/40 relative group overflow-hidden">
            <div className="absolute bottom-0 right-0 w-32 h-32 bg-mineral-200/50 rounded-full blur-3xl -mr-10 -mb-10 transition-all group-hover:bg-mineral-300/60"></div>
            <div className="relative z-10 space-y-4">
              <div className="w-14 h-14 rounded-2xl bg-sand-200 text-mineral-700 flex items-center justify-center text-2xl shadow-sm">
                🛡️
              </div>
              <h3 className="text-2xl font-serif font-bold text-mineral-900 dark:text-white">Privacy First</h3>
              <p className="text-mineral-600 dark:text-mineral-300 leading-relaxed">
                Your data never leaves your control. Built with local-first principles and automatic redaction for total peace of mind.
              </p>
            </div>
          </LiquidCard>
        </div>

        {/* Actions - Clear & High Contrast */}
        <div className="flex flex-col sm:flex-row gap-6 mt-8">
          <Link href="/upload">
            <LiquidButton variant="default">
              Begin Analysis
            </LiquidButton>
          </Link>
          <Link href="/dashboard">
            <LiquidButton variant="outline">
              View Dashboard
            </LiquidButton>
          </Link>
        </div>

      </div>

      <footer className="absolute bottom-6 w-full text-center text-mineral-400 text-xs font-medium tracking-widest uppercase">
        Organic Intelligence Systems &copy; {new Date().getFullYear()}
      </footer>
    </main>
  )
}
