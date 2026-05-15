export const runtime = 'edge';

export default async function StockDetailPage(props) {
  const params = await props.params;
  const ticker = params?.ticker || 'UNKNOWN';
  
  return (
    <html>
      <body style={{ padding: '2rem', fontFamily: 'monospace', background: '#000', color: '#0f0' }}>
        <h1>🚀 Edge Runtime Test</h1>
        <p>Ticker: <strong>{ticker}</strong></p>
        <p>Status: ✅ Edge runtime working!</p>
        <p>Time: {new Date().toISOString()}</p>
        <a href="/" style={{ color: '#0ff' }}>← Back to home</a>
      </body>
    </html>
  );
}
