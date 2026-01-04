'use client'

import { useState } from 'react'
import Timeline from './Timeline'
import WordCloud from './WordCloud'
import NetworkGraph from './NetworkGraph'
import { TrendingUp, Cloud, Users } from 'lucide-react'

interface VisualizationPanelProps {
    uploadId: string
    onSearchWord?: (word: string) => void
    onSearchContact?: (name: string) => void
}

type TabType = 'timeline' | 'wordcloud' | 'network'

export default function VisualizationPanel({
    uploadId,
    onSearchWord,
    onSearchContact
}: VisualizationPanelProps) {
    const [activeTab, setActiveTab] = useState<TabType>('timeline')

    const tabs = [
        { id: 'timeline' as TabType, label: 'Timeline', icon: TrendingUp },
        { id: 'wordcloud' as TabType, label: 'Topics', icon: Cloud },
        { id: 'network' as TabType, label: 'Connections', icon: Users },
    ]

    return (
        <div className="space-y-6">
            {/* Tab Navigation */}
            <div className="flex items-center gap-2 bg-white/60 p-1.5 rounded-full border border-mineral-100 shadow-sm w-fit mx-auto">
                {tabs.map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`
              px-4 py-2 rounded-full text-sm font-medium transition-all flex items-center gap-2
              ${activeTab === tab.id
                                ? 'bg-terra-600 text-white shadow-md'
                                : 'text-mineral-500 hover:text-terra-700 hover:bg-terra-50'
                            }
            `}
                    >
                        <tab.icon className="w-4 h-4" />
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* Tab Content */}
            <div className="transition-all duration-300">
                {activeTab === 'timeline' && (
                    <Timeline uploadId={uploadId} />
                )}

                {activeTab === 'wordcloud' && (
                    <WordCloud
                        uploadId={uploadId}
                        onWordClick={onSearchWord}
                    />
                )}

                {activeTab === 'network' && (
                    <NetworkGraph
                        uploadId={uploadId}
                        onNodeClick={onSearchContact}
                    />
                )}
            </div>
        </div>
    )
}
