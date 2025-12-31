import type { Metadata } from 'next'
import './globals.css'
import Sidebar from '@/components/Sidebar'

export const metadata: Metadata = {
  title: 'Stain Time Optimization System',
  description: 'Automated Giemsa Staining Time Determination via Slide Grading',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <div className="flex min-h-screen">
          <Sidebar />
          <main className="flex-1 bg-gray-50">
            {children}
          </main>
        </div>
      </body>
    </html>
  )
}
