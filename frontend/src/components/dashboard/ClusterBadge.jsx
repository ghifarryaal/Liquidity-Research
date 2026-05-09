'use client';

import { CLUSTER_CONFIG } from '@/constants/clusterConfig';

export default function ClusterBadge({ label, size = 'md' }) {
  const cfg = CLUSTER_CONFIG[label] ?? CLUSTER_CONFIG['Hold / Sideways'];

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 gap-1',
    md: 'text-xs px-2.5 py-1 gap-1.5',
    lg: 'text-sm px-3 py-1.5 gap-2',
  };

  return (
    <span
      className={`
        inline-flex items-center rounded-full font-semibold tracking-wide
        ${sizeClasses[size]}
        ${cfg.bgClass}
      `}
      style={{
        boxShadow: `0 0 12px ${cfg.glowColor}`,
        letterSpacing: '0.02em',
      }}
    >
      <span className={size === 'sm' ? 'text-xs' : 'text-sm'}>{cfg.icon}</span>
      <span>{label}</span>
    </span>
  );
}
