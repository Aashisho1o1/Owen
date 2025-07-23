/**
 * Character Voice Consistency API Service - Complete Implementation
 *
 * This service provides comprehensive character voice analysis including:
 * - Voice consistency analysis with debouncing
 * - Character profile management
 * - Dialogue detection and extraction
 * - Real-time feedback and suggestions
 */

import apiClient from './client';

// Types for character voice consistency
export interface VoiceConsistencyRequest {
  text: string;
}

export interface VoiceConsistencyResult {
  is_consistent: boolean;
  confidence_score: number;
  character_name: string;
  flagged_text: string;
  explanation: string;
  suggestions: string[];
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
  dialogue_samples: string[];
  voice_traits: Record<string, any>;
  last_updated: string;
  sample_count: number;
}

export interface CharacterVoiceProfilesResponse {
  profiles: CharacterVoiceProfile[];
}

// Debouncing for real-time analysis
let analysisTimeout: NodeJS.Timeout | null = null;

/**
 * Check if text contains dialogue worth analyzing
 */
export const hasDialogue = (text: string): boolean => {
  // IMPROVED: More inclusive dialogue detection patterns that match backend
  const dialoguePatterns = [
    /"[^"]{2,}"/g,                    // Basic quoted dialogue (matches backend)
    /'[^']{2,}'/g,                    // Single quoted dialogue  
    /—[^—\n]{2,}/g,                   // Em-dash dialogue
    /"[^"]{2,},"?\s*[a-zA-Z]/g,       // Dialogue with attribution
    /[A-Z][^.!?]*\s*"[^"]{2,}"/g      // Speaker tag dialogue
  ];
  
  // Return true if any pattern matches
  return dialoguePatterns.some(pattern => {
    const matches = text.match(pattern);
    return matches && matches.length > 0;
  });
};

/**
 * Analyze text for character voice consistency with immediate response.
 */
export const analyzeVoiceConsistency = async (
  text: string
): Promise<VoiceConsistencyResponse> => {
  try {
    // Validate input
    if (!text || text.trim().length < 10) {
      throw new Error("Text must be at least 10 characters long");
    }

    // Check if text contains dialogue
    if (!hasDialogue(text)) {
      return {
        results: [],
        characters_analyzed: 0,
        dialogue_segments_found: 0,
        processing_time_ms: 0
      };
    }

    console.log("🎭 Starting voice consistency analysis...");
    
    // DEBUG: Log detailed request information
    console.log("📊 Voice Analysis Request Details:", {
      textLength: text.length,
      textPreview: text.substring(0, 200) + (text.length > 200 ? '...' : ''),
      hasHTML: text.includes('<') && text.includes('>'),
      dialogueFound: hasDialogue(text),
      timestamp: new Date().toISOString()
    });
    
    const requestData: VoiceConsistencyRequest = { text };
    
    // DEBUG: Log the exact payload being sent
    console.log("📤 Sending voice analysis request:", {
      payload: requestData,
      payloadSize: JSON.stringify(requestData).length,
      endpoint: '/api/character-voice/analyze'
    });
    
    const response = await apiClient.post<VoiceConsistencyResponse>(
      '/api/character-voice/analyze',
      requestData
    );
    
    // DEBUG: Log successful response details
    console.log("📥 Voice analysis response received:", {
      status: response.status,
      statusText: response.statusText,
      dataKeys: Object.keys(response.data),
      charactersAnalyzed: response.data.characters_analyzed,
      dialogueSegments: response.data.dialogue_segments_found,
      resultsCount: response.data.results.length,
      processingTime: response.data.processing_time_ms
    });
    
    // DEBUG: Log each result for detailed inspection
    if (response.data.results.length > 0) {
      console.log("🎯 Voice analysis results breakdown:");
      response.data.results.forEach((result, index) => {
        console.log(`  Result ${index + 1}:`, {
          character: result.character_name,
          isConsistent: result.is_consistent,
          confidence: result.confidence_score,
          flaggedTextPreview: result.flagged_text.substring(0, 50) + '...',
          explanation: result.explanation
        });
      });
    }
    
    console.log(`✅ Voice analysis completed: ${response.data.characters_analyzed} characters analyzed`);
    return response.data;
  } catch (error) {
    // DEBUG: Enhanced error logging with full details
    console.error("❌ Voice analysis failed with detailed error info:");
    console.error("🔍 Error Type:", error.constructor.name);
    console.error("🔍 Error Message:", error.message);
    
    if (error.response) {
      console.error("🔍 Response Status:", error.response.status);
      console.error("🔍 Response Status Text:", error.response.statusText);
      console.error("🔍 Response Headers:", error.response.headers);
      console.error("🔍 Response Data:", error.response.data);
      
      // Try to extract more specific error information
      if (error.response.data) {
        console.error("🔍 Backend Error Details:", {
          detail: error.response.data.detail,
          error: error.response.data.error,
          message: error.response.data.message,
          traceback: error.response.data.traceback,
          timestamp: error.response.data.timestamp
        });
      }
    } else if (error.request) {
      console.error("🔍 Request Error (no response received):", error.request);
    } else {
      console.error("🔍 Setup Error:", error.message);
    }
    
    console.error("🔍 Full Error Object:", error);
    throw error;
  }
};

