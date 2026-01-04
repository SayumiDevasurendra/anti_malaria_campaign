"use client";

import React, { useState } from "react";
import { Card_10 } from "../components/Card_10";
import { Button_10 } from "../components/Button_10";
import { Select_10 } from "../components/Select_10";
import { Input_10 } from "../components/Input_10";
import { Badge_10 } from "../components/Badge_10";
import { forecastImportation_10 } from "../utils/api_10";
import { DISTRICTS_10 } from "../utils/constants_10";
import { ImportationForecastResponse_10 } from "../types/types_10";

export const ImportationPage_10 = () => {
    const [formData, setFormData] = useState({
        district: DISTRICTS_10[0],
        year: new Date().getFullYear(),
    });
    const [result, setResult] = useState<ImportationForecastResponse_10 | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setResult(null);

        try {
            const data = await forecastImportation_10({
                district: formData.district,
                year: Number(formData.year),
            });
            setResult(data);
        } catch (err: any) {
            setError(err.message || "Failed to fetch forecast");
        } finally {
            setLoading(false);
        }
    };

    const getRiskLabel = (pressure: number) => {
        if (pressure >= 0.5) return "High Risk";
        if (pressure >= 0.3) return "Medium Risk";
        return "Low Risk";
    };

    return (
        <div className="max-w-5xl mx-auto py-8 px-4 space-y-8">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-slate-900">Importation Risk Forecasting</h1>
                    <p className="text-slate-600 mt-1">Predict district-wise national importation risk</p>
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
                                        <h3 className="text-lg font-medium text-slate-500">Importation Pressure Risk</h3>
                                        <div className="mt-2">
                                            <Badge_10 label={getRiskLabel(result.district_monthly_importation_pressure)} size="lg" />
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <span className="block text-3xl font-bold text-slate-900">{result.district_monthly_importation_pressure.toFixed(4)}</span>
                                        <span className="text-sm text-slate-400">Pressure Score</span>
                                    </div>
                                </div>
                            </Card_10>

                            <div className="grid grid-cols-1 gap-4">
                                <Card_10 className="text-center">
                                    <span className="block text-sm text-slate-500 mb-1">Forecasted National Imported Cases (Annual)</span>
                                    <span className="block text-2xl font-semibold text-blue-600">{result.forecasted_national_imported_cases.toFixed(1)}</span>
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
