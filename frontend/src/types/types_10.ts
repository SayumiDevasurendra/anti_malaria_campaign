export interface ClimaticForecastRequest_10 {
    district: string;
    year: number;
    month: number;
}

export interface ClimaticForecastResponse_10 {
    district: string;
    year: number;
    month: number;
    forecasted_rainfall: number;
    forecasted_temperature: number;
    forecasted_humidity: number;
    forecasted_climatic_receptivity: number;
}

export interface ImportationForecastRequest_10 {
    district: string;
    year: number;
}

export interface ImportationForecastResponse_10 {
    district: string;
    year: number;
    forecasted_national_imported_cases: number;
    district_monthly_importation_pressure: number;
}

export interface DistrictPrediction_10 {
    id: string; // The ID from the SVG (e.g., LKA2448)
    name: string; // The name from the SVG (e.g., Mahanuwara)
    riskLevel: "Low" | "Moderate" | "High" | "Critical";
    cases: number;
    rainfall: number;
    temperature: number;
    humidity: number;
    importationPressure: number;
    details: string;
}
