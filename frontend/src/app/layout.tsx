import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "../../styles/global.css";
import Navbar from "../../components/Navbar";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "RuleBox F1 - AI Assistant",
  description: "AI-powered F1 regulations and rules assistant",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${inter.variable} antialiased`}
      >
        <div className="min-h-screen bg-[#0d0d0d] text-white">
          <Navbar />
          <main>{children}</main>
        </div>
      </body>
    </html>
  );
}
