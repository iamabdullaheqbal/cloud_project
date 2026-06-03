import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "FinStress Bot — Financial Study Pressure Assistant",
  description: "AI assistant for financial study pressure support.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full">
      <body className="h-full antialiased">{children}</body>
    </html>
  );
}
