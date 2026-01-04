"use client";

import React, { useState } from "react";
import { Card_10 } from "../components/Card_10";
import { Button_10 } from "../components/Button_10";
import { Select_10 } from "../components/Select_10";
import { Input_10 } from "../components/Input_10";
import { Badge_10 } from "../components/Badge_10";
import { forecastClimate_10 } from "../utils/api_10";
import { DISTRICTS_10, MONTHS_10 } from "../utils/constants_10";
import { ClimaticForecastResponse_10 } from "../types/types_10";

export const ClimaticPage_10 = () => {
    const [formData, setFormData] = useState({
        district: DISTRICTS_10[0],
        year: new Date().getFullYear(),
        month: new Date().getMonth() + 1,
    });
    const [result, setResult] = useState<ClimaticForecastResponse_10 | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setResult(null);

        try {
            const data = await forecastClimate_10({
                district: formData.district,
                year: Number(formData.year),
                month: Number(formData.month),
            });
            setResult(data);
        } catch (err: any) {
            setError(err.message || "Failed to fetch forecast");
        } finally {
            setLoading(false);
        }
    };

    const getRiskLabel = (score: number) => {
        if (score >= 1.5) return "High Risk";
        if (score >= 1.0) return "Medium Risk";
        if (score >= 0.5) return "Low Risk";
        return "No Risk";
    };

    return (
        <div className="max-w-5xl mx-auto py-8 px-4 space-y-8">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-slate-900">Climatic Forecasting</h1>
                    <p className="text-slate-600 mt-1">Predict climate variables and malaria receptivity</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Input Form */}
                <div className="lg:col-span-1">
                    <Card_10 title="Forecast Parameters" className="h-full">
                        <form onSubmit={handleSubmit} className="space-y-6">
                            <Select_10
                                label="District"
                                value={formData.district}
                                onChange={(e) => setFormData({ ...formData, district: e.target.value })}
                                options={DISTRICTS_10.map((d) => ({ label: d, value: d }))}
                            />
                            <Input_10
                                label="Year"
                                type="number"
                                min={2026}
                                max={2050}
                                value={formData.year}
                                onChange={(e) => setFormData({ ...formData, year: Number(e.target.value) })}
                            />
                            <Select_10
                                label="Month"
                                value={formData.month}
                                onChange={(e) => setFormData({ ...formData, month: Number(e.target.value) })}
                                options={MONTHS_10}
                            />
                            <Button_10 type="submit" isLoading={loading} className="w-full">
                                Generate Forecast
                            </Button_10>
                            {error && (
                                <div className="p-3 bg-red-50 text-red-700 text-sm rounded-lg border border-red-100">
                                    {error}
                                </div>
                            )}
                        </form>
                    </Card_10>
                </div>

                {/* Results */}
                <div className="lg:col-span-2 space-y-6">
                    {result ? (
                        <div className="space-y-6">
                            {/* Risk Badge */}
                            <Card_10 className="bg-gradient-to-br from-white to-slate-50">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <h3 className="text-lg font-medium text-slate-500">Climatic Receptivity Risk</h3>
                                        <div className="mt-2">
                                            <Badge_10 label={getRiskLabel(result.forecasted_climatic_receptivity)} size="lg" />
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <span className="block text-3xl font-bold text-slate-900">{result.forecasted_climatic_receptivity.toFixed(2)}</span>
                                        <span className="text-sm text-slate-400">Score</span>
                                    </div>
                                </div>
                            </Card_10>

                            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                                <Card_10 className="text-center">
                                    <span className="block text-sm text-slate-500 mb-1">Rainfall</span>
                                    <span className="block text-2xl font-semibold text-blue-600">{result.forecasted_rainfall.toFixed(1)} mm</span>
                                </Card_10>
                                <Card_10 className="text-center">
                                    <span className="block text-sm text-slate-500 mb-1">Temperature</span>
                                    <span className="block text-2xl font-semibold text-amber-600">{result.forecasted_temperature.toFixed(1)} °C</span>
                                </Card_10>
                                <Card_10 className="text-center">
                                    <span className="block text-sm text-slate-500 mb-1">Humidity</span>
                                    <span className="block text-2xl font-semibold text-teal-600">{result.forecasted_humidity.toFixed(1)} %</span>
                                </Card_10>
                            </div>
                        </div>
                    ) : (
                        <Card_10 className="h-full flex items-center justify-center p-12 text-slate-400 border-dashed">
                            <div className="text-center">
                                <p>Enter parameters and click Generate Forecast to see results.</p>
                            </div>
                        </Card_10>
                    )}
                </div>
            </div>
        </div>
    );
};
