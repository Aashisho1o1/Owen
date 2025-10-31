# Improved Frontend Implementation Guide

## 🎯 Goal
Create a **Grammarly-like** experience where voice inconsistencies are automatically underlined as users write.

## 🏗️ Architecture Overview

```
User types dialogue
    ↓
Auto-detect dialogue (debounced 2s)
    ↓
Send to Gemini API for voice analysis
    ↓
Get back: { character, isConsistent, issues }
    ↓
Underline inconsistent dialogue in editor
    ↓
Show tooltip on hover with explanation
```

## 📁 File Structure

```
frontend/src/
├── pages/
│   └── WritingWorkspace.tsx         ← Main page (NEW)
├── components/
│   ├── HighlightableEditor.tsx      ← TipTap editor (NEW)
│   ├── VoiceTooltip.tsx             ← Hover tooltip (NEW)
│   └── CharacterPanel.tsx           ← Sidebar with profiles (NEW)
├── services/
│   ├── gemini.service.ts            ← Keep existing
│   ├── api.service.ts               ← Backend API (NEW)
│   └── voice-detection.service.ts   ← Auto-detect dialogue (NEW)
├── extensions/
│   └── VoiceInconsistencyMark.ts    ← TipTap extension for underlines (NEW)
├── contexts/
│   ├── EditorContext.tsx            ← Editor state (NEW)
│   └── VoiceAnalysisContext.tsx     ← Analysis state (NEW)
└── styles/
    ├── editor.css                   ← Editor styles (NEW)
    └── voice-underlines.css         ← Underline styles (NEW)
```

## 🔧 Implementation Steps

### Step 1: Create Simple Writing Workspace

**File: `pages/WritingWorkspace.tsx`**

Key features:
- Simple layout: Editor on left, character profiles on right
- No tabs, no complex UI
- Just write and see underlines appear

### Step 2: TipTap Editor with Auto-Analysis

**File: `components/HighlightableEditor.tsx`**

```typescript
// Pseudocode
const editor = useEditor({
  extensions: [StarterKit, VoiceInconsistencyMark],
  content,
  onUpdate: ({ editor }) => {
    const text = editor.getText();
    debouncedAnalyze(text); // Wait 2s after typing stops
  }
});

const debouncedAnalyze = useDe bounce(async (text) => {
  // 1. Extract dialogue from text
  const dialogues = extractDialogue(text);

  // 2. Analyze with Gemini
  const results = await geminiService.analyzeVoiceConsistency(dialogues);

  // 3. Update editor decorations
  results.forEach(result => {
    if (!result.isConsistent) {
      // Find this dialogue in editor and underline it
      addInconsistencyMark(result.dialogue, result.issues);
    }
  });
}, 2000);
```

### Step 3: Voice Inconsistency Mark Extension

**File: `extensions/VoiceInconsistencyMark.ts`**

```typescript
import { Mark } from '@tiptap/core';

export const VoiceInconsistencyMark = Mark.create({
  name: 'voiceInconsistency',

  addAttributes() {
    return {
      character: { default: null },
      issues: { default: [] },
      suggestions: { default: [] }
    };
  },

  parseHTML() {
    return [{ tag: 'span.voice-inconsistency' }];
  },

  renderHTML({ HTMLAttributes }) {
    return ['span', {
      ...HTMLAttributes,
      class: 'voice-inconsistency',
      'data-tooltip': 'Voice inconsistency detected'
    }, 0];
  }
});
```

### Step 4: Auto-Detection Service

**File: `services/voice-detection.service.ts`**

```typescript
export const extractDialogue = (text: string): Dialogue[] => {
  // Simple regex for now (Gemini can do better later)
  const dialoguePattern = /"([^"]+)"/g;
  const dialogues: Dialogue[] = [];

  let match;
  while ((match = dialoguePattern.exec(text)) !== null) {
    dialogues.push({
      text: match[1],
      position: match.index,
      // Try to infer speaker from context
      speaker: inferSpeaker(text, match.index)
    });
  }

  return dialogues;
};

const inferSpeaker = (text: string, position: number): string => {
  // Look for "Name:" or "Name said" before the dialogue
  const before = text.substring(Math.max(0, position - 50), position);
  const speakerMatch = before.match(/([A-Z][a-z]+)[:|\s+said]/);
  return speakerMatch ? speakerMatch[1] : 'Unknown';
};
```

### Step 5: Tooltip Component

**File: `components/VoiceTooltip.tsx`**

