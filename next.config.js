/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  
  // 이미지 최적화 설정
  images: {
    // 외부 이미지 도메인 허용 (필요시 추가)
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
    // 이미지 포맷 최적화
    formats: ['image/avif', 'image/webp'],
    // 이미지 크기 제한
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
    // 최소화된 이미지 최적화
    minimumCacheTTL: 60,
    // 이미지 로더 (기본값 사용)
    // dangerouslyAllowSVG: true,
    // contentSecurityPolicy: "default-src 'self'; script-src 'none'; sandbox;",
  },

  // 성능 최적화
  compress: true,
  poweredByHeader: false,
  
  // 빌드 최적화
  swcMinify: true,
  
  // 실험적 기능 (필요시)
  // experimental: {
  //   optimizeCss: true,
  // },
}

module.exports = nextConfig
