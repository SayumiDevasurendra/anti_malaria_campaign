'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Home, Target, Clock, BarChart3, TrendingUp } from 'lucide-react'

const navigation = [
  { name: 'Home', href: '/', icon: Home },
  { name: 'Single Slide Grading', href: '/single-slide', icon: Target },
  { name: 'Optimal Time Finder', href: '/optimal-time', icon: Clock },
  { name: 'Batch Analysis', href: '/batch-analysis', icon: BarChart3 },
  { name: 'Pattern Viewer', href: '/pattern-viewer', icon: TrendingUp },
]

export default function Sidebar() {
  const pathname = usePathname()

  return (
    <div className="w-64 bg-white shadow-lg">
      <div className="flex flex-col h-full">
        {/* Logo */}
        <div className="p-6 border-b">
          <div className="bg-primary text-white rounded px-4 py-8 text-center">
            <h2 className="font-bold text-lg">AMC Logo</h2>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4">
          <h3 className="text-xs font-semibold text-gray-500 uppercase mb-3">Navigation</h3>
          <ul className="space-y-2">
            {navigation.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.href
              return (
                <li key={item.name}>
                  <Link
                    href={item.href}
                    className={`flex items-center gap-3 px-4 py-2 rounded-lg transition-colors ${
                      isActive
                        ? 'bg-primary text-white'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="text-sm font-medium">{item.name}</span>
                  </Link>
                </li>
              )
            })}
          </ul>
        </nav>

        {/* About */}
        <div className="p-4 border-t">
          <h3 className="text-xs font-semibold text-gray-500 uppercase mb-2">About</h3>
          <div className="text-xs text-gray-600">
            <p className="mb-1"><strong>Component:</strong> Stain Time Optimization</p>
            <p className="mb-1"><strong>Author:</strong> Sayumi Devasurendra</p>
            <p><strong>Version:</strong> 0.1.0</p>
          </div>
        </div>
      </div>
    </div>
  )
}
