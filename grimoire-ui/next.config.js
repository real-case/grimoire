/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  env: {
    FASTAPI_URL: process.env.FASTAPI_URL || 'http://localhost:8000',
  },
}

module.exports = nextConfig
