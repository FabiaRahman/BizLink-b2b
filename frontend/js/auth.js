// frontend/js/auth.js
window.BizLinkAuth = {
    async login(email, password) {
        if (!email || !password) throw new Error('Please fill in all fields');
        if (!email.includes('@')) throw new Error('Please enter a valid email address');
        if (password.length < 6) throw new Error('Password must be at least 6 characters');

        const formData = new FormData();
        formData.append('username', email);
        formData.append('password', password);

        try {
            const res = await fetch('http://127.0.0.1:8000/auth/login', {
                method: 'POST',
                body: formData
            });

            const data = await res.json();

            if (!res.ok) throw new Error(data.detail || 'Login failed');

            if (data.access_token) {
                localStorage.setItem('bizlink_token', data.access_token);
                // ✅ Ensure user object has consistent role format
                const user = data.user || { name: email, role: 'operator' };
                localStorage.setItem('bizlink_user', JSON.stringify({
                    name: user.name || user.username || email,
                    email: user.email || email,
                    role: user.role || 'operator'  // ✅ Normalize role
                }));
                return true;
            }
            throw new Error('Invalid response from server');
        } catch (error) {
            if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
                throw new Error('Cannot connect to server. Ensure backend is running on port 8000');
            }
            throw error;
        }
    },

    async register(name, email, password, role) {
        if (!name || !email || !password || !role) throw new Error('Please fill in all fields');
        if (!email.includes('@')) throw new Error('Please enter a valid email address');
        if (password.length < 6) throw new Error('Password must be at least 6 characters');

        try {
            await window.BizLinkAPI.call('/auth/register', {
                method: 'POST',
                body: JSON.stringify({
                    username: name,
                    email: email,
                    password: password,
                    role: role  // ✅ Ensure role is one of: admin, manager, operator
                })
            });
            return true;
        } catch (error) {
            if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
                throw new Error('Cannot connect to server. Ensure backend is running on port 8000');
            }
            throw error;
        }
    },

    checkAuth() {
        const token = localStorage.getItem('bizlink_token');
        if (!token) {
            window.location.href = 'index.html';
            return false;
        }
        return true;
    },

    getUser() {
        try {
            const userStr = localStorage.getItem('bizlink_user');
            return userStr ? JSON.parse(userStr) : {};
        } catch {
            return {};
        }
    },

    getRole() {
        const user = this.getUser();
        // ✅ Normalize role to lowercase and validate
        const role = (user.role || 'operator').toLowerCase();
        return ['admin', 'manager', 'operator'].includes(role) ? role : 'operator';
    },

    logout() {
        localStorage.clear();
        window.location.href = 'index.html';
    }
};