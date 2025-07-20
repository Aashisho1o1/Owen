import { Mark, mergeAttributes } from '@tiptap/core'

export interface VoiceInconsistencyOptions {
  HTMLAttributes: Record<string, any>
}

declare module '@tiptap/core' {
  interface Commands<ReturnType> {
    voiceInconsistency: {
      /**
       * Set a voice inconsistency mark
       */
      setVoiceInconsistency: (attributes?: {
        character: string
        confidence: number
        explanation: string
        confidenceLevel: 'low' | 'medium' | 'high'
      }) => ReturnType
      /**
       * Toggle a voice inconsistency mark
       */
      toggleVoiceInconsistency: (attributes?: {
        character: string
        confidence: number
        explanation: string
        confidenceLevel: 'low' | 'medium' | 'high'
      }) => ReturnType
      /**
       * Unset a voice inconsistency mark
       */
      unsetVoiceInconsistency: () => ReturnType
    }
  }
}

/**
 * TipTap Mark Extension for Voice Inconsistencies
 * 
 * This extension creates a proper TipTap mark that:
 * 1. Is recognized by TipTap's schema system
 * 2. Survives content edits and DOM reconciliation
 * 3. Can be applied/removed using TipTap's command system
 * 4. Supports serialization to/from HTML and JSON
 */
export const VoiceInconsistencyMark = Mark.create<VoiceInconsistencyOptions>({
  name: 'voiceInconsistency',

  addOptions() {
    return {
      HTMLAttributes: {},
    }
  },

  addAttributes() {
    return {
      character: {
        default: '',
        parseHTML: element => element.getAttribute('data-character'),
        renderHTML: attributes => {
          if (!attributes.character) {
            return {}
          }
          return {
            'data-character': attributes.character,
          }
        },
      },
      confidence: {
        default: 0.5,
        parseHTML: element => {
          const confidence = element.getAttribute('data-confidence')
          return confidence ? parseFloat(confidence) : 0.5
        },
        renderHTML: attributes => {
          if (!attributes.confidence) {
            return {}
          }
          return {
            'data-confidence': attributes.confidence.toString(),
          }
        },
      },
      explanation: {
        default: '',
        parseHTML: element => element.getAttribute('data-explanation'),
        renderHTML: attributes => {
          if (!attributes.explanation) {
            return {}
          }
          return {
            'data-explanation': attributes.explanation,
          }
        },
      },
      confidenceLevel: {
        default: 'medium',
        parseHTML: element => element.getAttribute('data-confidence-level') || 'medium',
        renderHTML: attributes => {
          return {
            'data-confidence-level': attributes.confidenceLevel || 'medium',
          }
        },
      },
    }
  },

  parseHTML() {
    return [
      {
        tag: 'span[data-voice-inconsistency]',
      },
      {
        tag: 'span.voice-inconsistent',
      },
    ]
  },

  renderHTML({ HTMLAttributes }) {
    return [
      'span',
      mergeAttributes(
        this.options.HTMLAttributes,
        HTMLAttributes,
        {
          'data-voice-inconsistency': 'true',
          'data-voice-underline': 'true',
          class: `voice-inconsistent ${HTMLAttributes['data-confidence-level']}-confidence`,
        }
      ),
      0,
    ]
  },

  addCommands() {
    return {
      setVoiceInconsistency:
        attributes =>
        ({ commands }) => {
          return commands.setMark(this.name, attributes)
        },
      toggleVoiceInconsistency:
        attributes =>
        ({ commands }) => {
          return commands.toggleMark(this.name, attributes)
        },
      unsetVoiceInconsistency:
        () =>
        ({ commands }) => {
          return commands.unsetMark(this.name)
        },
    }
  },

  // IMPORTANT: Make this mark inclusive so it doesn't trap the cursor
  inclusive: false,

  // Allow this mark to span multiple nodes
  spanning: true,

  // This mark should not exclude other marks (allow bold, italic, etc.)
  excludes: '',
}) 