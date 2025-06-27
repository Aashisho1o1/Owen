# AI Suggestions Debug Guide

## Current Issue
The AI suggestions feature is generating suggestions correctly on the backend, but they're not appearing automatically in the chat interface. Users have to click "Get Options" to see them.

## What We Know Works ✅
1. **Backend**: Generates 4 suggestions correctly
2. **API Endpoint**: `/api/chat/suggestions` returns proper data
3. **Event System**: `suggestionsGenerated` event is dispatched
4. **Components**: `SuggestionsDisplay`, `EnhancedChatMessage` are implemented
5. **Accept Buttons**: UI components have proper accept functionality

## What's Not Working ❌
1. **Automatic Display**: Suggestions don't appear automatically in Co-Edit mode
2. **Accept Functionality**: Check mark doesn't update editor content

## Debug Steps

### Step 1: Test Event Flow
Open browser console and run:
```javascript
// Test if event listener is working
window.addEventListener('suggestionsGenerated', (e) => {
  console.log('🎯 Event received:', e.detail);
});

// Dispatch test event
window.dispatchEvent(new CustomEvent('suggestionsGenerated', {
  detail: {
    suggestions: [
      { id: 'test-1', text: 'Test suggestion', type: 'clarity', confidence: 0.9, explanation: 'Test' }
    ],
    originalText: 'Test text',
    dialogueResponse: 'Test response'
  }
}));
```

### Step 2: Check ChatContext State
```javascript
// Check if ChatContext has suggestions
const chatContext = document.querySelector('[data-testid="chat-context"]');
console.log('ChatContext state:', chatContext);
```

### Step 3: Verify Component Rendering
```javascript
// Check if SuggestionsDisplay is in DOM
const suggestionsDisplay = document.querySelector('.suggestions-display');
console.log('SuggestionsDisplay found:', !!suggestionsDisplay);

// Check if EnhancedChatMessage is rendering suggestions
const enhancedMessages = document.querySelectorAll('.message.ai-message');
console.log('AI messages found:', enhancedMessages.length);
```

## Likely Root Causes

### 1. Timing Issue
The suggestions might be generated but cleared before they can be displayed.

**Fix**: Add persistence to suggestions state:
```typescript
// In ChatContext, prevent clearing suggestions too quickly
const clearSuggestions = () => {
  // Only clear if not in Co-Edit mode
  if (aiMode !== 'co-edit') {
    setCurrentSuggestions([]);
  }
};
```

### 2. State Update Issue
The `currentSuggestions` state might not be triggering re-renders.

**Fix**: Force re-render when suggestions are set:
```typescript
const [suggestionsTimestamp, setSuggestionsTimestamp] = useState(0);

// In event handler
setCurrentSuggestions(suggestions);
setSuggestionsTimestamp(Date.now()); // Force re-render
```

### 3. Component Props Issue
The suggestions might not be passed correctly to display components.

**Fix**: Verify props flow:
```typescript
// In MessagesContainer
console.log('MessagesContainer props:', { 
  currentSuggestions, 
  messagesCount: messages.length 
});
```

## Immediate Fixes to Try

### Fix 1: Add Debug Logging
Add console.log statements to track the flow:

1. **In useChat.ts** (line ~207):
```typescript
console.log('🚀 Dispatching suggestions event:', response.suggestions);
```

2. **In ChatContext.tsx** (event listener):
```typescript
console.log('📥 Received suggestions:', suggestions);
```

3. **In MessagesContainer.tsx**:
```typescript
console.log('💬 Rendering with suggestions:', currentSuggestions);
```

### Fix 2: Prevent Premature Clearing
In `ChatContext.tsx`, modify the `clearSuggestions` function:
```typescript
const clearSuggestions = () => {
  // Don't clear if we just generated suggestions
  if (Date.now() - lastSuggestionsTime > 5000) {
    setCurrentSuggestions([]);
  }
};
```

### Fix 3: Force Component Update
In `EnhancedChatMessage.tsx`, add a key based on suggestions:
```typescript
// In MessagesContainer
<EnhancedChatMessage 
  key={`${index}-${currentSuggestions.length}`}
  // ... other props
/>
```

## Testing Checklist

1. [ ] Open Co-Edit mode
2. [ ] Highlight text
3. [ ] Send a message
4. [ ] Check browser console for:
   - [ ] "Using suggestions endpoint" log
   - [ ] "Generated X suggestions" log  
   - [ ] "Dispatching suggestions event" log
   - [ ] "Received suggestions" log
5. [ ] Check if suggestions appear in chat
6. [ ] Test accept button functionality
7. [ ] Verify editor content updates

## Next Steps

1. **Add comprehensive logging** to track the exact flow
2. **Test in production** with browser console open
3. **Identify the exact point** where suggestions are lost
4. **Implement targeted fix** based on findings

## Expected Behavior
When user:
1. Switches to Co-Edit mode
2. Highlights text  
3. Sends a message

Should see:
1. Regular AI response
2. **4 suggestion cards** displayed automatically
3. **Accept buttons** (✓) on each suggestion
4. **One-click acceptance** that updates editor content 