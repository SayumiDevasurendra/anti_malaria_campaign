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
