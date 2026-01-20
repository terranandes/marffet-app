/* Configuration for Environment-Aware API Calls */
const CONFIG = {
    // Detect if running on the Production Frontend (martian-app)
    // If so, point to the Production Backend (martian-api)
    API_BASE: window.location.hostname === 'martian-app.zeabur.app'
        ? 'https://martian-api.zeabur.app'
        : '' // Default: Use relative path for localhost (or direct backend usage)
};

export default CONFIG;
