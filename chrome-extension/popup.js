
const API_URL = 'https://srineshtor21-coder.github.io/Green-Prompts-Optimizer/';

// Get elements
const loginSection = document.getElementById('loginSection');
const registerSection = document.getElementById('registerSection');
const appSection = document.getElementById('appSection');
const loadingSection = document.getElementById('loadingSection');

// Auth elements
const loginEmail = document.getElementById('loginEmail');
const loginPassword = document.getElementById('loginPassword');
const loginBtn = document.getElementById('loginBtn');
const regEmail = document.getElementById('regEmail');
const regUsername = document.getElementById('regUsername');
const regPassword = document.getElementById('regPassword');
const registerBtn = document.getElementById('registerBtn');
const showRegisterBtn = document.getElementById('showRegisterBtn');
const showLoginBtn = document.getElementById('showLoginBtn');
const logoutBtn = document.getElementById('logoutBtn');

// App elements
const promptInput = document.getElementById('promptInput');
const optimizeBtn = document.getElementById('optimizeBtn');
const result = document.getElementById('result');
const optimizedText = document.getElementById('optimizedText');
const copyBtn = document.getElementById('copyBtn');
const tokensSaved = document.getElementById('tokensSaved');
const energySaved = document.getElementById('energySaved');

// User stats elements
const userOptimizations = document.getElementById('userOptimizations');
const userTokens = document.getElementById('userTokens');
const userEnergy = document.getElementById('userEnergy');
const userCO2 = document.getElementById('userCO2');

// Error/success messages
const errorMessage = document.getElementById('errorMessage');
const regErrorMessage = document.getElementById('regErrorMessage');
const successMessage = document.getElementById('successMessage');

// Initialize
document.addEventListener('DOMContentLoaded', init);

async function init() {
  const token = await getStoredToken();
  if (token) {
    showApp();
    loadUserStats();
  } else {
    showLogin();
  }
}

// Storage helpers
async function getStoredToken() {
  return new Promise((resolve) => {
    chrome.storage.local.get(['authToken'], (result) => {
      resolve(result.authToken || null);
    });
  });
}

async function setStoredToken(token) {
  return new Promise((resolve) => {
    chrome.storage.local.set({ authToken: token }, resolve);
  });
}

async function clearStoredToken() {
  return new Promise((resolve) => {
    chrome.storage.local.remove(['authToken'], resolve);
  });
}

// API helpers
async function apiRequest(endpoint, options = {}) {
  const token = await getStoredToken();
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Request failed');
  }

  return await response.json();
}

// UI Navigation
function showLogin() {
  loginSection.classList.add('active');
  registerSection.classList.remove('active');
  appSection.classList.remove('active');
  loadingSection.style.display = 'none';
}

function showRegister() {
  loginSection.classList.remove('active');
  registerSection.classList.add('active');
  appSection.classList.remove('active');
  loadingSection.style.display = 'none';
}

function showApp() {
  loginSection.classList.remove('active');
  registerSection.classList.remove('active');
  appSection.classList.add('active');
  loadingSection.style.display = 'none';
}

function showLoading() {
  loginSection.classList.remove('active');
  registerSection.classList.remove('active');
  appSection.classList.remove('active');
  loadingSection.style.display = 'block';
}

function showError(message, element = errorMessage) {
  element.textContent = message;
  element.style.display = 'block';
  setTimeout(() => {
    element.style.display = 'none';
  }, 5000);
}

function showSuccess(message) {
  successMessage.textContent = message;
  successMessage.style.display = 'block';
  setTimeout(() => {
    successMessage.style.display = 'none';
  }, 3000);
}

// Auth handlers
loginBtn.addEventListener('click', async () => {
  const email = loginEmail.value.trim();
  const password = loginPassword.value;

  if (!email || !password) {
    showError('Please enter email and password');
    return;
  }

  try {
    showLoading();
    const data = await apiRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });

    await setStoredToken(data.token);
    showApp();
    loadUserStats();
    showSuccess('Login successful!');
  } catch (error) {
    showLogin();
    showError(error.message);
  }
});

registerBtn.addEventListener('click', async () => {
  const email = regEmail.value.trim();
  const password = regPassword.value;
  const username = regUsername.value.trim();

  if (!email || !password) {
    showError('Please enter email and password', regErrorMessage);
    return;
  }

  try {
    showLoading();
    const data = await apiRequest('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, username }),
    });

    await setStoredToken(data.token);
    showApp();
    loadUserStats();
    showSuccess('Account created successfully!');
  } catch (error) {
    showRegister();
    showError(error.message, regErrorMessage);
  }
});

showRegisterBtn.addEventListener('click', showRegister);
showLoginBtn.addEventListener('click', showLogin);

logoutBtn.addEventListener('click', async () => {
  await clearStoredToken();
  showLogin();
  loginEmail.value = '';
  loginPassword.value = '';
});

// Optimize prompt
optimizeBtn.addEventListener('click', async () => {
  const prompt = promptInput.value.trim();

  if (!prompt) {
    showError('Please enter a prompt to optimize', successMessage);
    return;
  }

  try {
    optimizeBtn.textContent = 'Optimizing...';
    optimizeBtn.disabled = true;

    const data = await apiRequest('/optimize', {
      method: 'POST',
      body: JSON.stringify({ prompt }),
    });

    // Show result
    optimizedText.textContent = data.optimized;
    tokensSaved.textContent = data.savings.tokens;
    energySaved.textContent = parseFloat(data.savings.energy).toFixed(4);
    result.classList.add('active');

    // Reload user stats
    loadUserStats();

    showSuccess('Prompt optimized successfully! ✨');
  } catch (error) {
    showError(error.message, successMessage);
  } finally {
    optimizeBtn.textContent = '⚡ Optimize Prompt';
    optimizeBtn.disabled = false;
  }
});

// Copy to clipboard
copyBtn.addEventListener('click', () => {
  const text = optimizedText.textContent;
  navigator.clipboard.writeText(text).then(() => {
    copyBtn.textContent = '✓ Copied!';
    setTimeout(() => {
      copyBtn.textContent = '📋 Copy to Clipboard';
    }, 2000);
  });
});

// Load user stats
async function loadUserStats() {
  try {
    const stats = await apiRequest('/user/stats');
    
    userOptimizations.textContent = stats.total_optimizations || 0;
    userTokens.textContent = (stats.total_tokens_saved || 0).toLocaleString();
    userEnergy.textContent = parseFloat(stats.total_energy_saved || 0).toFixed(2);
    userCO2.textContent = parseFloat(stats.total_co2_saved || 0).toFixed(2);
  } catch (error) {
    console.error('Failed to load user stats:', error);
  }
}

// Auto-fill from active page (if on ChatGPT/Claude)
chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
  if (tabs[0]) {
    const url = tabs[0].url;
    if (url && (url.includes('chat.openai.com') || url.includes('claude.ai'))) {
      // Send message to content script to get current prompt
      chrome.tabs.sendMessage(tabs[0].id, { action: 'getCurrentPrompt' }, (response) => {
        if (response && response.prompt) {
          promptInput.value = response.prompt;
        }
      });
    }
  }
});
