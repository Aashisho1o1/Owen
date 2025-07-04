/**
 * 🔍 COMPREHENSIVE DEBUG SCRIPT FOR OWEN AI WRITER
 * 
 * This script helps diagnose authentication and API connectivity issues.
 * Run this in the browser console when experiencing "Network Error" issues.
 * 
 * Usage: Copy and paste this entire script into the browser console and press Enter.
 */

console.log('🚀 Starting Owen AI Writer Debug Analysis...');

// === AUTHENTICATION DEBUGGING ===
function debugAuthentication() {
  console.log('\n🔐 === AUTHENTICATION DEBUG ===');
  
  // Check stored tokens
  const tokens = {
    owen_access_token: localStorage.getItem('owen_access_token'),
    owen_refresh_token: localStorage.getItem('owen_refresh_token'),
    owen_token_type: localStorage.getItem('owen_token_type'),
    owen_token_expires: localStorage.getItem('owen_token_expires'),
    // Legacy tokens
    access_token: localStorage.getItem('access_token'),
    refresh_token: localStorage.getItem('refresh_token'),
    token_type: localStorage.getItem('token_type'),
    token_expires: localStorage.getItem('token_expires')
  };
  
  console.log('📝 Stored Tokens:');
  Object.entries(tokens).forEach(([key, value]) => {
    if (value) {
      console.log(`  ✅ ${key}: ${value.substring(0, 20)}...`);
    } else {
      console.log(`  ❌ ${key}: null`);
    }
  });
  
  // Check token expiration
  const expiresAt = tokens.owen_token_expires || tokens.token_expires;
  if (expiresAt) {
    const expirationDate = new Date(parseInt(expiresAt));
    const now = new Date();
    const isExpired = now >= expirationDate;
    
    console.log(`⏰ Token Expiration:`);
    console.log(`  Expires at: ${expirationDate.toISOString()}`);
    console.log(`  Current time: ${now.toISOString()}`);
    console.log(`  Status: ${isExpired ? '❌ EXPIRED' : '✅ Valid'}`);
    
    if (isExpired) {
      console.log('🧹 RECOMMENDATION: Clear expired tokens');
      return false;
    }
  } else {
    console.log('⚠️ No expiration time found - tokens may be invalid');
    return false;
  }
  
  return true;
}

