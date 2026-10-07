import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Network Traffic Analyzer",
  description: "Advanced dashboard for network traffic analysis and packet inspection.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className="font-sans antialiased bg-background text-foreground h-screen overflow-hidden"
      >
        {children}
      </body>
    </html>
  );
}
