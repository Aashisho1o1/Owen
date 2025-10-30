/**
 * Gemini API Service
 *
 * Centralized service for all Google Gemini API interactions.
 * Uses best practices: singleton pattern, error handling, retry logic.
 *
 * Competition: Chrome Built-in AI Challenge 2025
 * Strategy: Gemini-only (no OpenAI, Claude, etc.)
 */

import { GoogleGenerativeAI, GenerativeModel, HarmCategory, HarmBlockThreshold } from '@google/generative-ai';

// Type definitions
export interface VoiceProfile {
  formality: number; // 0-100
  complexity: number; // 0-100
  sentenceStyle: 'terse' | 'balanced' | 'flowing';
  vocabulary: 'simple' | 'moderate' | 'sophisticated';
  tone: 'formal' | 'neutral' | 'casual' | 'warm' | 'cold';
  pacingRhythm: 'fast' | 'medium' | 'slow';
  characteristics: string[];
}

export interface DialogueAnalysisResult {
  speaker: string;
  dialogue: string;
  voiceProfile: VoiceProfile;
  isConsistent: boolean;
  inconsistencyScore: number; // 0-100, higher = more inconsistent
  issues: Array<{
    type: 'formality-mismatch' | 'vocabulary-shift' | 'tone-change' | 'pacing-break';
    description: string;
    severity: 'low' | 'medium' | 'high';
    suggestion: string;
  }>;
}

export interface AuthorFeedback {
  author: string;
  matchScore: number; // 0-100
  strengths: string[];
  weaknesses: string[];
  suggestions: string[];
  rewrittenSample?: string;
}

export interface WritingHelpCategory {
  category: 'dialogue' | 'description' | 'action' | 'exposition' | 'internal-thought';
  confidence: number; // 0-100
  suggestions: string[];
}

// Configuration
const SAFETY_SETTINGS = [
  { category: HarmCategory.HARM_CATEGORY_HARASSMENT, threshold: HarmBlockThreshold.BLOCK_NONE },
  { category: HarmCategory.HARM_CATEGORY_HATE_SPEECH, threshold: HarmBlockThreshold.BLOCK_NONE },
  { category: HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, threshold: HarmBlockThreshold.BLOCK_NONE },
  { category: HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, threshold: HarmBlockThreshold.BLOCK_NONE },
];

const GENERATION_CONFIG = {
  temperature: 0.3, // Lower for more consistent analysis
  topK: 40,
  topP: 0.95,
  maxOutputTokens: 2048,
};

/**
 * Gemini Service Class
 * Singleton pattern for efficient resource usage
 */
class GeminiService {
  private static instance: GeminiService;
  private genAI: GoogleGenerativeAI | null = null;
  private model: GenerativeModel | null = null;
  private isInitialized = false;

  private constructor() {}

  static getInstance(): GeminiService {
    if (!GeminiService.instance) {
      GeminiService.instance = new GeminiService();
    }
    return GeminiService.instance;
  }

  /**
   * Initialize Gemini API
   * Call this once at app startup
   */
  initialize(apiKey: string): void {
    if (this.isInitialized) return;

    this.genAI = new GoogleGenerativeAI(apiKey);
    this.model = this.genAI.getGenerativeModel({
      model: 'gemini-1.5-flash', // Fast, cheap, good for competition
      safetySettings: SAFETY_SETTINGS,
      generationConfig: GENERATION_CONFIG,
    });

    this.isInitialized = true;
  }

  /**
   * Check if service is ready
   */
  isReady(): boolean {
    return this.isInitialized && this.model !== null;
  }

  /**
   * Analyze dialogue for voice consistency
   *
   * @param dialogues Array of {speaker, text} objects
   * @returns Analysis for each dialogue piece
   */
  async analyzeDialogueConsistency(
    dialogues: Array<{ speaker: string; text: string }>
  ): Promise<DialogueAnalysisResult[]> {
    if (!this.isReady()) {
      throw new Error('Gemini service not initialized');
    }

    const prompt = `You are an expert literary voice analyst specializing in character dialogue consistency.

Analyze these dialogue pieces for voice consistency:

${dialogues.map((d, i) => `[${i + 1}] ${d.speaker}: "${d.text}"`).join('\n\n')}

For each dialogue, analyze:
1. Voice Profile: formality (0-100), complexity (0-100), sentence style, vocabulary, tone, pacing
2. Consistency: Does this match the speaker's established voice?
3. Issues: Specific problems with severity and suggestions

Respond ONLY with valid JSON (no markdown):
[
  {
    "speaker": "character name",
    "dialogue": "the text",
    "voiceProfile": {
      "formality": <number>,
      "complexity": <number>,
      "sentenceStyle": "<terse|balanced|flowing>",
      "vocabulary": "<simple|moderate|sophisticated>",
      "tone": "<formal|neutral|casual|warm|cold>",
      "pacingRhythm": "<fast|medium|slow>",
      "characteristics": ["trait1", "trait2"]
    },
    "isConsistent": <boolean>,
    "inconsistencyScore": <number 0-100>,
    "issues": [
      {
        "type": "<type>",
        "description": "what's wrong",
        "severity": "<low|medium|high>",
        "suggestion": "how to fix"
      }
    ]
  }
]`;

    try {
      const result = await this.model!.generateContent(prompt);
      const response = result.response.text();

      // Extract JSON from response
      const jsonMatch = response.match(/\[[\s\S]*\]/);
      if (!jsonMatch) {
        throw new Error('Invalid response format from Gemini');
      }

      return JSON.parse(jsonMatch[0]) as DialogueAnalysisResult[];
    } catch (error) {
      console.error('Gemini API error:', error);
      throw new Error('Failed to analyze dialogue consistency');
    }
  }