// === API CONNECTIVITY TESTING ===
async function testApiConnectivity() {
  console.log('\n🌐 === API CONNECTIVITY TEST ===');
  
  const apiUrl = 'https://backend-copy-production-95b5.up.railway.app';
  
  try {
    // Test health endpoint
    console.log('🔍 Testing health endpoint...');
    const healthResponse = await fetch(`${apiUrl}/api/health`);
    
    if (healthResponse.ok) {
      const healthData = await healthResponse.json();
      console.log('✅ Health check passed:', {
        status: healthData.status,
        environment: healthData.environment,
        version: healthData.version
      });
    } else {
      console.log('❌ Health check failed:', healthResponse.status, healthResponse.statusText);
      return false;
    }
    
    // Test authenticated endpoint
    console.log('🔍 Testing authenticated endpoint...');
    const token = localStorage.getItem('owen_access_token') || localStorage.getItem('access_token');
    
    if (!token) {
      console.log('❌ No access token found - cannot test authenticated endpoints');
      return false;
    }
    
    const authResponse = await fetch(`${apiUrl}/api/auth/profile`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (authResponse.ok) {
      const profileData = await authResponse.json();
      console.log('✅ Authentication test passed:', {
        username: profileData.username,
        email: profileData.email
      });
      return true;
    } else {
      console.log('❌ Authentication test failed:', authResponse.status, authResponse.statusText);
      
      if (authResponse.status === 401) {
        console.log('🔐 Token is invalid or expired');
      }
      
      return false;
    }
    
  } catch (error) {
    console.log('❌ Network error during API test:', error.message);
    return false;
  }
}

// === CHAT API TESTING ===
async function testChatApi() {
  console.log('\n💬 === CHAT API TEST ===');
  
  const apiUrl = 'https://backend-copy-production-95b5.up.railway.app';
  const token = localStorage.getItem('owen_access_token') || localStorage.getItem('access_token');
  
  if (!token) {
    console.log('❌ No access token found - cannot test chat API');
    return false;
  }
  
  const testPayload = {
    message: "Hello, this is a test message",
    editor_text: "Test document content",
    author_persona: "Ernest Hemingway",
    help_focus: "Dialogue Writing",
    chat_history: [],
    llm_provider: "Google Gemini",
    ai_mode: "talk",
    user_preferences: {
      onboarding_completed: false,
      user_corrections: []
    }
  };
  
  try {
    console.log('🔍 Testing chat endpoint...');
    const chatResponse = await fetch(`${apiUrl}/api/chat/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(testPayload)
    });
    
    if (chatResponse.ok) {
      const chatData = await chatResponse.json();
      console.log('✅ Chat API test passed:', {
        hasResponse: !!chatData.dialogue_response,
        responseLength: chatData.dialogue_response?.length || 0
      });
      return true;
    } else {
      const errorData = await chatResponse.text();
      console.log('❌ Chat API test failed:', {
        status: chatResponse.status,
        statusText: chatResponse.statusText,
        error: errorData
      });
      return false;
    }
    
  } catch (error) {
    console.log('❌ Network error during chat API test:', error.message);
    return false;
  }
}

// === BROWSER ENVIRONMENT CHECK ===
function checkBrowserEnvironment() {
  console.log('\n🌍 === BROWSER ENVIRONMENT ===');
  
  console.log('📊 Browser Info:', {
    userAgent: navigator.userAgent,
    language: navigator.language,
    cookieEnabled: navigator.cookieEnabled,
    onLine: navigator.onLine
  });
  
  console.log('🔧 Window Info:', {
    url: window.location.href,
    origin: window.location.origin,
    protocol: window.location.protocol
  });
  
  console.log('💾 Storage Info:', {
    localStorage: typeof localStorage !== 'undefined',
    sessionStorage: typeof sessionStorage !== 'undefined',
    localStorageItems: localStorage.length
  });
}

// === TOKEN CLEANUP FUNCTION ===
function clearAllTokens() {
  console.log('\n🧹 === CLEARING ALL TOKENS ===');
  
  const tokenKeys = [
    'owen_access_token',
    'owen_refresh_token', 
    'owen_token_type',
    'owen_token_expires',
    'access_token',
    'refresh_token',
    'token_type',
    'token_expires'
  ];
  
  tokenKeys.forEach(key => {
    if (localStorage.getItem(key)) {
      localStorage.removeItem(key);
      console.log(`🗑️ Removed: ${key}`);
    }
  });
  
  console.log('✅ All tokens cleared. Please refresh the page and sign in again.');
}

// === MAIN DEBUG FUNCTION ===
async function runFullDiagnosis() {
  console.log('🔍 === OWEN AI WRITER FULL DIAGNOSIS ===\n');
  
  // Check browser environment
  checkBrowserEnvironment();
  
  // Check authentication
  const authValid = debugAuthentication();
  
  // Test API connectivity
  const apiConnected = await testApiConnectivity();
  
  // Test chat API if auth is valid
  let chatWorking = false;
  if (authValid && apiConnected) {
    chatWorking = await testChatApi();
  }
  
  // Summary and recommendations
  console.log('\n📋 === DIAGNOSIS SUMMARY ===');
  console.log(`🔐 Authentication: ${authValid ? '✅ Valid' : '❌ Invalid'}`);
  console.log(`🌐 API Connectivity: ${apiConnected ? '✅ Working' : '❌ Failed'}`);
  console.log(`💬 Chat API: ${chatWorking ? '✅ Working' : '❌ Failed'}`);
  
  console.log('\n💡 === RECOMMENDATIONS ===');
  
  if (!authValid) {
    console.log('🔐 AUTHENTICATION ISSUE:');
    console.log('  1. Run clearAllTokens() to clear expired tokens');
    console.log('  2. Refresh the page');
    console.log('  3. Sign in again');
    console.log('  4. Try your request again');
  } else if (!apiConnected) {
    console.log('🌐 CONNECTIVITY ISSUE:');
    console.log('  1. Check your internet connection');
    console.log('  2. Try refreshing the page');
    console.log('  3. Check if the backend is down');
  } else if (!chatWorking) {
    console.log('💬 CHAT API ISSUE:');
    console.log('  1. The backend may be experiencing issues');
    console.log('  2. Try again in a few minutes');
    console.log('  3. Check the browser console for detailed errors');
  } else {
    console.log('✅ ALL SYSTEMS WORKING:');
    console.log('  Everything appears to be functioning correctly.');
    console.log('  If you\'re still experiencing issues, try:');
    console.log('  1. Refreshing the page');
    console.log('  2. Clearing browser cache');
    console.log('  3. Using a different browser');
  }
  
  console.log('\n🛠️ === AVAILABLE FUNCTIONS ===');
  console.log('clearAllTokens() - Clear all authentication tokens');
  console.log('testApiConnectivity() - Test API connectivity');
  console.log('testChatApi() - Test chat API specifically');
  console.log('debugAuthentication() - Check authentication status');
}

// === EXPOSE FUNCTIONS GLOBALLY ===
window.owenDebug = {
  runFullDiagnosis,
  clearAllTokens,
  testApiConnectivity,
  testChatApi,
  debugAuthentication,
  checkBrowserEnvironment
};

// === AUTO-RUN DIAGNOSIS ===
console.log('🚀 Running automatic diagnosis...');
runFullDiagnosis().then(() => {
  console.log('\n🎯 === QUICK ACTIONS ===');
  console.log('If you\'re seeing "Network Error" in the chat:');
  console.log('1. Most likely cause: Expired authentication tokens');
  console.log('2. Quick fix: Run clearAllTokens() then refresh and sign in');
  console.log('3. Alternative: Just refresh the page and sign in again');
  console.log('\n📞 Need help? The functions are available as window.owenDebug.*');
}); 