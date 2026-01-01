'use client'

import React, { useState } from 'react'
import { Upload, Clock, AlertCircle, CheckCircle, ArrowRight } from 'lucide-react'
import axios from 'axios'

interface TimeRecommendation {
  grade_numeric: number
  grade_label: string
  confidence: number
  status: 'OPTIMAL' | 'NOT_OPTIMAL'
  time_delta: number
  recommended_time: number
  recommendation_message: string
  reason: string
  probabilities: number[]
  metadata: {
    current_time: number
    dilution: string
    smear_type: string
  }
}

interface AttemptHistory {
  time: number
  grade: string
  status: string
  recommendation: string
}

export default function OptimalTimePage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<TimeRecommendation | null>(null)
  const [error, setError] = useState<string>('')
  const [attemptHistory, setAttemptHistory] = useState<AttemptHistory[]>([])
  const [validationError, setValidationError] = useState<string>('')

  // Form inputs
  const [dilution, setDilution] = useState('10%')
  const [smearType, setSmearType] = useState('Thin')
  const [currentTime, setCurrentTime] = useState<number>(5)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      setPreview(URL.createObjectURL(file))
      setResult(null)
      setError('')
    }
  }

  const validateStainTime = (time: number, dilutionMethod: string): string => {
    if (dilutionMethod === '10%') {
      if (time < 5 || time > 20) {
        return 'For 10% dilution, please enter a value between 5-20 minutes'
      }
    } else if (dilutionMethod === '3%') {
      if (time < 30 || time > 45) {
        return 'For 3% dilution, please enter a value between 30-45 minutes'
      }
    }
    return ''
  }

  const handleAnalyze = async () => {
    if (!selectedFile || !currentTime) return

    // Validate stain time
    const error = validateStainTime(currentTime, dilution)
    if (error) {
      setValidationError(error)
      return
    }

    setLoading(true)
    setError('')
    setValidationError('')

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)
      formData.append('current_time', currentTime.toString())
      formData.append('dilution', dilution)
      formData.append('smear_type', smearType)

      const response = await axios.post('http://localhost:8000/api/recommend-time', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      const data: TimeRecommendation = response.data
      setResult(data)

      // Add to history
      setAttemptHistory(prev => [...prev, {
        time: currentTime,
        grade: data.grade_label,
        status: data.status,
        recommendation: data.recommendation_message
      }])

      // If not optimal, suggest updating current_time to recommended time
      if (data.status === 'NOT_OPTIMAL') {
        setCurrentTime(Math.round(data.recommended_time))
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Error analyzing slide')
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setSelectedFile(null)
    setPreview('')
    setResult(null)
    setError('')
    setValidationError('')
    setAttemptHistory([])
    setCurrentTime(dilution === '10%' ? 5 : 30)
  }

  const handleTryAgain = () => {
    setSelectedFile(null)
    setPreview('')
    setResult(null)
    setError('')
    // Keep history and suggested time
  }

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-2">Optimal Time Finder</h1>
      <p className="text-gray-600 mb-8">
        Upload slide images one at a time to find the optimal staining time for your batch through iterative recommendations
      </p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left Column - Upload & Input */}
        <div>
          {/* Settings */}
          <div className="bg-white p-6 rounded-lg shadow mb-6">
            <h2 className="text-xl font-bold mb-4">Slide Information</h2>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium mb-2">Dilution Method</label>
                <select
                  value={dilution}
                  onChange={(e) => {
                    setDilution(e.target.value)
                    setCurrentTime(e.target.value === '10%' ? 5 : 30)
                    setValidationError('')
                  }}
                  className="w-full px-3 py-2 border rounded-lg"
                  disabled={attemptHistory.length > 0}
                >
                  <option value="10%">10% Rapid</option>
                  <option value="3%">3% Slow</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Smear Type</label>
                <select
                  value={smearType}
                  onChange={(e) => setSmearType(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg"
                  disabled={attemptHistory.length > 0}
                >
                  <option value="Thin">Thin</option>
                  <option value="Thick">Thick</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Current Staining Time (minutes) {result?.status === 'NOT_OPTIMAL' && '⏱️ Updated'}
              </label>
              <input
                type="number"
                value={currentTime}
                onChange={(e) => {
                  setCurrentTime(parseFloat(e.target.value))
                  setValidationError('')
                }}
                className="w-full px-3 py-2 border rounded-lg"
                min="1"
                step="0.5"
                placeholder={dilution === '10%' ? '5' : '30'}
              />
              <p className="text-xs text-gray-500 mt-1">
                Time at which the slide was stained
              </p>
              {validationError && (
                <p className="text-xs text-red-600 mt-1 font-medium">
                  {validationError}
                </p>
              )}
            </div>
          </div>

          {/* Upload */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-bold mb-4">Upload Slide Image</h2>

            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center mb-4">
              <input
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="hidden"
                id="file-upload-time"
              />
              <label htmlFor="file-upload-time" className="cursor-pointer">
                <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                <p className="text-sm text-gray-600">Click to upload slide image</p>
                <p className="text-xs text-gray-400 mt-2">JPG, PNG, TIF, or TIFF</p>
              </label>
            </div>

            {preview && (
              <div className="mb-4">
                <img src={preview} alt="Preview" className="w-full rounded border" />
              </div>
            )}

            {selectedFile && !loading && (
              <button
                onClick={handleAnalyze}
                className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
              >
                <Clock className="w-5 h-5" />
                Analyze & Get Time Recommendation
              </button>
            )}

            {loading && (
              <div className="text-center py-6">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-600">Analyzing slide...</p>
              </div>
            )}
          </div>

          {/* Attempt History */}
          {attemptHistory.length > 0 && (
            <div className="bg-white p-6 rounded-lg shadow mt-6">
              <h2 className="text-xl font-bold mb-4">Attempt History</h2>
              <div className="space-y-3">
                {attemptHistory.map((attempt, idx) => (
                  <div key={idx} className="border-l-4 border-gray-300 pl-4 py-2">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-semibold">Attempt {idx + 1}: {attempt.time} min</span>
                      <span className={`text-sm font-medium ${attempt.status === 'OPTIMAL' ? 'text-green-600' : 'text-orange-600'}`}>
                        {attempt.status === 'OPTIMAL' ? '✅ Optimal' : '⏱️ Grade ' + attempt.grade}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Right Column - Results */}
        <div>
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3 mb-6">
              <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold text-red-800">Error</p>
                <p className="text-sm text-red-600">{error}</p>
              </div>
            </div>
          )}

          {!result && !error && (
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-bold mb-4">Instructions</h2>
              <div className="space-y-4 text-gray-700">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h3 className="font-semibold text-blue-900 mb-2">How It Works:</h3>
                  <ol className="list-decimal list-inside space-y-2 text-sm">
                    <li>Enter the time (in minutes) at which you stained the slide</li>
                    <li>Upload the slide image</li>
                    <li>Model will predict the grade and recommend a time adjustment</li>
                    <li>If not Grade III, stain a new slide at the recommended time</li>
                    <li>Repeat until Grade III is achieved</li>
                  </ol>
                </div>

                <div>
                  <h3 className="font-semibold mb-2">Example Workflow:</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center gap-2 text-gray-600">
                      <ArrowRight className="w-4 h-4" />
                      <span>Upload image at 6 min → "Try 11-13 min"</span>
                    </div>
                    <div className="flex items-center gap-2 text-gray-600">
                      <ArrowRight className="w-4 h-4" />
                      <span>Upload image at 11 min → "✅ Optimal! 11 min is your time"</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {result && (
            <div className="space-y-6">
              {/* Main Result Card */}
              <div className={`${result.status === 'OPTIMAL' ? 'bg-green-50 border-green-200' : 'bg-orange-50 border-orange-200'} border-2 rounded-lg p-6`}>
                <div className="flex items-start gap-4 mb-4">
                  {result.status === 'OPTIMAL' ? (
                    <CheckCircle className="w-12 h-12 text-green-600 flex-shrink-0" />
                  ) : (
                    <Clock className="w-12 h-12 text-orange-600 flex-shrink-0" />
                  )}
                  <div className="flex-1">
                    <h2 className={`text-2xl font-bold mb-2 ${result.status === 'OPTIMAL' ? 'text-green-900' : 'text-orange-900'}`}>
                      {result.status === 'OPTIMAL' ? '✅ Optimal Time Found!' : '⏱️ Time Adjustment Needed'}
                    </h2>
                    <p className={`text-sm ${result.status === 'OPTIMAL' ? 'text-green-800' : 'text-orange-800'}`}>
                      Current Time: {result.metadata.current_time} minutes
                    </p>
                  </div>
                </div>

                {/* Metrics Grid */}
                <div className="grid grid-cols-3 gap-4 mb-4">
                  <div className="bg-white/50 p-3 rounded-lg text-center">
                    <p className="text-xs text-gray-600 mb-1">Grade</p>
                    <p className="text-xl font-bold">Grade {result.grade_label}</p>
                  </div>
                  <div className="bg-white/50 p-3 rounded-lg text-center">
                    <p className="text-xs text-gray-600 mb-1">Confidence</p>
                    <p className="text-xl font-bold">{(result.confidence * 100).toFixed(1)}%</p>
                  </div>
                  <div className="bg-white/50 p-3 rounded-lg text-center">
                    <p className="text-xs text-gray-600 mb-1">Time Delta</p>
                    <p className="text-xl font-bold">{result.time_delta > 0 ? '+' : ''}{result.time_delta.toFixed(1)} min</p>
                  </div>
                </div>

                <hr className="my-4 border-gray-300" />

                {/* Recommendation Message */}
                <div className="mb-4">
                  <p className={`font-semibold text-lg mb-2 ${result.status === 'OPTIMAL' ? 'text-green-900' : 'text-orange-900'}`}>
                    {result.status === 'OPTIMAL' ? '🎯 Recommendation:' : '💡 Next Step:'}
                  </p>
                  <p className={`${result.status === 'OPTIMAL' ? 'text-green-800' : 'text-orange-800'}`}>
                    {result.recommendation_message}
                  </p>
                </div>

                {/* Reason */}
                <div className="bg-white/70 rounded-lg p-3">
                  <p className="text-sm text-gray-700">
                    <strong>Reason:</strong> {result.reason}
                  </p>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="bg-white p-6 rounded-lg shadow">
                {result.status === 'OPTIMAL' ? (
                  <div className="space-y-3">
                    <button
                      onClick={handleReset}
                      className="w-full bg-green-600 text-white py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors"
                    >
                      ✅ Save & Start New Batch
                    </button>
                    <p className="text-sm text-gray-600 text-center">
                      Optimal time for this batch ({result.metadata.dilution} dilution, {result.metadata.smear_type} smear):
                      <strong> {result.metadata.current_time} minutes</strong>
                    </p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    <button
                      onClick={handleTryAgain}
                      className="w-full bg-orange-600 text-white py-3 rounded-lg font-semibold hover:bg-orange-700 transition-colors flex items-center justify-center gap-2"
                    >
                      <ArrowRight className="w-5 h-5" />
                      Try Another Slide at {Math.round(result.recommended_time)} min
                    </button>
                    <button
                      onClick={handleReset}
                      className="w-full bg-gray-200 text-gray-700 py-2 rounded-lg font-medium hover:bg-gray-300 transition-colors"
                    >
                      Reset & Start Over
                    </button>
                  </div>
                )}
              </div>

              {/* Probability Distribution */}
              <div className="bg-white p-6 rounded-lg shadow">
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
                          className={`h-2 rounded-full ${idx === 2 ? 'bg-green-600' : 'bg-blue-600'}`}
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
      </div>

      {/* Info Box */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mt-8">
        <h2 className="text-xl font-bold text-blue-900 mb-4">About Optimal Time Finder</h2>
        <div className="space-y-3 text-blue-800 text-sm">
          <p>
            <strong>Purpose:</strong> This tool uses AI to predict the optimal staining time for your batch through an iterative process.
          </p>
          <p>
            <strong>How it works:</strong> Upload images one at a time with their staining times. The model predicts the grade and recommends
            time adjustments until Grade III (optimal) is achieved.
          </p>
          <p>
            <strong>Note:</strong> The recommended time is based on the model's prediction. Always verify with visual inspection and
            follow AMC SOP guidelines.
          </p>
        </div>
      </div>
    </div>
  )
}
