export const BACKEND_URL =
  window.location.hostname === "localhost"
    ? "http://localhost:8000" // local FastAPI
    : "https://your-render-backend-url.onrender.com"; 
