/**
 * Character Voice Consistency API Service - Gemini Edition
 * 
 * Frontend service for character voice consistency detection using Gemini 1.5 Flash.
 * Integrates with the existing API client for authentication and error handling.
 * 
 * Gemini provides reliable character voice analysis through:
 * - Natural language understanding for voice patterns
 * - Cost-effective analysis using Gemini 1.5 Flash
 * - Simple deployment with no complex ML dependencies
 * - Fast and accurate character voice consistency detection
 */

import apiClient from './client';

// Types for character voice consistency
export interface VoiceConsistencyRequest {
  text: string;
  document_id?: string;
}

export interface VoiceConsistencyResult {
  is_consistent: boolean;
  confidence_score: number;
  similarity_score: number;
  character_name: string;
  flagged_text: string;
  explanation: string;
  suggestions: string[];
  analysis_method: string; // 'gemini_voice_analysis'
}

export interface VoiceConsistencyResponse {
  results: VoiceConsistencyResult[];
  characters_analyzed: number;
  dialogue_segments_found: number;
  processing_time_ms: number;
}

export interface CharacterVoiceProfile {
  character_id: string;
  character_name: string;
  sample_count: number;
  last_updated: string;
  voice_characteristics: Record<string, any>;
}

export interface CharacterVoiceProfilesResponse {
  profiles: CharacterVoiceProfile[];
  total_characters: number;
}

export interface VoiceAnalysisStats {
  user_id: number;
  total_characters: number;
  total_dialogue_samples: number;
  average_samples_per_character: number;
  service_status: string;
  cache_size: number;
  analysis_config: Record<string, any>;
  characters: Array<{
    name: string;
    sample_count: number;
    last_updated: string;
  }>;
}

/**
 * Analyze text for character voice consistency using TinyStyler
 */
export const analyzeVoiceConsistency = async (
  request: VoiceConsistencyRequest
): Promise<VoiceConsistencyResponse> => {
  const response = await apiClient.post('/api/character-voice/analyze', request);
  return response.data;
};

/**
 * Get all character voice profiles for the current user
 */
export const getCharacterProfiles = async (): Promise<CharacterVoiceProfilesResponse> => {
  const response = await apiClient.get('/api/character-voice/profiles');
  return response.data;
};

/**
 * Delete a character voice profile
 */
export const deleteCharacterProfile = async (characterName: string): Promise<void> => {
  await apiClient.delete(`/api/character-voice/profiles/${encodeURIComponent(characterName)}`);
};

/**
 * Reset all character voice profiles
 */
export const resetAllCharacterProfiles = async (): Promise<{ profiles_deleted: number }> => {
  const response = await apiClient.post('/api/character-voice/profiles/reset');
  return response.data;
};

/**
 * Get voice analysis statistics
 */
export const getVoiceAnalysisStats = async (): Promise<VoiceAnalysisStats> => {
  const response = await apiClient.get('/api/character-voice/stats');
  return response.data;
};

/**
 * Check character voice service health
 */
export const checkVoiceServiceHealth = async (): Promise<{
  service: string;
  status: string;
  timestamp: number;
  details: Record<string, any>;
}> => {
  const response = await apiClient.get('/api/character-voice/health');
  return response.data;
};

/**
 * Format voice consistency feedback for display
 * Enhanced for TinyStyler analysis results
 */
export const formatVoiceConsistencyFeedback = (
  results: VoiceConsistencyResult[]
): string => {
  if (!results || results.length === 0) {
    return '';
  }

  const inconsistentResults = results.filter(r => !r.is_consistent);
  
  if (inconsistentResults.length === 0) {
    return '✅ All character voices are consistent with their established patterns.';
  }

  let feedback = `🎭 **Voice Consistency Analysis (Gemini):**\n\n`;
  
  inconsistentResults.forEach((result, index) => {
    feedback += `**${result.character_name}** (${(result.confidence_score * 100).toFixed(1)}% confidence):\n`;
    feedback += `• ${result.explanation}\n`;
    
    if (result.suggestions && result.suggestions.length > 0) {
      feedback += `• Suggestion: ${result.suggestions[0]}\n`;
    }
    
    // Show analysis method for transparency
    const methodLabel = result.analysis_method === 'gemini_voice_analysis' 
      ? 'Gemini Voice Analysis' 
      : 'Character Voice Analysis';
    feedback += `• Method: ${methodLabel}\n`;
    
    if (index < inconsistentResults.length - 1) {
      feedback += '\n';
    }
  });

  return feedback;
};

