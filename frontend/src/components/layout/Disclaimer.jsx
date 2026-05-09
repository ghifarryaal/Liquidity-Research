'use client';

export default function Disclaimer() {
  return (
    <div className="mx-auto max-w-[1440px] px-container-padding mb-6">
      <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl p-4 flex items-center gap-4 animate-in fade-in slide-in-from-top-4 duration-700">
        <div className="flex-shrink-0 w-10 h-10 rounded-full bg-amber-500/20 flex items-center justify-center">
          <span className="material-symbols-outlined text-amber-500 text-[24px]">warning</span>
        </div>
        <div className="flex-1">
          <h4 className="text-[12px] font-black text-amber-500 uppercase tracking-widest mb-0.5">Financial Disclaimer</h4>
          <p className="text-[11px] text-white/60 font-medium leading-relaxed">
            Aplikasi ini adalah alat bantu analisis teknikal berbasis AI dan <span className="text-white font-bold text-amber-500/80">bukan merupakan penasihat keuangan resmi</span>. 
            Segala keputusan investasi sepenuhnya berada di tangan Anda. Gunakan data ini sebagai referensi, bukan satu-satunya dasar pengambilan keputusan.
          </p>
        </div>
      </div>
    </div>
  );
}
