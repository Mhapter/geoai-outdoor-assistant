import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Fieldwise — Your Outdoor Intelligence Assistant",
  description: "Live, evidence-grounded outdoor spatio-temporal reasoning assistant powered by an open-weights <=3B Small Language Model (Qwen2.5-1.5B-Instruct). CSRE, IIT Bombay 2026.",
  icons: {
    icon: "/favicon.ico",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
