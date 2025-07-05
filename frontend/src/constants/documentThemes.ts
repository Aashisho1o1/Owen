// World-Class Document Themes for Literary Excellence
// Inspired by premium publications like Harry Potter, Lord of the Rings, and other high-quality books

export interface DocumentTheme {
  id: string;
  name: string;
  genre: string;
  description: string;
  
  // Typography inspired by premium publications
  typography: {
    primaryFont: string;    // Main body text (Google Fonts)
    headingFont: string;    // Titles and headers
    accentFont: string;     // Special elements
    fontSize: {
      base: string;         // 16px-18px for readability
      h1: string;           // Large titles
      h2: string;           // Section headers
      h3: string;           // Subsections
    };
    lineHeight: string;     // 1.6-1.8 for premium readability
    letterSpacing: string; // Subtle spacing for elegance
  };
  
  // Color palette reflecting genre emotions
  colors: {
    // Primary theme colors
    background: string;     // Main background
    surface: string;        // Content areas
    primary: string;        // Brand/accent color
    secondary: string;      // Supporting color
    
    // Text hierarchy
    text: {
      primary: string;      // Main text
      secondary: string;    // Subtext
      muted: string;        // Captions
      accent: string;       // Highlights
    };
    
    // UI elements
    border: string;         // Borders and dividers
    shadow: string;         // Drop shadows
    selection: string;      // Text selection
    highlight: string;      // Important highlights
  };
  
  // Visual atmosphere and mood
  atmosphere: {
    backgroundPattern?: string; // Subtle textures
    borderRadius: string;       // Rounded corners
    shadows: {
      subtle: string;           // Light shadows
      medium: string;           // Card shadows
      dramatic: string;         // Modal shadows
    };
  };
  
  // Emotional characteristics for immersion
  mood: {
    energy: 'low' | 'medium' | 'high';
    warmth: 'cool' | 'neutral' | 'warm';
    sophistication: 'casual' | 'elegant' | 'luxury';
    era?: string; // Historical context
  };
}