/**
 * Analyze text for character voice consistency with debouncing for real-time analysis.
 */
export const analyzeVoiceConsistencyDebounced = (
  text: string,
  callback: (results: VoiceConsistencyResponse) => void,
  delay: number = 2000
): void => {
  // Clear existing timeout
  if (analysisTimeout) {
    clearTimeout(analysisTimeout);
  }

  // Set new timeout
  analysisTimeout = setTimeout(async () => {
    try {
      // Only analyze if text has sufficient content and dialogue
      if (text.trim().length < 50 || !hasDialogue(text)) {
        callback({
          results: [],
          characters_analyzed: 0,
          dialogue_segments_found: 0,
          processing_time_ms: 0
        });
        return;
      }

      const results = await analyzeVoiceConsistency(text);
      callback(results);
    } catch (error) {
      console.error("❌ Debounced voice analysis failed:", error);
      callback({
        results: [],
        characters_analyzed: 0,
        dialogue_segments_found: 0,
        processing_time_ms: 0
      });
    }
  }, delay);
};

/**
 * Get all character profiles for the current user.
 */
export const getCharacterProfiles = async (): Promise<CharacterVoiceProfilesResponse> => {
  try {
    console.log("📚 Fetching character profiles...");
    
    const response = await apiClient.get<CharacterVoiceProfilesResponse>(
      '/api/character-voice/profiles'
    );
    
    console.log(`✅ Retrieved ${response.data.profiles.length} character profiles`);
    return response.data;
  } catch (error) {
    console.error("❌ Failed to fetch character profiles:", error);
    throw error;
  }
};

/**
 * Update a character profile with new dialogue samples or traits.
 */
export const updateCharacterProfile = async (
  characterName: string,
  profileData: {
    dialogue_samples?: string[];
    voice_traits?: Record<string, any>;
  }
): Promise<{ success: boolean; message: string }> => {
  try {
    console.log(`📝 Updating character profile: ${characterName}`);
    
    const response = await apiClient.post<{ success: boolean; message: string }>(
      `/api/character-voice/profiles/${encodeURIComponent(characterName)}/update`,
      profileData
    );
    
    console.log(`✅ Updated character profile: ${characterName}`);
    return response.data;
  } catch (error) {
    console.error(`❌ Failed to update character profile ${characterName}:`, error);
    throw error;
  }
};

/**
 * Delete a character profile.
 */
export const deleteCharacterProfile = async (
  characterName: string
): Promise<{ success: boolean; message: string }> => {
  try {
    console.log(`🗑️ Deleting character profile: ${characterName}`);
    
    const response = await apiClient.delete<{ success: boolean; message: string }>(
      `/api/character-voice/profiles/${encodeURIComponent(characterName)}`
    );
    
    console.log(`✅ Deleted character profile: ${characterName}`);
    return response.data;
  } catch (error) {
    console.error(`❌ Failed to delete character profile ${characterName}:`, error);
    throw error;
  }
};

/**
 * Check the health of the character voice service.
 */
export const checkCharacterVoiceHealth = async (): Promise<{
  status: string;
  services: Record<string, string>;
  timestamp: string;
}> => {
  try {
    const response = await apiClient.get('/api/character-voice/health');
    return response.data;
  } catch (error) {
    console.error("❌ Character voice health check failed:", error);
    throw error;
  }
};

/**
 * Cancel any pending debounced analysis.
 */
export const cancelPendingAnalysis = (): void => {
  if (analysisTimeout) {
    clearTimeout(analysisTimeout);
    analysisTimeout = null;
  }
}; 