import { DocumentTheme } from './documentThemes';

export interface FictionTemplate {
  id: string;
  name: string;
  genre: string;
  description: string;
  icon: string;
  content: string;
  color: string;
  // Enhanced theming reference
  themeId: string; // References DOCUMENT_THEMES
}

export const FICTION_TEMPLATES: FictionTemplate[] = [
  {
    id: 'romance',
    name: 'Romance Novel',
    genre: 'Romance',
    description: 'A template for romantic fiction with character development arcs',
    icon: '💕',
    color: '#ff6b9d',
    themeId: 'romance',
    content: `# Romance Novel Template

## Main Characters
### Protagonist
- Name:
- Age:
- Occupation:
- Background:
- Personality traits:
- Internal conflict:

### Love Interest
- Name:
- Age:
- Occupation:
- Background:
- Personality traits:
- What makes them attractive:

## Plot Structure
### Meet-Cute (Chapter 1-2)
- How do they first encounter each other?
- What's the initial impression?
- What sparks their interest?

### Building Tension (Chapter 3-8)
- Obstacles to their relationship:
- Moments of connection:
- Misunderstandings:

### The Crisis (Chapter 9-10)
- What threatens to keep them apart?
- Dark moment:

### Resolution (Chapter 11-12)
- How do they overcome obstacles?
- The declaration of love:
- Happy ending:

## Chapter Outline
1. Chapter 1: [Title] - [Brief description]
2. Chapter 2: [Title] - [Brief description]
...

## Key Themes
- 
- 
- 

## Setting
- Time period:
- Location:
- Atmosphere:
`
  },
  {
    id: 'thriller',
    name: 'Thriller Novel',
    genre: 'Thriller',
    description: 'A template for suspenseful thrillers and mysteries',
    icon: '🔍',
    color: '#4c566a',
    themeId: 'thriller',
    content: `# Thriller Novel Template

## Main Characters
### Protagonist
- Name:
- Profession:
- Special skills:
- Personal stakes:
- Fatal flaw:

### Antagonist
- Name:
- Motivation:
- Methods:
- Resources:
- Connection to protagonist:

## Plot Structure
### The Hook (Chapter 1)
- Inciting incident:
- What grabs the reader immediately?

### Rising Action (Chapters 2-8)
- Clues discovered:
- Red herrings:
- Escalating danger:
- Plot twists:

### Climax (Chapters 9-10)
- Final confrontation:
- Revelation of truth:

### Resolution (Chapter 11)
- Aftermath:
- Justice served:

## Mystery Elements
- Central mystery:
- Key clues:
- False leads:
- Final revelation:

## Suspense Techniques
- Ticking clock:
- Information gaps:
- Foreshadowing:
- Cliffhangers:

## Chapter Outline
1. Chapter 1: [Title] - [The hook]
2. Chapter 2: [Title] - [First clue]
...
`
  },
  {
    id: 'fantasy',
    name: 'Fantasy Epic',
    genre: 'Fantasy',
    description: 'A template for epic fantasy adventures',
    icon: '🐉',
    color: '#8b5a3c',
    themeId: 'fantasy',
    content: `# Fantasy Epic Template

## World Building
### Magic System
- How magic works:
- Rules and limitations:
- Who can use magic:
- Cost of magic:

### Geography
- Main kingdoms/regions:
- Important locations:
- Climate and terrain:

### Cultures
- Major races/peoples:
- Languages:
- Customs and beliefs:
- Political structures:

## Main Characters
### Hero/Heroine
- Name:
- Background:
- Special abilities:
- Quest/goal:
- Character arc:

### Supporting Characters
- Mentor:
- Allies:
- Love interest:
- Companions:

### Villain
- Name:
- Motivation:
- Powers:
- Army/followers:

## The Quest
### Call to Adventure
- What forces the hero to act?
- Initial refusal:
- Crossing the threshold:

### Trials and Challenges
- Tests of character:
- Allies gained:
- Enemies faced:
- Magical items acquired:

### Final Battle
- Ultimate confrontation:
- Sacrifice required:
- Victory and transformation:

## Chapter Outline
1. Chapter 1: [Title] - [Ordinary world]
2. Chapter 2: [Title] - [Call to adventure]
...
`
  },
  {
    id: 'scifi',
    name: 'Science Fiction',
    genre: 'Sci-Fi',
    description: 'A template for futuristic science fiction stories',
    icon: '🚀',
    color: '#4169e1',
    themeId: 'scifi',
    content: `# Science Fiction Template

## Setting
### Time Period
- Year/era:
- Technological level:
- Scientific advances:

### World/Universe
- Planets/locations:
- Societies:
- Governments:
- Conflicts:

### Technology
- Key inventions:
- Transportation:
- Communication:
- Weapons:

## Main Characters
### Protagonist
- Name:
- Role/profession:
- Relationship to technology:
- Scientific knowledge:
- Personal conflict:

### Supporting Characters
- Scientists/engineers:
- Military/government:
- Aliens/AIs:
- Civilians:

## Central Concept
- Scientific premise:
- "What if" question:
- Implications explored:

## Plot Structure
### Setup (Chapters 1-3)
- World establishment:
- Character introduction:
- Scientific concept revealed:

### Development (Chapters 4-8)
- Consequences unfold:
- Characters adapt:
- Conflicts arise:

### Resolution (Chapters 9-12)
- Scientific solution:
- Character growth:
- New equilibrium:

## Chapter Outline
1. Chapter 1: [Title] - [World introduction]
2. Chapter 2: [Title] - [Characters and conflict]
...
`
  },
  {
    id: 'historical',
    name: 'Historical Fiction',
    genre: 'Historical',
    description: 'A template for historical fiction set in past eras',
    icon: '🏛️',
    color: '#8b4513',
    themeId: 'historical',
    content: `# Historical Fiction Template

## Historical Setting
### Time Period
- Exact dates:
- Major historical events:
- Social conditions:
- Political climate:

### Location
- Country/region:
- Cities/towns:
- Geography:
- Architecture:

### Daily Life
- Social classes:
- Occupations:
- Food and clothing:
- Transportation:
- Entertainment:

## Main Characters
### Protagonist
- Name:
- Social class:
- Occupation:
- Education level:
- Personal goals:

### Historical Figures
- Real people involved:
- Their roles in story:
- Accuracy vs. fiction:

## Historical Accuracy
### Research Areas
- Political events:
- Social customs:
- Technology:
- Language/dialect:
- Cultural attitudes:

### Anachronisms to Avoid
- Modern concepts:
- Incorrect technology:
- Wrong social attitudes:

## Plot Integration
### Historical Events
- How they affect characters:
- Character roles in events:
- Personal vs. historical stakes:

## Chapter Outline
1. Chapter 1: [Title] - [Setting establishment]
2. Chapter 2: [Title] - [Character in historical context]
...
`
  },
  {
    id: 'memoir',
    name: 'Biography/Memoir',
    genre: 'Non-Fiction',
    description: 'A template for personal stories and biographies',
    icon: '📖',
    color: '#2e7d32',
    themeId: 'memoir',
    content: `# Biography/Memoir Template

## Overview
### Subject
- Full name:
- Birth/death dates:
- Significance:
- Why their story matters:

### Scope
- Time period covered:
- Key life phases:
- Major themes:

## Life Phases
### Early Life
- Family background:
- Childhood experiences:
- Education:
- Formative events:

### Career/Achievements
- Professional life:
- Major accomplishments:
- Challenges overcome:
- Impact on others:

### Personal Life
- Relationships:
- Family:
- Personal struggles:
- Character development:

### Legacy
- Lasting impact:
- What they're remembered for:
- Lessons learned:

## Research Sources
### Primary Sources
- Letters/diaries:
- Interviews:
- Official documents:
- Photographs:

### Secondary Sources
- Biographies:
- Historical records:
- News articles:
- Academic papers:

## Narrative Structure
### Chronological vs. Thematic
- Timeline approach:
- Theme-based chapters:
- Flashbacks/forwards:

## Chapter Outline
1. Chapter 1: [Title] - [Early life]
2. Chapter 2: [Title] - [Formative period]
...
`
  },
  {
    id: 'comedy',
    name: 'Comedy Novel',
    genre: 'Comedy',
    description: 'A template for humorous fiction and satire',
    icon: '😂',
    color: '#ff9800',
    themeId: 'comedy',
    content: `# Comedy Novel Template

## Comedic Style
### Type of Humor
- Satirical:
- Absurdist:
- Romantic comedy:
- Dark comedy:
- Parody:

### Target
- What/who are you poking fun at?
- Social issues:
- Human nature:
- Specific groups/professions:

## Main Characters
### Comic Protagonist
- Name:
- Personality flaws (source of humor):
- Misunderstandings they create:
- How they grow:

### Supporting Cast
- Straight man/woman:
- Comic relief:
- Foils:
- Eccentric characters:

## Comedic Situations
### Running Gags
- Recurring jokes:
- Character quirks:
- Situational comedy:

### Set Pieces
- Major comedic scenes:
- Physical comedy:
- Dialogue-based humor:
- Ironic situations:

## Plot Structure
### Setup (Chapters 1-3)
- Normal world:
- Character introduction:
- Comedic premise:

### Complications (Chapters 4-8)
- Misunderstandings multiply:
- Situations escalate:
- Characters react:

### Resolution (Chapters 9-12)
- Truth revealed:
- Lessons learned:
- Happy ending:

## Chapter Outline
1. Chapter 1: [Title] - [Setup and first laugh]
2. Chapter 2: [Title] - [Complications begin]
...
`
  }
]; 