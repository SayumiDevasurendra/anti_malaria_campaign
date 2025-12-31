import {
    ClimaticForecastRequest_10,
    ClimaticForecastResponse_10,
    ImportationForecastRequest_10,
    ImportationForecastResponse_10,
} from "../types/types_10";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const forecastClimate_10 = async (
    data: ClimaticForecastRequest_10
): Promise<ClimaticForecastResponse_10> => {
    const response = await fetch(`${API_URL}/forecast/climate-risk`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Failed to fetch climatic forecast");
    }
    return response.json();
};

export const forecastImportation_10 = async (
    data: ImportationForecastRequest_10
): Promise<ImportationForecastResponse_10> => {
    const response = await fetch(`${API_URL}/forecast/importation`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Failed to fetch importation forecast");
    }
    return response.json();
};
