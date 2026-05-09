import useSWR from 'swr';
import { api } from '@/lib/api';

/**
 * SWR hook for fetching single stock OHLCV + indicator series.
 * Only fetches when `ticker` is non-null (lazy fetch on card expand).
 */
export function useStockDetail(ticker, periodDays = 180) {
  const key = ticker ? `stock-${ticker}-${periodDays}` : null;

  const { data, error, isLoading } = useSWR(
    key,
    () => api.getStockDetail(ticker, periodDays),
    {
      revalidateOnFocus: false,
      dedupingInterval: 10 * 60 * 1000, // 10 min cache per ticker
      errorRetryCount: 1,
    }
  );

  return {
    detail: data ?? null,
    ohlcv: data?.ohlcv ?? [],
    ema20: data?.ema_20_series ?? [],
    ema50: data?.ema_50_series ?? [],
    bbUpper: data?.bb_upper_series ?? [],
    bbMiddle: data?.bb_middle_series ?? [],
    bbLower: data?.bb_lower_series ?? [],
    indicators: data?.indicators ?? null,
    isLoading,
    isError: !!error,
  };
}