// World-Class Theme Definitions
export const DOCUMENT_THEMES: Record<string, DocumentTheme> = {
  romance: {
    id: 'romance',
    name: 'Romantic Elegance',
    genre: 'Romance',
    description: 'Warm, inviting, and emotionally rich - inspired by classic romance novels',
    
    typography: {
      primaryFont: 'Crimson Text', // Elegant serif for romantic prose
      headingFont: 'Playfair Display', // Sophisticated display font
      accentFont: 'Dancing Script', // Script for special moments
      fontSize: {
        base: '17px',
        h1: '2.5rem',
        h2: '2rem',
        h3: '1.5rem',
      },
      lineHeight: '1.7',
      letterSpacing: '0.01em',
    },
    
    colors: {
      background: '#fdf8f6', // Warm cream
      surface: '#ffffff',
      primary: '#d63384', // Rose pink
      secondary: '#f8d7da', // Soft blush
      
      text: {
        primary: '#2d1b1e', // Deep burgundy
        secondary: '#6c4a4f', // Muted rose
        muted: '#8b6b70', // Gentle gray-rose
        accent: '#d63384', // Matching primary
      },
      
      border: '#f0d4d7',
      shadow: 'rgba(214, 51, 132, 0.15)',
      selection: '#f8d7da',
      highlight: '#fff2f3',
    },
    
    atmosphere: {
      borderRadius: '12px',
      shadows: {
        subtle: '0 2px 4px rgba(214, 51, 132, 0.08)',
        medium: '0 8px 16px rgba(214, 51, 132, 0.12)',
        dramatic: '0 16px 32px rgba(214, 51, 132, 0.2)',
      },
    },
    
    mood: {
      energy: 'medium',
      warmth: 'warm',
      sophistication: 'elegant',
    },
  },

  fantasy: {
    id: 'fantasy',
    name: 'Epic Mystique',
    genre: 'Fantasy',
    description: 'Rich, mystical, and otherworldly - inspired by epic fantasy sagas',
    
    typography: {
      primaryFont: 'Libre Baskerville', // Classic serif with fantasy feel
      headingFont: 'Cinzel', // Roman-inspired capitals
      accentFont: 'UnifrakturMaguntia', // Medieval script for special elements
      fontSize: {
        base: '16px',
        h1: '2.8rem',
        h2: '2.2rem',
        h3: '1.6rem',
      },
      lineHeight: '1.8',
      letterSpacing: '0.02em',
    },
    
    colors: {
      background: '#0f0e17', // Deep midnight
      surface: '#1a1625',
      primary: '#7209b7', // Royal purple
      secondary: '#2d1b69', // Deep indigo
      
      text: {
        primary: '#fffffe', // Pure white
        secondary: '#a7a9be', // Mystic gray
        muted: '#6c6f85', // Muted lavender
        accent: '#f25f4c', // Dragon fire orange
      },
      
      border: '#2d1b69',
      shadow: 'rgba(114, 9, 183, 0.3)',
      selection: '#7209b7',
      highlight: '#2d1b69',
    },
    
    atmosphere: {
      backgroundPattern: 'radial-gradient(circle at 25% 25%, rgba(114, 9, 183, 0.1) 0%, transparent 50%)',
      borderRadius: '8px',
      shadows: {
        subtle: '0 2px 8px rgba(114, 9, 183, 0.2)',
        medium: '0 8px 24px rgba(114, 9, 183, 0.3)',
        dramatic: '0 16px 40px rgba(114, 9, 183, 0.4)',
      },
    },
    
    mood: {
      energy: 'high',
      warmth: 'cool',
      sophistication: 'luxury',
      era: 'Medieval/Mythical',
    },
  },

  thriller: {
    id: 'thriller',
    name: 'Noir Suspense',
    genre: 'Thriller',
    description: 'Dark, intense, and gripping - inspired by psychological thrillers',
    
    typography: {
      primaryFont: 'Source Sans Pro', // Clean, readable sans-serif
      headingFont: 'Oswald', // Bold, impactful headers
      accentFont: 'Courier Prime', // Typewriter for clues/evidence
      fontSize: {
        base: '16px',
        h1: '2.4rem',
        h2: '1.9rem',
        h3: '1.4rem',
      },
      lineHeight: '1.6',
      letterSpacing: '0.005em',
    },
    
    colors: {
      background: '#0d1117', // GitHub dark
      surface: '#161b22',
      primary: '#f85149', // Danger red
      secondary: '#ffa657', // Warning amber
      
      text: {
        primary: '#f0f6fc', // Near white
        secondary: '#8b949e', // Steel gray
        muted: '#6e7681', // Muted gray
        accent: '#f85149', // Matching primary
      },
      
      border: '#30363d',
      shadow: 'rgba(248, 81, 73, 0.25)',
      selection: '#264f78',
      highlight: '#1f2937',
    },
    
    atmosphere: {
      borderRadius: '4px',
      shadows: {
        subtle: '0 1px 3px rgba(0, 0, 0, 0.5)',
        medium: '0 4px 12px rgba(0, 0, 0, 0.6)',
        dramatic: '0 8px 24px rgba(0, 0, 0, 0.7)',
      },
    },
    
    mood: {
      energy: 'high',
      warmth: 'cool',
      sophistication: 'elegant',
    },
  },

  scifi: {
    id: 'scifi',
    name: 'Cybernetic Future',
    genre: 'Sci-Fi',
    description: 'Sleek, futuristic, and innovative - inspired by cyberpunk aesthetics',
    
    typography: {
      primaryFont: 'Inter', // Modern, tech-forward
      headingFont: 'Orbitron', // Futuristic display
      accentFont: 'Fira Code', // Monospace for tech elements
      fontSize: {
        base: '16px',
        h1: '2.6rem',
        h2: '2rem',
        h3: '1.5rem',
      },
      lineHeight: '1.6',
      letterSpacing: '0.01em',
    },
    
    colors: {
      background: '#0a0e27', // Deep space blue
      surface: '#1a1f3a',
      primary: '#00d9ff', // Cyan blue
      secondary: '#7c3aed', // Electric purple
      
      text: {
        primary: '#e2e8f0', // Light blue-gray
        secondary: '#94a3b8', // Medium gray
        muted: '#64748b', // Muted gray
        accent: '#00d9ff', // Matching primary
      },
      
      border: '#334155',
      shadow: 'rgba(0, 217, 255, 0.2)',
      selection: '#1e293b',
      highlight: '#0f172a',
    },
    
    atmosphere: {
      backgroundPattern: 'linear-gradient(135deg, rgba(0, 217, 255, 0.05) 0%, rgba(124, 58, 237, 0.05) 100%)',
      borderRadius: '6px',
      shadows: {
        subtle: '0 2px 4px rgba(0, 217, 255, 0.1)',
        medium: '0 8px 16px rgba(0, 217, 255, 0.15)',
        dramatic: '0 16px 32px rgba(0, 217, 255, 0.2)',
      },
    },
    
    mood: {
      energy: 'high',
      warmth: 'cool',
      sophistication: 'luxury',
      era: 'Future/Cyberpunk',
    },
  },

  historical: {
    id: 'historical',
    name: 'Classical Heritage',
    genre: 'Historical',
    description: 'Timeless, refined, and scholarly - inspired by period literature',
    
    typography: {
      primaryFont: 'Cormorant Garamond', // Classical serif
      headingFont: 'Spectral', // Elegant display serif
      accentFont: 'EB Garamond', // Traditional book font
      fontSize: {
        base: '17px',
        h1: '2.4rem',
        h2: '1.9rem',
        h3: '1.5rem',
      },
      lineHeight: '1.8',
      letterSpacing: '0.01em',
    },
    
    colors: {
      background: '#faf8f5', // Aged paper
      surface: '#ffffff',
      primary: '#8b4513', // Rich brown
      secondary: '#d2b48c', // Tan
      
      text: {
        primary: '#2c1810', // Dark brown
        secondary: '#5d4e37', // Medium brown
        muted: '#8b7355', // Light brown
        accent: '#8b4513', // Matching primary
      },
      
      border: '#e6ddd4',
      shadow: 'rgba(139, 69, 19, 0.15)',
      selection: '#f5e6d3',
      highlight: '#faf8f5',
    },
    
    atmosphere: {
      borderRadius: '8px',
      shadows: {
        subtle: '0 2px 4px rgba(139, 69, 19, 0.1)',
        medium: '0 6px 12px rgba(139, 69, 19, 0.15)',
        dramatic: '0 12px 24px rgba(139, 69, 19, 0.2)',
      },
    },
    
    mood: {
      energy: 'low',
      warmth: 'warm',
      sophistication: 'luxury',
      era: 'Classical/Victorian',
    },
  },

  comedy: {
    id: 'comedy',
    name: 'Joyful Wit',
    genre: 'Comedy',
    description: 'Bright, playful, and energetic - inspired by comedic literature',
    
    typography: {
      primaryFont: 'Open Sans', // Friendly and approachable
      headingFont: 'Fredoka One', // Playful display
      accentFont: 'Kalam', // Handwritten feel
      fontSize: {
        base: '16px',
        h1: '2.5rem',
        h2: '2rem',
        h3: '1.5rem',
      },
      lineHeight: '1.7',
      letterSpacing: '0.01em',
    },
    
    colors: {
      background: '#fffbf0', // Warm cream
      surface: '#ffffff',
      primary: '#ff6b35', // Vibrant orange
      secondary: '#f7931e', // Golden yellow
      
      text: {
        primary: '#2d3748', // Dark gray
        secondary: '#4a5568', // Medium gray
        muted: '#718096', // Light gray
        accent: '#ff6b35', // Matching primary
      },
      
      border: '#fed7aa',
      shadow: 'rgba(255, 107, 53, 0.2)',
      selection: '#fef3c7',
      highlight: '#fff7ed',
    },
    
    atmosphere: {
      borderRadius: '12px',
      shadows: {
        subtle: '0 2px 6px rgba(255, 107, 53, 0.1)',
        medium: '0 8px 16px rgba(255, 107, 53, 0.15)',
        dramatic: '0 16px 32px rgba(255, 107, 53, 0.2)',
      },
    },
    
    mood: {
      energy: 'high',
      warmth: 'warm',
      sophistication: 'casual',
    },
  },

  memoir: {
    id: 'memoir',
    name: 'Personal Reflection',
    genre: 'Memoir',
    description: 'Warm, intimate, and thoughtful - inspired by personal narratives',
    
    typography: {
      primaryFont: 'Lora', // Readable serif with personality
      headingFont: 'Merriweather', // Friendly serif headers
      accentFont: 'Satisfy', // Script for personal touches
      fontSize: {
        base: '17px',
        h1: '2.3rem',
        h2: '1.8rem',
        h3: '1.4rem',
      },
      lineHeight: '1.8',
      letterSpacing: '0.01em',
    },
    
    colors: {
      background: '#f7f3f0', // Soft beige
      surface: '#ffffff',
      primary: '#2e7d32', // Forest green
      secondary: '#81c784', // Light green
      
      text: {
        primary: '#1b2e1b', // Deep green-black
        secondary: '#2e5d2e', // Medium green
        muted: '#5a7c5a', // Muted green
        accent: '#2e7d32', // Matching primary
      },
      
      border: '#e8f5e8',
      shadow: 'rgba(46, 125, 50, 0.15)',
      selection: '#c8e6c9',
      highlight: '#f1f8e9',
    },
    
    atmosphere: {
      borderRadius: '10px',
      shadows: {
        subtle: '0 2px 4px rgba(46, 125, 50, 0.1)',
        medium: '0 6px 12px rgba(46, 125, 50, 0.15)',
        dramatic: '0 12px 24px rgba(46, 125, 50, 0.2)',
      },
    },
    
    mood: {
      energy: 'low',
      warmth: 'warm',
      sophistication: 'elegant',
    },
  },
};

// Helper function to get all available themes
export const getAllThemes = (): DocumentTheme[] => {
  return Object.values(DOCUMENT_THEMES);
}; 