/** @type {import('next').NextConfig} */

// O navegador fala sempre com a mesma origem (/api/*). O Next encaminha para
// o FastAPI sem o prefixo, para que os cookies httpOnly funcionem sem CORS.
const apiUrl = process.env.API_INTERNAL_URL ?? "http://localhost:8010";

const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${apiUrl}/:path*` }];
  },
};

export default nextConfig;
