// Utility functions for constructing correct media URLs across the app

// Trim trailing slash so we don't end up with double slashes when concatenating
const BACKEND = (process.env.REACT_APP_BACKEND_URL || '').replace(/\/$/, '');

/** Normalize a raw media URL returned from the backend. */
export function getMediaSrc(url) {
  if (!url) return '';
  
  // Absolute URLs (http/https) and data URIs should be returned unchanged
  if (/^(https?:)?\/\//.test(url) || url.startsWith('data:')) {
    return url;
  }
  
  let path = url;
  // Add /api prefix if missing and the path references the uploads directory
  if (path.startsWith('/uploads/')) {
    path = `/api${path}`;
  }
  
  // Ensure path starts with a single slash
  if (!path.startsWith('/')) {
    path = `/${path}`;
  }
  
  // Prefix the backend URL if provided; otherwise return the path relative
  // to the current origin
  return BACKEND ? `${BACKEND}${path}` : path;
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
