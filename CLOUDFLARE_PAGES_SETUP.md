# Cloudflare Pages Setup Instructions

## Build Configuration

**IMPORTANT**: Update these settings in Cloudflare Pages Dashboard:

### Build Settings:
- **Framework preset**: Next.js
- **Build command**: `npx next build && npx @cloudflare/next-on-pages`
- **Build output directory**: `.vercel/output/static`
- **Root directory**: `frontend`

### Environment Variables:
```
NEXT_PUBLIC_API_URL=https://api-quant.indonesiastockanalyst.my.id
NODE_VERSION=22
```

## Troubleshooting

If you get "routes not configured for edge runtime" error:
1. Make sure `frontend/src/app/stock/[ticker]/page.jsx` has `export const runtime = 'edge'`
2. Make sure build command includes `npx @cloudflare/next-on-pages`
3. Check that `pages_build_output_dir` in `wrangler.toml` is `.vercel/output/static`

## Alternative: Migrate to OpenNext

If @cloudflare/next-on-pages continues to fail, consider migrating to OpenNext:
https://opennext.js.org/cloudflare
