/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || '',
  },
  experimental: {
    serverComponentsExternalPackages: [],
  },
};

module.exports = nextConfig;
