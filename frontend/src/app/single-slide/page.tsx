'use client'

import React, { useState } from 'react'
import { Upload, FileImage, AlertCircle } from 'lucide-react'
import axios from 'axios'

interface GradeResult {
  grade_numeric: number
  grade_label: string
  confidence: number
  status: string
  reason: string
  overlay_image_base64?: string
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
  const [smearType, setSmearType] = useState('Thin')
  const [stainTime, setStainTime] = useState<number>(5)
  const [validationError, setValidationError] = useState<string>('')

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
      if (time < 27 || time > 41) {
        return 'For 3% dilution, please enter a value between 27-41 minutes'
      }
    }
    return ''
  }

  const handleAnalyze = async () => {
    if (!selectedFile) return

    // Validate stain time
    const error = validateStainTime(stainTime, dilution)
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
      formData.append('dilution', dilution)
      formData.append('smear_type', smearType)
      formData.append('stain_time', stainTime.toString())
      formData.append('return_overlay_base64', 'true')

      const response = await axios.post('http://localhost:8000/api/explain-grade', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })

      setResult(response.data)
    } catch (err: any) {
      setError(err.response?.data?.error || 'Error analyzing slide')
    } finally {
      setLoading(false)
    }
  }

  const getSopChecklist = (grade: number) => {
    const checklists = {
      1: [
        'Verify staining time was sufficient for the dilution method',
        'Check Giemsa working solution concentration (3% or 10%)',
        'Confirm buffered water pH = 7.2 ± 0.1',
        'Verify stock Giemsa quality (perform QC check)',
        'Ensure methanol fixation was adequate (thin smears)',
        'Check that stain solution is freshly prepared',
      ],
      2: [
        'Verify staining time was sufficient for the dilution method',
        'Check Giemsa working solution concentration',
        'Confirm buffered water pH = 7.2 ± 0.1',
        'Verify stock Giemsa quality',
        'Ensure proper fixation',
      ],
      3: [
        'Proceed with malaria parasite examination',
        'Document staining time and conditions for batch records',
      ],
      4: [
        'Verify staining time (may be too long for dilution method)',
        'Inspect stain solution for visible precipitates',
        'Confirm buffered water pH = 7.2 ± 0.1',
        'Check if working solution concentration is too high',
        'Verify stock Giemsa quality and expiration date',
        'Filter stain solution to remove precipitates if present',
      ],
      5: [
        'Verify staining time (likely too long)',
        'Inspect stain solution for precipitates',
        'Confirm buffered water pH = 7.2 ± 0.1',
        'Check working solution concentration',
        'Replace Giemsa working solution if necessary',
        'Review methanol fixation protocol',
      ]
    }
    return checklists[grade as keyof typeof checklists] || []
  }

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-2">Single Slide Grading</h1>
      <p className="text-gray-600 mb-8">Upload a Giemsa-stained slide image to get automated quality grading with GradCAM explanation</p>

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
                <p className="text-sm font-medium mb-2">Original Image:</p>
                <img src={preview} alt="Preview" className="w-full rounded border" />
              </div>
            )}
          </div>

          {/* Metadata */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h2 className="text-xl font-bold mb-4">Slide Information</h2>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <label className="block text-sm font-medium mb-2">Dilution Method</label>
                <select
                  value={dilution}
                  onChange={(e) => {
                    setDilution(e.target.value)
                    setStainTime(e.target.value === '10%' ? 5 : 27)
                    setValidationError('')
                  }}
                  className="w-full px-3 py-2 border rounded-lg"
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
                >
                  <option value="Thin">Thin</option>
                  <option value="Thick">Thick</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">
                Current Staining Time (minutes) <span className="text-red-500">*</span>
              </label>
              <input
                type="number"
                value={stainTime}
                onChange={(e) => {
                  setStainTime(parseFloat(e.target.value))
                  setValidationError('')
                }}
                className="w-full px-3 py-2 border rounded-lg"
                min="1"
                step="0.5"
                placeholder={dilution === '10%' ? '5' : '27'}
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
                disabled={!stainTime}
                className={`w-full py-3 rounded-lg font-semibold transition-colors ${
                  !stainTime
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
              >
                Analyze Slide with GradCAM
              </button>
            )}

            {loading && (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
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
                      {result.status === 'PASS' ? '✅' : '❌'}
                    </p>
                  </div>
                </div>

                {/* GradCAM Visualization */}
                {result.overlay_image_base64 && (
                  <div className="mb-6">
                    <h3 className="font-semibold mb-3">📊 GradCAM Visualization</h3>
                    <img
                      src={`data:image/png;base64,${result.overlay_image_base64}`}
                      alt="GradCAM Overlay"
                      className="w-full rounded border border-gray-300"
                    />
                    <p className="text-xs text-gray-500 mt-2">
                      Heatmap shows which regions the model focused on for classification
                    </p>
                  </div>
                )}

                <hr className="my-6" />

                {/* Explanation */}
                <div className="mb-6">
                  <h3 className="font-semibold mb-2">💡 Explanation</h3>
                  <p className="text-sm text-gray-700 bg-gray-50 p-4 rounded-lg">
                    {result.reason}
                  </p>
                </div>

                {/* Status Message */}
                {result.status === 'PASS' ? (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
                    <p className="font-semibold text-green-800 mb-2">
                      ✅ Slide Passed: Grade {result.grade_label}
                    </p>
                    <p className="text-sm text-green-700">
                      Grade III provides optimal color contrast for accurate malaria parasite identification.
                    </p>
                  </div>
                ) : (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                    <p className="font-semibold text-red-800 mb-2">
                      ❌ Slide Failed: Grade {result.grade_label}
                    </p>
                    <p className="text-sm text-red-700 mb-4">
                      {result.reason}
                    </p>
                  </div>
                )}

                {/* SOP Checklist */}
                {result.status === 'FAIL' && (
                  <div className="mb-6">
                    <h3 className="font-semibold mb-3">📋 Troubleshooting Checklist (AMC MM-SOP-03C)</h3>
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                      <ul className="space-y-2">
                        {getSopChecklist(result.grade_numeric).map((item, idx) => (
                          <li key={idx} className="text-sm flex items-start gap-2">
                            <span className="text-yellow-600">□</span>
                            <span>{item}</span>
                          </li>
                        ))}
                        <li className="text-sm flex items-start gap-2 text-red-600 font-medium">
                          <span>□</span>
                          <span>Consult supervisor if issue persists</span>
                        </li>
                      </ul>
                    </div>
                  </div>
                )}

                {/* Probability Distribution */}
                {result.probabilities && result.probabilities.length > 0 && (
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
                              className="bg-blue-600 h-2 rounded-full"
                              style={{ width: `${result.probabilities[idx] * 100}%` }}
                            ></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
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
