import React from "react";

export const Footer_10 = () => {
    return (
        <footer className="bg-white border-t border-slate-200 py-6 mt-auto">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex flex-col items-center justify-center text-center">
                    <p className="text-sm text-slate-500">
                        © {new Date().getFullYear()} Anti-Malaria Campaign Research Project. All rights reserved.
                    </p>
                    <p className="text-xs text-slate-400 mt-1">
                        Prediction of Risk of Re-establishment of Malaria in Sri Lanka (District-wise)
                    </p>
                </div>
            </div>
        </footer>
    );
};
