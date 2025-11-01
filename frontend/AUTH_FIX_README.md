# Authentication Token Handling Fix

## Problem

The frontend was experiencing persistent 401 "Invalid token" errors due to improper token formatting:

1. **Token wrapped in quotes**: Tokens stored with `JSON.stringify()` resulted in `"abc123"` instead of `abc123`
2. **Malformed Authorization header**: Headers like `Bearer"token"` or `Bearerabc123"` (missing space or extra quotes)
3. **No centralized error handling**: Each component handled 401 errors differently

## Solution

### Backend Fix (Already Applied)
- Fixed ID type conversion: `current_user.id` (string) → `int(current_user.id)` for PostgreSQL queries
- All endpoints now correctly convert string IDs to integers before database queries

### Frontend Fix (New)

#### 1. Created `authClient.js` utility (`/app/frontend/src/utils/authClient.js`)

**Features:**
- `getToken()`: Strips stray quotation marks from stored tokens
- `setToken()`: Stores tokens correctly without extra quotes
- `createHttpClient()`: Returns Axios instance with interceptors
- Automatic `Bearer ` prefix (with space) on all requests
- Global 401 handling (clears token & redirects to login)

#### 2. Updated `telegramStorage.js`
- Enhanced `getToken()` to strip quotation marks
- Maintains Telegram-user-specific storage isolation

## Usage

### Option 1: Use the HTTP Client (Recommended)

```javascript
import { httpClient } from '@/utils/authClient';

// Automatically adds Authorization header
const response = await httpClient.get('/auth/me');
```

### Option 2: Use getToken() Manually

```javascript
import { getToken } from '@/utils/authClient';
// or from telegramStorage for Telegram-specific storage
import { getToken } from '@/utils/telegramStorage';

const token = getToken(); // Returns normalized token without quotes
const response = await axios.get('/api/auth/me', {
  headers: {
    Authorization: `Bearer ${token}` // Note the space after Bearer
  }
});
```

## Token Format Examples

### ❌ Before (Broken)
```javascript
// Stored token
localStorage.getItem('token') // Returns: "abc123def456" (with quotes)

// Authorization header
Authorization: Bearer"abc123def456"  // Missing space, has quotes
Authorization: Bearerabc123def456   // Missing space
```

### ✅ After (Fixed)
```javascript
// Stored token (normalized)
getToken() // Returns: abc123def456 (no quotes)

// Authorization header
Authorization: Bearer abc123def456  // Correct format with space
```

## Migration Guide

To migrate existing code:

1. **Import the new helper:**
```javascript
// Old
import { getToken } from '@/utils/telegramStorage';

// Keep using telegramStorage for Telegram-specific storage
// OR use authClient for standard web app
import { getToken } from '@/utils/authClient';
```

2. **Use httpClient for API calls:**
```javascript
// Old
const token = getToken();
const response = await axios.get(`${API}/auth/me`, {
  headers: { Authorization: `Bearer ${token}` }
});

// New (simpler)
import { httpClient } from '@/utils/authClient';
const response = await httpClient.get('/auth/me');
```

3. **Remove manual 401 handling:**
```javascript
// Old
try {
  const response = await axios.get(...);
} catch (error) {
  if (error.response?.status === 401) {
    localStorage.removeItem('token');
    navigate('/login');
  }
}

// New (automatic)
const response = await httpClient.get(...);
// 401 handling is automatic
```

## Testing

1. **Clear old tokens:**
```javascript
localStorage.clear();
```

2. **Register/Login:**
- Token should be stored without quotes
- All API calls should work with 200 responses

3. **Verify token format:**
```javascript
console.log(localStorage.getItem('token')); // Should NOT have quotes
console.log(getToken()); // Should return clean token
```

4. **Test 401 handling:**
- Manually set invalid token: `localStorage.setItem('token', 'invalid')`
- Try to access profile
- Should auto-redirect to login and clear token

## Files Modified

- ✅ `/app/frontend/src/utils/authClient.js` (new file)
- ✅ `/app/frontend/src/utils/telegramStorage.js` (updated getToken)
- ✅ `/app/backend/server.py` (fixed ID conversion in 10+ locations)

## Benefits

1. ✅ **Centralized token handling** - One place for all token operations
2. ✅ **Automatic error recovery** - 401 errors handled globally
3. ✅ **Consistent format** - No more malformed Authorization headers
4. ✅ **Better UX** - Automatic redirects on auth failure
5. ✅ **Cleaner code** - Less boilerplate in components

## Next Steps

Consider gradually migrating all API calls to use `httpClient`:

```javascript
// In each component
import { httpClient } from '@/utils/authClient';

// Replace all axios calls
httpClient.get('/auth/me')
httpClient.put('/auth/profile', formData)
httpClient.post('/posts', postData)
```

This ensures consistent token handling across the entire application.
