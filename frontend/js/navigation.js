// frontend/js/navigation.js

window.BizLinkNav = {
    menuConfig: {
        admin: {
            menu: [
                { icon: '📊', label: 'Dashboard', href: 'dashboard.html', roles: ['admin'] },
                { icon: '📦', label: 'Orders', href: 'orders.html', roles: ['admin', 'manager', 'operator'] },
                { icon: '💸', label: 'Refund', href: 'refunds.html', roles: ['admin', 'manager'] },
                { icon: '👥', label: 'Leads', href: 'leads.html', roles: ['admin', 'manager', 'operator'] },
            ],
            management: [
                { icon: '🔍', label: 'Manual Reviews', href: 'reviews.html', roles: ['admin', 'manager'] },
                { icon: '📧', label: 'Scheduled Emails', href: 'scheduled-emails.html', roles: ['admin', 'manager'] },
                { icon: '⚠️', label: 'Error Logs', href: 'errors.html', roles: ['admin', 'manager', 'operator'] },
            ],
            others: [
                { icon: '⚙️', label: 'Settings', href: 'settings.html', roles: ['admin', 'manager', 'operator'] } // ✅ All roles get Settings
            ]
        },
        manager: {
            menu: [
                { icon: '📊', label: 'Dashboard', href: 'dashboard-manager.html', roles: ['manager'] },
                { icon: '📦', label: 'Orders', href: 'orders.html', roles: ['admin', 'manager', 'operator'] },
                { icon: '💸', label: 'Refund', href: 'refunds.html', roles: ['admin', 'manager'] },
                { icon: '👥', label: 'Leads', href: 'leads.html', roles: ['admin', 'manager', 'operator'] },
            ],
            management: [
                { icon: '🔍', label: 'Manual Reviews', href: 'reviews.html', roles: ['admin', 'manager'] },
                { icon: '⚠️', label: 'Error Logs', href: 'errors.html', roles: ['admin', 'manager', 'operator'] },
            ],
            others: [
                { icon: '⚙️', label: 'Settings', href: 'settings.html', roles: ['admin', 'manager', 'operator'] }
            ]
        },
        operator: {
            menu: [
                { icon: '📊', label: 'Dashboard', href: 'dashboard-operator.html', roles: ['operator'] },
                { icon: '📦', label: 'Orders', href: 'orders.html', roles: ['admin', 'manager', 'operator'] },
                { icon: '👥', label: 'Leads', href: 'leads.html', roles: ['admin', 'manager', 'operator'] },
            ],
            management: [
                { icon: '⚠️', label: 'Error Logs', href: 'errors.html', roles: ['admin', 'manager', 'operator'] },
            ],
            others: [
                { icon: '⚙️', label: 'Settings', href: 'settings.html', roles: ['admin', 'manager', 'operator'] } // ✅ Operator now has Settings
            ]
        }
    },

    init() {
        const user = BizLinkAuth.getUser();
        const role = user.role || 'operator';

        this.renderSidebar(role);
        this.initUserProfile(user);
        this.applyRoleBasedVisibility(role);
    },

    renderSidebar(role) {
        const config = this.menuConfig[role] || this.menuConfig.operator;
        const nav = document.querySelector('nav');
        if (!nav) return;

        let html = '<p class="px-4 text-xs font-semibold text-biz-muted uppercase mb-2">Menu</p>';

        config.menu.forEach(item => {
            const isActive = window.location.pathname.includes(item.href) || window.location.href.includes(item.href);
            html += `<a href="${item.href}" class="nav-link ${isActive ? 'active' : ''}">${item.icon} ${item.label}</a>`;
        });

        if (config.management.length > 0) {
            html += '<p class="px-4 text-xs font-semibold text-biz-muted uppercase mt-6 mb-2">Management</p>';
            config.management.forEach(item => {
                const isActive = window.location.pathname.includes(item.href) || window.location.href.includes(item.href);
                html += `<a href="${item.href}" class="nav-link ${isActive ? 'active' : ''}">${item.icon} ${item.label}</a>`;
            });
        }

        if (config.others.length > 0) {
            html += '<p class="px-4 text-xs font-semibold text-biz-muted uppercase mt-6 mb-2">Others</p>';
            config.others.forEach(item => {
                const isActive = window.location.pathname.includes(item.href) || window.location.href.includes(item.href);
                html += `<a href="${item.href}" class="nav-link ${isActive ? 'active' : ''}">${item.icon} ${item.label}</a>`;
            });
        }

        nav.innerHTML = html;
    },

    // ✅ NEW: Apply role-based visibility to elements
    applyRoleBasedVisibility(role) {
        // Hide/show elements based on data-role attribute
        document.querySelectorAll('[data-role]').forEach(el => {
            const allowedRoles = el.getAttribute('data-role').split(',');
            if (!allowedRoles.includes(role)) {
                el.style.display = 'none';
            }
        });

        // Hide admin-only tabs for non-admin users
        if (role !== 'admin') {
            document.querySelectorAll('.admin-only').forEach(el => {
                el.style.display = 'none';
            });
        }

        // Hide manager-only tabs for operator
        if (role === 'operator') {
            document.querySelectorAll('.manager-only').forEach(el => {
                el.style.display = 'none';
            });
        }
    },

    getInitials(name) {
        if (!name) return 'U';
        const parts = name.trim().split(' ');
        if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
        if (parts.length === 2) return (parts[0][0] + parts[1][0]).toUpperCase();
        return parts.map(p => p[0]).join('').substring(0, 3).toUpperCase();
    },

    initUserProfile(user) {
        const role = user.role || 'operator';
        const roleName = role.charAt(0).toUpperCase() + role.slice(1);
        const initials = this.getInitials(user.name);

        const updates = [
            { id: 'user-name', value: user.name || 'User' },
            { id: 'user-role', value: `${roleName} Workspace` },
            { id: 'user-avatar', value: initials },
            { id: 'header-avatar', value: initials }
        ];

        updates.forEach(({ id, value }) => {
            const el = document.getElementById(id);
            if (el && el.textContent !== value) {
                el.textContent = value;
            }
        });
    },

    getCurrentRole() {
        return BizLinkAuth.getRole();
    },

    hasAccess(requiredRoles) {
        const role = this.getCurrentRole();
        return requiredRoles.includes(role);
    }
};