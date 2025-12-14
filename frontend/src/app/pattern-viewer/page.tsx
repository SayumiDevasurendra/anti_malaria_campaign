'use client'

import React from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts'

export default function PatternViewerPage() {
  // Sample pattern data
  const nationalData = {
    '10%': {
      mean: 8.5,
      std: 1.2,
      median: 8.0,
      min: 6,
      max: 12,
      num_batches: 45,
      num_sites: 8
    },
    '3%': {
      mean: 33.2,
      std: 3.1,
      median: 32.0,
      min: 28,
      max: 40,
      num_batches: 38,
      num_sites: 7
    }
  }

  const regionalData = [
    { region: 'Western', '10%': 8.5, '3%': 33.2, sites: 3 },
    { region: 'Central', '10%': 8.2, '3%': 32.8, sites: 2 },
    { region: 'Southern', '10%': 8.7, '3%': 33.5, sites: 2 },
    { region: 'Northern', '10%': 8.3, '3%': 32.5, sites: 1 },
    { region: 'Eastern', '10%': 8.6, '3%': 33.8, sites: 2 },
  ]

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-2">National Staining Time Pattern Viewer</h1>
      <p className="text-gray-600 mb-8">Explore aggregated optimal staining time patterns across Sri Lanka</p>

      {/* National Summary */}
      <div className="mb-12">
        <h2 className="text-2xl font-bold mb-6">National Pattern Summary</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* 10% Method */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-xl font-bold mb-4">10% Rapid Method</h3>

            <div className="grid grid-cols-3 gap-4 mb-4">
              <div className="text-center">
                <p className="text-sm text-gray-600 mb-1">Mean Time</p>
                <p className="text-2xl font-bold">{nationalData['10%'].mean} min</p>
              </div>
              <div className="text-center">
                <p className="text-sm text-gray-600 mb-1">Median Time</p>
                <p className="text-2xl font-bold">{nationalData['10%'].median} min</p>
              </div>
              <div className="text-center">
                <p className="text-sm text-gray-600 mb-1">Std Dev</p>
                <p className="text-2xl font-bold">{nationalData['10%'].std} min</p>
              </div>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="font-semibold text-blue-900 mb-2">
                Recommended Starting Time: {nationalData['10%'].median} minutes
              </p>
              <p className="text-sm text-blue-800">
                Based on {nationalData['10%'].num_batches} batches from {nationalData['10%'].num_sites} sites.
              </p>
              <p className="text-sm text-blue-800">
                <strong>Range:</strong> {nationalData['10%'].min}-{nationalData['10%'].max} minutes
              </p>
            </div>
          </div>

          {/* 3% Method */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-xl font-bold mb-4">3% Slow Method</h3>

            <div className="grid grid-cols-3 gap-4 mb-4">
              <div className="text-center">
                <p className="text-sm text-gray-600 mb-1">Mean Time</p>
                <p className="text-2xl font-bold">{nationalData['3%'].mean} min</p>
              </div>
              <div className="text-center">
                <p className="text-sm text-gray-600 mb-1">Median Time</p>
                <p className="text-2xl font-bold">{nationalData['3%'].median} min</p>
              </div>
              <div className="text-center">
                <p className="text-sm text-gray-600 mb-1">Std Dev</p>
                <p className="text-2xl font-bold">{nationalData['3%'].std} min</p>
              </div>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="font-semibold text-blue-900 mb-2">
                Recommended Starting Time: {nationalData['3%'].median} minutes
              </p>
              <p className="text-sm text-blue-800">
                Based on {nationalData['3%'].num_batches} batches from {nationalData['3%'].num_sites} sites.
              </p>
              <p className="text-sm text-blue-800">
                <strong>Range:</strong> {nationalData['3%'].min}-{nationalData['3%'].max} minutes
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Regional Patterns */}
      <div className="mb-12">
        <h2 className="text-2xl font-bold mb-6">Regional Patterns</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          {/* 10% by Region */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-bold mb-4">10% Rapid Method by Region</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={regionalData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="region" />
                <YAxis domain={[6, 10]} label={{ value: 'Mean Time (min)', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <ReferenceLine y={nationalData['10%'].mean} stroke="red" strokeDasharray="3 3" label="National Mean" />
                <Bar dataKey="10%" fill="#1f77b4" name="Mean Time" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* 3% by Region */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-bold mb-4">3% Slow Method by Region</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={regionalData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="region" />
                <YAxis domain={[30, 36]} label={{ value: 'Mean Time (min)', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <ReferenceLine y={nationalData['3%'].mean} stroke="red" strokeDasharray="3 3" label="National Mean" />
                <Bar dataKey="3%" fill="#ff7f0e" name="Mean Time" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Regional Data Table */}
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Region</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">10% Mean (min)</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">3% Mean (min)</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sites</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {regionalData.map((row, idx) => (
                  <tr key={idx}>
                    <td className="px-6 py-4 whitespace-nowrap font-medium">{row.region}</td>
                    <td className="px-6 py-4 whitespace-nowrap">{row['10%']}</td>
                    <td className="px-6 py-4 whitespace-nowrap">{row['3%']}</td>
                    <td className="px-6 py-4 whitespace-nowrap">{row.sites}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Recommendations */}
      <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-12">
        <h2 className="text-xl font-bold text-green-900 mb-4">Recommendations for New Sites</h2>

        <div className="space-y-4 text-green-800">
          <div>
            <p className="font-semibold mb-2">Starting Point for New Sites/Locations:</p>
            <ol className="list-decimal list-inside space-y-2 ml-4">
              <li>
                <strong>10% Rapid Method:</strong> Start with <strong>8 minutes</strong>
                <ul className="list-disc list-inside ml-6 text-sm mt-1">
                  <li>Typical range: 7-10 minutes</li>
                  <li>Run confirmation sweep: 6-10 minutes</li>
                </ul>
              </li>
              <li>
                <strong>3% Slow Method:</strong> Start with <strong>32 minutes</strong>
                <ul className="list-disc list-inside ml-6 text-sm mt-1">
                  <li>Typical range: 30-35 minutes</li>
                  <li>Run confirmation sweep: 30-38 minutes</li>
                </ul>
              </li>
            </ol>
          </div>

          <div>
            <p className="font-semibold mb-2">Next Steps:</p>
            <ol className="list-decimal list-inside space-y-1 ml-4">
              <li>Prepare new working solution</li>
              <li>Run minute-by-minute sweep around recommended time</li>
              <li>Use Optimal Time Finder to confirm site-specific optimum</li>
              <li>Document and contribute to national pattern</li>
            </ol>
          </div>
        </div>
      </div>

      {/* Data Info */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-bold mb-4">About Pattern Data</h2>

        <div className="space-y-4 text-gray-700">
          <div>
            <h3 className="font-semibold mb-2">Data Aggregation</h3>
            <p className="text-sm">
              <strong>Data Sources:</strong> Anonymized batch records from AMC sites, quality-controlled optimal time determinations,
              verified against AMC SOPs.
            </p>
            <p className="text-sm mt-2">
              <strong>Privacy:</strong> All data is anonymized with no patient or operator identifiable information. Site-level aggregation only.
            </p>
          </div>

          <div>
            <h3 className="font-semibold mb-2">Interpretation</h3>
            <p className="text-sm">
              <strong>Recommended Starting Times:</strong> Based on median optimal times across sites. Provides a sensible initial guess
              but <strong>must be confirmed</strong> with local sweep.
            </p>
            <p className="text-sm mt-2">
              <strong>Regional Variations:</strong> May reflect local conditions (water, climate, etc.). Not causally explained - descriptive only.
              Use as guidance, not prescription.
            </p>
          </div>

          <div>
            <h3 className="font-semibold mb-2">Updates</h3>
            <p className="text-sm">
              Pattern data is updated as new batch records are submitted.
              Current data represents {nationalData['10%'].num_batches + nationalData['3%'].num_batches} batches
              from {Math.max(nationalData['10%'].num_sites, nationalData['3%'].num_sites)} sites.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
