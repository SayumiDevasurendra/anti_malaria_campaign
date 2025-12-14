'use client'

import React, { useState } from 'react'
import { Upload, Clock, AlertCircle } from 'lucide-react'
import axios from 'axios'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts'

interface FileWithTime {
  file: File
  assignedTime: number
}

interface OptimalTimeResult {
  status: string
  optimal_minute?: number
  pass_probability?: number
  mean_grade?: number
  message: string
  passing_minutes?: number[]
  minute_analyses: { [key: number]: any }
}

export default function OptimalTimePage() {
  const [dilution, setDilution] = useState('10%')
  const [files, setFiles] = useState<FileWithTime[]>([])
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<OptimalTimeResult | null>(null)
  const [error, setError] = useState<string>('')

  const defaultRange = dilution === '10%' ? { min: 5, max: 15 } : { min: 30, max: 45 }
  const [minTime, setMinTime] = useState(defaultRange.min)
  const [maxTime, setMaxTime] = useState(defaultRange.max)
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.8)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const fileList = e.target.files
    if (fileList) {
      const newFiles: FileWithTime[] = Array.from(fileList).map((file, idx) => {
        // Try to extract time from filename
        const match = file.name.match(/(\d+)min/)
        const time = match ? parseInt(match[1]) : minTime + idx

        return { file, assignedTime: time }
      })
      setFiles(newFiles)
      setResult(null)
      setError('')
    }
  }

  const updateFileTime = (index: number, time: number) => {
    const updated = [...files]
    updated[index].assignedTime = time
    setFiles(updated)
  }

  const handleAnalyze = async () => {
    if (files.length === 0) return

    setLoading(true)
    setError('')

    try {
      const formData = new FormData()
      formData.append('dilution', dilution)
      formData.append('confidence_threshold', confidenceThreshold.toString())

      files.forEach((fileWithTime, idx) => {
        formData.append('files', fileWithTime.file)
        formData.append(`time_${idx}`, fileWithTime.assignedTime.toString())
      })

      const response = await axios.post('/api/optimal-time', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      setResult(response.data)
    } catch (err: any) {
      setError(err.response?.data?.message || 'Error analyzing sweep')
    } finally {
      setLoading(false)
    }
  }

  const getChartData = () => {
    if (!result?.minute_analyses) return []

    return Object.entries(result.minute_analyses)
      .map(([minute, analysis]: [string, any]) => ({
        minute: parseInt(minute),
        passProbability: analysis.pass_probability * 100,
        meanGrade: analysis.mean_grade
      }))
      .sort((a, b) => a.minute - b.minute)
  }

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-2">Optimal Staining Time Finder</h1>
      <p className="text-gray-600 mb-8">Upload minute-by-minute sweep images to find the earliest acceptable staining time</p>

      {/* Settings */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4 mb-8">
        <div className="bg-white p-4 rounded-lg shadow">
          <label className="block text-sm font-medium mb-2">Dilution Method</label>
          <select
            value={dilution}
            onChange={(e) => {
              setDilution(e.target.value)
              const range = e.target.value === '10%' ? { min: 5, max: 15 } : { min: 30, max: 45 }
              setMinTime(range.min)
              setMaxTime(range.max)
            }}
            className="w-full px-3 py-2 border rounded-lg"
          >
            <option value="10%">10% Rapid (5-15 min)</option>
            <option value="3%">3% Slow (30-45 min)</option>
          </select>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <label className="block text-sm font-medium mb-2">Min Time (min)</label>
          <input
            type="number"
            value={minTime}
            onChange={(e) => setMinTime(parseInt(e.target.value))}
            className="w-full px-3 py-2 border rounded-lg"
            min="1"
          />
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <label className="block text-sm font-medium mb-2">Max Time (min)</label>
          <input
            type="number"
            value={maxTime}
            onChange={(e) => setMaxTime(parseInt(e.target.value))}
            className="w-full px-3 py-2 border rounded-lg"
            min={minTime}
          />
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <label className="block text-sm font-medium mb-2">Pass Confidence</label>
          <input
            type="number"
            value={confidenceThreshold}
            onChange={(e) => setConfidenceThreshold(parseFloat(e.target.value))}
            className="w-full px-3 py-2 border rounded-lg"
            min="0.5"
            max="1"
            step="0.05"
          />
        </div>
      </div>

      {/* Upload Section */}
      <div className="bg-white p-6 rounded-lg shadow mb-8">
        <h2 className="text-xl font-bold mb-4">Upload Sweep Images</h2>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
          <p className="text-sm text-blue-800">
            <strong>Instructions:</strong> Upload images for each minute in the range ({minTime}-{maxTime} minutes).
            Name files as: <code>{dilution}_Xmin_[grade]_[smear].jpg</code> (e.g., <code>{dilution}_8min_III_thin.jpg</code>)
            or manually assign times below.
          </p>
        </div>

        <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center mb-4">
          <input
            type="file"
            accept="image/*"
            multiple
            onChange={handleFileChange}
            className="hidden"
            id="file-upload-sweep"
          />
          <label htmlFor="file-upload-sweep" className="cursor-pointer">
            <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
            <p className="text-sm text-gray-600">Click to upload multiple sweep images</p>
            <p className="text-xs text-gray-400 mt-2">JPG, PNG, TIF, or TIFF</p>
          </label>
        </div>

        {files.length > 0 && (
          <div>
            <p className="text-sm font-medium mb-3">Uploaded {files.length} images - Assign staining times:</p>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {files.map((fileWithTime, idx) => (
                <div key={idx} className="border rounded p-3">
                  <p className="text-sm font-medium truncate mb-2" title={fileWithTime.file.name}>
                    {fileWithTime.file.name}
                  </p>
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4 text-gray-500" />
                    <input
                      type="number"
                      value={fileWithTime.assignedTime}
                      onChange={(e) => updateFileTime(idx, parseInt(e.target.value))}
                      className="flex-1 px-2 py-1 border rounded text-sm"
                      min={minTime}
                      max={maxTime}
                    />
                    <span className="text-sm text-gray-600">min</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Analyze Button */}
      {files.length > 0 && !loading && (
        <button
          onClick={handleAnalyze}
          className="w-full bg-primary text-white py-3 rounded-lg font-semibold hover:bg-blue-600 transition-colors mb-8"
        >
          Analyze Sweep & Find Optimal Time
        </button>
      )}

      {loading && (
        <div className="text-center py-12 mb-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-gray-600">Analyzing minute-by-minute sweep...</p>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3 mb-8">
          <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold text-red-800">Error</p>
            <p className="text-sm text-red-600">{error}</p>
          </div>
        </div>
      )}

      {/* Results */}
      {result && (
        <div>
          <h2 className="text-2xl font-bold mb-6">Analysis Results</h2>

          {result.status === 'success' ? (
            <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-6">
              <p className="text-2xl font-bold text-green-800 mb-4">
                ✅ Optimal Staining Time Found: {result.optimal_minute} minutes
              </p>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <p className="text-sm text-green-700">Optimal Time</p>
                  <p className="text-xl font-bold text-green-900">{result.optimal_minute} min</p>
                </div>
                <div>
                  <p className="text-sm text-green-700">Pass Probability</p>
                  <p className="text-xl font-bold text-green-900">{((result.pass_probability || 0) * 100).toFixed(1)}%</p>
                </div>
                <div>
                  <p className="text-sm text-green-700">Mean Grade</p>
                  <p className="text-xl font-bold text-green-900">{(result.mean_grade || 0).toFixed(1)}</p>
                </div>
              </div>
              {result.passing_minutes && result.passing_minutes.length > 1 && (
                <p className="text-sm text-green-700 mt-4">
                  <strong>All Passing Minutes:</strong> {result.passing_minutes.join(', ')} min
                </p>
              )}
            </div>
          ) : (
            <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-6">
              <p className="text-xl font-bold text-red-800 mb-2">❌ {result.message}</p>
              <p className="text-sm text-red-600">
                No minute in the sweep achieved passing grade. Review staining protocol.
              </p>
            </div>
          )}

          {/* Chart */}
          <div className="bg-white p-6 rounded-lg shadow mb-6">
            <h3 className="text-lg font-bold mb-4">Pass Probability Across Minutes</h3>
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={getChartData()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="minute" label={{ value: 'Staining Time (minutes)', position: 'insideBottom', offset: -5 }} />
                <YAxis domain={[0, 100]} label={{ value: 'Pass Probability (%)', angle: -90, position: 'insideLeft' }} />
                <Tooltip />
                <Legend />
                <ReferenceLine y={confidenceThreshold * 100} stroke="red" strokeDasharray="3 3" label="Threshold" />
                {result.optimal_minute && (
                  <ReferenceLine x={result.optimal_minute} stroke="green" strokeDasharray="3 3" label="Optimal" />
                )}
                <Line type="monotone" dataKey="passProbability" stroke="#1f77b4" strokeWidth={3} name="Pass Probability" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Detailed Table */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-bold mb-4">Detailed Minute-by-Minute Results</h3>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Time (min)</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Mean Grade</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Pass Probability</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Confidence</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {Object.entries(result.minute_analyses)
                    .sort(([a], [b]) => parseInt(a) - parseInt(b))
                    .map(([minute, analysis]: [string, any]) => (
                      <tr key={minute}>
                        <td className="px-6 py-4 whitespace-nowrap font-medium">{minute}</td>
                        <td className="px-6 py-4 whitespace-nowrap">{analysis.mean_grade.toFixed(1)}</td>
                        <td className="px-6 py-4 whitespace-nowrap">{(analysis.pass_probability * 100).toFixed(1)}%</td>
                        <td className="px-6 py-4 whitespace-nowrap">{(analysis.mean_confidence * 100).toFixed(1)}%</td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={analysis.is_pass ? 'text-green-600 font-semibold' : 'text-red-600'}>
                            {analysis.is_pass ? '✅ Pass' : '❌ Fail'}
                          </span>
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
