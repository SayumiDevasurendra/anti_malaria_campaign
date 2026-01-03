"use client";

import React, { useState, useMemo } from "react";
import { Card_10 } from "../components/Card_10";
import { Button_10 } from "../components/Button_10";
import { Select_10 } from "../components/Select_10";
import { Input_10 } from "../components/Input_10";
import { Badge_10 } from "../components/Badge_10";
import { forecastClimate_10 } from "../utils/api_10";
import { DISTRICTS_10, MONTHS_10 } from "../utils/constants_10";
import { ClimaticForecastResponse_10 } from "../types/types_10";

export const ReceptivityPage_10 = () => {
    // --- Step 1: Climatic Forecast ---
    const [formData, setFormData] = useState({
        district: DISTRICTS_10[0],
        year: new Date().getFullYear(),
        month: new Date().getMonth() + 1,
    });
    const [climaticResult, setClimaticResult] = useState<ClimaticForecastResponse_10 | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // --- Step 2: Checklist State ---
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

    const handleForecast = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        try {
            const data = await forecastClimate_10({
                district: formData.district,
                year: Number(formData.year),
                month: Number(formData.month),
            });
            setClimaticResult(data);
        } catch (err: any) {
            setError(err.message || "Failed to fetch climatic forecast");
        } finally {
            setLoading(false);
        }
    };

    const handleChecklistChange = (key: keyof typeof checklist, value: string) => {
        setChecklist((prev) => ({ ...prev, [key]: Number(value) }));
    };

    const totalScore = useMemo(() => {
        if (!climaticResult) return 0;
        const checklistSum = Object.values(checklist).reduce((a, b) => a + b, 0);
        return climaticResult.forecasted_climatic_receptivity + checklistSum;
    }, [climaticResult, checklist]);

    const riskLevel = useMemo(() => {
        if (totalScore >= 17) return "High Risk";
        if (totalScore >= 8) return "Moderate Risk";
        return "Low Risk";
    }, [totalScore]);

    return (
        <div className="max-w-5xl mx-auto py-8 px-4 space-y-8">
            <div>
                <h1 className="text-3xl font-bold text-slate-900">Receptivity Forecasting</h1>
                <p className="text-slate-600 mt-1">Assess malaria transmission potential using climatic and entomological factors</p>
            </div>

            {/* Step 1: Climatic Forecast */}
            <Card_10 title="Step 1: Climatic Risk Assessment">
                <form onSubmit={handleForecast} className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
                    <Select_10
                        label="District"
                        value={formData.district}
                        onChange={(e) => setFormData({ ...formData, district: e.target.value })}
                        options={DISTRICTS_10.map((d) => ({ label: d, value: d }))}
                    />
                    <Input_10
                        label="Year"
                        type="number"
                        min={2000}
                        max={2100}
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
                        Get Climatic Score
                    </Button_10>
                </form>
                {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
                {climaticResult && (
                    <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-100 flex items-center justify-between">
                        <span className="text-blue-800 font-medium">Climatic Risk Score Retrieved:</span>
                        <span className="text-2xl font-bold text-blue-900">{climaticResult.forecasted_climatic_receptivity.toFixed(2)}</span>
                    </div>
                )}
            </Card_10>

            {/* Step 2: Checklist (Only show if climatic result exists) */}
            {climaticResult && (
                <div className="space-y-6">
                    <Card_10 title="Step 2: Receptivity Assessment Checklist">
                        <div className="space-y-8">

                            {/* Section 1 */}
                            <div>
                                <h4 className="text-lg font-semibold text-slate-800 mb-4 border-b pb-2">🦟 Presence and Density of Vectors</h4>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
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
                                        label="Secondary vector larvae present?"
                                        value={checklist.secondary_larvae}
                                        onChange={(e) => handleChecklistChange("secondary_larvae", e.target.value)}
                                        options={[{ label: "No", value: 0 }, { label: "Yes", value: 1 }]}
                                    />
                                    <Select_10
                                        label="Secondary vector adults present?"
                                        value={checklist.secondary_adults}
                                        onChange={(e) => handleChecklistChange("secondary_adults", e.target.value)}
                                        options={[{ label: "No", value: 0 }, { label: "Yes", value: 1 }]}
                                    />
                                    <Select_10
                                        label="An. stephensi larvae present?"
                                        value={checklist.stephensi_larvae}
                                        onChange={(e) => handleChecklistChange("stephensi_larvae", e.target.value)}
                                        options={[{ label: "No", value: 0 }, { label: "Yes", value: 2 }]}
                                    />
                                    <Select_10
                                        label="An. stephensi adults present?"
                                        value={checklist.stephensi_adults}
                                        onChange={(e) => handleChecklistChange("stephensi_adults", e.target.value)}
                                        options={[{ label: "No", value: 0 }, { label: "Yes", value: 2 }]}
                                    />
                                </div>
                            </div>

                            {/* Section 2 */}
                            <div>
                                <h4 className="text-lg font-semibold text-slate-800 mb-4 border-b pb-2">🧬 Biting Behaviour and Density</h4>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <Select_10
                                        label="An. culicifacies indoor biting (per man hour)"
                                        value={checklist.culicifacies_indoor}
                                        onChange={(e) => handleChecklistChange("culicifacies_indoor", e.target.value)}
                                        options={[
                                            { label: "None", value: 0 },
                                            { label: "0 < 1", value: 5 },
                                            { label: ">= 1", value: 6 },
                                        ]}
                                    />
                                    <Select_10
                                        label="An. culicifacies outdoor biting (per man hour)"
                                        value={checklist.culicifacies_outdoor}
                                        onChange={(e) => handleChecklistChange("culicifacies_outdoor", e.target.value)}
                                        options={[
                                            { label: "None", value: 0 },
                                            { label: "0 < 1", value: 5 },
                                            { label: ">= 1", value: 6 },
                                        ]}
                                    />
                                    <Select_10
                                        label="Secondary malaria vectors biting (Outdoor)?"
                                        value={checklist.sec_outdoor}
                                        onChange={(e) => handleChecklistChange("sec_outdoor", e.target.value)}
                                        options={[{ label: "No ", value: 0 }, { label: "Yes", value: 2 }]}
                                    />
                                    <Select_10
                                        label="Secondary malaria vectors biting (Indoor)?"
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
                                        label="Parous secondary malaria vectors present?"
                                        value={checklist.parous_sec}
                                        onChange={(e) => handleChecklistChange("parous_sec", e.target.value)}
                                        options={[{ label: "No", value: 0 }, { label: "Yes", value: 2 }]}
                                    />
                                </div>
                            </div>

                            {/* Section 3 */}
                            <div>
                                <h4 className="text-lg font-semibold text-slate-800 mb-4 border-b pb-2">🌍 Geographical and Topographical Factors</h4>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <Select_10
                                        label="Key breeding places for primary vector present?"
                                        value={checklist.breeding_places}
                                        onChange={(e) => handleChecklistChange("breeding_places", e.target.value)}
                                        options={[{ label: "No", value: 0 }, { label: "Yes", value: 1 }]}
                                    />
                                    <Select_10
                                        label="Developmental projects creating breeding grounds?"
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

                    {/* Final Result */}
                    <Card_10 className="bg-slate-900 text-white border-slate-800 sticky bottom-4 shadow-xl z-40">
                        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
                            <div>
                                <h3 className="text-xl font-bold text-black">Total Receptivity Score</h3>
                                <p className="text-slate-400 text-sm">Sum of Climatic Receptivity ({climaticResult.forecasted_climatic_receptivity.toFixed(2)}) & Entomological Score ({totalScore - climaticResult.forecasted_climatic_receptivity})</p>
                            </div>
                            <div className="flex items-center gap-6">
                                <span className="text-4xl font-extrabold text-black">{totalScore.toFixed(2)}</span>
                                <Badge_10 label={riskLevel} className="text-lg px-6 py-2" />
                            </div>
                        </div>
                    </Card_10>
                </div>
            )}
        </div>
    );
};
