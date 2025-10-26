/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  // Use standalone output for production builds (SSR)
  // This skips static page generation which causes pre-rendering errors
  output: 'standalone',
  env: {
    FASTAPI_URL: process.env.FASTAPI_URL || 'http://localhost:8000',
  },
}

module.exports = nextConfig
