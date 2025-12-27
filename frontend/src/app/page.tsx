import React from 'react'
import { Microscope, Target, Clock, TrendingUp } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="container mx-auto p-8">
      {/* Header */}
      <div className="text-center mb-12">
        <div className="flex items-center justify-center gap-3 mb-4">
          <Microscope className="w-12 h-12 text-primary" />
          <h1 className="text-4xl font-bold text-primary">Stain Time Optimization System</h1>
        </div>
        <p className="text-xl text-gray-600">
          Automated Giemsa Staining Time Determination via Slide Grading
        </p>
      </div>

      {/* System Features */}
      <section className="mb-12">
        <h2 className="text-3xl font-bold mb-6">System Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <FeatureCard
            icon={<Target className="w-8 h-8 text-primary" />}
            title="Slide Grading"
            description="Automated grading of Giemsa-stained slides using AMC criteria (Grades I-V)"
            features={[
              'Single slide analysis',
              'Confidence scores',
              'Pass/fail determination',
              'Failure diagnosis'
            ]}
          />
          <FeatureCard
            icon={<Clock className="w-8 h-8 text-primary" />}
            title="Optimal Time Selection"
            description="Find the earliest acceptable staining time for each staining session"
            features={[
              'Minute-by-minute sweep',
              '10% rapid method (5-15 min)',
              '3% slow method (30-45 min)',
              'Stability analysis'
            ]}
          />
          <FeatureCard
            icon={<TrendingUp className="w-8 h-8 text-primary" />}
            title="Pattern Viewer"
            description="View country-level staining time patterns and regional trends"
            features={[
              'National data aggregation',
              'Site-level patterns',
              'Regional recommendations',
              'Historical trend analysis'
            ]}
          />
        </div>
      </section>

      {/* Quick Start Guide */}
      <section className="mb-12 bg-white p-6 rounded-lg shadow">
        <h2 className="text-2xl font-bold mb-4">Quick Start Guide</h2>
        <div className="space-y-4">
          <GuideStep
            number={1}
            title="Single Slide Grading"
            description="Go to Single Slide Grading page, upload a slide image, and view grade, confidence, and pass/fail status"
          />
          <GuideStep
            number={2}
            title="Find Optimal Staining Time"
            description="Select dilution (10% or 3%), upload minute-by-minute sweep images, and get recommended optimal time"
          />
          <GuideStep
            number={3}
            title="View National Patterns"
            description="Explore aggregated staining time data from across Sri Lanka and see recommended starting times by region"
          />
        </div>
      </section>

      {/* AMC Grade Scale */}
      <section className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-2xl font-bold mb-4">AMC Grade Scale Reference</h2>
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
          <p className="font-semibold">
            Important: Per AMC MM-SOP-03C guidelines, only Grade III is acceptable for malaria diagnosis.
            All other grades indicate staining issues requiring corrective action.
          </p>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Grade</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Classification</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Corrective Action</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              <GradeRow grade="I" classification="Under-stained" status="Fail" action="Increase staining time 2-3 min" />
              <GradeRow grade="II" classification="Lightly stained" status="Fail" action="Increase staining time 1-2 min" />
              <GradeRow grade="III" classification="Optimal staining" status="Pass" action="No action needed - optimal" />
              <GradeRow grade="IV" classification="Over-stained" status="Fail" action="Decrease staining time 1-2 min" />
              <GradeRow grade="V" classification="Deeply over-stained" status="Fail" action="Decrease staining time 2-4 min" />
            </tbody>
          </table>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-12 text-center text-gray-600 border-t pt-6">
        <p className="mb-2">Anti-Malaria Campaign Sri Lanka | Stain Time Optimization Component</p>
        <p className="text-sm">Author: Sayumi Devasurendra | Version: 0.1.0</p>
      </footer>
    </div>
  )
}

function FeatureCard({ icon, title, description, features }: { icon: React.ReactNode, title: string, description: string, features: string[] }) {
  return (
    <div className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow">
      <div className="flex items-center gap-3 mb-3">
        {icon}
        <h3 className="text-xl font-bold">{title}</h3>
      </div>
      <p className="text-gray-600 mb-4">{description}</p>
      <ul className="space-y-2">
        {features.map((feature, idx) => (
          <li key={idx} className="flex items-start gap-2 text-sm text-gray-700">
            <span className="text-primary mt-1">•</span>
            <span>{feature}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

function GuideStep({ number, title, description }: { number: number, title: string, description: string }) {
  return (
    <div className="flex gap-4">
      <div className="flex-shrink-0 w-8 h-8 bg-primary text-white rounded-full flex items-center justify-center font-bold">
        {number}
      </div>
      <div>
        <h3 className="font-bold text-lg">{title}</h3>
        <p className="text-gray-600">{description}</p>
      </div>
    </div>
  )
}

function GradeRow({ grade, classification, status, action }: { grade: string, classification: string, status: string, action: string }) {
  const statusColor = status === 'Pass' ? 'text-green-600' : 'text-red-600';
  const statusSymbol = status === 'Pass' ? '✅' : '❌';

  return (
    <tr>
      <td className="px-6 py-4 whitespace-nowrap font-medium">{grade}</td>
      <td className="px-6 py-4">{classification}</td>
      <td className={`px-6 py-4 font-semibold ${statusColor}`}>{statusSymbol} {status}</td>
      <td className="px-6 py-4">{action}</td>
    </tr>
  )
}
