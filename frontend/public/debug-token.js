/**
 * Token Debug Utility
 * 
 * Add this to your browser console after login/registration to debug token issues:
 * 
 * Usage:
 * 1. Open browser DevTools (F12)
 * 2. Go to Console tab
 * 3. Copy-paste this entire file
 * 4. Run: debugToken()
 */

function debugToken() {
  console.log("🔍 TOKEN DEBUG REPORT");
  console.log("=" + "=".repeat(50));
  
  // Check raw token storage
  const rawToken = localStorage.getItem('token');
  const rawTgToken = localStorage.getItem('tg_default_token');
  
  console.log("\n📦 Raw Storage:");
  console.log("  localStorage['token']:", rawToken);
  console.log("  localStorage['tg_default_token']:", rawTgToken);
  console.log("  Type:", typeof rawToken);
  console.log("  Has quotes:", rawToken && /^".*"$/.test(rawToken));
  
  // Check cleaned token
  const cleanToken = rawToken ? rawToken.replace(/^"+|"+$/g, '') : null;
  console.log("\n🧹 Cleaned Token:");
  console.log("  Value:", cleanToken);
  console.log("  Length:", cleanToken?.length || 0);
  console.log("  First 10 chars:", cleanToken?.substring(0, 10));
  
  // Check Authorization header format
  const authHeader = `Bearer ${cleanToken}`;
  console.log("\n📨 Authorization Header:");
  console.log("  Full header:", authHeader);
  console.log("  Has space after Bearer:", /^Bearer /.test(authHeader));
  console.log("  Has quotes:", /"/.test(authHeader));
  
  // Test token format
  console.log("\n✅ Validation:");
  const isValid = cleanToken && 
                  !/"/.test(cleanToken) && 
                  /^Bearer /.test(authHeader) &&
                  cleanToken.length > 20;
  console.log("  Token appears valid:", isValid);
  
  if (!isValid) {
    console.log("\n⚠️  ISSUES DETECTED:");
    if (!cleanToken) console.log("  - Token is null or empty");
    if (cleanToken && /"/.test(cleanToken)) console.log("  - Token contains quotes");
    if (cleanToken && !/^Bearer /.test(authHeader)) console.log("  - Bearer prefix issue");
    if (cleanToken && cleanToken.length < 20) console.log("  - Token too short");
  }
  
  // Try a test API call
  console.log("\n🧪 Test API Call:");
  fetch('/api/auth/me', {
    headers: {
      'Authorization': authHeader
    }
  })
  .then(res => {
    console.log("  Status:", res.status);
    if (res.status === 200) {
      console.log("  ✅ Authentication successful!");
    } else if (res.status === 401) {
      console.log("  ❌ 401 Unauthorized - Token is invalid");
    } else {
      console.log("  ⚠️  Unexpected status:", res.status);
    }
    return res.json();
  })
  .then(data => {
    console.log("  Response:", data);
  })
  .catch(err => {
    console.log("  ❌ Error:", err.message);
  });
  
  console.log("\n" + "=".repeat(50));
}

// Auto-run
debugToken();
