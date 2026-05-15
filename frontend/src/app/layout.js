import './globals.css';
import { MentorProvider } from '@/lib/mentorContext';
import ChatWidget from '@/components/ui/ChatWidget';

export const metadata = {
  title: 'LiquidityResearch — Analisis Saham LQ45 & KOMPAS100',
  description:
    'Platform analisis saham Indonesia berbasis Machine Learning. Temukan peluang Buy the Dip, Momentum, dan lebih banyak insight untuk LQ45 dan KOMPAS100 — tanpa perlu login.',
  keywords: ['saham Indonesia', 'LQ45', 'KOMPAS100', 'analisis teknikal', 'RSI', 'MACD', 'clustering ML'],
  authors: [{ name: 'Ghifar Ryal', url: 'https://github.com/ghifarryaal' }],
  creator: 'Ghifar Ryal',
  metadataBase: new URL('https://quant.indonesiastockanalyst.my.id'),
  openGraph: {
    title: 'LiquidityResearch — Analisis Saham AI',
    description: 'Platform analisis saham LQ45 & KOMPAS100 dengan Machine Learning. Trade plan otomatis, backtest real-time, AI assistant.',
    type: 'website',
    url: 'https://quant.indonesiastockanalyst.my.id',
    siteName: 'LiquidityResearch',
    locale: 'id_ID',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'LiquidityResearch — Analisis Saham AI',
    description: 'Platform analisis saham LQ45 & KOMPAS100 dengan Machine Learning.',
  },
  robots: {
    index: true,
    follow: true,
  },
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 5,
  },
};

export default function RootLayout({ children }) {
  return (
    <html lang="id" suppressHydrationWarning>
      <head>
        {/* Preconnect for faster font loading */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />

        {/* Fonts — display=swap prevents render blocking */}
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Geist+Mono:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />

        {/* Material Symbols — display=block prevents FOUT */}
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20,300,0,0&display=block"
        />

        {/* Favicon */}
        <link rel="icon" href="/favicon.ico" sizes="any" />
        <link rel="icon" href="/icon.svg" type="image/svg+xml" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />

        {/* Theme color for mobile browser chrome */}
        <meta name="theme-color" content="#0f1418" />
        <meta name="color-scheme" content="dark" />
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
