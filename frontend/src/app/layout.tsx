import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Intelligent Research Agent — Scholar Intelligence System',
  description: 'Hệ thống Nghiên cứu Thông minh sử dụng Agentic RAG',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="vi">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body>{children}</body>
    </html>
  );
}
