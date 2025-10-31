# Next Steps - Frontend Integration

## Current Status

✅ **Backend Complete** - Minimal backend (900 lines, working)
✅ **Dependencies Installed** - TipTap, Axios, Gemini
✅ **Core Files Copied** - WritingWorkspace, HighlightableEditor, contexts
✅ **API Service Created** - api.service.ts for backend calls

## ⚠️ Current Issues

The WritingWorkspace from main branch has dependencies on:
1. **Document Management** - DocumentManager, StoryGeneratorModal
2. **Auth Modals** - AuthModal, UserProfileModal
3. **API Types** - services/api/types
4. **Heavy Dependencies** - Mantine UI components

These don't exist in the minimal competition version.

## 🎯 Two Options Forward

### Option A: Fix Dependencies (2-3 hours)
Create all missing components:
- DocumentManager (simplified)
- AuthModal (simple login/register)
- UserProfileModal
- API types
- Remove Mantine dependencies

**Pros**: Full-featured writing workspace
**Cons**: Time-consuming, adds complexity

### Option B: Create Minimal Workspace (30 mins)
Fresh, simple WritingWorkspace with just:
- TipTap editor
- Auto voice analysis
- Gemini integration
- No document management (use localStorage)
- No auth UI (optional backend)

**Pros**: Fast, focused, competition-ready
**Cons**: Less features

## 💡 Recommended: Option B (Minimal)

Create `WritingWorkspaceSimple.tsx`:

```typescript
import React, { useState, useEffect } from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import { geminiService } from '../services/gemini.service';

export const WritingWorkspace: React.FC = () => {
  const [voiceResults, setVoiceResults] = useState([]);

  // TipTap editor
  const editor = useEditor({
    extensions: [StarterKit],
    content: localStorage.getItem('document_content') || '',
    onUpdate: ({ editor }) => {
      const text = editor.getText();
      localStorage.setItem('document_content', text);

      // Auto-analyze after 2 seconds of no typing
      debouncedAnalyze(text);
    }
  });

  // Auto voice analysis
  const debouncedAnalyze = useMemo(
    () => debounce(async (text) => {
      // Extract dialogue
      const dialogues = extractDialogue(text);

      // Analyze with Gemini
      const results = await geminiService.analyzeDialogueConsistency(dialogues);

      // Update underlines
      setVoiceResults(results);

      // TODO: Add marks to editor for inconsistent dialogues
    }, 2000),
    []
  );

  return (
    <div className="workspace">
      <div className="editor-panel">
        <EditorContent editor={editor} />
      </div>

      <div className="voice-panel">
        <h3>Character Profiles</h3>
        {voiceResults.map(result => (
          <div key={result.character} className="profile-card">
            <h4>{result.character}</h4>
            <p>Consistency: {result.consistency}%</p>
            <p>Tone: {result.voice_traits.tone}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
```

## 🚀 Quick Implementation Plan

### 1. Create Simple Workspace (15 min)
```bash
# File: frontend/src/components/WritingWorkspaceSimple.tsx
```

### 2. Add Voice Analysis Extension (20 min)
```bash
# File: frontend/src/extensions/VoiceInconsistencyMark.ts
```

### 3. Style It (10 min)
```bash
# File: frontend/src/styles/workspace.css
```

### 4. Test (5 min)
```bash
npm run dev
```

## 📝 Implementation Code

I'll create the minimal version now. It will:
- ✅ Work standalone (no heavy dependencies)
- ✅ Auto-analyze voice as you type
- ✅ Show red underlines on inconsistencies
- ✅ Display character profiles
- ✅ Optional backend integration

## 🎯 Decision Time

**Choose one:**
1. **"Create minimal workspace"** - I'll build Option B (simple, fast)
2. **"Fix all dependencies"** - I'll build Option A (full-featured, slow)
3. **"Show me both approaches"** - I'll create side-by-side comparison

Which would you like me to proceed with?
