"use client";

import React from "react";
import Link from "next/link";
import { Card_10 } from "../components/Card_10";
import { Button_10 } from "../components/Button_10";

export const LandingPage_10 = () => {
    return (
        <div className="space-y-12 py-10">
            {/* Hero Section */}
            <section className="text-center max-w-4xl mx-auto px-4">
                <h1 className="text-4xl font-extrabold text-slate-900 tracking-tight sm:text-5xl mb-6">
                    Prediction of Risk of Re-establishment of Malaria in Sri Lanka
                </h1>
                <p className="text-xl text-slate-600 leading-relaxed mb-8">
                    A comprehensive district-wise forecasting system to monitor climate conditions,
                    vector receptivity, and importation risks to prevent the return of malaria.
                </p>
                <div className="flex justify-center gap-4">
                    <Link href="/climatic">
                        <Button_10 size="lg">Start Forecasting</Button_10>
                    </Link>
                    <Link href="/re-establishment">
                        <Button_10 variant="outline" size="lg">View Final Risk</Button_10>
                    </Link>
                </div>
            </section>

            {/* Features Grid */}
            <section className="max-w-7xl mx-auto px-4 grid gap-8 md:grid-cols-2 lg:grid-cols-4">
                <Card_10 title="Climatic Forecasting" className="h-full flex flex-col hover:shadow-lg transition-shadow">
                    <div className="flex-1">
                        <p className="text-slate-600 mb-6">
                            Forecast Rainfall, Temperature, and Humidity using advanced time-series models (SARIMA/Random Forest) to determine climatic receptivity.
                        </p>
                    </div>
                    <Link href="/climatic" className="mt-auto">
                        <Button_10 variant="secondary" className="w-full">
                            Go to Climatic
                        </Button_10>
                    </Link>
                </Card_10>

                <Card_10 title="Receptivity Forecasting" className="h-full flex flex-col hover:shadow-lg transition-shadow">
                    <div className="flex-1">
                        <p className="text-slate-600 mb-6">
                            Assess the potential for malaria transmission based on vector density, biting behavior, and topographical factors combined with climate data.
                        </p>
                    </div>
                    <Link href="/receptivity" className="mt-auto">
                        <Button_10 variant="secondary" className="w-full">
                            Go to Receptivity
                        </Button_10>
                    </Link>
                </Card_10>

                <Card_10 title="Importation Risk" className="h-full flex flex-col hover:shadow-lg transition-shadow">
                    <div className="flex-1">
                        <p className="text-slate-600 mb-6">
                            Predict the risk of malaria cases being imported into districts based on national trends and population movement patterns.
                        </p>
                    </div>
                    <Link href="/importation" className="mt-auto">
                        <Button_10 variant="secondary" className="w-full">
                            Go to Importation
                        </Button_10>
                    </Link>
                </Card_10>

                <Card_10 title="District Risk Map" className="h-full flex flex-col hover:shadow-lg transition-shadow border-blue-100 bg-blue-50/30">
                    <div className="flex-1">
                        <p className="text-slate-600 mb-6">
                            Visualize the combined risk of re-establishment across Sri Lanka with interactive maps, metric selection, and detailed district-wise analysis.
                        </p>
                    </div>
                    <Link href="/district-map" className="mt-auto">
                        <Button_10 variant="secondary" className="w-full">
                            Open Map
                        </Button_10>
                    </Link>
                </Card_10>
            </section>
        </div>
    );
};
