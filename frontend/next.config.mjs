import { setupDevPlatform } from '@cloudflare/next-on-pages/next-dev';

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
};

// Enable Cloudflare bindings in local dev (no-op in production build)
if (process.env.NODE_ENV === 'development') {
  await setupDevPlatform();
}

export default nextConfig;
