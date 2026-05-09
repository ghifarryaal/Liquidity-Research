'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

export default function Navbar({ activeIndex, onIndexChange, generatedAt, onRefresh }) {
  const [time, setTime] = useState('');
  const [isRefreshing, setIsRefreshing] = useState(false);

  useEffect(() => {
    const update = () => {
      setTime(new Date().toLocaleTimeString('id-ID', {
        timeZone: 'Asia/Jakarta', hour: '2-digit', minute: '2-digit'
      }));
    };
    update();
    const id = setInterval(update, 60000);
    return () => clearInterval(id);
  }, []);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await onRefresh();
    // Keep spinning for at least 1s for visual feedback
    setTimeout(() => setIsRefreshing(false), 1000);
  };

  return (
    <nav className="bg-surface-container-low/90 backdrop-blur-lg border-b border-outline-variant fixed top-0 left-0 w-full z-50 flex justify-between items-center h-[64px] px-container-padding shadow-lg">
      <div className="flex items-center gap-12">
        {/* Brand Logo */}
        <div className="text-2xl font-bold text-primary tracking-tighter flex items-center gap-3">
          <div className="w-2.5 h-2.5 bg-primary rounded-full animate-pulse shadow-[0_0_12px_rgba(0,255,178,1)]" />
          LiquidityResearch
        </div>

        {/* Navigation Links (Web) */}
        <div className="hidden md:flex gap-8 h-full items-center">
          {['lq45', 'kompas100', 'dbx'].map((id) => (
            <button 
              key={id}
              onClick={() => onIndexChange(id)}
              className={`font-body-standard text-[13px] font-bold uppercase tracking-[0.1em] transition-all relative py-2 ${activeIndex === id ? 'text-primary' : 'text-on-surface-variant hover:text-on-surface'}`}
            >
              {id === 'dbx' ? 'DBX (Second Liner)' : id.toUpperCase()}
              {activeIndex === id && (
                <motion.div 
                  layoutId="nav-underline"
                  className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary"
                />
              )}
            </button>
          ))}
        </div>
      </div>

      <div className="flex items-center gap-8">
        {/* Market Clock */}
        <div className="hidden lg:flex items-center gap-3 text-on-surface-variant bg-surface-container-highest/40 px-4 py-2 rounded-xl border border-outline-variant/50">
          <span className="material-symbols-outlined text-[18px] text-primary animate-pulse">schedule</span>
          <span className="font-data-mono text-[11px] font-bold tracking-tight uppercase">{time} WIB | JKT OPEN</span>
        </div>

        {/* Trailing Icons */}
        <div className="flex items-center gap-4">
          <button 
            onClick={handleRefresh} 
            className={`transition-all p-2.5 rounded-xl hover:bg-primary/10 group ${isRefreshing ? 'text-primary' : 'text-on-surface-variant'}`}
            title="Refresh Data"
          >
            <span className={`material-symbols-outlined text-[24px] ${isRefreshing ? 'animate-spin' : 'group-hover:rotate-180 transition-transform duration-700'}`}>refresh</span>
          </button>
          
          <button className="relative transition-all p-2.5 rounded-xl hover:bg-primary/10 group text-on-surface-variant" title="Live Sensors">
            <span className="material-symbols-outlined text-[24px] group-hover:text-primary transition-colors">sensors</span>
            {/* Active Monitoring Indicator */}
            <span className="absolute top-3 right-3 w-2 h-2 bg-primary rounded-full animate-ping opacity-75" />
            <span className="absolute top-3 right-3 w-2 h-2 bg-primary rounded-full shadow-[0_0_8px_rgba(0,255,178,0.6)]" />
          </button>
        </div>
      </div>
    </nav>
  );
}
