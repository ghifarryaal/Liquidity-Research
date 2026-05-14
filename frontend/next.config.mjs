/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // NOTE: rewrites() only work in server-rendered Next.js, NOT in Cloudflare Pages static export.
  // The frontend calls the backend directly via NEXT_PUBLIC_API_URL from the browser.
};

export default nextConfig;
