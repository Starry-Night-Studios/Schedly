// Detect if we're in production (on Render) or development
const isProduction = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1';

const API_BASE_URL = isProduction 
    ? 'https://schedly-backend.onrender.com'  // Replace with your actual Render backend URL
    : 'http://localhost:5000';

const API_ENDPOINTS = {
    VERIFY: `${API_BASE_URL}/verify`,
    UPLOAD: `${API_BASE_URL}/upload`,
    REGISTER: `${API_BASE_URL}/register`
};

// Export for use in other scripts
window.API_CONFIG = {
    BASE_URL: API_BASE_URL,
    ENDPOINTS: API_ENDPOINTS
};

// Also export the base URL for backwards compatibility
window.API_BASE_URL = API_BASE_URL;