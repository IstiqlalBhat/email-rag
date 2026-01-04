'use client'

import { useState, useCallback } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import LiquidCard from '@/components/ui/LiquidCard'
import LiquidButton from '@/components/ui/LiquidButton'
import { Upload, FileCheck, Loader2, ArrowLeft, Sparkles, AlertCircle } from 'lucide-react'
import api from '@/lib/api'

type UploadStatus = 'idle' | 'uploading' | 'processing' | 'complete' | 'error'

export default function UploadPage() {
  const router = useRouter()
  const [file, setFile] = useState<File | null>(null)
  const [status, setStatus] = useState<UploadStatus>('idle')
  const [uploadId, setUploadId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [dragActive, setDragActive] = useState(false)

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0]
      if (droppedFile.name.endsWith('.pst')) {
        setFile(droppedFile)
        setError(null)
      } else {
        setError('Please upload a .pst file')
      }
    }
  }, [])

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0]
      if (selectedFile.name.endsWith('.pst')) {
        setFile(selectedFile)
        setError(null)
      } else {
        setError('Please upload a .pst file')
      }
    }
  }

  const handleUpload = async () => {
    if (!file) return

    setStatus('uploading')
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await api.post('/api/uploads/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      const { upload_id } = response.data
      setUploadId(upload_id)
      setStatus('processing')

      // Store upload_id for later use
      localStorage.setItem('current_upload_id', upload_id)

      // Wait a bit then redirect to chat
      setTimeout(() => {
        setStatus('complete')
      }, 2000)

    } catch (err: any) {
      setStatus('error')
      setError(err.response?.data?.detail || 'Upload failed. Please try again.')
    }
  }

  const handleGoToChat = () => {
    router.push('/chat')
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <div className="min-h-screen py-12 px-4 md:px-8">
      {/* Background provided by globals.css (Warm Gradient) */}

      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Link href="/" className="inline-flex items-center gap-2 text-mineral-600 hover:text-terra-600 transition-colors font-medium">
            <ArrowLeft className="w-4 h-4" />
            Back to Home
          </Link>
        </div>

        <LiquidCard className="bg-white/80 dark:bg-mineral-900/50 backdrop-blur-xl shadow-xl border-white/50">
          <div className="text-center space-y-8">
            <div className="space-y-3">
              <h1 className="text-4xl md:text-5xl display-text text-mineral-900 dark:text-white">Upload Your PST</h1>
              <p className="text-lg text-mineral-600 dark:text-mineral-300">
                Drop your Outlook PST file to unlock organic insights about your communication.
              </p>
            </div>

            {/* Upload Zone */}
            {status === 'idle' && (
              <div
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                className={`
                  border-3 border-dashed rounded-2xl p-12 transition-all duration-300 cursor-pointer group
                  ${dragActive
                    ? 'border-terra-500 bg-terra-50'
                    : 'border-mineral-200 hover:border-terra-400 hover:bg-sand-50'
                  }
                `}
                onClick={() => document.getElementById('file-input')?.click()}
              >
                <input
                  id="file-input"
                  type="file"
                  accept=".pst"
                  onChange={handleFileChange}
                  className="hidden"
                />

                <div className="flex flex-col items-center gap-6">
                  <div className={`
                    w-20 h-20 rounded-full flex items-center justify-center transition-colors
                    ${dragActive ? 'bg-terra-100 text-terra-600' : 'bg-sand-100 text-mineral-500 group-hover:text-terra-600 group-hover:bg-terra-100'}
                  `}>
                    <Upload className="w-10 h-10" />
                  </div>
                  <div>
                    <p className="text-xl font-semibold text-mineral-900 group-hover:text-terra-700">
                      Drag & drop your PST file here
                    </p>
                    <p className="text-mineral-500 mt-2 font-medium">
                      or click to browse • Max 5GB
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* File Selected */}
            {file && status === 'idle' && (
              <div className="bg-sand-50 border border-sand-200 rounded-xl p-6 flex items-center justify-between shadow-sm">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-terra-100 rounded-lg">
                    <FileCheck className="w-6 h-6 text-terra-600" />
                  </div>
                  <div className="text-left">
                    <p className="font-semibold text-mineral-900">{file.name}</p>
                    <p className="text-sm text-mineral-500">{formatFileSize(file.size)}</p>
                  </div>
                </div>
                <button
                  onClick={() => setFile(null)}
                  className="text-mineral-400 hover:text-terra-600 text-sm font-medium px-4 py-2 hover:bg-terra-50 rounded-lg transition-colors"
                >
                  Remove
                </button>
              </div>
            )}

            {/* Uploading State */}
            {status === 'uploading' && (
              <div className="py-16 flex flex-col items-center gap-6">
                <Loader2 className="w-16 h-16 text-terra-500 animate-spin" />
                <div>
                  <p className="text-2xl font-serif text-mineral-900">Uploading your file...</p>
                  <p className="text-mineral-500 mt-2">Please keep this window open</p>
                </div>
              </div>
            )}

            {/* Processing State */}
            {status === 'processing' && (
              <div className="py-16 flex flex-col items-center gap-6">
                <div className="relative">
                  <Loader2 className="w-16 h-16 text-terra-500 animate-spin" />
                  <Sparkles className="w-8 h-8 text-amber-400 absolute -top-2 -right-2 animate-pulse" />
                </div>
                <div className="text-center">
                  <p className="text-2xl font-serif text-mineral-900">Analyzing your emails...</p>
                  <p className="text-mineral-500 mt-2">We are identifying organic patterns in your communication</p>
                </div>
              </div>
            )}

            {/* Complete State */}
            {status === 'complete' && (
              <div className="py-12 flex flex-col items-center gap-8">
                <div className="w-24 h-24 rounded-full bg-green-100 flex items-center justify-center ring-8 ring-green-50">
                  <FileCheck className="w-12 h-12 text-green-600" />
                </div>
                <div className="text-center">
                  <p className="text-3xl font-serif text-mineral-900">Analysis Complete!</p>
                  <p className="text-lg text-mineral-500 mt-2">Your ecosystem has been mapped.</p>
                </div>
                <LiquidButton onClick={handleGoToChat} className="animate-bounce-subtle">
                  Enter Dashboard
                </LiquidButton>
              </div>
            )}

            {/* Error State */}
            {error && (
              <div className="bg-red-50 border border-red-100 rounded-xl p-4 flex items-center gap-3 text-red-700">
                <AlertCircle className="w-5 h-5 shrink-0" />
                <p className="font-medium">{error}</p>
              </div>
            )}

            {/* Upload Button */}
            {file && status === 'idle' && (
              <LiquidButton onClick={handleUpload} className="w-full text-xl shadow-xl shadow-terra-200/50">
                Begin Analysis
              </LiquidButton>
            )}

            {/* Privacy Note */}
            <p className="text-xs text-mineral-400 mt-8 flex items-center justify-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-green-500"></span>
              Secure Encryption • Local Processing • Redaction Enabled
            </p>
          </div>
        </LiquidCard>
      </div>
    </div>
  )
}
