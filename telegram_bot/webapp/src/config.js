// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || window.location.origin || 'http://localhost:8001';

export const API_ENDPOINTS = {
  CREATE_POST: `${API_BASE_URL}/api/posts/create`,
  CREATE_STORY: `${API_BASE_URL}/api/stories/create`,
  GET_POSTS: `${API_BASE_URL}/api/posts/feed`,
  GET_STORIES: `${API_BASE_URL}/api/stories/feed`
};

export default {
  API_BASE_URL,
  API_ENDPOINTS
};
