/**
 * Shared TypeScript types
 */

export interface User {
  id: number
  email: string
  full_name?: string
  tenant_id: number
}

export interface Upload {
  id: number
  filename: string
  size_bytes: number
  status: 'pending' | 'uploading' | 'completed' | 'failed'
  created_at: string
}

export interface Job {
  id: number
  type: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress: number
  total: number
  current_stage?: string
  started_at?: string
}

export interface Mailbox {
  id: number
  display_name: string
  total_messages: number
  total_threads: number
  date_range: {
    first_message: string
    last_message: string
  }
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface Citation {
  message_id: string
  date: string
  folder?: string
  snippet?: string
}

export interface ChatResponse {
  content: string
  citations: Citation[]
  mode_used: string
}

export interface PrivacySettings {
  redaction_level: 'strict' | 'moderate' | 'minimal' | 'none'
  excerpt_policy: 'never' | 'ask' | 'always'
  retention_days: number
  auto_delete_pst: boolean
}
