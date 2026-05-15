'use client';

import { useState } from 'react';

export default function Disclaimer() {
  const [dismissed, setDismissed] = useState(false);

  if (dismissed) return null;

  return (
    <div className="mx-auto max-w-[1440px] px-4 md:px-6 lg:px-8 mb-4">
      <div className="bg-amber-500/8 border border-amber-500/20 rounded-xl px-4 py-2.5 flex items-center gap-3 animate-in fade-in slide-in-from-top-2 duration-500">
        <span className="material-symbols-outlined text-amber-500/80 text-[18px] shrink-0">info</span>
        <p className="text-[11px] text-white/50 font-medium leading-relaxed flex-1">
          <span className="text-amber-500/80 font-bold">Disclaimer:</span>{' '}
          Alat bantu analisis teknikal berbasis AI — bukan penasihat keuangan resmi. Keputusan investasi sepenuhnya tanggung jawab Anda.
        </p>
        <button
          onClick={() => setDismissed(true)}
          className="text-white/30 hover:text-white/60 transition-colors shrink-0"
          aria-label="Tutup disclaimer"
        >
          <span className="material-symbols-outlined text-[16px]">close</span>
        </button>
      </div>
    </div>
  );
}
