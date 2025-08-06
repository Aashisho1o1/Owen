/**
 * HighlightDecorations Extension for Tiptap
 * 
 * This extension provides persistent text highlighting using Prosemirror decorations
 * instead of direct DOM manipulation. Decorations survive React re-renders because
 * they are part of the editor's state management system.
 * 
 * Key Benefits:
 * - Highlights persist through React re-renders
 * - No race conditions with component updates
 * - Proper integration with editor undo/redo
 * - Performance optimized by Prosemirror
 */

import { Extension } from '@tiptap/core';
import { Plugin, PluginKey } from '@tiptap/pm/state';
import { Decoration, DecorationSet } from '@tiptap/pm/view';

// Declare the commands for TypeScript
declare module '@tiptap/core' {
  interface Commands<ReturnType> {
    highlightDecorations: {
      addHighlight: (options: { id: string; text: string; className?: string }) => ReturnType;
      removeHighlight: (id: string) => ReturnType;
      clearAllHighlights: () => ReturnType;
    };
  }
}

// Plugin state interface
interface HighlightState {
  highlights: Array<{
    id: string;
    from: number;
    to: number;
    text: string;
    className: string;
  }>;
}

// Plugin key for unique identification
const highlightPluginKey = new PluginKey<HighlightState>('highlightDecorations');

export const HighlightDecorations = Extension.create({
  name: 'highlightDecorations',

  addProseMirrorPlugins() {
    return [
      new Plugin<HighlightState>({
        key: highlightPluginKey,
        
        state: {
          init() {
            return {
              highlights: []
            };
          },
          
          apply(tr, value) {
            // Handle highlight commands from transactions
            const highlightCommand = tr.getMeta('highlightCommand');
            
            if (highlightCommand) {
              switch (highlightCommand.type) {
                case 'add':
                  // Remove existing highlights first to avoid overlaps
                  const filteredHighlights = value.highlights.filter(h => h.id !== highlightCommand.id);
                  return {
                    highlights: [
                      ...filteredHighlights,
                      {
                        id: highlightCommand.id,
                        from: highlightCommand.from,
                        to: highlightCommand.to,
                        text: highlightCommand.text,
                        className: highlightCommand.className || 'active-discussion-highlight'
                      }
                    ]
                  };
                  
                case 'remove':
                  return {
                    highlights: value.highlights.filter(h => h.id !== highlightCommand.id)
                  };
                  
                case 'clear':
                  return {
                    highlights: []
                  };
                  
                default:
                  return value;
              }
            }
            
            // Update highlight positions on document changes
            if (tr.docChanged) {
              const updatedHighlights = value.highlights.map(highlight => {
                const mappedFrom = tr.mapping.map(highlight.from);
                const mappedTo = tr.mapping.map(highlight.to);
                
                // Check if highlight is still valid after document changes
                if (mappedFrom < mappedTo && mappedFrom >= 0 && mappedTo <= tr.doc.content.size) {
                  return {
                    ...highlight,
                    from: mappedFrom,
                    to: mappedTo
                  };
                }
                return null;
              }).filter(Boolean) as typeof value.highlights;
              
              return {
                highlights: updatedHighlights
              };
            }
            
            return value;
          }
        },
        
        props: {
          decorations(state) {
            const { highlights } = highlightPluginKey.getState(state) || { highlights: [] };
            
            const decorations = highlights.map(highlight => {
              return Decoration.inline(highlight.from, highlight.to, {
                class: highlight.className,
                'data-highlight-id': highlight.id,
                'data-highlight-text': highlight.text
              });
            });
            
            return DecorationSet.create(state.doc, decorations);
          }
        }
      })
    ];
  },

  addCommands() {
    return {
      addHighlight: (options: { id: string; text: string; className?: string }) => ({ tr, state, dispatch }: any) => {
        // Find the text in the document
        const doc = state.doc;
        let found = false;
        let from = 0;
        let to = 0;
        
        // Search for the text in the document
        doc.descendants((node, pos) => {
          if (found || node.type.name !== 'text') return;
          
          const nodeText = node.text || '';
          const index = nodeText.indexOf(options.text);
          
          if (index >= 0) {
            from = pos + index;
            to = pos + index + options.text.length;
            found = true;
          }
        });
        
        if (!found) {
          console.warn('❌ Text not found for highlighting:', options.text);
          return false;
        }
        
        if (dispatch) {
          tr.setMeta('highlightCommand', {
            type: 'add',
            id: options.id,
            from,
            to,
            text: options.text,
            className: options.className || 'active-discussion-highlight'
          });
          dispatch(tr);
        }
        
        return true;
      },
      
      removeHighlight: (id: string) => ({ tr, dispatch }: any) => {
        if (dispatch) {
          tr.setMeta('highlightCommand', {
            type: 'remove',
            id
          });
          dispatch(tr);
        }
        return true;
      },
      
      clearAllHighlights: () => ({ tr, dispatch }: any) => {
        if (dispatch) {
          tr.setMeta('highlightCommand', {
            type: 'clear'
          });
          dispatch(tr);
        }
        return true;
      }
    };
  }
});

// Export utility functions for external use
export const getHighlightState = (editor: any) => {
  return highlightPluginKey.getState(editor.state);
};

export const hasHighlights = (editor: any): boolean => {
  const state = getHighlightState(editor);
  return state ? state.highlights.length > 0 : false;
};