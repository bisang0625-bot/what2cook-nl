/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  
  // 이미지 최적화 설정
  images: {
    // 모든 외부 이미지 도메인 허용 (보안보다 편의성 우선 설정)
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
      {
        protocol: 'http',
        hostname: '**',
      },
    ],
    // 이미지 포맷 최적화 (압축률 향상)
    formats: ['image/avif', 'image/webp'],
    // 이미지 크기 최적화 (다양한 디바이스 대응)
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
    // 캐시 유지 시간 (초 단위)
    minimumCacheTTL: 60,
  },

  // 성능 및 보안 최적화
  compress: true,
  poweredByHeader: false,
  
  // 빌드 속도 및 결과물 최적화
  swcMinify: true,

  // Webpack 설정: JSON 파일 경로 해석
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': __dirname,
    }
    return config
  },
}

module.exports = nextConfig