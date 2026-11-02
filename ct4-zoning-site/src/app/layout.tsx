import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const inter = Inter({
  variable: "--font-sans",
  subsets: ["latin"],
});

const mono = JetBrains_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "CT-4 Zoning Code Reader",
  description: "District-level zoning restrictiveness for the towns of Connecticut's 4th Congressional District, checked against the National Zoning Atlas.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className={`${inter.variable} ${mono.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col">
        <nav className="border-b border-(--rule) bg-(--surface)" aria-label="Main">
          <div className="max-w-6xl mx-auto px-4 h-11 flex items-center justify-between text-sm">
            <Link href="/" className="font-semibold tracking-tight">CT-4 Zoning Code Reader</Link>
            <div className="flex items-center gap-5 text-(--ink-dim)">
              <Link href="/" className="hover:text-(--accent)">Dashboard</Link>
              <Link href="/method" className="hover:text-(--accent)">Method</Link>
            </div>
          </div>
        </nav>
        {children}
      </body>
    </html>
  );
}
