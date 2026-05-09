'use client';

export default function Spinner({ size = 'md', color = 'cyan' }) {
  const sizes = { sm: 'w-4 h-4', md: 'w-8 h-8', lg: 'w-12 h-12' };
  const colors = {
    cyan:  'border-cyan-400',
    green: 'border-emerald-400',
    white: 'border-white',
  };

  return (
    <div
      className={`${sizes[size]} rounded-full border-2 border-navy-500 ${colors[color]} border-t-transparent animate-spin`}
      role="status"
      aria-label="Memuat data..."
    />
  );
}

export function SkeletonCard() {
  return (
    <div className="glass-card p-5 space-y-4">
      <div className="flex items-start justify-between">
        <div className="space-y-2">
          <div className="skeleton h-4 w-20 rounded" />
          <div className="skeleton h-3 w-32 rounded" />
        </div>
        <div className="skeleton h-6 w-24 rounded-full" />
      </div>
      <div className="skeleton h-8 w-28 rounded" />
      <div className="flex gap-2">
        <div className="skeleton h-6 w-16 rounded-lg" />
        <div className="skeleton h-6 w-16 rounded-lg" />
        <div className="skeleton h-6 w-16 rounded-lg" />
      </div>
      <div className="skeleton h-3 w-full rounded" />
      <div className="skeleton h-3 w-3/4 rounded" />
    </div>
  );
}

export function SkeletonGrid({ count = 9 }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
      {Array.from({ length: count }).map((_, i) => (
        <SkeletonCard key={i} />
      ))}
    </div>
  );
}
