/*
 * This file demonstrates a robust way to handle authentication tokens
 * on the client.  The problems seen in the mobile web app stem from
 * constructing the `Authorization` header incorrectly – the token was
 * being stringified and wrapped in quotation marks or concatenated
 * without a separating space.  When the server receives a header
 * formatted as `Bearer"abc123"` or `Bearerabc123` it rejects it as
 * invalid, which is why all calls to `/auth/me` and related endpoints
 * returned `401 Invalid token`.  The solution is to normalize the
 * token when it is loaded from storage and ensure that the header is
 * always prefaced with `Bearer ` (note the space) before the token.
 *
 * The code below exposes a helper to read a token from localStorage,
 * strip any stray quotation marks, and configure an axios instance
 * with proper request/response interceptors.  A 401 response will
 * automatically remove the stale token and redirect the user to the
 * login page.
 */

import axios from 'axios';

/**
 * Get Telegram user ID for scoped storage
 */
function getTelegramUserId() {
  try {
    if (window.Telegram?.WebApp?.initDataUnsafe?.user?.id) {
      return window.Telegram.WebApp.initDataUnsafe.user.id;
    }
  } catch (e) {
    // Not in Telegram context
  }
  return 'default';
}

/**
 * Read the persisted JWT from localStorage and remove extraneous
 * quotation marks if the token was previously stored using
 * `JSON.stringify`.  Without this sanitisation the server will
 * interpret the value as a literal string surrounded by quotes
 * (e.g. "abcdef") and respond with `401 Invalid token`.
 * 
 * ALSO checks Telegram-scoped storage (tg_[id]_token) for compatibility
 */
export function getToken() {
  // First try Telegram-scoped storage (for Telegram Mini App compatibility)
  const telegramUserId = getTelegramUserId();
  const telegramKey = `tg_${telegramUserId}_token`;
  let stored = localStorage.getItem(telegramKey);
  
  // Fallback to regular token key if Telegram token not found
  if (!stored) {
    stored = localStorage.getItem('token');
  }
  
  if (!stored) return null;
  
  // If the token is wrapped in quotes (e.g. "abc"), remove them.
  return stored.replace(/^"+|"+$/g, '');
}

/**
 * Store token in localStorage without extra quotes
 */
export function setToken(token) {
  if (token) {
    localStorage.setItem('token', token);
  } else {
    localStorage.removeItem('token');
  }
}

/**
 * Create an axios instance that automatically adds the `Authorization`
 * header to each request when a token is present.  If the server
 * responds with a 401 status code the client will assume the token is
 * invalid or expired, remove it from storage and redirect to the
 * login route.  This centralises token handling in one place and
 * prevents silent failures when individual API calls forget to add
 * the header or use an outdated token.
 */
export function createHttpClient(
  baseURL = process.env.REACT_APP_BACKEND_URL || '/api',
) {
  const http = axios.create({ baseURL });

  http.interceptors.request.use(
    (config) => {
      const token = getToken();
      if (token) {
        // Always prefix the token with `Bearer ` (note the space)
        config.headers = {
          ...config.headers,
          Authorization: `Bearer ${token}`,
        };
      }
      return config;
    },
    (error) => Promise.reject(error),
  );

  http.interceptors.response.use(
    (response) => response,
    (error) => {
      // Handle 401 errors globally
      if (error.response && error.response.status === 401) {
        // Remove the invalid token
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        // Optionally dispatch a logout event or use your router to redirect
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
      }
      return Promise.reject(error);
    },
  );

  return http;
}

// Export a default configured instance
export const httpClient = createHttpClient();
