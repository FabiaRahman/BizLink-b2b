// frontend/js/api.js
const API_BASE = 'http://127.0.0.1:8000';

window.BizLinkAPI = {
    async call(endpoint, options = {}) {
        const token = localStorage.getItem('bizlink_token');
        const headers = {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` }),
            ...options.headers
        };

        try {
            const res = await fetch(`${API_BASE}${endpoint}`, {
                ...options,
                headers
            });

            if (res.status === 401) {
                localStorage.removeItem('bizlink_token');
                localStorage.removeItem('bizlink_user');
                window.location.href = 'index.html';
                return null;
            }
            if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
            return await res.json();
        } catch (err) {
            console.error('API Call Failed:', err);
            throw err;
        }
    }
};