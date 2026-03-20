/**
 * AUTH.JS - Green Prompts Optimizer
 * Shared authentication helpers
 */

const SESSION_KEY = 'gpo_session';
const USERS_KEY   = 'gpo_users';

function getUsers() {
    try { return JSON.parse(localStorage.getItem(USERS_KEY) || '{}'); }
    catch { return {}; }
}

function saveUsers(users) {
    localStorage.setItem(USERS_KEY, JSON.stringify(users));
}

function getSession() {
    try {
        const s = localStorage.getItem(SESSION_KEY);
        if (!s) return null;
        const session = JSON.parse(s);
        // Expire after 7 days
        if (Date.now() - session.loginTime > 7 * 24 * 60 * 60 * 1000) {
            localStorage.removeItem(SESSION_KEY);
            return null;
        }
        return session;
    } catch { return null; }
}

function getCurrentUser() {
    const session = getSession();
    if (!session) return null;
    const users = getUsers();
    return users[session.email] || null;
}

function saveCurrentUser(user) {
    const session = getSession();
    if (!session) return;
    const users = getUsers();
    users[session.email] = user;
    saveUsers(users);
}

function signup(name, email, password) {
    const users = getUsers();
    if (users[email]) return { ok: false, error: 'Email already registered.' };
    const newUser = {
        name, email,
        passwordHash: btoa(password), // simple obfuscation (not crypto-secure)
        createdAt: Date.now(),
        stats: { totalOptimizations: 0, totalTokensSaved: 0, totalEnergySaved: 0, totalCO2Saved: 0 },
        history: []
    };
    users[email] = newUser;
    saveUsers(users);
    // Auto-login
    localStorage.setItem(SESSION_KEY, JSON.stringify({ email, loginTime: Date.now() }));
    // Track signup in global stats
    if (window.GPO) window.GPO.trackSignup();
    return { ok: true, user: newUser };
}

function login(email, password) {
    const users = getUsers();
    const user = users[email];
    if (!user) return { ok: false, error: 'No account found with that email.' };
    if (user.passwordHash !== btoa(password)) return { ok: false, error: 'Incorrect password.' };
    localStorage.setItem(SESSION_KEY, JSON.stringify({ email, loginTime: Date.now() }));
    return { ok: true, user };
}

function logout() {
    localStorage.removeItem(SESSION_KEY);
    window.location.href = 'index.html';
}

function requireAuth() {
    if (!getSession()) {
        window.location.href = 'login.html';
        return false;
    }
    return true;
}

/** Update nav buttons based on login state */
function updateNavAuth() {
    const user = getCurrentUser();
    const loginBtn  = document.querySelector('.btn-login');
    const signupBtn = document.querySelector('.btn-signup');
    const dashBtn   = document.getElementById('nav-dashboard');

    if (user) {
        if (loginBtn)  { loginBtn.textContent = user.name.split(' ')[0]; loginBtn.href = 'dashboard.html'; }
        if (signupBtn) { signupBtn.textContent = 'Dashboard'; signupBtn.href = 'dashboard.html'; }
    }
}

window.AUTH = { signup, login, logout, getCurrentUser, saveCurrentUser, getSession, requireAuth, updateNavAuth };
