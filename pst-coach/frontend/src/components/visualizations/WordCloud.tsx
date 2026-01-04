'use client'

import { useEffect, useState, useCallback } from 'react'
import { Loader2, Cloud } from 'lucide-react'
import api from '@/lib/api'

interface WordCloudProps {
    uploadId: string
    onWordClick?: (word: string) => void
}

interface WordData {
    text: string
    value: number
}

export default function WordCloud({ uploadId, onWordClick }: WordCloudProps) {
    const [words, setWords] = useState<WordData[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true)
                const response = await api.get('/api/analytics/wordcloud', {
                    params: { upload_id: uploadId, top_n: 60 }
                })

                setWords(response.data.words || [])
                setError(null)
            } catch (err: any) {
                setError('Failed to load word cloud data')
                console.error('WordCloud fetch error:', err)
            } finally {
                setLoading(false)
            }
        }

        if (uploadId) {
            fetchData()
        }
    }, [uploadId])

    const handleWordClick = useCallback((word: string) => {
        if (onWordClick) {
            onWordClick(word)
        }
    }, [onWordClick])

    // Calculate font size based on value range
    const getWordStyle = (word: WordData, maxValue: number) => {
        const minSize = 12
        const maxSize = 48
        const normalizedValue = word.value / maxValue
        const fontSize = minSize + (maxSize - minSize) * normalizedValue

        // Color variations in the terra-mineral palette
        const colors = [
            '#C07A5C', // terra-500
            '#A66B4F', // terra-600
            '#4A5568', // mineral-600
            '#2D3748', // mineral-700
            '#D4A484', // terra-400
            '#718096', // mineral-500
            '#8B7355', // sand-600
        ]
        const colorIndex = Math.floor(Math.random() * colors.length)

        return {
            fontSize: `${fontSize}px`,
            color: colors[colorIndex],
            opacity: 0.7 + 0.3 * normalizedValue,
        }
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64 bg-white/40 rounded-2xl">
                <Loader2 className="w-8 h-8 text-terra-500 animate-spin" />
            </div>
        )
    }

    if (error || words.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center h-64 bg-white/40 rounded-2xl">
                <Cloud className="w-12 h-12 text-mineral-300 mb-4" />
                <p className="text-mineral-500">
                    {error || 'No word cloud data available yet'}
                </p>
            </div>
        )
    }

    const maxValue = Math.max(...words.map(w => w.value))

    return (
        <div className="bg-white/60 backdrop-blur-md rounded-2xl p-6 border border-white/50">
            <h3 className="text-lg font-semibold text-mineral-900 mb-4 flex items-center gap-2">
                <Cloud className="w-5 h-5 text-terra-600" />
                Common Topics & Terms
            </h3>

            <div className="flex flex-wrap gap-3 justify-center items-center min-h-[250px] p-4">
                {words.map((word, i) => {
                    const style = getWordStyle(word, maxValue)
                    return (
                        <button
                            key={`${word.text}-${i}`}
                            onClick={() => handleWordClick(word.text)}
                            className="font-medium hover:scale-110 transition-transform cursor-pointer hover:underline"
                            style={style}
                            title={`${word.value} occurrences - Click to search`}
                        >
                            {word.text}
                        </button>
                    )
                })}
            </div>

            <p className="text-xs text-mineral-400 text-center mt-4">
                Click a word to search emails containing it
            </p>
        </div>
    )
}
