'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import LiquidCard from '@/components/ui/LiquidCard'
import LiquidButton from '@/components/ui/LiquidButton'
import {
  Upload,
  MessageCircle,
  Sparkles,
  BarChart3,
  Mail,
  Clock,
  TrendingUp,
  Settings,
  ArrowLeft
} from 'lucide-react'

export default function DashboardPage() {
  const [hasUpload, setHasUpload] = useState(false)
  const [uploadId, setUploadId] = useState<string | null>(null)

  useEffect(() => {
    const storedUploadId = localStorage.getItem('current_upload_id')
    if (storedUploadId) {
      setHasUpload(true)
      setUploadId(storedUploadId)
    }
  }, [])

  const quickActions = [
    {
      href: '/upload',
      icon: Upload,
      title: 'Upload PST',
      description: 'Import another email archive',
      // Warm Terra gradient
      gradient: 'from-terra-500/10 to-terra-600/10',
      border: 'hover:border-terra-300',
      iconColor: 'text-terra-600',
      iconBg: 'bg-terra-100'
    },
    {
      href: '/chat',
      icon: MessageCircle,
      title: 'Ask My Inbox',
      description: 'Search your history with AI',
      // Cool Mineral gradient
      gradient: 'from-mineral-500/10 to-mineral-600/10',
      border: 'hover:border-mineral-300',
      iconColor: 'text-mineral-600',
      iconBg: 'bg-mineral-100'
    },
    {
      href: '/chat?mode=coach',
      icon: Sparkles,
      title: 'Coach Me',
      description: 'Get behavioral insights',
      // Gold/Sand gradient
      gradient: 'from-amber-500/10 to-amber-600/10',
      border: 'hover:border-amber-300',
      iconColor: 'text-amber-600',
      iconBg: 'bg-amber-100'
    },
  ]

  const insights = [
    { icon: Mail, label: 'Emails Indexed', value: hasUpload ? '---' : '0', color: 'text-mineral-600' },
    { icon: Clock, label: 'Avg Response', value: hasUpload ? '---' : '--', color: 'text-terra-600' },
    { icon: TrendingUp, label: 'Insights Ready', value: hasUpload ? '1' : '0', color: 'text-amber-600' },
    { icon: BarChart3, label: 'After-Hours', value: hasUpload ? '---' : '--%', color: 'text-slate-600' },
  ]

  return (
    <div className="min-h-screen">
      {/* Background handles itself via globals.css */}

      {/* Header */}
      <header className="border-b border-mineral-200/50 backdrop-blur-md bg-white/50 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/" className="text-mineral-500 hover:text-terra-600 transition-colors">
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <h1 className="text-2xl font-serif font-bold text-mineral-900">Dashboard</h1>
          </div>
          <Link href="/settings" className="p-2 rounded-lg hover:bg-mineral-100 transition-colors">
            <Settings className="w-5 h-5 text-mineral-500" />
          </Link>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-12 space-y-12">
        {/* Welcome Section */}
        <div className="space-y-4">
          <h2 className="text-4xl font-serif font-medium text-mineral-900">
            Welcome back.
          </h2>
          <p className="text-lg text-mineral-600 max-w-2xl font-light">
            {hasUpload
              ? 'Your ecosystem is active. Explore your communication patterns below.'
              : 'Upload a PST file to begin mapping your digital habits.'
            }
          </p>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {quickActions.map((action, i) => (
            <Link href={action.href} key={i}>
              <div className={`
                h-full p-8 rounded-3xl bg-white/60 backdrop-blur-md border border-white/50 
                hover:bg-white/80 transition-all duration-300 hover:scale-[1.02] hover:shadow-lg
                flex flex-col gap-6 group cursor-pointer ${action.border} border-2 border-transparent
              `}>
                <div className={`w-14 h-14 rounded-2xl ${action.iconBg} flex items-center justify-center transition-transform group-hover:scale-110`}>
                  <action.icon className={`w-7 h-7 ${action.iconColor}`} />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-mineral-900 group-hover:text-terra-700 transition-colors">
                    {action.title}
                  </h3>
                  <p className="text-mineral-500 text-sm mt-2 leading-relaxed">
                    {action.description}
                  </p>
                </div>
              </div>
            </Link>
          ))}
        </div>

        {/* Stats Overview */}
        <div className="space-y-6">
          <h3 className="text-2xl font-serif font-medium text-mineral-900">Platform Insights</h3>

          <LiquidCard className="bg-white/40 border border-white/60">
            {!hasUpload ? (
              <div className="text-center py-12">
                <div className="w-20 h-20 rounded-full bg-sand-100 flex items-center justify-center mx-auto mb-6">
                  <Upload className="w-8 h-8 text-sand-500" />
                </div>
                <h4 className="text-xl font-medium text-mineral-800 mb-2">No Data Available</h4>
                <p className="text-mineral-500 mb-8 max-w-sm mx-auto">
                  Upload a PST file to populate your personal analytics dashboard.
                </p>
                <Link href="/upload">
                  <LiquidButton>Upload PST File</LiquidButton>
                </Link>
              </div>
            ) : (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
                {insights.map((stat, i) => (
                  <div key={i} className="text-center p-6 rounded-2xl bg-white/50 border border-white/50 shadow-sm">
                    <stat.icon className={`w-8 h-8 mx-auto mb-4 ${stat.color}`} />
                    <div className="text-3xl font-bold text-mineral-900 mb-1">{stat.value}</div>
                    <div className="text-mineral-500 text-sm font-medium uppercase tracking-wider">{stat.label}</div>
                  </div>
                ))}
              </div>
            )}
          </LiquidCard>
        </div>

        {/* Coaching Tips Preview */}
        {hasUpload && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="text-2xl font-serif font-medium text-mineral-900">Coaching Seeds</h3>
              <Link href="/chat?mode=coach" className="text-terra-600 font-medium hover:text-terra-700 hover:underline">
                View all insights →
              </Link>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="p-8 rounded-3xl bg-terra-50 border border-terra-100">
                <p className="text-terra-900 text-lg font-medium mb-2">💡 Discovery Pattern</p>
                <p className="text-mineral-700 leading-relaxed">
                  "It looks like you respond to 80% of emails within 5 minutes. Consider batching your responses to reduce context switching."
                </p>
              </div>
              <div className="p-8 rounded-3xl bg-mineral-50 border border-mineral-100">
                <p className="text-mineral-900 text-lg font-medium mb-2">🎯 Suggested Goal</p>
                <p className="text-mineral-700 leading-relaxed">
                  "Try setting 'Deep Work' hours on Tuesday mornings where you don't check Outlook."
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="text-center pt-12 border-t border-mineral-200">
          <p className="text-mineral-400 text-xs font-medium uppercase tracking-widest">
            Organic Intelligence Systems &copy; {new Date().getFullYear()}
          </p>
        </div>
      </main>
    </div>
  )
}
