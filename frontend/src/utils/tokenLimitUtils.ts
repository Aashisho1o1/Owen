/**
 * Token Limit Utilities
 * Handles intelligent content truncation for AI chat to prevent 400 "Input too long" errors
 * while preserving highlighted text and surrounding context.
 */

interface TruncationOptions {
  maxTotalLength: number;
  highlightedText?: string;
  contextWindow: number; // Characters to keep around highlighted text
  preserveStructure: boolean; // Try to preserve paragraph boundaries
}

interface TruncationResult {
  truncatedContent: string;
  wasTruncated: boolean;
  originalLength: number;
  truncatedLength: number;
  highlightPreserved: boolean;
}

/**
 * Intelligently truncate editor content while preserving highlighted text and context
 */
export function truncateEditorContent(
  editorContent: string,
  message: string,
  options: Partial<TruncationOptions> = {}
): TruncationResult {
  const {
    maxTotalLength = 12000, // Conservative limit (15000 - buffer for other data)
    highlightedText,
    contextWindow = 2000, // 2000 chars around highlighted text
    preserveStructure = true
  } = options;

  const messageLength = message.length;
  const availableContentLength = maxTotalLength - messageLength - 500; // Buffer for other fields

  // If content is already within limits, return as-is
  if (editorContent.length <= availableContentLength) {
    return {
      truncatedContent: editorContent,
      wasTruncated: false,
      originalLength: editorContent.length,
      truncatedLength: editorContent.length,
      highlightPreserved: true
    };
  }

  // If no highlighted text, truncate from the beginning
  if (!highlightedText || !highlightedText.trim()) {
    const truncated = editorContent.substring(0, availableContentLength);
    return {
      truncatedContent: truncated + (truncated.length < editorContent.length ? "\n\n[Content truncated...]" : ""),
      wasTruncated: true,
      originalLength: editorContent.length,
      truncatedLength: truncated.length,
      highlightPreserved: false
    };
  }

  // Find the highlighted text in the editor content
  const highlightIndex = editorContent.indexOf(highlightedText);
  
  if (highlightIndex === -1) {
    // Highlighted text not found, fallback to beginning truncation
    const truncated = editorContent.substring(0, availableContentLength);
    return {
      truncatedContent: truncated + (truncated.length < editorContent.length ? "\n\n[Content truncated...]" : ""),
      wasTruncated: true,
      originalLength: editorContent.length,
      truncatedLength: truncated.length,
      highlightPreserved: false
    };
  }

  // Calculate context window around highlighted text
  const contextStart = Math.max(0, highlightIndex - contextWindow);
  const contextEnd = Math.min(editorContent.length, highlightIndex + highlightedText.length + contextWindow);
  
  let contextContent = editorContent.substring(contextStart, contextEnd);
  
  // If context is still too long, prioritize highlighted text
  if (contextContent.length > availableContentLength) {
    const halfAvailable = Math.floor((availableContentLength - highlightedText.length) / 2);
    const beforeHighlight = editorContent.substring(
      Math.max(0, highlightIndex - halfAvailable),
      highlightIndex
    );
    const afterHighlight = editorContent.substring(
      highlightIndex + highlightedText.length,
      Math.min(editorContent.length, highlightIndex + highlightedText.length + halfAvailable)
    );
    
    contextContent = beforeHighlight + highlightedText + afterHighlight;
  }

  // Add truncation indicators
  let truncatedContent = contextContent;
  if (contextStart > 0) {
    truncatedContent = "[...content before...]\n\n" + truncatedContent;
  }
  if (contextEnd < editorContent.length) {
    truncatedContent = truncatedContent + "\n\n[...content after...]";
  }

  // Try to preserve paragraph structure if requested
  if (preserveStructure && truncatedContent.length > availableContentLength) {
    truncatedContent = preserveParagraphStructure(truncatedContent, availableContentLength);
  }

  return {
    truncatedContent,
    wasTruncated: true,
    originalLength: editorContent.length,
    truncatedLength: truncatedContent.length,
    highlightPreserved: true
  };
}

/**
 * Preserve paragraph structure when truncating
 */
function preserveParagraphStructure(content: string, maxLength: number): string {
  if (content.length <= maxLength) return content;

  const paragraphs = content.split('\n\n');
  let result = '';
  
  for (const paragraph of paragraphs) {
    if ((result + paragraph).length <= maxLength - 50) { // Leave room for truncation indicator
      result += (result ? '\n\n' : '') + paragraph;
    } else {
      break;
    }
  }
  
  return result + '\n\n[...content truncated...]';
}

/**
 * Estimate token count (rough approximation: 1 token ≈ 4 characters)
 */
export function estimateTokenCount(text: string): number {
  return Math.ceil(text.length / 4);
}

/**
 * Check if content would exceed token limits
 */
export function wouldExceedTokenLimit(
  message: string,
  editorContent: string,
  maxTokens: number = 3000
): boolean {
  const totalChars = message.length + editorContent.length;
  const estimatedTokens = estimateTokenCount(totalChars);
  return estimatedTokens > maxTokens;
}

/**
 * Create user-friendly error message for token limit issues
 */
export function createTokenLimitErrorMessage(
  originalLength: number,
  truncatedLength: number,
  highlightPreserved: boolean
): string {
  const savedChars = originalLength - truncatedLength;
  const savedPercentage = Math.round((savedChars / originalLength) * 100);
  
  let message = `📝 Your document was automatically shortened for AI processing (${savedPercentage}% reduction). `;
  
  if (highlightPreserved) {
    message += "Your highlighted text and surrounding context were preserved. ";
  } else {
    message += "The beginning of your document was used. ";
  }
  
  message += "For full document analysis, consider breaking it into smaller sections.";
  
  return message;
} 