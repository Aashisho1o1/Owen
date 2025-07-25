/**
 * COMPREHENSIVE FOLDERSCOPE TESTING SCRIPT
 * Tests the complete FolderScope flow to identify exact failure points
 */

// Mock browser environment for frontend testing
const mockLocalStorage = {
  data: {},
  getItem: (key) => mockLocalStorage.data[key] || null,
  setItem: (key, value) => { mockLocalStorage.data[key] = value; },
  removeItem: (key) => { delete mockLocalStorage.data[key]; }
};

global.localStorage = mockLocalStorage;

// Test 1: Frontend Request Building
console.log('🧪 TEST 1: Frontend Chat Request Building');
console.log('==========================================');

// Simulate the buildChatRequest function
const buildChatRequest = (
  message,
  editorText,
  authorPersona,
  helpFocus,
  chatHistory,
  llmProvider,
  userPreferences,
  feedbackOnPrevious,
  highlightedText,
  highlightId,
  aiMode = 'talk',
  folderScope = false,
  voiceGuard = false
) => {
  return {
    message,
    editor_text: editorText,
    author_persona: authorPersona,
    help_focus: helpFocus,
    chat_history: chatHistory,
    llm_provider: llmProvider,
    user_preferences: userPreferences || { user_corrections: [] },
    feedback_on_previous: feedbackOnPrevious || '',
    highlighted_text: highlightedText || '',
    highlight_id: highlightId || '',
    ai_mode: aiMode,
    folder_scope: folderScope,
    voice_guard: voiceGuard
  };
};

// Test with FolderScope enabled
const testRequest = buildChatRequest(
  "Who is the main character in my story?",
  "Chapter 1: Alice walked through the forest...",
  "Ernest Hemingway",
  "Character Introduction",
  [],
  "Google Gemini",
  { user_corrections: [] },
  "",
  "",
  "",
  "talk",
  true,  // FolderScope enabled
  false  // VoiceGuard disabled
);

console.log('✅ Request object structure:');
console.log(JSON.stringify(testRequest, null, 2));

// Test 2: Premium Feature State Management
console.log('\n🧪 TEST 2: Premium Feature State Management');
console.log('============================================');

// Simulate localStorage for FolderScope toggle
mockLocalStorage.setItem('owen_folder_scope', JSON.stringify(true));
const savedFolderScope = JSON.parse(mockLocalStorage.getItem('owen_folder_scope'));
console.log(`✅ FolderScope localStorage state: ${savedFolderScope}`);

// Test 3: API Request Preparation
console.log('\n🧪 TEST 3: API Request Headers and Body');
console.log('======================================');

const prepareApiRequest = (request) => {
  const timeoutMs = (request.folder_scope || request.voice_guard) ? 150000 : 45000;
  
  return {
    url: '/api/chat/',
    method: 'POST',
    body: request,
    headers: {
      'Content-Type': 'application/json',
      'X-Request-Type': request.folder_scope ? 'folder-scope' : 'standard'
    },
    timeout: timeoutMs
  };
};

const apiRequest = prepareApiRequest(testRequest);
console.log('✅ API Request Configuration:');
console.log(`   URL: ${apiRequest.url}`);
console.log(`   Method: ${apiRequest.method}`);
console.log(`   Timeout: ${apiRequest.timeout}ms`);
console.log(`   Headers:`, JSON.stringify(apiRequest.headers, null, 2));
console.log(`   Body folder_scope: ${apiRequest.body.folder_scope}`);
console.log(`   Body voice_guard: ${apiRequest.body.voice_guard}`);

// Test 4: Backend Request Validation
console.log('\n🧪 TEST 4: Backend Request Schema Validation');
console.log('===========================================');

// Simulate Pydantic schema validation
const validateChatRequest = (request) => {
  const requiredFields = [
    'message', 'editor_text', 'author_persona', 'help_focus', 
    'chat_history', 'llm_provider', 'ai_mode'
  ];
  
  const optionalFields = [
    'folder_scope', 'voice_guard', 'user_preferences', 
    'feedback_on_previous', 'highlighted_text', 'highlight_id'
  ];
  
  const errors = [];
  
  // Check required fields
  for (const field of requiredFields) {
    if (!(field in request)) {
      errors.push(`Missing required field: ${field}`);
    }
  }
  
  // Check data types
  if (typeof request.folder_scope !== 'boolean') {
    errors.push(`folder_scope must be boolean, got: ${typeof request.folder_scope}`);
  }
  
  if (typeof request.voice_guard !== 'boolean') {
    errors.push(`voice_guard must be boolean, got: ${typeof request.voice_guard}`);
  }
  
  return {
    valid: errors.length === 0,
    errors
  };
};

