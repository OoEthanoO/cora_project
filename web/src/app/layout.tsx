import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const mono = JetBrains_Mono({
  variable: "--font-mono-code",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  metadataBase: new URL(
    process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000",
  ),
  title: "CORA — Coastal Risk Analyzer",
  description:
    "A desktop tool for modelling coastal flooding: sea level rise scenarios, population exposure, infrastructure impact, and adaptation strategies like sea walls and wetland restoration.",
  openGraph: {
    title: "CORA — Coastal Risk Analyzer",
    description:
      "Model coastal flood risk, population exposure and adaptation strategies on your own machine.",
    type: "website",
    images: ["/img/cora-screenshot.png"],
  },
  icons: {
    icon: "/img/cora-icon.png",
  },
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${mono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col font-sans">{children}</body>
    </html>
  );
}
