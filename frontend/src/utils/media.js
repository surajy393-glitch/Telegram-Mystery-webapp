// Utility functions for constructing correct media URLs across the app

// Trim trailing slash so we don't end up with double slashes when concatenating
const BACKEND = (process.env.REACT_APP_BACKEND_URL || '').replace(/\/$/, '');

/** Normalize a raw media URL returned from the backend. */
export function getMediaSrc(url) {
  if (!url) return '';
  // The backend serves static files at /uploads; strip an accidental /api prefix
  let cleaned = url.startsWith('/api/uploads/') ? url.replace('/api', '') : url;

  // Prefix relative /uploads paths with the configured backend domain (if provided)
  if (cleaned.startsWith('/uploads')) return `${BACKEND}${cleaned}`;

  // Absolute or data: URIs — return as-is
  return cleaned;
}

/** Resolve the best media URL for a post and normalize it. */
export function getPostMediaUrl(post) {
  if (!post) return null;

  let url = null;
  if (post.mediaUrl && post.mediaUrl.trim()) url = post.mediaUrl;
  else if (post.imageUrl && post.imageUrl.trim()) url = post.imageUrl;

  // Telegram file fallback (served by our proxy)
  if (!url && post.telegramFileId) url = `/api/media/${post.telegramFileId}`;

  return url ? getMediaSrc(url) : null;
}