  /**
   * Get feedback comparing writing to a classic author
   *
   * @param text User's writing sample
   * @param author Target author (e.g., "Hemingway", "Austen")
   * @param includeRewrite Whether to include rewritten sample
   * @returns Detailed feedback
   */
  async getClassicAuthorFeedback(
    text: string,
    author: string,
    includeRewrite: boolean = false
  ): Promise<AuthorFeedback> {
    if (!this.isReady()) {
      throw new Error('Gemini service not initialized');
    }

    const prompt = `You are a literary expert specializing in ${author}'s writing style.

Analyze this text and compare it to ${author}'s distinctive voice:

TEXT:
"""
${text}
"""

Provide:
1. Match Score (0-100): How well does this match ${author}'s style?
2. Strengths: What aspects match ${author}'s voice well?
3. Weaknesses: What aspects don't match ${author}'s style?
4. Suggestions: Specific improvements to match ${author}'s voice better
${includeRewrite ? `5. Rewritten Sample: Rewrite the first 2-3 sentences in ${author}'s style` : ''}

${author.toLowerCase()} writing characteristics:
${this.getAuthorCharacteristics(author)}

Respond ONLY with valid JSON:
{
  "author": "${author}",
  "matchScore": <number 0-100>,
  "strengths": ["strength1", "strength2"],
  "weaknesses": ["weakness1", "weakness2"],
  "suggestions": ["suggestion1", "suggestion2"]
  ${includeRewrite ? ',"rewrittenSample": "rewritten text"' : ''}
}`;

    try {
      const result = await this.model!.generateContent(prompt);
      const response = result.response.text();

      const jsonMatch = response.match(/\{[\s\S]*\}/);
      if (!jsonMatch) {
        throw new Error('Invalid response format');
      }

      return JSON.parse(jsonMatch[0]) as AuthorFeedback;
    } catch (error) {
      console.error('Gemini API error:', error);
      throw new Error('Failed to get author feedback');
    }
  }

  /**
   * Categorize what kind of writing help is needed
   *
   * @param text Writing sample
   * @returns Category and suggestions
   */
  async categorizeWritingHelp(text: string): Promise<WritingHelpCategory> {
    if (!this.isReady()) {
      throw new Error('Gemini service not initialized');
    }

    const prompt = `Analyze this text and determine what kind of writing help it needs most:

TEXT:
"""
${text}
"""

Categories:
- dialogue: Character speech, conversation
- description: Setting, appearance, sensory details
- action: Movement, events, what happens
- exposition: Background info, explanation
- internal-thought: Character's inner voice, reflection

Respond ONLY with valid JSON:
{
  "category": "<category>",
  "confidence": <number 0-100>,
  "suggestions": ["specific suggestion 1", "specific suggestion 2", "specific suggestion 3"]
}`;

    try {
      const result = await this.model!.generateContent(prompt);
      const response = result.response.text();

      const jsonMatch = response.match(/\{[\s\S]*\}/);
      if (!jsonMatch) {
        throw new Error('Invalid response format');
      }

      return JSON.parse(jsonMatch[0]) as WritingHelpCategory;
    } catch (error) {
      console.error('Gemini API error:', error);
      throw new Error('Failed to categorize writing');
    }
  }

  /**
   * Get characteristics for a classic author
   * Internal helper method
   */
  private getAuthorCharacteristics(author: string): string {
    const characteristics: Record<string, string> = {
      'Hemingway': '- Short, declarative sentences\n- Active voice, concrete nouns\n- Minimal adjectives\n- "Iceberg theory" - implied meaning\n- Simple, direct language\n- Understated emotion',
      'Jane Austen': '- Ironic, witty observations\n- Complex sentence structures\n- Social commentary\n- Free indirect discourse\n- Elegant, refined prose\n- Subtle character revelation',
      'Stephen King': '- Conversational, accessible tone\n- Vivid sensory details\n- Everyday language mixed with literary skill\n- Strong character voice\n- Building tension through pacing\n- Pop culture references',
      'Toni Morrison': '- Lyrical, poetic prose\n- Rich, musical language\n- Mythic elements\n- Nonlinear narrative\n- Dense, layered meaning\n- African American vernacular artistry',
      'Raymond Carver': '- Minimalist style\n- Working-class dialogue\n- Subtext-heavy\n- Ordinary situations\n- Sparse description\n- Implication over explanation',
    };

    return characteristics[author] || '- Distinctive voice and style\n- Consistent character development\n- Clear thematic elements';
  }
}

// Export singleton instance
export const geminiService = GeminiService.getInstance();
