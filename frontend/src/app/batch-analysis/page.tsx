'use client'

import React, { useState } from 'react'
import { Upload, Download } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ScatterChart, Scatter, LineChart, Line } from 'recharts'

interface BatchData {
  batch_id: string
  site?: string
  dilution: string
  optimal_minute: number
  pass_probability: number
  mean_grade: number
  date?: string
}

export default function BatchAnalysisPage() {
  const [data, setData] = useState<BatchData[]>([])
  const [analysisType, setAnalysisType] = useState<'single' | 'multi' | 'site'>('multi')
  const [dilutionFilter, setDilutionFilter] = useState<string[]>(['10%', '3%'])

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (event) => {
        const text = event.target?.result as string
        const rows = text.split('\n').map(row => row.split(','))
        const headers = rows[0]
        const batchData: BatchData[] = rows.slice(1)
          .filter(row => row.length === headers.length && row[0])
          .map(row => {
            const obj: any = {}
            headers.forEach((header, idx) => {
              obj[header.trim()] = row[idx]?.trim()
            })
            return {
              batch_id: obj.batch_id,
              site: obj.site,
              dilution: obj.dilution,
              optimal_minute: parseFloat(obj.optimal_minute),
              pass_probability: parseFloat(obj.pass_probability),
              mean_grade: parseFloat(obj.mean_grade),
              date: obj.date
            }
          })
        setData(batchData)
      }
      reader.readAsText(file)
    }
  }

  const loadSampleData = () => {
    const sampleData: BatchData[] = [
      { batch_id: 'BATCH_001', site: 'AMC_HQ', dilution: '10%', optimal_minute: 8, pass_probability: 0.92, mean_grade: 3.4, date: '2025-01-10' },
      { batch_id: 'BATCH_002', site: 'AMC_HQ', dilution: '3%', optimal_minute: 32, pass_probability: 0.88, mean_grade: 3.2, date: '2025-01-11' },
      { batch_id: 'BATCH_003', site: 'Regional_A', dilution: '10%', optimal_minute: 9, pass_probability: 0.85, mean_grade: 3.1, date: '2025-01-12' },
      { batch_id: 'BATCH_004', site: 'Regional_B', dilution: '10%', optimal_minute: 7, pass_probability: 0.90, mean_grade: 3.5, date: '2025-01-13' },
      { batch_id: 'BATCH_005', site: 'Regional_A', dilution: '3%', optimal_minute: 35, pass_probability: 0.87, mean_grade: 3.3, date: '2025-01-14' },
    ]
    setData(sampleData)
  }

  const filteredData = data.filter(d => dilutionFilter.includes(d.dilution))

  const avgOptimalTime = filteredData.length > 0
    ? (filteredData.reduce((sum, d) => sum + d.optimal_minute, 0) / filteredData.length).toFixed(1)
    : '0'

  const avgPassProb = filteredData.length > 0
    ? (filteredData.reduce((sum, d) => sum + d.pass_probability, 0) / filteredData.length).toFixed(3)
    : '0'

  const uniqueSites = new Set(filteredData.map(d => d.site).filter(Boolean)).size

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-2">Batch Analysis</h1>
      <p className="text-gray-600 mb-8">Compare optimal staining times across batches and sites</p>

      {/* Settings */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-white p-4 rounded-lg shadow">
          <label className="block text-sm font-medium mb-2">Analysis Type</label>
          <select
            value={analysisType}
            onChange={(e) => setAnalysisType(e.target.value as any)}
            className="w-full px-3 py-2 border rounded-lg"
          >
            <option value="single">Single Batch</option>
            <option value="multi">Multi-Batch Comparison</option>
            <option value="site">Site-Level Analysis</option>
          </select>
        </div>

        <div className="bg-white p-4 rounded-lg shadow col-span-2">
          <label className="block text-sm font-medium mb-2">Filter by Dilution</label>
          <div className="flex gap-4">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={dilutionFilter.includes('10%')}
                onChange={(e) => {
                  if (e.target.checked) {
                    setDilutionFilter([...dilutionFilter, '10%'])
                  } else {
                    setDilutionFilter(dilutionFilter.filter(d => d !== '10%'))
                  }
                }}
              />
              <span>10%</span>
            </label>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={dilutionFilter.includes('3%')}
                onChange={(e) => {
                  if (e.target.checked) {
                    setDilutionFilter([...dilutionFilter, '3%'])
                  } else {
                    setDilutionFilter(dilutionFilter.filter(d => d !== '3%'))
                  }
                }}
              />
              <span>3%</span>
            </label>
          </div>
        </div>
      </div>

      {/* Upload Section */}
      <div className="bg-white p-6 rounded-lg shadow mb-8">
        <h2 className="text-xl font-bold mb-4">Upload Batch Data</h2>

        <div className="flex gap-4">
          <div className="flex-1 border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
            <input
              type="file"
              accept=".csv"
              onChange={handleFileUpload}
              className="hidden"
              id="file-upload-batch"
            />
            <label htmlFor="file-upload-batch" className="cursor-pointer">
              <Upload className="w-10 h-10 mx-auto mb-3 text-gray-400" />
              <p className="text-sm text-gray-600">Upload batch data CSV</p>
            </label>
          </div>

          <button
            onClick={loadSampleData}
            className="px-6 py-3 bg-gray-100 hover:bg-gray-200 rounded-lg font-medium"
          >
            Load Sample Data
          </button>
        </div>
      </div>

      {/* Summary Statistics */}
      {data.length > 0 && (
        <>
          <div className="grid grid-cols-4 gap-4 mb-8">
            <div className="bg-white p-6 rounded-lg shadow text-center">
              <p className="text-sm text-gray-600 mb-1">Total Batches</p>
              <p className="text-3xl font-bold">{filteredData.length}</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow text-center">
              <p className="text-sm text-gray-600 mb-1">Unique Sites</p>
              <p className="text-3xl font-bold">{uniqueSites || 'N/A'}</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow text-center">
              <p className="text-sm text-gray-600 mb-1">Avg Optimal Time</p>
              <p className="text-3xl font-bold">{avgOptimalTime} min</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow text-center">
              <p className="text-sm text-gray-600 mb-1">Avg Pass Prob</p>
              <p className="text-3xl font-bold">{(parseFloat(avgPassProb) * 100).toFixed(1)}%</p>
            </div>
          </div>

          {/* Data Table */}
          <div className="bg-white p-6 rounded-lg shadow mb-8">
            <h2 className="text-xl font-bold mb-4">Batch Records</h2>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Batch ID</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Site</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Dilution</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Optimal Time</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Pass Prob</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Mean Grade</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredData.map((batch, idx) => (
                    <tr key={idx}>
                      <td className="px-6 py-4 whitespace-nowrap font-medium">{batch.batch_id}</td>
                      <td className="px-6 py-4 whitespace-nowrap">{batch.site || 'N/A'}</td>
                      <td className="px-6 py-4 whitespace-nowrap">{batch.dilution}</td>
                      <td className="px-6 py-4 whitespace-nowrap">{batch.optimal_minute} min</td>
                      <td className="px-6 py-4 whitespace-nowrap">{(batch.pass_probability * 100).toFixed(1)}%</td>
                      <td className="px-6 py-4 whitespace-nowrap">{batch.mean_grade.toFixed(1)}</td>
                      <td className="px-6 py-4 whitespace-nowrap">{batch.date || 'N/A'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Visualizations */}
          {analysisType === 'multi' && (
            <div className="space-y-8">
              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-bold mb-4">Optimal Time Distribution by Dilution</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={filteredData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="dilution" />
                    <YAxis label={{ value: 'Optimal Time (min)', angle: -90, position: 'insideLeft' }} />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="optimal_minute" fill="#1f77b4" name="Optimal Time" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-bold mb-4">Pass Probability vs Optimal Time</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <ScatterChart>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="optimal_minute" name="Optimal Time" label={{ value: 'Optimal Time (min)', position: 'insideBottom', offset: -5 }} />
                    <YAxis dataKey="pass_probability" name="Pass Probability" label={{ value: 'Pass Probability', angle: -90, position: 'insideLeft' }} />
                    <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                    <Legend />
                    <Scatter name="Batches" data={filteredData} fill="#1f77b4" />
                  </ScatterChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {analysisType === 'site' && (
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-bold mb-4">Optimal Time by Site and Dilution</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={filteredData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="site" />
                  <YAxis label={{ value: 'Optimal Time (min)', angle: -90, position: 'insideLeft' }} />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="optimal_minute" fill="#1f77b4" name="Optimal Time" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </>
      )}

      {data.length === 0 && (
        <div className="text-center py-12 text-gray-400">
          <Upload className="w-16 h-16 mx-auto mb-4" />
          <p>Upload batch data CSV or load sample data to begin analysis</p>
        </div>
      )}
    </div>
  )
}
