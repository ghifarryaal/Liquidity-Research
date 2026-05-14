import './globals.css';
import { MentorProvider } from '@/lib/mentorContext';
import ChatWidget from '@/components/ui/ChatWidget';

// Required for Cloudflare Pages (next-on-pages)
export const runtime = 'edge';

export const metadata = {
  title: 'LiquidityResearch — Analisis Saham LQ45 & KOMPAS100',
  description:
    'Platform analisis saham Indonesia berbasis Machine Learning. Temukan peluang Buy the Dip, Momentum, dan lebih banyak insight untuk LQ45 dan KOMPAS100 — tanpa perlu login.',
  keywords: ['saham Indonesia', 'LQ45', 'KOMPAS100', 'analisis teknikal', 'RSI', 'MACD', 'clustering ML'],
  openGraph: {
    title: 'LiquidityResearch',
    description: 'Analisis saham LQ45 & KOMPAS100 dengan Machine Learning',
    type: 'website',
  },
};

export default function RootLayout({ children }) {
  return (
    <html lang="id" className="dark" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap"
          rel="stylesheet"
        />
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20,300,0,0&display=block" />
      </head>
      <body>
        <MentorProvider>
          {children}
          <ChatWidget />
        </MentorProvider>
      </body>
    </html>
  );
}

