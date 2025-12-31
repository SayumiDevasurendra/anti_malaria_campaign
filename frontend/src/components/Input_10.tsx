import React from "react";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
    label?: string;
    error?: string;
}

export const Input_10: React.FC<InputProps> = ({
    label,
    error,
    className = "",
    id,
    ...props
}) => {
    const inputId = id || props.name;

    return (
        <div className={`w-full ${className}`}>
            {label && (
                <label
                    htmlFor={inputId}
                    className="block text-sm font-medium text-slate-700 mb-1.5"
                >
                    {label}
                </label>
            )}
            <input
                id={inputId}
                className={`block w-full rounded-lg border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm 
        disabled:bg-slate-50 disabled:text-slate-500
        ${error ? "border-red-300 focus:border-red-500 focus:ring-red-500" : "border-slate-200"}`}
                {...props}
            />
            {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
        </div>
    );
};
