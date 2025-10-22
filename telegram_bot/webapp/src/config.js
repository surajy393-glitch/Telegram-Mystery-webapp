// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || window.location.origin || 'http://localhost:8001';

export const API_ENDPOINTS = {
  CREATE_POST: `${API_BASE_URL}/api/posts`,  // Changed to match backend endpoint
  CREATE_STORY: `${API_BASE_URL}/api/stories`,  // Changed to match backend endpoint
  GET_POSTS: `${API_BASE_URL}/api/posts/feed`,
  GET_STORIES: `${API_BASE_URL}/api/stories/feed`
};

export default {
  API_BASE_URL,
  API_ENDPOINTS
};
