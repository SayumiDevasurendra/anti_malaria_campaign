import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Navbar_10 } from "../components/Navbar_10";
import { Footer_10 } from "../components/Footer_10";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Malaria Risk Prediction | Sri Lanka",
  description: "District-wise malaria risk forecasting system",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} min-h-screen bg-slate-50 text-slate-900 flex flex-col`}>
        <Navbar_10 />
        <main className="flex-grow">
          {children}
        </main>
        <Footer_10 />
      </body>
    </html>
  );
}
