const API_BASE_URL = 'http://localhost:5000';  // Your Flask backend URL

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