/**
 * GREEN PROMPTS OPTIMIZER - Content Script
 * Runs on web pages to detect and optimize prompts
 */

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'getSelectedText') {
        const selectedText = window.getSelection().toString().trim();
        sendResponse({ text: selectedText });
    }
    return true;
});
// This would allow right-click to optimize selected text
console.log('🌱 Green Prompts content script loaded');
