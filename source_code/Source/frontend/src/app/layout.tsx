import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Intelligent Research Agent — Scholar Intelligence System',
  description: 'Intelligent Research System using Agentic RAG',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body>{children}</body>
    </html>
  );
}
