/** @type {import('next').NextConfig} */
const nextConfig = {
  /**
   * STATIC EXPORT CONFIGURATION
   * Disabled temporarily to allow dynamic routes to build
   * Re-enable after implementing generateStaticParams() for all dynamic routes
   */
  // output: 'export',

  /**
   * IMAGE OPTIMIZATION
   * Static exports don't support Next.js Image Optimization API
   * Set unoptimized to true to use standard <img> tags
   */
  images: {
    unoptimized: true,
  },

  /**
   * TRAILING SLASH
   * Ensures consistent URL structure for static hosting
   */
  trailingSlash: true,

  /**
   * STRICT MODE
   * Enables React strict mode for better development warnings
   */
  reactStrictMode: true,

  /**
   * TYPESCRIPT
   * Optionally ignore build errors during production build
   * Set to false for production builds
   */
  typescript: {
    ignoreBuildErrors: false,
  },

  /**
   * ESLINT
   * Optionally ignore ESLint errors during production build
   * Set to false for production builds
   */
  eslint: {
    ignoreDuringBuilds: false,
  },
}

module.exports = nextConfig
