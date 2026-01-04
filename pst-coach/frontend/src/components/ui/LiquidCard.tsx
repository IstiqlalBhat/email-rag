import { ReactNode } from 'react'

interface LiquidCardProps {
  children: ReactNode
  className?: string
}

export default function LiquidCard({ children, className = '' }: LiquidCardProps) {
  return (
    <div className={`rich-glass rounded-3xl p-8 md:p-10 ${className}`}>
      {children}
    </div>
  )
}
