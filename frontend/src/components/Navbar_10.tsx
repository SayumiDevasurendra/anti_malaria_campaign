"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

export const Navbar_10 = () => {
    const [isOpen, setIsOpen] = useState(false);
    const pathname = usePathname();

    const links = [
        { href: "/", label: "Home" },
        { href: "/climatic", label: "Climatic" },
        { href: "/receptivity", label: "Receptivity" },
        { href: "/importation", label: "Importation" },
        { href: "/re-establishment", label: "Re-establishment" },
        { href: "/district-map", label: "District Map" },
    ];

    const isActive = (path: string) => {
        if (path === "/" && pathname === "/") return true;
        if (path !== "/" && pathname?.startsWith(path)) return true;
        return false;
    };

    return (
        <nav className="bg-white border-b border-slate-200 sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16">
                    <div className="flex">
                        <div className="flex-shrink-0 flex items-center">
                            <Link href="/" className="flex items-center gap-2">
                                <span className="text-xl font-bold text-blue-800 tracking-tight">
                                    Malaria Risk Sri Lanka
                                </span>
                            </Link>
                        </div>
                    </div>

                    {/* Desktop Menu */}
                    <div className="hidden md:ml-6 md:flex md:space-x-8">
                        {links.map((link) => (
                            <Link
                                key={link.href}
                                href={link.href}
                                className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors duration-200 ${isActive(link.href)
                                    ? "border-blue-500 text-slate-900"
                                    : "border-transparent text-slate-500 hover:border-slate-300 hover:text-slate-700"
                                    }`}
                            >
                                {link.label}
                            </Link>
                        ))}
                    </div>

                    {/* Mobile Menu Button */}
                    <div className="-mr-2 flex items-center md:hidden">
                        <button
                            onClick={() => setIsOpen(!isOpen)}
                            className="inline-flex items-center justify-center p-2 rounded-md text-slate-400 hover:text-slate-500 hover:bg-slate-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500"
                        >
                            <span className="sr-only">Open main menu</span>
                            {/* Hamburger Icon */}
                            <svg
                                className={`${isOpen ? "hidden" : "block"} h-6 w-6`}
                                xmlns="http://www.w3.org/2000/svg"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M4 6h16M4 12h16M4 18h16"
                                />
                            </svg>
                            {/* Close Icon */}
                            <svg
                                className={`${isOpen ? "block" : "hidden"} h-6 w-6`}
                                xmlns="http://www.w3.org/2000/svg"
                                fill="none"
                                viewBox="0 0 24 24"
                                stroke="currentColor"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M6 18L18 6M6 6l12 12"
                                />
                            </svg>
                        </button>
                    </div>
                </div>
            </div>

            {/* Mobile Menu */}
            <div className={`${isOpen ? "block" : "hidden"} md:hidden bg-white border-b border-slate-200`}>
                <div className="pt-2 pb-3 space-y-1">
                    {links.map((link) => (
                        <Link
                            key={link.href}
                            href={link.href}
                            onClick={() => setIsOpen(false)}
                            className={`block pl-3 pr-4 py-2 border-l-4 text-base font-medium ${isActive(link.href)
                                ? "bg-blue-50 border-blue-500 text-blue-700"
                                : "border-transparent text-slate-500 hover:bg-slate-50 hover:border-slate-300 hover:text-slate-700"
                                }`}
                        >
                            {link.label}
                        </Link>
                    ))}
                </div>
            </div>
        </nav>
    );
};
