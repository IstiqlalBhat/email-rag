/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  safelist: [
    'bg-azure-600',
    'bg-azure-500',
    'text-azure-600',
    { pattern: /(bg|text|border)-(azure|sage|clay|ochre)-(50|100|200|300|400|500|600|700|800|900)/ }
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['var(--font-outfit)', 'sans-serif'],
        serif: ['var(--font-playfair)', 'serif'],
      },
      colors: {
        // Rich Earth Palette
        terra: {
          50: '#fdf8f6',
          100: '#f2e8e5',
          200: '#eaddd7',
          300: '#e0cec7',
          400: '#d2bab0',
          500: '#9f7aea', // For checking vividness, but sticking to requested style:
          DEFAULT: '#c05621', // Terracotta
          600: '#9c4221',
          900: '#7b341e',
        },
        mineral: {
          50: '#f0f4f8',
          100: '#d9e2ec',
          200: '#bcccdc',
          300: '#9fb3c8',
          400: '#829ab1',
          500: '#627d98',
          600: '#486581',
          700: '#334e68',
          800: '#243b53', // Deep Blue/Grey
          900: '#102a43',
        },
        sand: {
          50: '#f9f8fa',
          100: '#f3f3f3',
          200: '#e3e3e3',
          300: '#d1d1d1', // Darker sand for contrast
          DEFAULT: '#ded9d2',
        }
      },
      borderRadius: {
        'organic': '2rem',
        'blob': '60% 40% 30% 70% / 60% 30% 70% 40%',
      },
      boxShadow: {
        'soft': '0 10px 40px -10px rgba(0,0,0,0.08)',
        'glow': '0 0 20px rgba(159, 122, 234, 0.3)',
      },
      animation: {
        'float-slow': 'float 8s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-15px)' },
        }
      }
    },
  },
  plugins: [],
}