const validation = validateChatRequest(testRequest);
console.log(`✅ Schema validation result: ${validation.valid ? 'VALID' : 'INVALID'}`);
if (!validation.valid) {
  console.log('   Errors:', validation.errors);
}

// Test 5: Backend Conditional Logic Simulation
console.log('\n🧪 TEST 5: Backend Conditional Logic');
console.log('===================================');

const simulateBackendLogic = (chatRequest) => {
  console.log(`📥 Received request with folder_scope: ${chatRequest.folder_scope} (type: ${typeof chatRequest.folder_scope})`);
  console.log(`📥 Received request with voice_guard: ${chatRequest.voice_guard} (type: ${typeof chatRequest.voice_guard})`);
  
  // Simulate the exact condition from backend
  const folderScopeCondition = chatRequest.folder_scope;
  const voiceGuardCondition = chatRequest.voice_guard;
  
  console.log(`🔧 DEBUGGING - folder_scope type: ${typeof chatRequest.folder_scope}`);
  console.log(`🔧 DEBUGGING - folder_scope value: ${JSON.stringify(chatRequest.folder_scope)}`);
  console.log(`🔧 DEBUGGING - folder_scope bool conversion: ${Boolean(chatRequest.folder_scope)}`);
  console.log(`🔧 DEBUGGING - if chat_request.folder_scope evaluates to: ${Boolean(folderScopeCondition)}`);
  
  if (folderScopeCondition) {
    console.log('✅ FolderScope condition PASSED - would execute folder context retrieval');
  } else {
    console.log('❌ FolderScope condition FAILED - folder context retrieval would NOT execute');
    console.log(`   Reason: folder_scope=${chatRequest.folder_scope} evaluates to falsy`);
  }
  
  if (voiceGuardCondition) {
    console.log('✅ VoiceGuard condition PASSED - would execute voice analysis');
  } else {
    console.log('❌ VoiceGuard condition FAILED - voice analysis would NOT execute');
  }
};

simulateBackendLogic(testRequest);

// Test 6: Edge Cases
console.log('\n🧪 TEST 6: Edge Case Testing');
console.log('============================');

const edgeCases = [
  { folder_scope: undefined, voice_guard: false, description: 'undefined folder_scope' },
  { folder_scope: null, voice_guard: false, description: 'null folder_scope' },
  { folder_scope: 'true', voice_guard: false, description: 'string "true" folder_scope' },
  { folder_scope: 1, voice_guard: false, description: 'number 1 folder_scope' },
  { folder_scope: 0, voice_guard: false, description: 'number 0 folder_scope' },
  { folder_scope: '', voice_guard: false, description: 'empty string folder_scope' }
];

edgeCases.forEach((testCase, index) => {
  console.log(`\n   Edge Case ${index + 1}: ${testCase.description}`);
  const edgeRequest = { ...testRequest, ...testCase };
  console.log(`   Value: ${JSON.stringify(testCase.folder_scope)} (type: ${typeof testCase.folder_scope})`);
  console.log(`   Boolean conversion: ${Boolean(testCase.folder_scope)}`);
  console.log(`   Truthiness: ${testCase.folder_scope ? 'truthy' : 'falsy'}`);
});

// Test 7: Network Request Simulation
console.log('\n🧪 TEST 7: Network Request Simulation');
console.log('====================================');

const simulateNetworkRequest = async (request) => {
  console.log('📡 Simulating network request...');
  console.log(`   Request URL: /api/chat/`);
  console.log(`   Request Method: POST`);
  console.log(`   Request Body Preview:`);
  console.log(`     - message: "${request.message.substring(0, 50)}..."`);
  console.log(`     - folder_scope: ${request.folder_scope}`);
  console.log(`     - voice_guard: ${request.voice_guard}`);
  console.log(`     - ai_mode: ${request.ai_mode}`);
  
  // Simulate successful request
  return {
    status: 200,
    data: {
      dialogue_response: "Based on your folder context, Alice appears to be your main character...",
      thinking_trail: "I analyzed all documents in your folder and found consistent references to Alice..."
    }
  };
};

// Run network simulation
simulateNetworkRequest(testRequest).then(response => {
  console.log('✅ Simulated response received:');
  console.log(`   Status: ${response.status}`);
  console.log(`   Response preview: "${response.data.dialogue_response.substring(0, 50)}..."`);
});

console.log('\n🏁 COMPREHENSIVE TESTING COMPLETE');
console.log('=================================');
console.log('All tests completed. Review the output above to identify any issues.'); 