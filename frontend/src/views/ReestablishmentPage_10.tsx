"use client";

import React, { useState, useMemo } from "react";
import { Card_10 } from "../components/Card_10";
import { Button_10 } from "../components/Button_10";
import { Select_10 } from "../components/Select_10";
import { Input_10 } from "../components/Input_10";
import { Badge_10 } from "../components/Badge_10";
import { forecastClimate_10, forecastImportation_10 } from "../utils/api_10";
import { DISTRICTS_10, MONTHS_10, DISTRICT_OPTIONS_10 } from "../utils/constants_10";
import { ClimaticForecastResponse_10, ImportationForecastResponse_10 } from "../types/types_10";

export const ReestablishmentPage_10 = () => {
    // --- Basic Inputs ---
    const [formData, setFormData] = useState({
        district: DISTRICTS_10[0],
        year: new Date().getFullYear(),
        month: new Date().getMonth() + 1,
    });

    // --- API Results ---
    const [climaticResult, setClimaticResult] = useState<ClimaticForecastResponse_10 | null>(null);
    const [importationResult, setImportationResult] = useState<ImportationForecastResponse_10 | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // --- Checklist State ---
    const [checklist, setChecklist] = useState({
        // Presence and Density
        primary_larvae: 0,
        primary_adults: 0,
        secondary_larvae: 0,
        secondary_adults: 0,
        stephensi_larvae: 0,
        stephensi_adults: 0,

        // Biting Behaviour
        culicifacies_indoor: 0,
        culicifacies_outdoor: 0,
        sec_outdoor: 0,
        sec_indoor: 0,
        parous_culicifacies: 0,
        parous_sec: 0,

        // Geo/Topo
        breeding_places: 0,
        dev_projects: 0,
        prev_endemicity: 0,
    });

    const handleAssessRisk = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setClimaticResult(null);
        setImportationResult(null);

        try {
            // Fetch both forecasts in parallel
            const [climaticData, importationData] = await Promise.all([
                forecastClimate_10({
                    district: formData.district,
                    year: Number(formData.year),
                    month: Number(formData.month),
                }),
                forecastImportation_10({
                    district: formData.district,
                    year: Number(formData.year),
                }),
            ]);

            setClimaticResult(climaticData);
            setImportationResult(importationData);
        } catch (err: any) {
            setError(err.message || "Failed to fetch forecasts");
        } finally {
            setLoading(false);
        }
    };

    const handleChecklistChange = (key: keyof typeof checklist, value: string) => {
        setChecklist((prev) => ({ ...prev, [key]: Number(value) }));
    };

    // --- Calculations ---

    // 1. Receptivity Score
    const totalReceptivityScore = useMemo(() => {
        if (!climaticResult) return 0;
        const checklistSum = Object.values(checklist).reduce((a, b) => a + b, 0);
        return climaticResult.forecasted_climatic_receptivity + checklistSum;
    }, [climaticResult, checklist]);

    // 2. Receptivity Risk Level
    const receptivityRiskLevel = useMemo(() => {
        if (totalReceptivityScore >= 17) return "High";
        if (totalReceptivityScore >= 8) return "Moderate";
        return "Low";
    }, [totalReceptivityScore]);

    // 3. Importation Risk Level
    const importationRiskLevel = useMemo(() => {
        if (!importationResult) return "Low";
        const pressure = importationResult.district_monthly_importation_pressure;
        if (pressure >= 0.5) return "High";
        if (pressure >= 0.3) return "Medium"; // Using "Medium" to match earlier spec
        return "Low";
    }, [importationResult]);

    // 4. Final Re-establishment Risk
    const finalRisk = useMemo(() => {
        if (!climaticResult || !importationResult) return "Unknown";

        const imp = importationRiskLevel;
        const rec = receptivityRiskLevel;

        // Matrix Rules:
        // Imp Low + Rec Low or Moderate -> Low Risk
        // Imp Low + Rec High -> Moderate Risk
        // Imp Medium + Rec Low -> Low Risk
        // Imp Medium + Rec Moderate or High -> Moderate Risk
        // Imp High + Rec Low or Moderate -> Moderate Risk
        // Imp High + Rec High -> High Risk

        if (imp === "Low") {
            if (rec === "High") return "Moderate Risk";
            return "Low Risk";
        }
        if (imp === "Medium") {
            if (rec === "Low") return "Low Risk";
            return "Moderate Risk";
        }
        if (imp === "High") {
            if (rec === "High") return "High Risk";
            return "Moderate Risk";
        }
        return "Unknown";
    }, [importationRiskLevel, receptivityRiskLevel, climaticResult, importationResult]);

    return (
        <div className="max-w-6xl mx-auto py-8 px-4 space-y-8">
            <div>
                <h1 className="text-3xl font-bold text-slate-900">Risk of Re-establishment Assessment</h1>
                <p className="text-slate-600 mt-1">Comprehensive analysis combining climatic, entomological, and importation factors</p>
            </div>

            {/* Inputs */}
            <Card_10 title="Step 1: Define Parameters">
                <form onSubmit={handleAssessRisk} className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
                    <Select_10
                        label="District"
                        value={formData.district}
                        onChange={(e) => setFormData({ ...formData, district: e.target.value })}
                        options={DISTRICT_OPTIONS_10}
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
                    <Button_10 type="submit" isLoading={loading}>
                        Assess Risk
                    </Button_10>
                </form>
                {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
            </Card_10>

            {/* Analysis Section */}
            {climaticResult && importationResult && (
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">

                    {/* Left Column: Automated Forecasts */}
                    <div className="lg:col-span-4 space-y-6">
                        <Card_10 title="Automated Forecasts">
                            <div className="space-y-6">
                                {/* Climatic */}
                                <div className="p-4 bg-blue-50 rounded-lg border border-blue-100">
                                    <span className="block text-sm text-blue-600 font-medium mb-1">Climatic Risk Score</span>
                                    <span className="text-2xl font-bold text-blue-900">{climaticResult.forecasted_climatic_receptivity.toFixed(2)}</span>
                                    <div className="mt-2 text-xs text-blue-800 space-y-1">
                                        <p>Rainfall: {climaticResult.forecasted_rainfall.toFixed(1)} mm</p>
                                        <p>Temp: {climaticResult.forecasted_temperature.toFixed(1)} °C</p>
                                        <p>Humidity: {climaticResult.forecasted_humidity.toFixed(1)} %</p>
                                    </div>
                                </div>

                                {/* Importation */}
                                <div className="p-4 bg-purple-50 rounded-lg border border-purple-100">
                                    <span className="block text-sm text-purple-600 font-medium mb-1">Importation Pressure</span>
                                    <span className="text-2xl font-bold text-purple-900">{importationResult.district_monthly_importation_pressure.toFixed(4)}</span>
                                    <div className="mt-2">
                                        <Badge_10 label={`${importationRiskLevel} Risk`} size="sm" />
                                    </div>
                                </div>
                            </div>
                        </Card_10>

                        {/* Intermediate Status */}
                        <Card_10 title="Receptivity Status" className="bg-slate-50">
                            <div className="text-center">
                                <span className="block text-sm text-slate-500 mb-2">Total Receptivity Score</span>
                                <span className="text-3xl font-bold text-slate-800">{totalReceptivityScore.toFixed(2)}</span>
                                <div className="mt-3">
                                    <Badge_10 label={`${receptivityRiskLevel} Risk`} />
                                </div>
                            </div>
                        </Card_10>
                    </div>

                    {/* Middle Column: Checklist */}
                    <div className="lg:col-span-8">
                        <Card_10 title="Step 2: Entomological Checklist (Receptivity)">
                            <div className="space-y-8 max-h-[800px] overflow-y-auto pr-2">

                                {/* Section 1 */}
                                <div>
                                    <h4 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4 border-b pb-2">Vector Presence</h4>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <Select_10
                                            label="Primary vector larvae (per 100 dips)"
                                            value={checklist.primary_larvae}
                                            onChange={(e) => handleChecklistChange("primary_larvae", e.target.value)}
                                            options={[
                                                { label: "None", value: 0 },
                                                { label: "0–10", value: 2 },
                                                { label: "10–20", value: 3 },
                                                { label: "> 20", value: 4 },
                                            ]}
                                        />
                                        <Select_10
                                            label="Primary vector adults (per hut)"
                                            value={checklist.primary_adults}
                                            onChange={(e) => handleChecklistChange("primary_adults", e.target.value)}
                                            options={[
                                                { label: "None", value: 0 },
                                                { label: "0–10", value: 4 },
                                                { label: "10–20", value: 6 },
                                                { label: "> 20", value: 8 },
                                            ]}
                                        />
                                        <Select_10
                                            label="Secondary vector larvae?"
                                            value={checklist.secondary_larvae}
                                            onChange={(e) => handleChecklistChange("secondary_larvae", e.target.value)}
                                            options={[{ label: "No", value: 0 }, { label: "Yes", value: 1 }]}
                                        />
                                        <Select_10
                                            label="Secondary vector adults?"
                                            value={checklist.secondary_adults}
                                            onChange={(e) => handleChecklistChange("secondary_adults", e.target.value)}
                                            options={[{ label: "No", value: 0 }, { label: "Yes", value: 1 }]}
                                        />
                                        <Select_10
                                            label="An. stephensi larvae?"
                                            value={checklist.stephensi_larvae}
                                            onChange={(e) => handleChecklistChange("stephensi_larvae", e.target.value)}
                                            options={[{ label: "No", value: 0 }, { label: "Yes", value: 2 }]}
                                        />
                                        <Select_10
                                            label="An. stephensi adults?"
                                            value={checklist.stephensi_adults}
                                            onChange={(e) => handleChecklistChange("stephensi_adults", e.target.value)}
                                            options={[{ label: "No", value: 0 }, { label: "Yes", value: 2 }]}
                                        />
                                    </div>
                                </div>

                                {/* Section 2 */}
                                <div>
                                    <h4 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4 border-b pb-2">Biting Behaviour</h4>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <Select_10
                                            label="An. culicifacies indoor (per man hour)"
                                            value={checklist.culicifacies_indoor}
                                            onChange={(e) => handleChecklistChange("culicifacies_indoor", e.target.value)}
                                            options={[
                                                { label: "None", value: 0 },
                                                { label: "0 < 1", value: 5 },
                                                { label: ">= 1", value: 6 },
                                            ]}
                                        />
                                        <Select_10
                                            label="An. culicifacies outdoor (per man hour)"
                                            value={checklist.culicifacies_outdoor}
                                            onChange={(e) => handleChecklistChange("culicifacies_outdoor", e.target.value)}
                                            options={[
                                                { label: "None", value: 0 },
                                                { label: "0 < 1", value: 5 },
                                                { label: ">= 1", value: 6 },
                                            ]}
                                        />
                                        <Select_10
                                            label="Secondary vectors biting (Outdoor)?"
                                            value={checklist.sec_outdoor}
                                            onChange={(e) => handleChecklistChange("sec_outdoor", e.target.value)}
                                            options={[{ label: "No", value: 0 }, { label: "Yes", value: 2 }]}
                                        />
                                        <Select_10
                                            label="Secondary vectors biting (Indoor)?"
                                            value={checklist.sec_indoor}
                                            onChange={(e) => handleChecklistChange("sec_indoor", e.target.value)}
                                            options={[{ label: "No", value: 0 }, { label: "Yes", value: 2 }]}
                                        />
                                        <Select_10
                                            label="Parous An. culicifacies present?"
                                            value={checklist.parous_culicifacies}
                                            onChange={(e) => handleChecklistChange("parous_culicifacies", e.target.value)}
                                            options={[{ label: "No", value: 0 }, { label: "Yes", value: 4 }]}
                                        />
                                        <Select_10
                                            label="Parous secondary vectors present?"
                                            value={checklist.parous_sec}
                                            onChange={(e) => handleChecklistChange("parous_sec", e.target.value)}
                                            options={[{ label: "No", value: 0 }, { label: "Yes", value: 2 }]}
                                        />
                                    </div>
                                </div>

                                {/* Section 3 */}
                                <div>
                                    <h4 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4 border-b pb-2">Geography</h4>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <Select_10
                                            label="Key breeding places present?"
                                            value={checklist.breeding_places}
                                            onChange={(e) => handleChecklistChange("breeding_places", e.target.value)}
                                            options={[{ label: "No", value: 0 }, { label: "Yes", value: 1 }]}
                                        />
                                        <Select_10
                                            label="Projects creating breeding grounds?"
                                            value={checklist.dev_projects}
                                            onChange={(e) => handleChecklistChange("dev_projects", e.target.value)}
                                            options={[{ label: "No", value: 0 }, { label: "Yes", value: 1 }]}
                                        />
                                        <Select_10
                                            label="Previous malaria endemicity?"
                                            value={checklist.prev_endemicity}
                                            onChange={(e) => handleChecklistChange("prev_endemicity", e.target.value)}
                                            options={[{ label: "No", value: 0 }, { label: "Yes", value: 1 }]}
                                        />
                                    </div>
                                </div>

                            </div>
                        </Card_10>
                    </div>
                </div>
            )}

            {/* Final Sticky Result */}
            {climaticResult && importationResult && (
                <Card_10 className="bg-slate-900 text-white border-slate-800 sticky bottom-4 shadow-2xl z-50">
                    <div className="flex flex-col md:flex-row items-center justify-between gap-6">
                        <div className="text-center md:text-left">
                            <p className="text-xs text-black uppercase tracking-widest font-bold">Final Assessment</p>
                            <h2 className="text-2xl font-bold text-black mt-1">Risk of Re-establishment</h2>
                        </div>

                        <div className="flex items-center gap-8">
                            <div className="text-right hidden md:block">
                                <p className="text-sm text-black">Receptivity: <span className="text-black font-medium">{receptivityRiskLevel}</span></p>
                                <p className="text-sm text-black">Importation: <span className="text-black font-medium">{importationRiskLevel}</span></p>
                            </div>
                            <Badge_10 label={finalRisk} className="text-xl px-8 py-3" />
                        </div>
                    </div>
                </Card_10>
            )}

        </div>
    );
};
