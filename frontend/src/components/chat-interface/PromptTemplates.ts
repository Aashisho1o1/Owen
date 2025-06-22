// Question templates for each focus area
export const QUESTION_TEMPLATES = {
  "Dialogue Writing": [
    "How would {author} improve this dialogue?",
    "What makes dialogue sound authentic and natural?",
    "How can I develop distinct character voices?",
    "What dialogue techniques does {author} use?"
  ],
  "Scene Description": [
    "How would {author} enhance this scene?",
    "What sensory details would strengthen this setting?",
    "How can I create more vivid imagery?",
    "What's {author}'s approach to setting description?"
  ],
  "Plot Development": [
    "How would {author} develop this plot point?",
    "What narrative techniques would strengthen this section?",
    "How can I build more tension here?",
    "What's missing from this story development?"
  ],
  "Character Introduction": [
    "How would {author} introduce this character?",
    "What character details would make this more compelling?",
    "How can I establish this character's voice more distinctly?",
    "What character development techniques should I use?"
  ],
  "Overall Tone": [
    "How would {author} adjust the tone here?",
    "What stylistic changes would improve consistency?",
    "How can I modify the mood of this section?",
    "What tone should I aim for in this piece?"
  ]
};

export const CONTEXTUAL_PROMPTS = [
  "Analyze this text in the style of {author}",
  "How would {author} rewrite this passage?",
  "What specific improvements would you make to this text?",
  "Critique this writing focusing on {focus}",
  "What writing techniques are used here and how can they be improved?"
];

/**
 * Generate suggested questions based on help focus and author persona
 */
export const generateSuggestedQuestions = (helpFocus: string, authorPersona: string): string[] => {
  const templates = QUESTION_TEMPLATES[helpFocus as keyof typeof QUESTION_TEMPLATES] || QUESTION_TEMPLATES["Overall Tone"];
  return templates.map(template => template.replace('{author}', authorPersona));
};

/**
 * Generate contextual prompts for highlighted text
 */
export const generateContextualPrompts = (authorPersona: string, helpFocus: string): string[] => {
  return CONTEXTUAL_PROMPTS.map(template => 
    template.replace('{author}', authorPersona).replace('{focus}', helpFocus.toLowerCase())
  );
}; 
 