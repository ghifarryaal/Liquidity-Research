'use client';

import { useState, useRef, useEffect } from 'react';
import { INDICATOR_TOOLTIPS } from '@/constants/clusterConfig';

/**
 * InfoTooltip — ? icon with hover tooltip explaining an indicator in Indonesian.
 * @param {string} indicator  Key from INDICATOR_TOOLTIPS
 * @param {string} [className]
 */
export default function InfoTooltip({ indicator, className = '' }) {
  const [visible, setVisible] = useState(false);
  const [position, setPosition] = useState({ top: 0, left: 0 });
  const ref = useRef(null);
  const tip = INDICATOR_TOOLTIPS[indicator];

  if (!tip) return null;

  const show = () => {
    if (ref.current) {
      const rect = ref.current.getBoundingClientRect();
      setPosition({
        top: rect.bottom + window.scrollY + 8,
        left: Math.max(8, rect.left + window.scrollX - 100),
      });
    }
    setVisible(true);
  };

  const hide = () => setVisible(false);

  return (
    <>
      <span
        ref={ref}
        onMouseEnter={show}
        onMouseLeave={hide}
        onFocus={show}
        onBlur={hide}
        tabIndex={0}
        role="button"
        aria-label={`Info tentang ${tip.title}`}
        className={`
          inline-flex items-center justify-center
          w-4 h-4 rounded-full text-xs font-bold cursor-help
          select-none transition-all duration-150
          ${className}
        `}
        style={{
          background: 'rgba(6,182,212,0.15)',
          border: '1px solid rgba(6,182,212,0.35)',
          color: '#06b6d4',
          fontSize: '10px',
          lineHeight: 1,
        }}
      >
        ?
      </span>

      {visible && (
        <div
          className="tooltip-content"
          style={{
            position: 'fixed',
            top: position.top,
            left: position.left,
            zIndex: 9999,
          }}
          role="tooltip"
        >
          <p className="font-semibold text-cyan-400 mb-1.5" style={{ fontSize: 13 }}>
            {tip.title}
          </p>
          <p className="text-slate-300 leading-relaxed" style={{ fontSize: 12 }}>
            {tip.body}
          </p>
        </div>
      )}
    </>
  );
}

/** Inline label with tooltip icon */
export function LabelWithTooltip({ label, indicator, className = '' }) {
  return (
    <span className={`inline-flex items-center gap-1.5 ${className}`}>
      <span>{label}</span>
      <InfoTooltip indicator={indicator} />
    </span>
  );
}
