import React from "react";

interface Option {
    label: string;
    value: string | number;
}

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
    label?: string;
    error?: string;
    options: Option[];
    placeholder?: string;
}

export const Select_10: React.FC<SelectProps> = ({
    label,
    error,
    options,
    placeholder,
    className = "",
    id,
    ...props
}) => {
    const selectId = id || props.name;

    return (
        <div className={`w-full ${className}`}>
            {label && (
                <label
                    htmlFor={selectId}
                    className="block text-sm font-medium text-slate-700 mb-1.5"
                >
                    {label}
                </label>
            )}
            <select
                id={selectId}
                className={`block w-full rounded-lg border-slate-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm 
        disabled:bg-slate-50 disabled:text-slate-500
        ${error ? "border-red-300 focus:border-red-500 focus:ring-red-500" : "border-slate-200"}`}
                {...props}
            >
                {placeholder && (
                    <option value="" disabled>
                        {placeholder}
                    </option>
                )}
                {options.map((option) => (
                    <option key={option.value} value={option.value}>
                        {option.label}
                    </option>
                ))}
            </select>
            {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
        </div>
    );
};
