/**
 * 🔍 COMPREHENSIVE DEBUG SCRIPT FOR OWEN AI WRITER
 * 
 * This script helps diagnose authentication and API connectivity issues.
 * Run this in the browser console when experiencing "Network Error" issues.
 * 
 * Usage: Copy and paste this entire script into the browser console and press Enter.
 */

console.log('🚀 Starting Owen AI Writer Debug Analysis...');

// === COMPREHENSIVE AUTHENTICATION & ERROR DEBUGGING SCRIPT ===
// Enhanced version with detailed testing for the new error handling system
// Last updated: July 4, 2025

console.log('🔍 DOG Writer Authentication & Error Debug Script v2.0');
console.log('📋 This script will help diagnose authentication and chat API issues');

// === 1. AUTHENTICATION DEBUGGING ===
function debugAuthentication() {
  console.log('\n🔐 === AUTHENTICATION DEBUG ===');
  
  // Check all possible token storage locations
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
  
  console.log('📦 Stored Tokens:', tokens);
  
  // Check token expiration
  const expiresAt = tokens.owen_token_expires || tokens.token_expires;
  if (expiresAt) {
    const expirationDate = new Date(parseInt(expiresAt));
    const now = new Date();
    const isExpired = now >= expirationDate;
    
    console.log(`⏰ Token Expiration:`, {
      expiresAt: expirationDate.toISOString(),
      currentTime: now.toISOString(),
      isExpired,
      timeUntilExpiry: isExpired ? 'EXPIRED' : `${Math.round((expirationDate - now) / 1000 / 60)} minutes`
    });
    
    if (isExpired) {
      console.log('❌ ISSUE: Authentication token has expired');
      console.log('💡 SOLUTION: Clear tokens and sign in again');
      return false;
    }
  } else {
    console.log('⚠️ WARNING: No token expiration information found');
  }
  
  // Check if user appears to be logged in
  const hasValidTokens = !!(tokens.owen_access_token && tokens.owen_refresh_token);
  console.log(`✅ Has Valid Token Structure: ${hasValidTokens}`);
  
  return hasValidTokens;
}

