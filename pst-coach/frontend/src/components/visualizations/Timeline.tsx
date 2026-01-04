'use client'

import { useEffect, useState } from 'react'
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer
} from 'recharts'
import { Loader2, TrendingUp } from 'lucide-react'
import api from '@/lib/api'

interface TimelineProps {
    uploadId: string
}

interface TimelineData {
    date: string
    count: number
}

export default function Timeline({ uploadId }: TimelineProps) {
    const [data, setData] = useState<TimelineData[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true)
                const response = await api.get('/api/analytics/timeline', {
                    params: { upload_id: uploadId }
                })

                // Transform API response to chart format
                const chartData = response.data.dates.map((date: string, i: number) => ({
                    date: formatDate(date),
                    count: response.data.counts[i]
                }))

                setData(chartData)
                setError(null)
            } catch (err: any) {
                setError('Failed to load timeline data')
                console.error('Timeline fetch error:', err)
            } finally {
                setLoading(false)
            }
        }

        if (uploadId) {
            fetchData()
        }
    }, [uploadId])

    const formatDate = (dateStr: string) => {
        const date = new Date(dateStr)
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64 bg-white/40 rounded-2xl">
                <Loader2 className="w-8 h-8 text-terra-500 animate-spin" />
            </div>
        )
    }

    if (error || data.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center h-64 bg-white/40 rounded-2xl">
                <TrendingUp className="w-12 h-12 text-mineral-300 mb-4" />
                <p className="text-mineral-500">
                    {error || 'No timeline data available yet'}
                </p>
            </div>
        )
    }

    return (
        <div className="bg-white/60 backdrop-blur-md rounded-2xl p-6 border border-white/50">
            <h3 className="text-lg font-semibold text-mineral-900 mb-4 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-terra-600" />
                Email Activity Over Time
            </h3>

            <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                    <defs>
                        <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#C07A5C" stopOpacity={0.8} />
                            <stop offset="95%" stopColor="#C07A5C" stopOpacity={0.1} />
                        </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#E5DDD5" />
                    <XAxis
                        dataKey="date"
                        tick={{ fill: '#6B7280', fontSize: 12 }}
                        tickLine={{ stroke: '#E5DDD5' }}
                    />
                    <YAxis
                        tick={{ fill: '#6B7280', fontSize: 12 }}
                        tickLine={{ stroke: '#E5DDD5' }}
                    />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: 'rgba(255, 255, 255, 0.95)',
                            border: '1px solid #E5DDD5',
                            borderRadius: '12px',
                            boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                        }}
                        labelStyle={{ color: '#374151', fontWeight: 600 }}
                        itemStyle={{ color: '#C07A5C' }}
                    />
                    <Area
                        type="monotone"
                        dataKey="count"
                        stroke="#C07A5C"
                        strokeWidth={2}
                        fillOpacity={1}
                        fill="url(#colorCount)"
                        name="Emails"
                    />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    )
}
