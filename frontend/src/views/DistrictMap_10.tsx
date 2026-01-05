"use client";

import React, { useState } from "react";
import { DistrictMapSVG_10 } from "../components/DistrictMapSVG_10";
import { DistrictPrediction_10 } from "../types/types_10";
import { Button_10 } from "../components/Button_10";
import { Select_10 } from "../components/Select_10";
import { Input_10 } from "../components/Input_10";
import { Card_10 } from "../components/Card_10";
import { forecastClimate_10, forecastImportation_10 } from "../utils/api_10";
import { MONTHS_10, DISTRICTS_10, DISTRICT_DISPLAY_NAMES_10 } from "../utils/constants_10";

// District name mapping if needed (SVG names to Backend names)
// Currently they seem to match the constants.
const DISTRICT_NAMES = DISTRICTS_10;

export const DistrictMap_10 = () => {
    const [year, setYear] = useState(new Date().getFullYear());
    const [month, setMonth] = useState(new Date().getMonth() + 1);
    const [vizMode, setVizMode] = useState<"risk" | "pressure">("risk");
    const [predictions, setPredictions] = useState<Record<string, DistrictPrediction_10>>({});
    const [selectedDistrict, setSelectedDistrict] = useState<DistrictPrediction_10 | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        const newPredictions: Record<string, DistrictPrediction_10> = {};

        try {
            // Fetch for all districts in parallel
            await Promise.all(DISTRICT_NAMES.map(async (name) => {
                try {
                    const [climate, importation] = await Promise.all([
                        forecastClimate_10({ district: name, year, month }),
                        forecastImportation_10({ district: name, year })
                    ]);

                    const riskScore = climate.forecasted_climatic_receptivity;
                    let riskLevel: "Low" | "Moderate" | "High" | "Critical" = "Low"; // Keeping types but using for display
                    let displayRisk: string = "No Risk";

                    if (riskScore >= 1.5) displayRisk = "High Risk";
                    else if (riskScore >= 1.0) displayRisk = "Medium Risk";
                    else if (riskScore >= 0.5) displayRisk = "Low Risk";
                    else displayRisk = "No Risk";

                    newPredictions[name] = {
                        id: name,
                        name,
                        riskLevel: riskScore >= 1.5 ? "Critical" : riskScore >= 1.0 ? "High" : riskScore >= 0.5 ? "Moderate" : "Low",
                        cases: Math.round(importation.forecasted_national_imported_cases),
                        rainfall: climate.forecasted_rainfall,
                        temperature: climate.forecasted_temperature,
                        humidity: climate.forecasted_humidity,
                        importationPressure: importation.district_monthly_importation_pressure,
                        details: `Rainfall: ${climate.forecasted_rainfall.toFixed(1)}mm, Temperature: ${climate.forecasted_temperature.toFixed(1)}°C. Importation Pressure: ${importation.district_monthly_importation_pressure.toFixed(2)}.`
                    };
                } catch (err) {
                    console.error(`Failed to fetch for ${name}`, err);
                }
            }));

            setPredictions(newPredictions);
            if (selectedDistrict) {
                setSelectedDistrict(newPredictions[selectedDistrict.name] || null);
            }
        } catch (err: any) {
            setError("Failed to fetch district data. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    const handleDistrictClick = (id: string, name: string) => {
        const prediction = predictions[name];
        if (prediction) {
            setSelectedDistrict(prediction);
        } else {
            setSelectedDistrict({
                id,
                name,
                riskLevel: "Low",
                cases: 0,
                rainfall: 0,
                temperature: 0,
                humidity: 0,
                importationPressure: 0,
                details: "No data available for the selected period. Please click 'Generate Map Data'."
            });
        }
    };

    return (
        <div className="min-h-screen bg-slate-50 py-8">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold text-slate-900">District-wise Malaria Risk Map</h1>
                    <p className="mt-2 text-lg text-slate-600">
                        Analyze Sri Lanka's malaria vulnerability by risk score or importation pressure.
                    </p>
                </div>

                {/* Controls */}
                <Card_10 className="mb-8">
                    <div className="space-y-6">
                        <form onSubmit={handleSubmit} className="flex flex-wrap items-end gap-4">
                            <div className="w-full md:w-32">
                                <Input_10
                                    label="Year"
                                    type="number"
                                    value={year}
                                    onChange={(e) => setYear(Number(e.target.value))}
                                    min={2026}
                                    max={2050}
                                />
                            </div>
                            <div className="w-full md:w-48">
                                <Select_10
                                    label="Month"
                                    value={month}
                                    onChange={(e) => setMonth(Number(e.target.value))}
                                    options={MONTHS_10}
                                />
                            </div>
                            <Button_10 type="submit" isLoading={loading} className="md:w-48">
                                Generate Map Data
                            </Button_10>
                            {error && <p className="text-red-600 text-sm mb-2">{error}</p>}
                        </form>

                        <div className="flex items-center gap-8 pt-4 border-t border-slate-100">
                            <span className="text-sm font-medium text-slate-700">Visualization Mode:</span>
                            <div className="flex items-center gap-6">
                                <label className="flex items-center gap-2 cursor-pointer group">
                                    <input
                                        type="radio"
                                        name="vizMode"
                                        checked={vizMode === "risk"}
                                        onChange={() => setVizMode("risk")}
                                        className="w-4 h-4 text-blue-600 border-slate-300 focus:ring-blue-500"
                                    />
                                    <span className="text-sm text-slate-600 group-hover:text-slate-900">Risk Score</span>
                                </label>
                                <label className="flex items-center gap-2 cursor-pointer group">
                                    <input
                                        type="radio"
                                        name="vizMode"
                                        checked={vizMode === "pressure"}
                                        onChange={() => setVizMode("pressure")}
                                        className="w-4 h-4 text-blue-600 border-slate-300 focus:ring-blue-500"
                                    />
                                    <span className="text-sm text-slate-600 group-hover:text-slate-900">Importation Pressure</span>
                                </label>
                            </div>
                        </div>
                    </div>
                </Card_10>

                <div className="flex flex-col lg:flex-row gap-8 items-start">
                    {/* Map Section */}
                    <div className="w-full lg:w-2/3 bg-white p-4 rounded-xl shadow-sm border border-slate-200">
                        <DistrictMapSVG_10
                            onDistrictClick={handleDistrictClick}
                            selectedDistrictId={selectedDistrict?.id}
                            predictions={predictions}
                            vizMode={vizMode}
                            className="bg-slate-50 rounded-lg"
                        />

                        {/* Legend */}
                        <div className="mt-6 flex flex-wrap items-center justify-center gap-6 p-4 bg-slate-50 rounded-lg border border-slate-100">
                            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Legend</span>
                            {vizMode === "risk" ? (
                                <>
                                    <div className="flex items-center gap-2">
                                        <div className="w-4 h-4 rounded bg-[#ef4444]" />
                                        <span className="text-sm text-slate-600">High Risk (≥1.5)</span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <div className="w-4 h-4 rounded bg-[#facc15]" />
                                        <span className="text-sm text-slate-600">Medium Risk (≥1.0)</span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <div className="w-4 h-4 rounded bg-[#4ade80]" />
                                        <span className="text-sm text-slate-600">Low Risk (≥0.5)</span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <div className="w-4 h-4 rounded border border-slate-300 bg-white" />
                                        <span className="text-sm text-slate-600">No Risk (&lt;0.5)</span>
                                    </div>
                                </>
                            ) : (
                                <>
                                    <div className="flex items-center gap-2">
                                        <div className="w-4 h-4 rounded bg-[#ef4444]" />
                                        <span className="text-sm text-slate-600">High (≥0.5)</span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <div className="w-4 h-4 rounded bg-[#facc15]" />
                                        <span className="text-sm text-slate-600">Medium (≥0.3)</span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <div className="w-4 h-4 rounded bg-[#4ade80]" />
                                        <span className="text-sm text-slate-600">Low (&lt;0.3)</span>
                                    </div>
                                </>
                            )}
                        </div>
                    </div>

                    {/* Details Section */}
                    <div className="w-full lg:w-1/3 space-y-6">
                        {selectedDistrict ? (
                            <div className="bg-white p-6 rounded-xl shadow-lg border border-slate-200 animate-fade-in-up">
                                <h2 className="text-2xl font-bold text-slate-900 mb-4 border-b pb-2">
                                    {DISTRICT_DISPLAY_NAMES_10[selectedDistrict.name] || selectedDistrict.name}
                                </h2>

                                <div className="space-y-4">
                                    <div className="flex justify-between items-center">
                                        <span className="text-slate-600">Metric Summary</span>
                                        <span className={`px-3 py-1 rounded-full text-sm font-semibold
                                            ${vizMode === 'risk' ? (
                                                selectedDistrict.riskLevel === 'Critical' ? 'bg-red-100 text-red-800' :
                                                    selectedDistrict.riskLevel === 'High' ? 'bg-yellow-100 text-yellow-800' :
                                                        selectedDistrict.riskLevel === 'Moderate' ? 'bg-green-100 text-green-800' :
                                                            'bg-slate-100 text-slate-800'
                                            ) : (
                                                selectedDistrict.importationPressure >= 0.5 ? 'bg-red-100 text-red-800' :
                                                    selectedDistrict.importationPressure >= 0.3 ? 'bg-yellow-100 text-yellow-800' :
                                                        'bg-green-100 text-green-800'
                                            )}`}>
                                            {vizMode === 'risk' ? (
                                                selectedDistrict.riskLevel === 'Critical' ? 'High Risk' :
                                                    selectedDistrict.riskLevel === 'High' ? 'Medium Risk' :
                                                        selectedDistrict.riskLevel === 'Moderate' ? 'Low Risk' : 'No Risk'
                                            ) : (
                                                selectedDistrict.importationPressure >= 0.5 ? 'High Pressure' :
                                                    selectedDistrict.importationPressure >= 0.3 ? 'Medium Pressure' : 'Low Pressure'
                                            )}
                                        </span>
                                    </div>

                                    <div className="grid grid-cols-2 gap-4">
                                        <Card_10 className="p-3 !bg-blue-50 border-none">
                                            <p className="text-xs text-blue-600 font-medium uppercase">Rainfall</p>
                                            <p className="text-lg font-bold text-slate-900">{selectedDistrict.rainfall.toFixed(1)} mm</p>
                                        </Card_10>
                                        <Card_10 className="p-3 !bg-amber-50 border-none">
                                            <p className="text-xs text-amber-600 font-medium uppercase">Temp</p>
                                            <p className="text-lg font-bold text-slate-900">{selectedDistrict.temperature.toFixed(1)}°C</p>
                                        </Card_10>
                                        <Card_10 className="p-3 !bg-teal-50 border-none">
                                            <p className="text-xs text-teal-600 font-medium uppercase">Humidity</p>
                                            <p className="text-lg font-bold text-slate-900">{selectedDistrict.humidity.toFixed(1)}%</p>
                                        </Card_10>
                                        <Card_10 className="p-3 !bg-purple-50 border-none">
                                            <p className="text-xs text-purple-600 font-medium uppercase">Imp. Pressure</p>
                                            <p className="text-lg font-bold text-slate-900">{selectedDistrict.importationPressure.toFixed(2)}</p>
                                        </Card_10>
                                    </div>

                                    <div className="pt-2">
                                        <p className="text-sm text-slate-500 mb-1">Analysis Summary</p>
                                        <p className="text-slate-700 leading-relaxed text-sm">
                                            {selectedDistrict.details}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="bg-white p-8 rounded-xl shadow-sm border border-slate-200 text-center">
                                <div className="inline-block p-4 rounded-full bg-blue-50 mb-4">
                                    <svg className="w-8 h-8 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                                    </svg>
                                </div>
                                <h3 className="text-lg font-medium text-slate-900">Select a District</h3>
                                <p className="text-slate-500 mt-2">
                                    Click on any district in the map after generating data to view detailed values.
                                </p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};