// Utility: strip HTML tags and decode basic HTML entities
const htmlToPlain = (html: string): string => {
  if (!html) return '';
  
  // Remove tags and replace with spaces to maintain word boundaries
  let text = html.replace(/<[^>]*>/g, ' ');
  
  // Decode common HTML entities (expanded list)
  const entities: Record<string, string> = {
    '&quot;': '"',
    '&#39;': "'",
    '&#x27;': "'",
    '&apos;': "'",
    '&amp;': '&',
    '&lt;': '<',
    '&gt;': '>',
    '&nbsp;': ' ',
    '&#160;': ' ',
    '&mdash;': '—',
    '&ndash;': '–',
    '&ldquo;': '"',
    '&rdquo;': '"',
    '&lsquo;': "'",
    '&rsquo;': "'",
    '&#8220;': '"',
    '&#8221;': '"',
    '&#8216;': "'",
    '&#8217;': "'",
    '&#8211;': '–',
    '&#8212;': '—'
  };
  
  // Decode entities
  Object.entries(entities).forEach(([entity, char]) => {
    text = text.split(entity).join(char);
  });
  
  // Normalize whitespace
  text = text.replace(/\s+/g, ' ').trim();
  
  console.log('🔧 htmlToPlain conversion:', {
    originalLength: html.length,
    processedLength: text.length,
    hasQuotes: /["""''']/.test(text),
    originalPreview: html.substring(0, 100) + '...',
    processedPreview: text.substring(0, 100) + '...'
  });
  
  return text;
};

/**
 * Check if text contains dialogue worth analyzing
 * Now robust to HTML input from TipTap (strips tags & decodes entities)
 * Enhanced with better debugging and more flexible patterns
 */
export const hasDialogue = (text: string): boolean => {
  if (!text || text.trim().length === 0) {
    console.log('🔍 hasDialogue: No text provided');
    return false;
  }

  // Work with plain text
  const plain = htmlToPlain(text);
  console.log('🔍 hasDialogue: Processing text:', {
    originalLength: text.length,
    plainLength: plain.length,
    plainPreview: plain.substring(0, 200) + '...'
  });

  // Enhanced dialogue detection patterns - more flexible
  const dialoguePatterns = [
    // Basic quoted speech (reduced minimum to 3 chars)
    /"[^"\n]{3,}?"/g,
    /'[^'\n]{3,}?'/g,
    
    // Dialogue with attribution (more flexible)
    /["""][^"""]{3,}?["""][^.!?]*(?:said|asked|replied|whispered|shouted|murmured|declared|exclaimed|stated|mentioned|noted|observed|remarked|responded|answered|continued|added|interrupted|began|concluded|insisted|suggested|wondered|demanded|pleaded|begged|cried|laughed|sighed|muttered|growled|hissed|snapped|barked|roared|screamed|yelled|called|announced|proclaimed|revealed|admitted|confessed|explained|described|told|informed|warned|advised|reminded|promised|threatened|accused|blamed|criticized|praised|complimented|thanked|apologized|complained|protested|argued|debated|discussed|chatted|gossiped|joked|teased|flirted|comforted|consoled|encouraged|supported|agreed|disagreed|confirmed|denied|corrected|clarified|emphasized|stressed|repeated|echoed|quoted|paraphrased|summarized)/gi,
    
    // Attribution before dialogue
    /\b[A-Z][a-z]+\s+(?:said|asked|replied|whispered|shouted|murmured|declared|exclaimed|stated|mentioned|noted|observed|remarked|responded|answered|continued|added|interrupted|began|concluded|insisted|suggested|wondered|demanded|pleaded|begged|cried|laughed|sighed|muttered|growled|hissed|snapped|barked|roared|screamed|yelled|called|announced|proclaimed|revealed|admitted|confessed|explained|described|told|informed|warned|advised|reminded|promised|threatened|accused|blamed|criticized|praised|complimented|thanked|apologized|complained|protested|argued|debated|discussed|chatted|gossiped|joked|teased|flirted|comforted|consoled|encouraged|supported|agreed|disagreed|confirmed|denied|corrected|clarified|emphasized|stressed|repeated|echoed|quoted|paraphrased|summarized)[^.!?]*["""][^"""]{3,}?["""]/gi,
    
    // Simple dialogue patterns without attribution
    /^\s*["""][^"""]{3,}?["""]$/gm,
    /^\s*"[^"]{3,}?"$/gm,
    /^\s*'[^']{3,}?'$/gm,
    
    // Dialogue in the middle of paragraphs
    /\.\s*["""][^"""]{3,}?["""][\s,]/g,
    /\.\s*"[^"]{3,}?"[\s,]/g,
    /\.\s*'[^']{3,}?'[\s,]/g,
    
    // Dialogue with em-dashes (common in literature)
    /—\s*[A-Z][^—]{3,}?[.!?]?\s*—/g,
    /—[^—]{3,}?—/g
  ];

  // Test each pattern and log results
  for (let i = 0; i < dialoguePatterns.length; i++) {
    const pattern = dialoguePatterns[i];
    const matches = plain.match(pattern);
    
    if (matches && matches.length > 0) {
      console.log(`✅ hasDialogue: Pattern ${i + 1} matched:`, {
        pattern: pattern.toString(),
        matches: matches.slice(0, 3), // Show first 3 matches
        totalMatches: matches.length
      });
      return true;
    } else {
      console.log(`❌ hasDialogue: Pattern ${i + 1} no match:`, {
        pattern: pattern.toString()
      });
    }
  }

  // Additional check: look for any quotation marks with reasonable content
  const basicQuoteCheck = /["""''"][^"""''']{3,}?["""'']/g;
  const basicMatches = plain.match(basicQuoteCheck);
  if (basicMatches && basicMatches.length > 0) {
    console.log('✅ hasDialogue: Basic quote check passed:', {
      matches: basicMatches.slice(0, 3),
      totalMatches: basicMatches.length
    });
    return true;
  }

  console.log('❌ hasDialogue: No dialogue patterns found');
  return false;
};

// Debounced voice consistency analysis
let debounceTimer: NodeJS.Timeout | null = null;

/**
 * Analyze voice consistency with debouncing for real-time analysis
 * Optimized for Gemini's processing characteristics
 */
export const analyzeVoiceConsistencyDebounced = (
  text: string,
  callback: (results: VoiceConsistencyResult[]) => void,
  delay: number = 1500 // Shorter delay for Gemini processing
): void => {
  console.log('🔄 Voice analysis debounced called:', { textLength: text.length });
  if (debounceTimer) {
    clearTimeout(debounceTimer);
  }

  debounceTimer = setTimeout(async () => {
    try {
      const response = await apiClient.post<VoiceConsistencyResponse>('/api/character-voice/analyze', {
        text,
        document_id: undefined
      });
      
      console.log('✅ Voice analysis response:', response.data);
      callback(response.data.results);
    } catch (error) {
      console.error('❌ Voice analysis error:', error);
      callback([]);
    }
  }, delay);
};

/**
 * Get voice consistency status summary
 * Optimized for Gemini analysis results
 */
export const getVoiceConsistencyStatus = (
  results: VoiceConsistencyResult[]
): {
  status: 'good' | 'warning' | 'error';
  message: string;
  count: number;
} => {
  if (!results || results.length === 0) {
    return {
      status: 'good',
      message: 'No dialogue detected for analysis',
      count: 0
    };
  }

  const inconsistentResults = results.filter(r => !r.is_consistent);
  const totalCharacters = new Set(results.map(r => r.character_name)).size;
  
  if (inconsistentResults.length === 0) {
    return {
      status: 'good',
      message: `All ${totalCharacters} character(s) have consistent voices`,
      count: 0
    };
  }

  const inconsistentCharacters = new Set(inconsistentResults.map(r => r.character_name)).size;
  
  if (inconsistentCharacters === 1) {
    return {
      status: 'warning',
      message: `1 character has voice inconsistencies`,
      count: inconsistentResults.length
    };
  }

  return {
    status: 'error',
    message: `${inconsistentCharacters} characters have voice inconsistencies`,
    count: inconsistentResults.length
  };
}; 