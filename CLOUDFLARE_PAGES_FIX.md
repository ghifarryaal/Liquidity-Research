# Cloudflare Pages - Alternative Setup (Without Edge Runtime)

## Problem
@cloudflare/next-on-pages has strict edge runtime requirements that cause 500 errors with certain libraries (SWR, lightweight-charts, etc.)

## Solution: Use Static Export

### Step 1: Update Build Settings in Cloudflare Pages Dashboard

Go to: **Cloudflare Dashboard → Pages → Your Project → Settings → Builds & deployments**

Change to:
```
Framework preset: Next.js (Static HTML Export)
Build command: npm run build
Build output directory: out
Root directory: frontend
```

### Step 2: Update next.config.mjs

The config needs to enable static export:
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'export',
  images: {
    unoptimized: true,
  },
  trailingSlash: true,
};

export default nextConfig;
```

### Step 3: Environment Variables

Keep the same:
```
NEXT_PUBLIC_API_URL=https://api-quant.indonesiastockanalyst.my.id
```

## Trade-offs

**Pros:**
- ✅ No edge runtime restrictions
- ✅ All libraries work (SWR, lightweight-charts, etc.)
- ✅ Simpler deployment
- ✅ Still uses Cloudflare CDN

**Cons:**
- ❌ No server-side rendering (SSR) - but we're using client-side rendering anyway
- ❌ No API routes - but we have separate backend
- ❌ Dynamic routes need client-side routing - already using this

## Alternative: Keep Cloudflare Proxy + Deploy to Vercel

If static export doesn't work, you can:
1. Deploy frontend to Vercel
2. Keep Cloudflare as DNS + proxy in front of Vercel
3. Get Cloudflare security + Vercel's Next.js compatibility

Setup:
- Vercel: Deploy app
- Cloudflare: Set DNS to proxy through Cloudflare (orange cloud icon)
- Result: Cloudflare DDoS protection + WAF + Vercel hosting
