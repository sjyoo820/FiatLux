/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  env: {
    STREAMLIT_CHATBOT_URL: process.env.STREAMLIT_CHATBOT_URL || 'http://localhost:8501',
    BACKEND_API_URL: process.env.BACKEND_API_URL || 'http://localhost:3001'
  }
}

module.exports = nextConfig
