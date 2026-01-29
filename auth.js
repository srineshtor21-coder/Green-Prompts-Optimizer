/**
 * GREEN PROMPTS OPTIMIZER - Authentication
 * Simple client-side authentication using localStorage
 * (For production, this should be replaced with a proper backend)
 */

let isLoginMode = true;

// Show error message
function showError(message) {
    const errorEl = document.getElementById('error-message');
    errorEl.textContent = message;
    errorEl.classList.add('active');
    setTimeout(() => {
        errorEl.classList.remove('active');
    }, 5000);
}

// Show success message
function showSuccess(message) {
    const successEl = document.getElementById('success-message');
    successEl.textContent = message;
    successEl.classList.add('active');
    setTimeout(() => {
        successEl.classList.remove('active');
    }, 3000);
}

// Toggle between login and signup forms
function toggleForms() {
    const loginForm = document.getElementById('login-form');
    const signupForm = document.getElementById('signup-form');
    const toggleText = document.getElementById('toggle-text');
    const toggleLink = document.getElementById('toggle-link');
    const subtitle = document.querySelector('.subtitle');
    
    isLoginMode = !isLoginMode;
    
    if (isLoginMode) {
        loginForm.style.display = 'block';
        signupForm.style.display = 'none';
        toggleText.textContent = "Don't have an account? ";
        toggleLink.textContent = 'Sign up';
        subtitle.textContent = 'Sign in to track your environmental impact';
    } else {
        loginForm.style.display = 'none';
        signupForm.style.display = 'block';
        toggleText.textContent = 'Already have an account? ';
        toggleLink.textContent = 'Sign in';
        subtitle.textContent = 'Create an account to get started';
    }
}

// Hash password (simple client-side hashing - NOT SECURE FOR PRODUCTION)
async function hashPassword(password) {
    const encoder = new TextEncoder();
    const data = encoder.encode(password);
    const hash = await crypto.subtle.digest('SHA-256', data);
    return Array.from(new Uint8Array(hash))
        .map(b => b.toString(16).padStart(2, '0'))
        .join('');
}

// Handle login
async function handleLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    
    // Get users from localStorage
    const users = JSON.parse(localStorage.getItem('greenPromptsUsers') || '{}');
    
    const user = users[email];
    
    if (!user) {
        showError('Account not found. Please sign up first.');
        return;
    }
    
    // Check password
    const hashedPassword = await hashPassword(password);
    if (user.password !== hashedPassword) {
        showError('Incorrect password.');
        return;
    }
    
    // Store session
    const session = {
        email: user.email,
        name: user.name,
        loginTime: Date.now()
    };
    localStorage.setItem('greenPromptsSession', JSON.stringify(session));
    
    showSuccess('Login successful! Redirecting...');
    
    // Redirect to dashboard
    setTimeout(() => {
        window.location.href = 'dashboard.html';
    }, 1000);
}

// Handle signup
async function handleSignup(e) {
    e.preventDefault();
    
    const name = document.getElementById('signup-name').value;
    const email = document.getElementById('signup-email').value;
    const password = document.getElementById('signup-password').value;
    const confirmPassword = document.getElementById('signup-password-confirm').value;
    
    // Validation
    if (password !== confirmPassword) {
        showError('Passwords do not match.');
        return;
    }
    
    if (password.length < 6) {
        showError('Password must be at least 6 characters.');
        return;
    }
    
    // Check if user exists
    const users = JSON.parse(localStorage.getItem('greenPromptsUsers') || '{}');
    
    if (users[email]) {
        showError('An account with this email already exists.');
        return;
    }
    
    // Create user
    const hashedPassword = await hashPassword(password);
    users[email] = {
        name,
        email,
        password: hashedPassword,
        createdAt: Date.now(),
        stats: {
            totalOptimizations: 0,
            totalTokensSaved: 0,
            totalEnergySaved: 0,
            totalCO2Saved: 0
        },
        history: []
    };
    
    localStorage.setItem('greenPromptsUsers', JSON.stringify(users));
    
    showSuccess('Account created successfully! You can now sign in.');
    
    // Switch to login form
    setTimeout(() => {
        toggleForms();
        document.getElementById('login-email').value = email;
    }, 1500);
}

// Check if user is already logged in
function checkExistingSession() {
    const session = localStorage.getItem('greenPromptsSession');
    if (session) {
        const { loginTime } = JSON.parse(session);
        const dayInMs = 24 * 60 * 60 * 1000;
        
        // Session expires after 7 days
        if (Date.now() - loginTime < 7 * dayInMs) {
            window.location.href = 'dashboard.html';
            return;
        } else {
            // Clear expired session
            localStorage.removeItem('greenPromptsSession');
        }
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkExistingSession();
    
    // Set up event listeners
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('signup-form').addEventListener('submit', handleSignup);
    document.getElementById('toggle-link').addEventListener('click', (e) => {
        e.preventDefault();
        toggleForms();
    });
    
    console.log('🔐 Authentication system initialized');
});
