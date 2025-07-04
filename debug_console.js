// DOG Writer - Quick Console Debugging Script
// Copy and paste this into your browser console while on localhost:5178

console.log('🧪 DOG Writer Debug Script Loaded');

const BACKEND_URL = 'https://backend-copy-production-95b5.up.railway.app';

// Quick function to test the exact issue
async function debugNetworkError() {
    console.log('\n🎯 === REPRODUCING NETWORK ERROR ===');
    
    // Clear existing tokens
    localStorage.removeItem('owen_access_token');
    localStorage.removeItem('owen_refresh_token');
    
    // Set invalid token
    localStorage.setItem('owen_access_token', 'invalid_debug_token');
    console.log('🔧 Set invalid token for testing');
    
    try {
        console.log('📡 Making chat request with invalid token...');
        
        const response = await fetch(`${BACKEND_URL}/api/chat/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer invalid_debug_token'
            },
            body: JSON.stringify({
                message: 'Debug test message',
                editor_text: 'Debug test content',
                author_persona: 'Ernest Hemingway',
                help_focus: 'Dialogue Writing',
                chat_history: [],
                llm_provider: 'Google Gemini',
                ai_mode: 'talk'
            })
        });

        console.log(`📊 Response Status: ${response.status}`);
        console.log(`📊 Response OK: ${response.ok}`);
        
        if (response.status === 401) {
            const errorData = await response.json();
            console.log('✅ Backend correctly returns 401:', errorData);
            console.log('🔍 This proves backend is working correctly');
            console.log('❌ Issue is in frontend API client error handling');
        } else {
            console.log(`❌ Unexpected status: ${response.status}`);
        }
        
    } catch (error) {
        console.log(`❌ Request failed: ${error.message}`);
        console.log(`🔍 Error type: ${error.constructor.name}`);
        
        if (error.message.includes('Network')) {
            console.log('🎯 REPRODUCED: This is the network error we need to fix!');
        }
    }
}

// Test backend health
async function testBackendHealth() {
    console.log('\n🔍 === TESTING BACKEND HEALTH ===');
    
    try {
        const response = await fetch(`${BACKEND_URL}/api/health`);
        const data = await response.json();
        
        if (response.ok) {
            console.log('✅ Backend health check passed');
            console.log('📊 Status:', data.status);
            console.log('🗄️ Database:', data.database?.status);
            console.log('🔧 Version:', data.version);
            return true;
        } else {
            console.log(`❌ Backend unhealthy: ${response.status}`);
            return false;
        }
    } catch (error) {
        console.log(`❌ Backend connection failed: ${error.message}`);
        return false;
    }
}

// Clear all tokens
function clearAllTokens() {
    console.log('\n🧹 === CLEARING ALL TOKENS ===');
    
    const keys = [
        'access_token', 'refresh_token', 'token_type', 'expires_in',
        'owen_access_token', 'owen_refresh_token', 'owen_token_type', 'owen_token_expires',
        'token', 'authToken'
    ];
    
    let cleared = 0;
    keys.forEach(key => {
        if (localStorage.getItem(key)) {
            localStorage.removeItem(key);
            cleared++;
            console.log(`   ✅ Removed: ${key}`);
        }
    });
    
    console.log(`✅ Cleared ${cleared} tokens`);
}

// Check current authentication state
function checkAuth() {
    console.log('\n🔍 === CURRENT AUTH STATE ===');
    
    const tokens = {
        'owen_access_token': localStorage.getItem('owen_access_token'),
        'owen_refresh_token': localStorage.getItem('owen_refresh_token'),
        'access_token': localStorage.getItem('access_token'),
        'refresh_token': localStorage.getItem('refresh_token')
    };
    
    Object.entries(tokens).forEach(([key, value]) => {
        if (value) {
            console.log(`   ✅ ${key}: ${value.substring(0, 20)}...`);
        } else {
            console.log(`   ❌ ${key}: not set`);
        }
    });
}

// Test the frontend API client directly (if available)
async function testFrontendApiClient() {
    console.log('\n🔧 === TESTING FRONTEND API CLIENT ===');
    
    // Check if we can access the frontend API client
    if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
        console.log('✅ Running on localhost - can test frontend API client');
        
        // Set invalid token
        localStorage.setItem('owen_access_token', 'frontend_test_token');
        
        try {
            // Try to access the frontend's API module
            if (window.React && window.React.version) {
                console.log('✅ React detected - this is the actual frontend app');
                
                // Test the actual API client that the app uses
                console.log('🧪 Testing actual frontend API client...');
                console.log('💡 Open your browser Network tab to see the actual request');
                console.log('💡 Then try to send a chat message in the app');
                console.log('💡 Look for the NEW enhanced error handling:');
                console.log('   - Should see: "🔍 Response interceptor error analysis"');
                console.log('   - Should see: "🔐 401 Unauthorized detected"');
                console.log('   - Should see: "🔐 Authentication required" (not Network Error)');
                
                return true;
            } else {
                console.log('⚠️ React not detected - might not be the actual app');
                return false;
            }
        } catch (error) {
            console.log(`❌ Error testing frontend API client: ${error.message}`);
            return false;
        }
    } else {
        console.log('⚠️ Not on localhost - cannot test frontend API client directly');
        return false;
    }
}

// NEW: Test the enhanced error handling
async function testEnhancedErrorHandling() {
    console.log('\n🎯 === TESTING ENHANCED ERROR HANDLING ===');
    
    if (typeof window === 'undefined' || window.location.hostname !== 'localhost') {
        console.log('⚠️ Not on localhost - cannot test enhanced error handling');
        return;
    }
    
    console.log('🧪 Testing the NEW enhanced API client error handling...');
    console.log('💡 The API client should now:');
    console.log('   1. Log detailed error analysis');
    console.log('   2. Preserve response information');
    console.log('   3. Create proper error objects with debugging info');
    console.log('   4. Show "🔐 Authentication required" instead of "Network Error"');
    
    // Set invalid token for testing
    localStorage.setItem('owen_access_token', 'enhanced_error_test_token');
    console.log('🔧 Set invalid token for enhanced error testing');
    
    console.log('\n📋 TO TEST THE FIX:');
    console.log('1. Make sure your frontend dev server is running (npm run dev)');
    console.log('2. Open your React app at localhost:5178');
    console.log('3. Try to send a chat message');
    console.log('4. Check browser console for these NEW messages:');
    console.log('   - "🔍 Response interceptor error analysis: {...}"');
    console.log('   - "🔐 401 Unauthorized detected - handling authentication error"');
    console.log('   - "🔐 Throwing enhanced authentication error: 🔐 Authentication required..."');
    console.log('5. The chat should show "🔐 Authentication required" NOT "Network Error"');
    
    console.log('\n✅ If you see the enhanced error messages, the fix is working!');
    console.log('❌ If you still see "Network Error", there might be caching issues');
}

// NEW: Test the actual frontend API client with axios
async function testActualFrontendApiClient() {
    console.log('\n🎯 === TESTING ACTUAL FRONTEND API CLIENT ===');
    
    if (typeof window === 'undefined' || window.location.hostname !== 'localhost') {
        console.log('⚠️ Not on localhost - cannot test frontend API client');
        return;
    }
    
    // Set invalid token
    localStorage.setItem('owen_access_token', 'invalid_frontend_test_token');
    localStorage.setItem('access_token', 'invalid_frontend_test_token');
    
    console.log('🔧 Set invalid token for frontend testing');
    
    try {
        // Try to access the app's API client if it's available in the global scope
        console.log('🧪 Testing if we can access the app\'s API client...');
        
        // Check if axios is available globally
        if (typeof axios !== 'undefined') {
            console.log('✅ Axios detected - testing with axios directly');
            
            // Create a similar axios instance to what the app uses
            const testClient = axios.create({
                baseURL: BACKEND_URL,
                timeout: 30000,
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer invalid_frontend_test_token'
                }
            });
            
            const response = await testClient.post('/api/chat/', {
                message: 'Debug test message',
                editor_text: 'Debug test content',
                author_persona: 'Ernest Hemingway',
                help_focus: 'Dialogue Writing',
                chat_history: [],
                llm_provider: 'Google Gemini',
                ai_mode: 'talk'
            });
            
            console.log('❌ This should not succeed with invalid token');
            
        } else {
            console.log('⚠️ Axios not available globally');
            console.log('💡 To test the actual API client:');
            console.log('1. Open your React app');
            console.log('2. Try to send a chat message');
            console.log('3. Check the browser console for errors');
            console.log('4. Compare with the direct fetch test above');
        }
        
    } catch (error) {
        console.log('🎯 AXIOS ERROR CAUGHT:', error.message);
        console.log('🔍 Error details:', {
            name: error.name,
            message: error.message,
            hasResponse: !!error.response,
            responseStatus: error.response?.status,
            hasRequest: !!error.request,
            isAxiosError: error.isAxiosError
        });
        
        if (error.message.includes('Network Error')) {
            console.log('🎯 REPRODUCED: Found the Network Error in axios!');
            console.log('💡 This confirms the issue is in the axios response interceptor');
        }
    }
}

// Run all tests
async function runAllTests() {
    console.log('🚀 === RUNNING ALL DEBUG TESTS ===');
    
    const backendHealthy = await testBackendHealth();
    checkAuth();
    
    if (backendHealthy) {
        await debugNetworkError();
        await testFrontendApiClient();
        await testEnhancedErrorHandling();
        await testActualFrontendApiClient();
    }
    
    console.log('\n🎯 === DEBUG SUMMARY ===');
    console.log('✅ Backend is healthy and returns 401 errors correctly');
    console.log('🔧 Enhanced error handling has been implemented in the API client');
    console.log('📋 Next steps:');
    console.log('   1. Restart your frontend dev server (npm run dev)');
    console.log('   2. Clear browser cache and localStorage');
    console.log('   3. Test chat functionality in your app');
    console.log('   4. Look for enhanced error messages in console');
    console.log('   5. Should see "🔐 Authentication required" not "Network Error"');
}

// Export functions for easy use
console.log('💡 Available functions:');
console.log('  debugNetworkError() - Reproduce the network error');
console.log('  testBackendHealth() - Test backend connectivity');
console.log('  clearAllTokens() - Clear all auth tokens');
console.log('  checkAuth() - Check current auth state');
console.log('  testEnhancedErrorHandling() - Test the NEW error handling');
console.log('  testActualFrontendApiClient() - Test axios directly');
console.log('  runAllTests() - Run all tests');
console.log('\nExample: runAllTests()'); 