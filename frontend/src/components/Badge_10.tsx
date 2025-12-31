import React from "react";

interface BadgeProps {
    label: string;
    className?: string;
    size?: "sm" | "md" | "lg";
}

export const Badge_10: React.FC<BadgeProps> = ({ label, className = "", size = "md" }) => {
    let colorClass = "bg-slate-100 text-slate-800 border-slate-200";
    const lowerLabel = label.toLowerCase();

    if (lowerLabel.includes("high")) {
        colorClass = "bg-red-50 text-red-700 border-red-200";
    } else if (lowerLabel.includes("medium") || lowerLabel.includes("moderate")) {
        colorClass = "bg-orange-50 text-orange-700 border-orange-200";
    } else if (lowerLabel.includes("low")) {
        // User requested yellow for low risk.
        // Yellow text on yellow bg can be hard to read.
        // Using amber-50 and amber-700 for better contrast or yellow-100/yellow-800.
        colorClass = "bg-yellow-50 text-yellow-700 border-yellow-200";
    } else if (lowerLabel.includes("no")) {
        colorClass = "bg-emerald-50 text-emerald-700 border-emerald-200";
    }

    const sizeClass =
        size === "sm" ? "px-2 py-0.5 text-xs" :
            size === "lg" ? "px-4 py-2 text-base" :
                "px-3 py-1 text-sm";

    return (
        <span className={`inline-flex items-center justify-center font-medium rounded-full border ${colorClass} ${sizeClass} ${className}`}>
            {label}
        </span>
    );
};