// === 2. API CONNECTIVITY TESTING ===
async function testApiConnectivity() {
  console.log('\n🌐 === API CONNECTIVITY TEST ===');
  
  const apiUrl = 'https://backend-copy-production-95b5.up.railway.app';
  
  try {
    // Test 1: Health endpoint (no auth required)
    console.log('🔍 Testing health endpoint...');
    const healthResponse = await fetch(`${apiUrl}/api/health`);
    const healthData = await healthResponse.json();
    
    console.log(`✅ Health Check: ${healthResponse.status}`, {
      status: healthData.status,
      database: healthData.database?.status,
      version: healthData.version
    });
    
    // Test 2: Authenticated endpoint with current token
    console.log('🔍 Testing authenticated endpoint...');
    const token = localStorage.getItem('owen_access_token') || localStorage.getItem('access_token');
    
    if (!token) {
      console.log('❌ No access token found for authenticated test');
      return false;
    }
    
    const authResponse = await fetch(`${apiUrl}/api/auth/profile`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    console.log(`🔐 Auth Test: ${authResponse.status}`);
    
    if (authResponse.status === 401) {
      console.log('❌ ISSUE: Authentication token is invalid or expired');
      console.log('💡 SOLUTION: Clear tokens and sign in again');
      
      // Test the enhanced error handling
      try {
        const errorData = await authResponse.json();
        console.log('📄 Error Response:', errorData);
      } catch (e) {
        console.log('📄 Error Response: (Could not parse JSON)');
      }
      
      return false;
    } else if (authResponse.ok) {
      const userData = await authResponse.json();
      console.log('✅ Authentication successful:', {
        id: userData.id,
        email: userData.email,
        username: userData.username
      });
      return true;
    } else {
      console.log(`❌ Unexpected auth response: ${authResponse.status}`);
      return false;
    }
    
  } catch (error) {
    console.error('❌ API Connectivity Error:', error);
    console.log('💡 SOLUTION: Check internet connection and backend status');
    return false;
  }
}

// === 3. CHAT API TESTING ===
async function testChatApi() {
  console.log('\n💬 === CHAT API TEST ===');
  
  const apiUrl = 'https://backend-copy-production-95b5.up.railway.app';
  const token = localStorage.getItem('owen_access_token') || localStorage.getItem('access_token');
  
  if (!token) {
    console.log('❌ No access token found for chat test');
    return false;
  }
  
  const testPayload = {
    message: "Test message for debugging",
    editor_text: "Test editor content",
    author_persona: "Ernest Hemingway",
    help_focus: "Dialogue Writing",
    chat_history: [],
    llm_provider: "Google Gemini",
    ai_mode: "talk",
    user_preferences: {
      onboarding_completed: false,
      user_corrections: []
    },
    feedback_on_previous: "",
    highlighted_text: "",
    highlight_id: "",
    english_variant: "US"
  };
  
  try {
    console.log('🚀 Sending chat request...');
    const response = await fetch(`${apiUrl}/api/chat/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(testPayload)
    });
    
    console.log(`📥 Chat Response: ${response.status}`);
    
    if (response.status === 401) {
      console.log('❌ ISSUE: Chat API returned 401 - Authentication required');
      console.log('💡 SOLUTION: This should trigger the enhanced error handling');
      
      // Test if the enhanced error handling is working
      const errorData = await response.json();
      console.log('📄 Chat Error Response:', errorData);
      
      // Simulate what the frontend should do
      console.log('🧪 Testing Enhanced Error Handling...');
      console.log('Expected: Enhanced error message with authentication guidance');
      console.log('Expected: Automatic token cleanup');
      console.log('Expected: auth:token-expired event dispatch');
      
      return false;
    } else if (response.ok) {
      const chatData = await response.json();
      console.log('✅ Chat API successful:', {
        hasDialogueResponse: !!chatData.dialogue_response,
        hasThinkingTrail: !!chatData.thinking_trail,
        responseLength: chatData.dialogue_response?.length || 0
      });
      return true;
    } else {
      console.log(`❌ Chat API error: ${response.status}`);
      const errorData = await response.text();
      console.log('📄 Error details:', errorData);
      return false;
    }
    
  } catch (error) {
    console.error('❌ Chat API Error:', error);
    console.log('💡 This error should be caught by enhanced error handling');
    return false;
  }
}

// === 4. TOKEN CLEANUP UTILITY ===
function clearAllTokens() {
  console.log('\n🧹 === CLEARING ALL TOKENS ===');
  
  const tokensToRemove = [
    'owen_access_token',
    'owen_refresh_token', 
    'owen_token_type',
    'owen_token_expires',
    // Legacy tokens
    'access_token',
    'refresh_token',
    'token_type',
    'token_expires'
  ];
  
  let removedCount = 0;
  tokensToRemove.forEach(key => {
    if (localStorage.getItem(key)) {
      localStorage.removeItem(key);
      removedCount++;
      console.log(`🗑️ Removed: ${key}`);
    }
  });
  
  console.log(`✅ Cleared ${removedCount} stored tokens`);
  console.log('💡 Please refresh the page and sign in again');
  
  // Dispatch the auth:token-expired event to notify the app
  console.log('📢 Dispatching auth:token-expired event...');
  window.dispatchEvent(new CustomEvent('auth:token-expired', {
    detail: { reason: 'Manual token cleanup', source: 'debug_script' }
  }));
}

// === 5. ENHANCED ERROR TESTING ===
async function testEnhancedErrorHandling() {
  console.log('\n🧪 === ENHANCED ERROR HANDLING TEST ===');
  
  // Test 1: Force a 401 error to see enhanced handling
  console.log('🔍 Testing 401 error handling...');
  
  try {
    const response = await fetch('https://backend-copy-production-95b5.up.railway.app/api/chat/', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer invalid_token_for_testing',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: "test",
        editor_text: "test",
        author_persona: "Ernest Hemingway",
        help_focus: "Dialogue Writing",
        chat_history: [],
        llm_provider: "Google Gemini",
        ai_mode: "talk"
      })
    });
    
    console.log(`📥 Response Status: ${response.status}`);
    
    if (response.status === 401) {
      const errorData = await response.json();
      console.log('✅ 401 Error received as expected:', errorData);
      console.log('🧪 This should trigger:');
      console.log('  - Enhanced error message with 🔐 icon');
      console.log('  - Automatic token cleanup');
      console.log('  - auth:token-expired event');
      console.log('  - User-friendly error display');
    }
    
  } catch (error) {
    console.log('❌ Network error during test:', error);
    console.log('🧪 This should trigger network error handling');
  }
  
  // Test 2: Test the axios client directly with invalid token
  console.log('\n🔍 Testing Axios client 401 error handling...');
  
  try {
    // Clear any existing tokens first
    localStorage.removeItem('owen_access_token');
    localStorage.removeItem('owen_refresh_token');
    
    // Set an invalid token
    localStorage.setItem('owen_access_token', 'invalid_test_token_12345');
    
    // Try to make a request - this should trigger our enhanced 401 handling
    const axiosResponse = await fetch('https://backend-copy-production-95b5.up.railway.app/api/chat/', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer invalid_test_token_12345',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: "test axios error handling",
        editor_text: "test content",
        author_persona: "Ernest Hemingway",
        help_focus: "Dialogue Writing",
        chat_history: [],
        llm_provider: "Google Gemini",
        ai_mode: "talk"
      })
    });
    
    console.log('❌ Unexpected success - should have failed with 401');
    
  } catch (error) {
    console.log('✅ Axios request failed as expected');
    console.log('🔍 Error details:', {
      message: error.message,
      name: error.name,
      isAuthError: error.message?.includes('🔐'),
      isNetworkError: error.message?.includes('Network')
    });
    
    if (error.message?.includes('🔐')) {
      console.log('🎉 SUCCESS: Enhanced authentication error detected!');
      console.log('✅ Error contains 🔐 icon and proper auth message');
    } else if (error.message?.includes('Network')) {
      console.log('❌ FAILURE: Still getting network error instead of auth error');
      console.log('💡 The fix may need additional work');
    } else {
      console.log('⚠️ UNKNOWN: Error format is different than expected');
    }
  }
  
  // Test 3: Check if auth:token-expired event is dispatched
  console.log('\n🔍 Testing auth:token-expired event dispatch...');
  
  let eventReceived = false;
  const eventListener = (event) => {
    console.log('📢 auth:token-expired event received!', event.detail);
    eventReceived = true;
  };
  
  window.addEventListener('auth:token-expired', eventListener);
  
  // Trigger another 401 error
  try {
    await fetch('https://backend-copy-production-95b5.up.railway.app/api/chat/', {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer another_invalid_token',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: "test event dispatch",
        editor_text: "test",
        author_persona: "Ernest Hemingway",
        help_focus: "Dialogue Writing",
        chat_history: [],
        llm_provider: "Google Gemini",
        ai_mode: "talk"
      })
    });
  } catch (error) {
    // Expected to fail
  }
  
  // Wait a moment for event to be dispatched
  await new Promise(resolve => setTimeout(resolve, 500));
  
  window.removeEventListener('auth:token-expired', eventListener);
  
  if (eventReceived) {
    console.log('✅ auth:token-expired event successfully dispatched');
  } else {
    console.log('❌ auth:token-expired event was NOT dispatched');
    console.log('💡 Event dispatch mechanism may need debugging');
  }
}

// === 6. COMPREHENSIVE DIAGNOSIS ===
async function runFullDiagnosis() {
  console.log('🔍 === RUNNING FULL DOG WRITER DIAGNOSTIC ===');
  console.log('📋 This will test all critical systems...\n');
  
  try {
    // Run all diagnostic functions
    debugAuthentication();
    await testApiConnectivity();
    await testChatApi();
    await testEnhancedErrorHandling();
    
    console.log('\n🎯 === DIAGNOSIS COMPLETE ===');
    console.log('📊 Check the results above for any issues.');
    console.log('💡 If you see any ❌ errors, those need to be addressed.');
    
    // Provide recommendations
    console.log('\n💡 === RECOMMENDATIONS ===');
    
    const tokens = {
      owen_access_token: localStorage.getItem('owen_access_token'),
      owen_refresh_token: localStorage.getItem('owen_refresh_token')
    };
    
    if (!tokens.owen_access_token && !tokens.owen_refresh_token) {
      console.log('🔐 AUTHENTICATION: Please sign in to test chat functionality');
    } else if (tokens.owen_access_token) {
      console.log('✅ AUTHENTICATION: Tokens present - if chat still fails, they may be expired');
      console.log('💡 Try: clearAllTokens() then sign in again');
    }
    
    console.log('🌐 NETWORK: If you see network errors, check your internet connection');
    console.log('🔧 BACKEND: If backend is unhealthy, wait a moment and try again');
    console.log('🧪 ERROR HANDLING: New enhanced error handling should show 🔐 icons for auth errors');
    
  } catch (error) {
    console.error('❌ Diagnosis failed:', error);
  }
}

// === 7. ERROR EVENT LISTENERS ===
function setupErrorEventListeners() {
  console.log('\n👂 === SETTING UP ERROR EVENT LISTENERS ===');
  
  // Listen for auth:token-expired events
  window.addEventListener('auth:token-expired', (event) => {
    console.log('📢 auth:token-expired event received:', event.detail);
  });
  
  // Listen for any unhandled promise rejections
  window.addEventListener('unhandledrejection', (event) => {
    console.log('❌ Unhandled promise rejection:', event.reason);
  });
  
  console.log('✅ Error event listeners set up');
}

// Auto-setup event listeners
setupErrorEventListeners();

// Make functions available globally
window.debugAuthentication = debugAuthentication;
window.testApiConnectivity = testApiConnectivity;
window.testChatApi = testChatApi;
window.clearAllTokens = clearAllTokens;
window.testEnhancedErrorHandling = testEnhancedErrorHandling;
window.runFullDiagnosis = runFullDiagnosis;

console.log('\n🚀 === READY TO DEBUG ===');
console.log('Quick start: Run runFullDiagnosis() to test everything');
console.log('Or run individual functions to test specific components');
console.log('\n📚 TROUBLESHOOTING GUIDE:');
console.log('1. If you see "Network Error" in chat:');
console.log('   → This is likely an authentication issue');
console.log('   → Run clearAllTokens() and sign in again');
console.log('2. If enhanced error messages are not showing:');
console.log('   → Check browser console for error details');
console.log('   → Run testEnhancedErrorHandling() to verify');
console.log('3. If chat API fails with 401:');
console.log('   → Enhanced error handling should show proper auth message');
console.log('   → Automatic token cleanup should occur');
console.log('   → You should see 🔐 icon in error display'); 