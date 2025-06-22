import { Mark } from '@tiptap/core';

/**
 * Custom TipTap Extension: Multi-color Highlighting
 * 
 * Single Responsibility: Provide highlighting functionality with multiple colors
 * Used by: HighlightableEditor components
 */
export const CustomHighlight = Mark.create({
  name: 'customHighlight',
  
  addOptions() {
    return {
      multicolor: true,
      HTMLAttributes: {},
    }
  },

  addAttributes() {
    return {
      color: {
        default: 'feedback-request',
        parseHTML: element => element.getAttribute('data-color'),
        renderHTML: attributes => {
          if (!attributes.color) {
            return {}
          }
          return { 'data-color': attributes.color, class: `highlight-${attributes.color}` }
        },
      },
      id: {
        default: null,
        parseHTML: element => element.getAttribute('data-highlight-id'),
        renderHTML: attributes => {
          if (!attributes.id) {
            return {}
          }
          return { 'data-highlight-id': attributes.id }
        },
      },
    }
  },

  parseHTML() {
    return [
      {
        tag: 'mark[data-color]',
      },
    ]
  },

  renderHTML({ HTMLAttributes }) {
    return ['mark', HTMLAttributes, 0]
  },

  addCommands() {
    return {
      setHighlight:
        (attributes) =>
        ({ commands }) => {
          return commands.setMark(this.name, attributes)
        },
      toggleHighlight:
        (attributes) =>
        ({ commands }) => {
          return commands.toggleMark(this.name, attributes)
        },
      unsetHighlight:
        () =>
        ({ commands }) => {
          return commands.unsetMark(this.name)
        },
    }
  },
});

// Types for the extension
export interface HighlightAttributes {
  color?: string;
  id?: string;
}

export interface HighlightInfo {
  id: string;
  text: string;
  color: string;
  position: { from: number; to: number };
  timestamp: number;
} 