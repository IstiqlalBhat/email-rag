import { ReactNode, ButtonHTMLAttributes } from 'react'

interface LiquidButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  children: ReactNode
  variant?: 'default' | 'outline'
  className?: string
}

export default function LiquidButton({
  children,
  variant = 'default',
  className = '',
  ...props
}: LiquidButtonProps) {
  // Pill shape, slightly flatter for modern look
  const baseStyles = 'px-12 py-4 rounded-full font-sans font-semibold text-lg transition-all duration-300 transform active:scale-95'

  const variants = {
    // Terracotta Primary - High Visibility
    default: 'bg-terra-600 hover:bg-terra-500 text-white shadow-lg shadow-terra-200 hover:shadow-terra-300 hover:-translate-y-0.5',

    // Mineral Outline
    outline: 'border-2 border-mineral-300 text-mineral-700 hover:border-mineral-800 hover:text-mineral-900 bg-transparent hover:bg-mineral-50'
  }

  return (
    <button
      className={`${baseStyles} ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  )
}
