import useSWR from 'swr';
import { api } from '@/lib/api';

/**
 * SWR hook for fetching cluster analysis data.
 *
 * @param {string} indexName  'lq45' or 'kompas100'
 * @param {number} periodDays  Default 180
 */
export function useClusterData(indexName, periodDays = 180) {
  const key = indexName ? `cluster-${indexName}-${periodDays}` : null;

  const { data, error, isLoading, mutate } = useSWR(
    key,
    () => api.getClusterData(indexName, periodDays),
    {
      revalidateOnFocus: false,
      dedupingInterval: 60 * 1000, // 1 min dedup (was 5min)
      errorRetryCount: 2,
      errorRetryInterval: 3000,
    }
  );

  return {
    data,
    stocks: data?.stocks ?? [],
    macro: data?.macro ?? null,
    macroSentiment: data?.macro_sentiment ?? null,
    supervisedValidation: data?.supervised_validation ?? null,
    clusterSummary: data?.cluster_summary ?? {},
    generatedAt: data?.generated_at ?? null,
    totalStocks: data?.total_stocks ?? 0,
    isLoading,
    isError: !!error,
    error,
    refresh: () => mutate(),
  };
}
