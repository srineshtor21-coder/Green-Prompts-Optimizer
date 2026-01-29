{
  "manifest_version": 3,
  "name": "Green Prompts Optimizer",
  "version": "1.0.0",
  "description": "Optimize AI prompts to reduce energy consumption and CO₂ emissions",
  "permissions": [
    "storage",
    "activeTab"
  ],
  "action": {
    "default_popup": "popup.html",
    "default_icon": {
      "16": "icons/icon16.png",
      "48": "icons/icon48.png",
      "128": "icons/icon128.png"
    }
  },
  "icons": {
    "16": "icons/icon16.png",
    "48": "icons/icon48.png",
    "128": "icons/icon128.png"
  },
  "content_scripts": [
    {
      "matches": ["<all_urls>"],
      "js": ["content.js"],
      "css": ["content.css"]
    }
  ],
  "host_permissions": [
    "https://sirenice-greenpromptsoptimizer.hf.space/*"
  ]
}
