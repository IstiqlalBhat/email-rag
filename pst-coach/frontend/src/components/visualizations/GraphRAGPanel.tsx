'use client'

import { useState, useEffect, useCallback } from 'react'
import api from '@/lib/api'
import {
  Loader2,
  Network,
  Play,
  AlertCircle,
  CheckCircle2,
  ChevronDown,
  ChevronUp
} from 'lucide-react'

interface GraphStats {
  node_count: number
  edge_count: number
  average_degree: number
  max_degree: number
  min_degree: number
  unique_concepts: number
  top_concepts: { concept: string; count: number }[]
}

interface GraphRAGPanelProps {
  uploadId: string
  onQueryClick?: (query: string) => void
}

export default function GraphRAGPanel({ uploadId, onQueryClick }: GraphRAGPanelProps) {
  const [buildStatus, setBuildStatus] = useState<string>('loading')
  const [progress, setProgress] = useState<number>(0)
  const [nodeCount, setNodeCount] = useState<number>(0)
  const [edgeCount, setEdgeCount] = useState<number>(0)
  const [error, setError] = useState<string | null>(null)
  const [stats, setStats] = useState<GraphStats | null>(null)
  const [isBuilding, setIsBuilding] = useState(false)
  const [showStats, setShowStats] = useState(true)
  const [isInitialLoad, setIsInitialLoad] = useState(true)

  // Check build status on mount and periodically while building
  const checkStatus = useCallback(async () => {
    try {
      const response = await api.get(`/api/graph/status/${uploadId}`)
      const data = response.data
      setBuildStatus(data.status)
      setProgress(data.progress)
      setNodeCount(data.node_count)
      setEdgeCount(data.edge_count)
      setError(data.error)
      setIsInitialLoad(false)

      if (data.status === 'ready') {
        setIsBuilding(false)
        // Fetch stats
        fetchStats()
      } else if (data.status === 'building') {
        setIsBuilding(true)
      } else if (data.status === 'error') {
        setIsBuilding(false)
      }
    } catch (err) {
      console.error('Failed to check graph status:', err)
      setIsInitialLoad(false)
      setError('Cannot connect to backend. Please ensure the server is running.')
      setBuildStatus('error')
    }
  }, [uploadId])

  const fetchStats = async () => {
    try {
      const response = await api.get(`/api/graph/stats/${uploadId}`)
      if (response.data.stats) {
        setStats(response.data.stats)
      }
    } catch (err) {
      console.error('Failed to fetch graph stats:', err)
    }
  }

  useEffect(() => {
    checkStatus()
  }, [checkStatus])

  // Poll while building
  useEffect(() => {
    if (!isBuilding) return

    const interval = setInterval(checkStatus, 3000)
    return () => clearInterval(interval)
  }, [isBuilding, checkStatus])

  const handleBuild = async () => {
    setIsBuilding(true)
    setError(null)
    setBuildStatus('building')
    setProgress(0)

    try {
      await api.post('/api/graph/build', { upload_id: uploadId })
      // Start polling
      checkStatus()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to start build')
      setIsBuilding(false)
      setBuildStatus('error')
    }
  }

  const suggestedQueries = [
    'What are the main topics discussed in my emails?',
    'Who are my most frequent contacts?',
    'Find conversations about project deadlines',
    'Analyze my communication patterns'
  ]

  // Show loading during initial check
  if (isInitialLoad) {
    return (
      <div className="space-y-6">
        <div className="bg-white/60 rounded-2xl p-6 border border-white/80 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-mineral-100">
              <Loader2 className="w-5 h-5 text-mineral-600 animate-spin" />
            </div>
            <div>
              <h3 className="font-semibold text-mineral-900">Knowledge Graph</h3>
              <p className="text-sm text-mineral-500">Checking status...</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Build Status Card */}
      <div className="bg-white/60 rounded-2xl p-6 border border-white/80 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg ${
              buildStatus === 'ready' ? 'bg-green-100' :
              buildStatus === 'building' ? 'bg-amber-100' :
              buildStatus === 'error' ? 'bg-red-100' :
              'bg-mineral-100'
            }`}>
              {buildStatus === 'building' ? (
                <Loader2 className="w-5 h-5 text-amber-600 animate-spin" />
              ) : (
                <Network className={`w-5 h-5 ${
                  buildStatus === 'ready' ? 'text-green-600' :
                  buildStatus === 'error' ? 'text-red-600' :
                  'text-mineral-600'
                }`} />
              )}
            </div>
            <div>
              <h3 className="font-semibold text-mineral-900">Knowledge Graph</h3>
              <p className="text-sm text-mineral-500">
                {buildStatus === 'ready' ? 'Ready for queries' :
                 buildStatus === 'building' ? 'Building graph...' :
                 buildStatus === 'error' ? 'Build failed' :
                 'Not built yet'}
              </p>
            </div>
          </div>

          {buildStatus === 'ready' && (
            <CheckCircle2 className="w-6 h-6 text-green-500" />
          )}
          {buildStatus === 'error' && (
            <AlertCircle className="w-6 h-6 text-red-500" />
          )}
        </div>

        {/* Progress bar when building */}
        {buildStatus === 'building' && (
          <div className="space-y-2">
            <div className="h-2 bg-mineral-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-amber-500 transition-all duration-500"
                style={{ width: `${progress * 100}%` }}
              />
            </div>
            <p className="text-xs text-mineral-500 text-center">
              {Math.round(progress * 100)}% complete - This may take several minutes for large datasets
            </p>
          </div>
        )}

        {/* Node/Edge counts */}
        {(nodeCount > 0 || edgeCount > 0) && (
          <div className="flex gap-6 mt-4 pt-4 border-t border-mineral-100">
            <div className="text-center">
              <p className="text-2xl font-bold text-mineral-900">{nodeCount.toLocaleString()}</p>
              <p className="text-xs text-mineral-500">Nodes</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-mineral-900">{edgeCount.toLocaleString()}</p>
              <p className="text-xs text-mineral-500">Edges</p>
            </div>
          </div>
        )}

        {/* Error message */}
        {error && (
          <div className="mt-4 p-3 bg-red-50 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        {/* Build button - Only shown when graph is NOT built yet */}
        {buildStatus === 'pending' && !isBuilding && (
          <button
            onClick={handleBuild}
            className="mt-4 w-full py-3 px-4 bg-terra-600 hover:bg-terra-500 text-white rounded-xl font-medium flex items-center justify-center gap-2 transition-colors"
          >
            <Play className="w-4 h-4" />
            Build Knowledge Graph
          </button>
        )}
      </div>

      {/* Stats Card */}
      {stats && (
        <div className="bg-white/60 rounded-2xl border border-white/80 shadow-sm overflow-hidden">
          <button
            onClick={() => setShowStats(!showStats)}
            className="w-full p-4 flex items-center justify-between hover:bg-white/40 transition-colors"
          >
            <h3 className="font-semibold text-mineral-900">Graph Statistics</h3>
            {showStats ? (
              <ChevronUp className="w-5 h-5 text-mineral-400" />
            ) : (
              <ChevronDown className="w-5 h-5 text-mineral-400" />
            )}
          </button>

          {showStats && (
            <div className="px-4 pb-4 space-y-4">
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center p-3 bg-mineral-50 rounded-lg">
                  <p className="text-lg font-bold text-mineral-900">{stats.average_degree.toFixed(1)}</p>
                  <p className="text-xs text-mineral-500">Avg Degree</p>
                </div>
                <div className="text-center p-3 bg-mineral-50 rounded-lg">
                  <p className="text-lg font-bold text-mineral-900">{stats.max_degree}</p>
                  <p className="text-xs text-mineral-500">Max Degree</p>
                </div>
                <div className="text-center p-3 bg-mineral-50 rounded-lg">
                  <p className="text-lg font-bold text-mineral-900">{stats.unique_concepts}</p>
                  <p className="text-xs text-mineral-500">Concepts</p>
                </div>
              </div>

              {/* Top Concepts */}
              {stats.top_concepts && stats.top_concepts.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-mineral-700 mb-2">Top Concepts</p>
                  <div className="flex flex-wrap gap-2">
                    {stats.top_concepts.slice(0, 10).map((item, i) => (
                      <span
                        key={i}
                        className="px-2 py-1 bg-terra-100 text-terra-700 rounded-full text-xs font-medium"
                      >
                        {item.concept} ({item.count})
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Suggested Queries */}
      {buildStatus === 'ready' && onQueryClick && (
        <div className="bg-white/60 rounded-2xl p-6 border border-white/80 shadow-sm">
          <h3 className="font-semibold text-mineral-900 mb-4">Try Graph-Enhanced Queries</h3>
          <div className="space-y-2">
            {suggestedQueries.map((query, i) => (
              <button
                key={i}
                onClick={() => onQueryClick(query)}
                className="w-full text-left p-3 bg-mineral-50 hover:bg-terra-50 rounded-lg text-sm text-mineral-700 hover:text-terra-700 transition-colors"
              >
                {query}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Info */}
      <div className="text-center text-sm text-mineral-500 px-4">
        <p>
          Graph RAG builds a knowledge graph from your emails, connecting related concepts
          for deeper, more contextual answers.
        </p>
      </div>
    </div>
  )
}
