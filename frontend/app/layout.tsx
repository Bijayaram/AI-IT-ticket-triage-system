import type { Metadata } from "next";
// import { Inter } from "next/font/google"; // Commented out due to Windows ESM path issue
import "./globals.css";
import { Toaster } from "react-hot-toast";

// const inter = Inter({ subsets: ["latin"] }); // Commented out due to Windows ESM path issue

export const metadata: Metadata = {
  title: "IT Support Portal",
  description: "AI-powered IT ticket triage and support system",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="font-sans">
        {children}
        <Toaster position="top-right" />
      </body>
    </html>
  );
}
