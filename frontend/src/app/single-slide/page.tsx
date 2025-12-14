'use client'

import React, { useState } from 'react'
import { Upload, FileImage, AlertCircle } from 'lucide-react'
import axios from 'axios'

interface GradeResult {
  grade_numeric: number
  grade_label: string
  confidence: number
  status: string
  probabilities: number[]
}

export default function SingleSlidePage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<GradeResult | null>(null)
  const [error, setError] = useState<string>('')

  // Form metadata
  const [dilution, setDilution] = useState('10%')
  const [smearType, setSmearType] = useState('thin')
  const [stainTime, setStainTime] = useState(0)
  const [batchId, setBatchId] = useState('')

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      setPreview(URL.createObjectURL(file))
      setResult(null)
      setError('')
    }
  }

  const handleAnalyze = async () => {
    if (!selectedFile) return

    setLoading(true)
    setError('')

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)
      formData.append('dilution', dilution)
      formData.append('smear_type', smearType)
      formData.append('stain_time', stainTime.toString())
      formData.append('batch_id', batchId)

      const response = await axios.post('/api/grade-slide', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      setResult(response.data)
    } catch (err: any) {
      setError(err.response?.data?.message || 'Error analyzing slide')
    } finally {
      setLoading(false)
    }
  }

  const getGradeInfo = (grade: number) => {
    const gradeInfo = {
      1: {
        name: 'Under-stained',
        action: 'Increase staining time by 2-3 minutes. Check Giemsa working solution concentration and buffered water pH (should be 7.2).'
      },
      2: {
        name: 'Lightly stained',
        action: 'Increase staining time by 1-2 minutes. Verify Giemsa concentration is accurate and ensure stain solution is freshly prepared.'
      },
      3: {
        name: 'Optimal staining',
        action: 'No action needed - optimal staining quality for malaria diagnosis.'
      },
      4: {
        name: 'Over-stained',
        action: 'Decrease staining time by 1-2 minutes. Check for Giemsa precipitates and verify buffered water pH is exactly 7.2.'
      },
      5: {
        name: 'Deeply over-stained',
        action: 'Decrease staining time by 2-4 minutes. Replace Giemsa working solution and check stock Giemsa quality (perform QC check).'
      }
    }
    return gradeInfo[grade as keyof typeof gradeInfo] || { name: 'Unknown', action: '' }
  }

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-2">Single Slide Grading</h1>
      <p className="text-gray-600 mb-8">Upload a Giemsa-stained slide image to get automated quality grading (AMC Grades I-V)</p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Column - Upload */}
        <div>
          <div className="bg-white p-6 rounded-lg shadow mb-6">
            <h2 className="text-xl font-bold mb-4">Upload Slide Image</h2>

            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center mb-4">
              <input
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="hidden"
                id="file-upload"
              />
              <label htmlFor="file-upload" className="cursor-pointer">
                <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                <p className="text-sm text-gray-600">Click to upload slide image</p>
                <p className="text-xs text-gray-400 mt-2">JPG, PNG, TIF, or TIFF</p>
              </label>
            </div>

            {preview && (
              <div className="mb-4">
                <img src={preview} alt="Preview" className="w-full rounded" />
              </div>
            )}
          </div>

          {/* Metadata */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-bold mb-4">Slide Metadata (Optional)</h2>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Dilution</label>
                <select
                  value={dilution}
                  onChange={(e) => setDilution(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg"
                >
                  <option value="10%">10%</option>
                  <option value="3%">3%</option>
                  <option value="Unknown">Unknown</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Smear Type</label>
                <select
                  value={smearType}
                  onChange={(e) => setSmearType(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg"
                >
                  <option value="thin">Thin</option>
                  <option value="thick">Thick</option>
                  <option value="unknown">Unknown</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Staining Time (min)</label>
                <input
                  type="number"
                  value={stainTime}
                  onChange={(e) => setStainTime(parseInt(e.target.value))}
                  className="w-full px-3 py-2 border rounded-lg"
                  min="0"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Batch ID</label>
                <input
                  type="text"
                  value={batchId}
                  onChange={(e) => setBatchId(e.target.value)}
                  placeholder="Optional"
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Right Column - Results */}
        <div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-bold mb-4">Analysis Results</h2>

            {!selectedFile && (
              <div className="text-center py-12 text-gray-400">
                <FileImage className="w-16 h-16 mx-auto mb-4" />
                <p>Upload a slide image to begin analysis</p>
              </div>
            )}

            {selectedFile && !result && !loading && (
              <button
                onClick={handleAnalyze}
                className="w-full bg-primary text-white py-3 rounded-lg font-semibold hover:bg-blue-600 transition-colors"
              >
                Analyze Slide
              </button>
            )}

            {loading && (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
                <p className="text-gray-600">Analyzing slide...</p>
              </div>
            )}

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold text-red-800">Error</p>
                  <p className="text-sm text-red-600">{error}</p>
                </div>
              </div>
            )}

            {result && (
              <div>
                {/* Metrics */}
                <div className="grid grid-cols-3 gap-4 mb-6">
                  <div className="bg-gray-50 p-4 rounded-lg text-center">
                    <p className="text-sm text-gray-600 mb-1">Grade</p>
                    <p className="text-2xl font-bold">Grade {result.grade_label}</p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg text-center">
                    <p className="text-sm text-gray-600 mb-1">Confidence</p>
                    <p className="text-2xl font-bold">{(result.confidence * 100).toFixed(1)}%</p>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg text-center">
                    <p className="text-sm text-gray-600 mb-1">Status</p>
                    <p className={`text-2xl font-bold ${result.status === 'PASS' ? 'text-green-600' : 'text-red-600'}`}>
                      {result.status === 'PASS' ? '✅' : '❌'} {result.status}
                    </p>
                  </div>
                </div>

                <hr className="my-6" />

                {/* Pass/Fail Info */}
                {result.status === 'PASS' ? (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
                    <p className="font-semibold text-green-800 mb-2">
                      Slide Passed: Grade {result.grade_label} with {(result.confidence * 100).toFixed(1)}% confidence
                    </p>
                    <p className="text-sm text-green-700">
                      Grade III provides optimal color contrast for accurate malaria parasite identification.
                    </p>
                  </div>
                ) : (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                    <p className="font-semibold text-red-800 mb-2">
                      Slide Failed: Grade {result.grade_label} with {(result.confidence * 100).toFixed(1)}% confidence
                    </p>
                    <div className="mt-4">
                      <p className="font-semibold text-sm mb-2">Failure Diagnosis (AMC Guidelines)</p>
                      <p className="text-sm text-red-700 mb-2">
                        <strong>{getGradeInfo(result.grade_numeric).name}</strong>
                      </p>
                      <p className="text-sm text-gray-700">
                        {getGradeInfo(result.grade_numeric).action}
                      </p>
                    </div>
                  </div>
                )}

                {/* Probability Distribution */}
                <div>
                  <h3 className="font-semibold mb-3">Grade Probability Distribution</h3>
                  <div className="space-y-2">
                    {['I', 'II', 'III', 'IV', 'V'].map((grade, idx) => (
                      <div key={grade}>
                        <div className="flex justify-between text-sm mb-1">
                          <span>Grade {grade}</span>
                          <span>{(result.probabilities[idx] * 100).toFixed(1)}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-primary h-2 rounded-full"
                            style={{ width: `${result.probabilities[idx] * 100}%` }}
                          ></div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* AMC Grade Scale Reference */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-6">
            <h3 className="font-semibold mb-2 text-blue-900">AMC Grade Scale</h3>
            <ul className="text-sm space-y-1 text-blue-800">
              <li><strong>Grade I:</strong> Under-stained ❌</li>
              <li><strong>Grade II:</strong> Lightly stained ❌</li>
              <li><strong>Grade III:</strong> Optimal staining ✅</li>
              <li><strong>Grade IV:</strong> Over-stained ❌</li>
              <li><strong>Grade V:</strong> Deeply over-stained ❌</li>
            </ul>
            <p className="text-xs mt-2 text-blue-700">
              Per AMC guidelines, only Grade III provides optimal color contrast for accurate malaria parasite identification.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
