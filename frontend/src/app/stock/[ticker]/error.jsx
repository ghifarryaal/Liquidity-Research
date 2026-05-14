'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function StockError({ error, reset }) {
  const router = useRouter();

  useEffect(() => {
    console.error('[StockDetailPage] Render error:', error);
  }, [error]);

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-6">
      <div className="max-w-md w-full bg-surface-container rounded-lg border border-error/30 p-8 text-center">
        <span className="material-symbols-outlined text-error text-5xl mb-4 block">error</span>
        <h1 className="text-2xl font-bold text-on-surface mb-2">Halaman Gagal Dimuat</h1>
        <p className="text-on-surface-variant mb-6 text-sm">
          {error?.message || 'Terjadi kesalahan saat memuat detail saham. Coba lagi atau kembali ke dashboard.'}
        </p>
        <div className="flex gap-3 justify-center">
          <button
            onClick={() => reset()}
            className="px-5 py-2 bg-surface border border-primary text-primary rounded font-bold uppercase tracking-widest text-xs hover:bg-primary/10 transition-colors"
          >
            Coba Lagi
          </button>
          <button
            onClick={() => router.push('/')}
            className="px-5 py-2 bg-primary text-on-primary rounded font-bold uppercase tracking-widest text-xs"
          >
            Kembali
          </button>
        </div>
      </div>
    </div>
  );
}