```typescript
export const VoiceTooltip: React.FC<{
  character: string;
  issues: string[];
  suggestions: string[];
}> = ({ character, issues, suggestions }) => {
  return (
    <div className="voice-tooltip">
      <div className="tooltip-header">
        <span className="character-name">{character}</span>
        <span className="inconsistency-badge">Voice Inconsistency</span>
      </div>

      <div className="tooltip-issues">
        <strong>Issues:</strong>
        <ul>
          {issues.map((issue, i) => (
            <key={i}>{issue}</li>
          ))}
        </ul>
      </div>

      <div className="tooltip-suggestions">
        <strong>Suggestions:</strong>
        <ul>
          {suggestions.map((suggestion, i) => (
            <li key={i}>{suggestion}</li>
          ))}
        </ul>
      </div>
    </div>
  );
};
```

### Step 6: Styling

**File: `styles/voice-underlines.css`**

```css
/* Grammarly-style wavy underline */
.voice-inconsistency {
  text-decoration: none;
  position: relative;
  cursor: pointer;
}

.voice-inconsistency::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  bottom: -2px;
  height: 2px;
  background-image: repeating-linear-gradient(
    135deg,
    transparent,
    transparent 4px,
    #ef4444 4px,
    #ef4444 8px
  );
  animation: wave 1s linear infinite;
}

@keyframes wave {
  0% { background-position: 0 0; }
  100% { background-position: 16px 0; }
}

/* Tooltip positioning */
.voice-tooltip {
  position: absolute;
  z-index: 1000;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  max-width: 300px;
}
```

## 🎯 User Experience Flow

1. **User opens app** → Sees clean editor
2. **User types dialogue** → "Hey there!" she said cheerfully.
3. **2 seconds after typing stops** → Auto-analysis runs
4. **If inconsistent** → Red wavy underline appears
5. **User hovers over underline** → Tooltip shows:
   ```
   Emma - Voice Inconsistency

   Issues:
   - Tone changed from formal to casual
   - Vocabulary doesn't match previous samples

   Suggestions:
   - Keep formal tone: "Greetings" instead of "Hey"
   - Maintain sophisticated vocabulary
   ```

## 🔌 Backend Integration (Optional)

### With Backend
- Login/register
- Save character profiles to PostgreSQL
- Profiles persist across sessions
- Multi-document support

### Without Backend
- Works offline
- Profiles in localStorage
- Still full-featured
- Perfect for demo

## 📊 Performance

- **Typing**: No lag, smooth 60fps
- **Analysis**: 2-3 seconds after typing stops
- **Underline**: Instant once analysis completes
- **Tooltip**: Appears on hover, no delay

## 🎨 UI Design

```
┌────────────────────────────────────────────────────────┐
│  Owen - Fiction Voice Checker  [Word Count] [Login]   │
├──────────────────────────────┬─────────────────────────┤
│                              │  Character Profiles      │
│  Editor                      │  ┌──────────────────┐   │
│                              │  │ Emma             │   │
│  Emma walked into the room.  │  │ Tone: Formal     │   │
│  "Hey there!" she said.      │  │ Vocab: Sophist.  │   │
│   ~~~~~~~~~~~                │  │ Consistency: 78% │   │
│  (red wavy underline)        │  └──────────────────┘   │
│                              │                          │
│  [Hover shows tooltip]       │  ┌──────────────────┐   │
│                              │  │ Jake             │   │
│                              │  │ Tone: Gruff      │   │
│                              │  │ Vocab: Simple    │   │
│                              │  │ Consistency: 95% │   │
│                              │  └──────────────────┘   │
└──────────────────────────────┴─────────────────────────┘
```

## ✅ MVP Checklist

- [ ] TipTap editor working
- [ ] Dialogue detection working
- [ ] Gemini API integration
- [ ] Wavy underlines appear
- [ ] Tooltips show on hover
- [ ] Character profiles display
- [ ] Backend integration (optional)
- [ ] Clean, professional design

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Open http://localhost:5173
```

## 📝 Next Steps

Due to token/time constraints, I recommend:

1. **Start with MVP**: Just editor + underlines
2. **Test with sample text**: "Hey!" vs "Greetings!"
3. **Add tooltip**: Show why it's inconsistent
4. **Polish UI**: Make it beautiful
5. **Add backend**: Optional enhancement

Would you like me to:
1. Create the core WritingWorkspace component?
2. Create the HighlightableEditor with auto-analysis?
3. Set up the basic structure and let you build from there?

Let me know which approach you prefer!
