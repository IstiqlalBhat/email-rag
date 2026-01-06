'use client'

import { useState, useRef, useEffect } from 'react'
import Link from 'next/link'
import LiquidButton from '@/components/ui/LiquidButton'
import VisualizationPanel from '@/components/visualizations/VisualizationPanel'
import GraphRAGPanel from '@/components/visualizations/GraphRAGPanel'
import {
  Send,
  ArrowLeft,
  MessageCircle,
  Sparkles,
  User,
  Bot,
  Loader2,
  FileText,
  Calendar,
  Mail,
  Quote,
  BarChart3,
  Network
} from 'lucide-react'
import api from '@/lib/api'

interface Citation {
  date: string
  sender: string
  subject: string
  snippet?: string
}

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  citations?: Citation[]
  mode?: string
}

const SUGGESTED_PROMPTS = [
  { icon: '💭', text: 'What patterns do you see in my communication style?' },
  { icon: '⚡', text: 'How do I handle urgent requests?' },
  { icon: '🌙', text: 'Am I sending too many after-hours emails?' },
  { icon: '🎯', text: 'What topics do I discuss most frequently?' },
]

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [activeMode, setActiveMode] = useState<'ask' | 'coach' | 'explore' | 'graph'>('coach')
  const [uploadId, setUploadId] = useState<string | null>(null)
  const [isInitialized, setIsInitialized] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Fetch existing uploads on mount
  useEffect(() => {
    const initializeUploadId = async () => {
      // First check localStorage
      const storedId = localStorage.getItem('current_upload_id')
      if (storedId) {
        setUploadId(storedId)
        setIsInitialized(true)
        return
      }

      // Otherwise fetch from API
      try {
        const response = await api.get('/api/uploads/')
        const uploads = response.data?.uploads || []

        if (uploads.length > 0) {
          // Use the upload with the most vectors
          const sortedUploads = [...uploads].sort((a: any, b: any) =>
            (b.vector_count || 0) - (a.vector_count || 0)
          )
          const bestUpload = sortedUploads[0]

          if (bestUpload?.upload_id && bestUpload.vector_count > 0) {
            setUploadId(bestUpload.upload_id)
            localStorage.setItem('current_upload_id', bestUpload.upload_id)
          }
        }
      } catch (error) {
        console.error('Failed to fetch uploads:', error)
      }
      setIsInitialized(true)
    }

    initializeUploadId()
  }, [])

  const handleSend = async (messageText?: string) => {
    const text = messageText || input
    if (!text.trim() || isLoading) return

    // If not initialized yet, wait a moment
    if (!isInitialized) {
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: 'assistant',
        content: 'Loading your email data, please wait...',
        mode: 'info'
      }])
      return
    }

    if (!uploadId) {
      // Show a message about needing to upload first
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: 'assistant',
        content: 'Please upload a PST file first to analyze your emails. Go to the Upload page to get started.',
        mode: 'info'
      }])
      return
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      // Send full conversation history for context-aware responses
      const fullHistory = messages
        .map(m => ({ role: m.role, content: m.content }))
        .concat([{ role: 'user', content: text }])

      const response = await api.post('/api/chat/router', {
        messages: fullHistory,
        upload_id: uploadId,
        mode: activeMode === 'coach' ? 'insights' : activeMode === 'graph' ? 'graph' : 'content',
      })

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.data.content,
        citations: response.data.citations,
        mode: response.data.mode_used,
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (err: any) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        mode: 'error',
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Background provided by globals.css */}

      {/* Header */}
      <header className="border-b border-mineral-200/50 backdrop-blur-md bg-white/50 sticky top-0 z-50">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/" className="text-mineral-500 hover:text-terra-600 transition-colors">
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <h1 className="text-xl font-serif font-bold text-mineral-900">PST Coach</h1>
          </div>

          {/* Mode Toggle */}
          <div className="flex items-center gap-2 bg-white/60 p-1.5 rounded-full border border-mineral-100 shadow-sm">
            <button
              onClick={() => setActiveMode('ask')}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-all flex items-center gap-2 ${activeMode === 'ask'
                ? 'bg-mineral-800 text-white shadow-md'
                : 'text-mineral-500 hover:text-mineral-800 hover:bg-mineral-50'
                }`}
            >
              <MessageCircle className="w-4 h-4" />
              Ask Inbox
            </button>
            <button
              onClick={() => setActiveMode('coach')}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-all flex items-center gap-2 ${activeMode === 'coach'
                ? 'bg-terra-600 text-white shadow-md'
                : 'text-mineral-500 hover:text-terra-700 hover:bg-terra-50'
                }`}
            >
              <Sparkles className="w-4 h-4" />
              Coach Me
            </button>
            <button
              onClick={() => setActiveMode('explore')}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-all flex items-center gap-2 ${activeMode === 'explore'
                ? 'bg-amber-600 text-white shadow-md'
                : 'text-mineral-500 hover:text-amber-700 hover:bg-amber-50'
                }`}
            >
              <BarChart3 className="w-4 h-4" />
              Explore
            </button>
            <button
              onClick={() => setActiveMode('graph')}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-all flex items-center gap-2 ${activeMode === 'graph'
                ? 'bg-purple-600 text-white shadow-md'
                : 'text-mineral-500 hover:text-purple-700 hover:bg-purple-50'
                }`}
            >
              <Network className="w-4 h-4" />
              Graph
            </button>
          </div>
        </div>
      </header>

      {/* Messages Area */}
      <main className="flex-1 overflow-y-auto w-full">
        <div className="max-w-4xl mx-auto px-4 py-10">
          {activeMode === 'explore' ? (
            // Explore Mode - Visualizations
            <div className="space-y-6">
              <div className="text-center space-y-3 mb-8">
                <h2 className="text-3xl font-serif font-medium text-mineral-900">
                  Explore Your Patterns
                </h2>
                <p className="text-mineral-600">
                  Visualize your email activity, common topics, and connections
                </p>
              </div>
              {uploadId ? (
                <VisualizationPanel
                  uploadId={uploadId}
                  onSearchWord={(word) => {
                    setActiveMode('ask')
                    setInput(`Show me emails about "${word}"`)
                  }}
                  onSearchContact={(name) => {
                    setActiveMode('ask')
                    setInput(`Show me emails with ${name}`)
                  }}
                />
              ) : (
                <div className="text-center py-16 bg-white/40 rounded-2xl">
                  <p className="text-mineral-500">Upload a PST file first to see visualizations</p>
                </div>
              )}
            </div>
          ) : activeMode === 'graph' ? (
            // Graph Mode - Knowledge Graph
            <div className="space-y-6">
              <div className="text-center space-y-3 mb-8">
                <h2 className="text-3xl font-serif font-medium text-mineral-900">
                  Knowledge Graph
                </h2>
                <p className="text-mineral-600">
                  Build and query a knowledge graph for deeper insights
                </p>
              </div>
              {uploadId ? (
                <div className="grid md:grid-cols-2 gap-6">
                  <GraphRAGPanel
                    uploadId={uploadId}
                    onQueryClick={(query) => {
                      setInput(query)
                      handleSend(query)
                    }}
                  />
                  {/* Messages area for graph mode */}
                  <div className="bg-white/60 rounded-2xl p-6 border border-white/80 shadow-sm min-h-[400px]">
                    <h3 className="font-semibold text-mineral-900 mb-4">Graph Query Results</h3>
                    {messages.length === 0 ? (
                      <div className="text-center py-12 text-mineral-400">
                        <Network className="w-12 h-12 mx-auto mb-4 opacity-50" />
                        <p>Build the graph and ask questions to see results here</p>
                      </div>
                    ) : (
                      <div className="space-y-4 max-h-[500px] overflow-y-auto">
                        {messages.filter(m => m.role === 'assistant').slice(-3).map((message) => (
                          <div key={message.id} className="bg-mineral-50 rounded-lg p-4">
                            <p className="text-mineral-800 text-sm whitespace-pre-wrap">{message.content}</p>
                            {message.citations && message.citations.length > 0 && (
                              <div className="mt-3 pt-3 border-t border-mineral-200">
                                <p className="text-xs text-mineral-400 mb-2">Sources:</p>
                                {message.citations.slice(0, 3).map((c, i) => (
                                  <p key={i} className="text-xs text-mineral-500 truncate">
                                    {c.sender} - {c.subject}
                                  </p>
                                ))}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="text-center py-16 bg-white/40 rounded-2xl">
                  <p className="text-mineral-500">Upload a PST file first to build a knowledge graph</p>
                </div>
              )}
            </div>
          ) : (
            messages.length === 0 ? (
              // Empty State
              <div className="text-center py-16 space-y-8">
                <div className={`
                w-24 h-24 rounded-full flex items-center justify-center mx-auto shadow-lg
                ${activeMode === 'coach' ? 'bg-terra-100 text-terra-600' : 'bg-mineral-100 text-mineral-600'}
              `}>
                  {activeMode === 'coach' ? (
                    <Sparkles className="w-12 h-12" />
                  ) : (
                    <MessageCircle className="w-12 h-12" />
                  )}
                </div>

                <div className="space-y-3">
                  <h2 className="text-4xl font-serif font-medium text-mineral-900">
                    {activeMode === 'coach'
                      ? 'Ready to coach you'
                      : 'Ask about your emails'
                    }
                  </h2>
                  <p className="text-lg text-mineral-600 max-w-lg mx-auto">
                    {activeMode === 'coach'
                      ? 'I uncover patterns in your communication style and workload.'
                      : 'Search your history using natural language. No keywords needed.'
                    }
                  </p>
                </div>

                {/* Suggested Prompts */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl mx-auto">
                  {SUGGESTED_PROMPTS.map((prompt, i) => (
                    <button
                      key={i}
                      onClick={() => handleSend(prompt.text)}
                      className="
                      text-left p-6 rounded-2xl bg-white/60 border border-white/80 shadow-sm
                      hover:bg-white hover:shadow-md hover:border-terra-200 transition-all duration-300 group
                    "
                    >
                      <span className="text-2xl mr-3 inline-block">{prompt.icon}</span>
                      <span className="text-mineral-700 font-medium group-hover:text-terra-700 transition-colors">
                        {prompt.text}
                      </span>
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              // Messages List
              <div className="space-y-8">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex gap-4 ${message.role === 'user' ? 'justify-end' : ''}`}
                  >
                    {message.role === 'assistant' && (
                      <div className="w-10 h-10 rounded-full bg-terra-100 flex items-center justify-center flex-shrink-0 border border-terra-200">
                        <Bot className="w-5 h-5 text-terra-700" />
                      </div>
                    )}

                    <div className={`max-w-[85%] lg:max-w-[75%] ${message.role === 'user' ? 'order-first' : ''}`}>
                      <div
                        className={`rounded-3xl px-6 py-4 shadow-sm ${message.role === 'user'
                          ? 'bg-terra-600 text-white rounded-br-sm'
                          : 'bg-white text-mineral-800 border border-mineral-100 rounded-bl-sm'
                          }`}
                      >
                        <p className="whitespace-pre-wrap leading-relaxed text-base">{message.content}</p>
                      </div>

                      {/* Citations */}
                      {message.citations && message.citations.length > 0 && (
                        <div className="mt-4 space-y-3 pl-4 border-l-2 border-terra-200">
                          <p className="text-xs text-mineral-400 uppercase tracking-widest font-bold">Sources Identified</p>
                          {message.citations.map((citation, i) => (
                            <div
                              key={i}
                              className="bg-white/40 rounded-xl p-4 text-sm border border-white/60 hover:bg-white/80 transition-colors cursor-pointer"
                            >
                              <div className="flex items-center gap-3 text-mineral-500 mb-2">
                                <Calendar className="w-3.5 h-3.5" />
                                <span className="font-medium">{citation.date}</span>
                                <Mail className="w-3.5 h-3.5 ml-2" />
                                <span className="font-medium">{citation.sender}</span>
                              </div>
                              {citation.subject && (
                                <p className="text-mineral-800 font-medium flex items-start gap-2">
                                  <Quote className="w-3.5 h-3.5 mt-1 text-terra-500 flex-shrink-0" />
                                  {citation.subject}
                                </p>
                              )}
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Mode Badge */}
                      {message.mode && message.role === 'assistant' && (
                        <div className="mt-2 ml-2">
                          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-mineral-100 text-mineral-600">
                            {message.mode === 'insights' ? (
                              <>
                                <Sparkles className="w-3 h-3 text-terra-500" />
                                Coaching Insight
                              </>
                            ) : message.mode === 'graph' ? (
                              <>
                                <Network className="w-3 h-3 text-purple-500" />
                                Graph RAG
                              </>
                            ) : (
                              <>
                                <MessageCircle className="w-3 h-3 text-mineral-600" />
                                Search Result
                              </>
                            )}
                          </span>
                        </div>
                      )}
                    </div>

                    {message.role === 'user' && (
                      <div className="w-10 h-10 rounded-full bg-mineral-800 flex items-center justify-center flex-shrink-0 shadow-md">
                        <User className="w-5 h-5 text-white" />
                      </div>
                    )}
                  </div>
                ))}

                {/* Loading Indicator */}
                {isLoading && (
                  <div className="flex gap-4">
                    <div className="w-10 h-10 rounded-full bg-terra-100 flex items-center justify-center border border-terra-200">
                      <Loader2 className="w-5 h-5 text-terra-600 animate-spin" />
                    </div>
                    <div className="bg-white/50 rounded-2xl px-6 py-4 border border-white/60">
                      <div className="flex items-center gap-2 text-mineral-500">
                        <span className="font-medium">Analyzing patterns</span>
                        <span className="animate-pulse">...</span>
                      </div>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>
            )
          )}
        </div>
      </main>

      {/* Input Area - Hidden in Explore and Graph modes */}
      {activeMode !== 'explore' && activeMode !== 'graph' && (
        <footer className="border-t border-mineral-200 bg-white/80 backdrop-blur-xl sticky bottom-0 z-50">
          <div className="max-w-4xl mx-auto px-4 py-6">
            <div className="relative shadow-lg rounded-2xl bg-white transition-shadow hover:shadow-xl">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder={
                  activeMode === 'coach'
                    ? 'Ask for coaching insights...'
                    : 'Search your emails...'
                }
                rows={1}
                className="
                  w-full bg-transparent border-0 rounded-2xl px-6 py-4 pr-16 
                  text-mineral-900 placeholder-mineral-400 
                  focus:ring-2 focus:ring-terra-500/50 resize-none max-h-32 min-h-[60px]
                  text-lg
                "
              />
              <div className="absolute right-2 bottom-2">
                <LiquidButton
                  onClick={() => handleSend()}
                  disabled={!input.trim() || isLoading}
                  className="!p-3 !rounded-xl !bg-terra-600 hover:!bg-terra-500 !shadow-none"
                >
                  <Send className="w-5 h-5 text-white" />
                </LiquidButton>
              </div>
            </div>
            <p className="text-xs text-mineral-400 mt-4 text-center font-medium">
              AI-generated insights based on your email history. Privacy protected.
            </p>
          </div>
        </footer>
      )}
    </div>
  )
}
