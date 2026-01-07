/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  env: {
    BACKEND_API_URL: process.env.BACKEND_API_URL || 'http://localhost:8000/api/v1',
  },
}

module.exports = nextConfig