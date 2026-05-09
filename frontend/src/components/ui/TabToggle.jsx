'use client';

import { motion } from 'framer-motion';

const INDEX_OPTIONS = [
  { value: 'lq45',      label: 'LQ45',       sublabel: '45 Saham' },
  { value: 'kompas100', label: 'KOMPAS 100',  sublabel: '100 Saham' },
];

export default function TabToggle({ activeIndex, onIndexChange }) {
  return (
    <div
      className="inline-flex rounded-xl p-1 gap-1"
      style={{
        background: 'rgba(255,255,255,0.04)',
        border: '1px solid rgba(255,255,255,0.08)',
      }}
      role="tablist"
      aria-label="Pilih indeks saham"
    >
      {INDEX_OPTIONS.map((opt) => {
        const isActive = activeIndex === opt.value;
        return (
          <button
            key={opt.value}
            role="tab"
            aria-selected={isActive}
            onClick={() => onIndexChange(opt.value)}
            className={`
              relative flex flex-col items-center px-5 py-2 rounded-lg text-sm font-semibold
              transition-all duration-200 cursor-pointer
              ${isActive
                ? 'text-cyan-400'
                : 'text-slate-400 hover:text-slate-200'
              }
            `}
            style={{
              border: isActive ? '1px solid rgba(6,182,212,0.4)' : '1px solid transparent',
              background: isActive ? 'rgba(6,182,212,0.12)' : 'transparent',
            }}
          >
            {isActive && (
              <motion.div
                layoutId="tab-highlight"
                className="absolute inset-0 rounded-lg"
                style={{
                  background: 'rgba(6,182,212,0.1)',
                  boxShadow: '0 0 12px rgba(6,182,212,0.2)',
                }}
                transition={{ type: 'spring', bounce: 0.2, duration: 0.4 }}
              />
            )}
            <span className="relative z-10 leading-tight">{opt.label}</span>
            <span className="relative z-10 text-xs font-normal opacity-60">{opt.sublabel}</span>
          </button>
        );
      })}
    </div>
  );
}
