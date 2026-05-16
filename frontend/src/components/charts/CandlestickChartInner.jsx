'use client';

import { useEffect, useRef } from 'react';

/**
 * Inner chart component — only rendered client-side via dynamic import.
 * Compatible with lightweight-charts v4 AND v5 API.
 */
export default function CandlestickChartInner({ ohlcv, ema20, ema50, bbUpper, bbMiddle, bbLower }) {
  const containerRef = useRef(null);
  const chartRef = useRef(null);

  useEffect(() => {
      let isMounted = true;
      const container = containerRef.current;
      if (!container || !ohlcv?.length) return;

      let ro;

      async function initChart() {
        // Clear previous content immediately
        container.innerHTML = '';
        if (chartRef.current) {
          try {
            chartRef.current.remove();
          } catch (e) {
            console.error('Error removing chart:', e);
          }
          chartRef.current = null;
        }

        const LWC = await import('lightweight-charts');
        
        if (!isMounted || !containerRef.current) return;

        // Clear again just in case another call slipped through
        container.innerHTML = '';

        const height = 500;
        const chartOptions = {
          width:  container.clientWidth,
          height,
          layout: {
            background: { color: '#0a0f12' },
            textColor:  '#87929a',
            fontSize:   11,
          },
          grid: {
            vertLines: { color: 'rgba(255,255,255,0.04)' },
            horzLines: { color: 'rgba(255,255,255,0.04)' },
          },
          crosshair: {
            vertLine: { color: 'rgba(6,182,212,0.4)', labelBackgroundColor: '#0f172a' },
            horzLine: { color: 'rgba(6,182,212,0.4)', labelBackgroundColor: '#0f172a' },
          },
          rightPriceScale: { 
            borderColor: 'rgba(255,255,255,0.05)', 
            textColor: '#64748b',
            autoScale: true,
            scaleMargins: {
              top: 0.08,
              bottom: 0.08,
            },
          },
          timeScale: {
            borderColor:     'rgba(255,255,255,0.05)',
            timeVisible:     true,
            secondsVisible:  false,
            fixLeftEdge:     true,
            fixRightEdge:    true,
            rightOffset:     0,
          },
          handleScroll: { mouseWheel: true, pressedMouseMove: true },
          handleScale:  { mouseWheel: true },
        };

        const chart = LWC.createChart(container, chartOptions);
        chartRef.current = chart;

        // ── Detect v4 vs v5 API ──────────────────────────────────────────────
        const isV5 = typeof LWC.CandlestickSeries !== 'undefined';

        const candleOpts = {
          upColor:         '#00FFB2',
          downColor:       '#ef4444',
          borderUpColor:   '#00FFB2',
          borderDownColor: '#ef4444',
          wickUpColor:     '#00FFB280',
          wickDownColor:   '#ef444480',
        };

        let candleSeries;
        if (isV5) {
          candleSeries = chart.addSeries(LWC.CandlestickSeries, candleOpts);
        } else {
          candleSeries = chart.addCandlestickSeries(candleOpts);
        }

        candleSeries.setData(ohlcv.map(bar => ({
          time:  bar.time,
          open:  bar.open,
          high:  bar.high,
          low:   bar.low,
          close: bar.close,
        })));

        // ── Helper to add line series ─────────────────────────────────────────
        function addLine(data, opts) {
          if (!data?.length) return;
          let series;
          if (isV5) {
            series = chart.addSeries(LWC.LineSeries, opts);
          } else {
            series = chart.addLineSeries(opts);
          }
          series.setData(data.map(d => ({ time: d.time, value: d.value })));
        }

        const LineStyle = LWC.LineStyle ?? { Dashed: 1, Dotted: 2 };

        addLine(ema20, {
          color: '#06b6d4', lineWidth: 1.5,
          priceLineVisible: false, lastValueVisible: false,
        });
        addLine(ema50, {
          color: '#a855f7', lineWidth: 1.5,
          priceLineVisible: false, lastValueVisible: false,
        });
        addLine(bbUpper, {
          color: 'rgba(245,158,11,0.7)', lineWidth: 1,
          lineStyle: LineStyle.Dashed,
          priceLineVisible: false, lastValueVisible: false,
        });
        addLine(bbMiddle, {
          color: 'rgba(245,158,11,0.35)', lineWidth: 1,
          lineStyle: LineStyle.Dotted,
          priceLineVisible: false, lastValueVisible: false,
        });
        addLine(bbLower, {
          color: 'rgba(245,158,11,0.7)', lineWidth: 1,
          lineStyle: LineStyle.Dashed,
          priceLineVisible: false, lastValueVisible: false,
        });

        chart.timeScale().fitContent();

        // Responsive
        ro = new ResizeObserver(entries => {
          if (!isMounted || !chartRef.current) return;
          const { width: w } = entries[0].contentRect;
          chartRef.current.resize(w, height);
        });
        ro.observe(container);
      }

      initChart();

      return () => {
        isMounted = false;
        ro?.disconnect();
        if (chartRef.current) {
          chartRef.current.remove();
          chartRef.current = null;
        }
      };
    }, [ohlcv, ema20, ema50, bbUpper, bbMiddle, bbLower]);

  return (
    <div className="w-full h-full relative">
      <div
        ref={containerRef}
        className="w-full h-full outline-none"
        style={{ minHeight: 500 }}
      />
    </div>
  );
}
