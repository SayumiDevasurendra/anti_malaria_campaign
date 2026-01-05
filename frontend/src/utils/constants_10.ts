export const DISTRICTS_10 = [
    "Anuradhapura",
    "Badulla",
    "Batticaloa",
    "Colombo",
    "Galle",
    "Hambantota",
    "Jaffna",
    "Katugastota",
    "Katunayake",
    "Kurunegala",
    "Mahaillukpallama",
    "Mannar",
    "Mattala",
    "Monaragala",
    "Nuwara Eliya",
    "Polonnaruwa",
    "Potuvil",
    "Puttalam",
    "Ratmalana",
    "Ratnapura",
    "Trincomalee",
    "Vavuniya",
];

export const DISTRICT_DISPLAY_NAMES_10: Record<string, string> = {
    "Katugastota": "Mahanuwara",
    "Katunayake": "Gampaha",
    "Mahaillukpallama": "Matale",
    "Mattala": "Matara",
    "Potuvil": "Ampara",
    "Vavuniya": "Vavuniya & Mulativ",
    "Mannar": "Mannar & Kilinochi",
    "Ratnapura": "Ratnapura & Kegalle",
    "Ratmalana": "Kalutara",
};

export const DISTRICT_OPTIONS_10 = DISTRICTS_10.map((district) => ({
    value: district,
    label: DISTRICT_DISPLAY_NAMES_10[district] || district,
}));

export const MONTHS_10 = [
    { value: 1, label: "January" },
    { value: 2, label: "February" },
    { value: 3, label: "March" },
    { value: 4, label: "April" },
    { value: 5, label: "May" },
    { value: 6, label: "June" },
    { value: 7, label: "July" },
    { value: 8, label: "August" },
    { value: 9, label: "September" },
    { value: 10, label: "October" },
    { value: 11, label: "November" },
    { value: 12, label: "December" },
];

export const RISK_LEVELS_10 = {
    HIGH: "High Risk",
    MODERATE: "Moderate Risk",
    LOW: "Low Risk",
    NO: "No Risk",
};
