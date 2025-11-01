// Utility functions for Telegram-user-specific storage
// This ensures each Telegram account has isolated storage

/**
 * Get Telegram user ID from WebApp context
 * @returns {string} Telegram user ID or 'default'
 */
export const getTelegramUserId = () => {
  try {
    if (window.Telegram?.WebApp?.initDataUnsafe?.user?.id) {
      return window.Telegram.WebApp.initDataUnsafe.user.id;
    }
  } catch (e) {
    console.log("Not in Telegram WebApp context");
  }
  return 'default';
};

/**
 * Get storage key prefix for current Telegram user
 * @returns {string} Storage prefix like 'tg_123456_'
 */
export const getStoragePrefix = () => {
  const telegramUserId = getTelegramUserId();
  return `tg_${telegramUserId}_`;
};

/**
 * Get token from localStorage for current Telegram user
 * Normalizes token by removing any stray quotation marks that may have been
 * added during JSON.stringify operations
 * @returns {string|null} Auth token or null
 */
export const getToken = () => {
  const storagePrefix = getStoragePrefix();
  const stored = localStorage.getItem(`${storagePrefix}token`);
  if (!stored) return null;
  // Remove any stray quotation marks (e.g., "abc" becomes abc)
  return stored.replace(/^"+|"+$/g, '');
};

/**
 * Set token in localStorage for current Telegram user
 * @param {string} token - Auth token to store
 */
export const setToken = (token) => {
  const storagePrefix = getStoragePrefix();
  localStorage.setItem(`${storagePrefix}token`, token);
};

/**
 * Remove token from localStorage for current Telegram user
 */
export const removeToken = () => {
  const storagePrefix = getStoragePrefix();
  localStorage.removeItem(`${storagePrefix}token`);
};

/**
 * Get user data from localStorage for current Telegram user
 * @returns {object|null} User data or null
 */
export const getUser = () => {
  const storagePrefix = getStoragePrefix();
  const userDataString = localStorage.getItem(`${storagePrefix}user`);
  if (userDataString) {
    try {
      return JSON.parse(userDataString);
    } catch (e) {
      console.error("Failed to parse user data:", e);
      return null;
    }
  }
  return null;
};

/**
 * Set user data in localStorage for current Telegram user
 * @param {object} userData - User data to store
 */
export const setUser = (userData) => {
  const storagePrefix = getStoragePrefix();
  localStorage.setItem(`${storagePrefix}user`, JSON.stringify(userData));
};

/**
 * Remove user data from localStorage for current Telegram user
 */
export const removeUser = () => {
  const storagePrefix = getStoragePrefix();
  localStorage.removeItem(`${storagePrefix}user`);
};

/**
 * Clear all auth data for current Telegram user
 */
export const clearAuth = () => {
  removeToken();
  removeUser();
};
