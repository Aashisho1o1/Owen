"""
Fiction Templates Service
Provides writing templates specifically designed for fiction writers
"""

from typing import List, Dict, Any, Optional
from models.schemas import FictionTemplate, DocumentType

class FictionTemplateService:
    """
    Service for managing fiction writing templates
    
    SCALABLE DESIGN:
    - Templates stored in code for MVP (fast startup)
    - Easy migration to database when needed
    - Category-based organization
    - Extensible template system
    """
    
    def __init__(self):
        self.templates = self._initialize_templates()
        # PERFORMANCE: Add caching for frequently accessed templates
        self._template_cache = {}
        self._category_cache = None
        self._search_cache = {}
    
    def _initialize_templates(self) -> List[FictionTemplate]:
        """Initialize fiction writing templates"""
        return [
            # === CHARACTER TEMPLATES ===
            FictionTemplate(
                id="character_profile_basic",
                name="Character Profile - Basic",
                category="character",
                description="Essential character development template",
                document_type=DocumentType.CHARACTER_PROFILE,
                content="""# Character Profile: [Character Name]

## Basic Information
- **Full Name:** 
- **Age:** 
- **Occupation:** 
- **Location:** 

## Physical Description
- **Appearance:** 
- **Distinguishing Features:** 

## Personality
- **Core Traits:** 
- **Strengths:** 
- **Flaws:** 
- **Fears:** 
- **Motivations:** 

## Background
- **Backstory:** 
- **Family:** 
- **Education:** 
- **Key Life Events:** 

## Role in Story
- **Character Arc:** 
- **Relationships:** 
- **Conflicts:** 
- **Goals:** 

## Voice & Dialogue
- **Speech Patterns:** 
- **Vocabulary:** 
- **Accent/Dialect:** 

## Notes
""",
                tags=["character", "development", "profile"]
            ),
            
            FictionTemplate(
                id="character_profile_detailed",
                name="Character Profile - Detailed",
                category="character",
                description="Comprehensive character development worksheet",
                document_type=DocumentType.CHARACTER_PROFILE,
                content="""# Character Profile: [Character Name]

## Identity
- **Full Name:** 
- **Nickname/Aliases:** 
- **Age:** 
- **Birthday:** 
- **Zodiac Sign:** 
- **Gender:** 
- **Sexual Orientation:** 
- **Occupation:** 
- **Income Level:** 
- **Location:** 
- **Nationality/Ethnicity:** 

## Physical Description
- **Height/Weight:** 
- **Build:** 
- **Hair:** 
- **Eyes:** 
- **Skin:** 
- **Distinguishing Features:** 
- **Style/Fashion:** 
- **Posture/Gait:** 
- **Gestures/Mannerisms:** 

## Personality Deep Dive
- **MBTI Type:** 
- **Core Values:** 
- **Beliefs:** 
- **Moral Code:** 
- **Sense of Humor:** 
- **Temperament:** 
- **Introvert/Extrovert:** 
- **Optimist/Pessimist:** 
- **Confidence Level:** 
- **Emotional Intelligence:** 

## Psychology
- **Greatest Fear:** 
- **Greatest Desire:** 
- **What They Want vs What They Need:** 
- **Internal Conflicts:** 
- **Coping Mechanisms:** 
- **Triggers:** 
- **Secrets:** 
- **Lies They Tell Themselves:** 

## Background & History
- **Childhood:** 
- **Adolescence:** 
- **Education:** 
- **Career Path:** 
- **Romantic History:** 
- **Friendships:** 
- **Family Dynamics:** 
- **Traumatic Events:** 
- **Life-Changing Moments:** 
- **Current Life Situation:** 

## Relationships
- **Family Members:** 
- **Friends:** 
- **Romantic Interests:** 
- **Enemies/Rivals:** 
- **Mentors:** 
- **How Others See Them:** 
- **How They See Themselves:** 

## Skills & Abilities
- **Talents:** 
- **Skills:** 
- **Hobbies:** 
- **Languages:** 
- **Special Abilities:** 
- **Weaknesses:** 

## Story Role
- **Character Arc:** 
- **Starting Point:** 
- **Ending Point:** 
- **Key Scenes:** 
- **Relationships with Other Characters:** 
- **Role in Plot:** 
- **Conflicts They Face:** 

## Voice & Dialogue
- **Speech Patterns:** 
- **Vocabulary Level:** 
- **Accent/Dialect:** 
- **Favorite Phrases:** 
- **How They Express Emotions:** 
- **Communication Style:** 

## Miscellaneous
- **Favorite Color:** 
- **Favorite Food:** 
- **Pet Peeves:** 
- **Habits:** 
- **Superstitions:** 
- **Collections:** 
- **Dreams:** 
- **Regrets:** 

## Character Evolution Notes
""",
                tags=["character", "detailed", "psychology", "development"]
            ),
            
            # === PLOT TEMPLATES ===
            FictionTemplate(
                id="three_act_structure",
                name="Three-Act Structure Outline",
                category="plot",
                description="Classic three-act story structure template",
                document_type=DocumentType.PLOT_OUTLINE,
                content="""# Three-Act Structure: [Story Title]

## Story Premise
**Logline:** 
**Genre:** 
**Target Audience:** 
**Theme:** 

## ACT I - Setup (25%)

### Opening Image
- **First Scene:** 
- **Mood/Tone:** 

### Inciting Incident
- **What happens:** 
- **When:** 
- **Impact on protagonist:** 

### Plot Point 1 - End of Act I
- **The point of no return:** 
- **Stakes established:** 
- **Goal defined:** 

## ACT II - Confrontation (50%)

### First Half (Rising Action)
- **Obstacles:** 
- **Character development:** 
- **Subplots:** 

### Midpoint
- **Major revelation/twist:** 
- **Stakes raised:** 
- **Character change:** 

### Second Half (Complications)
- **Increasing pressure:** 
- **Character's lowest point:** 
- **All seems lost:** 

### Plot Point 2 - End of Act II
- **Final obstacle:** 
- **Character's darkest moment:** 
- **Preparation for climax:** 

## ACT III - Resolution (25%)

### Climax
- **Final confrontation:** 
- **Character's choice:** 
- **Resolution of main conflict:** 

### Falling Action
- **Immediate aftermath:** 
- **Loose ends tied up:** 

### Resolution/Denouement
- **New normal:** 
- **Character growth shown:** 
- **Final image:** 

## Character Arcs
- **Protagonist:** 
- **Antagonist:** 
- **Supporting Characters:** 

## Themes Explored
""",
                tags=["plot", "structure", "outline", "three-act"]
            ),
            
            # === WORLD BUILDING TEMPLATES ===
            FictionTemplate(
                id="world_building_fantasy",
                name="Fantasy World Building",
                category="world",
                description="Comprehensive fantasy world development guide",
                document_type=DocumentType.WORLD_BUILDING,
                content="""# World Building: [World Name]

## Overview
- **World Name:** 
- **Genre:** Fantasy
- **Time Period:** 
- **Technology Level:** 
- **Magic System:** 

## Geography & Environment
- **Continents/Regions:** 
- **Climate Zones:** 
- **Notable Landmarks:** 
- **Natural Resources:** 
- **Dangerous Areas:** 

## Magic System
- **How Magic Works:** 
- **Who Can Use Magic:** 
- **Limitations:** 
- **Cost/Consequences:** 
- **Magical Creatures:** 
- **Magical Items:** 

## Societies & Cultures
- **Major Civilizations:** 
- **Government Systems:** 
- **Social Hierarchies:** 
- **Customs & Traditions:** 
- **Languages:** 
- **Religions:** 

## History
- **Creation Myth:** 
- **Major Historical Events:** 
- **Wars & Conflicts:** 
- **Important Figures:** 
- **Lost Civilizations:** 

## Economy & Trade
- **Currency:** 
- **Trade Routes:** 
- **Major Industries:** 
- **Guilds/Organizations:** 

## Technology & Innovation
- **Level of Technology:** 
- **Transportation:** 
- **Communication:** 
- **Medicine:** 
- **Weapons & Armor:** 

## Creatures & Races
- **Intelligent Races:** 
- **Monsters/Beasts:** 
- **Relationships Between Races:** 

## Current Events
- **Political Situation:** 
- **Ongoing Conflicts:** 
- **Recent Discoveries:** 
- **Threats:** 

## Story-Specific Elements
- **How This World Affects Your Story:** 
- **Unique Aspects:** 
- **Rules Important to Plot:** 

## World Building Notes
""",
                tags=["world-building", "fantasy", "magic", "cultures"]
            ),
            
            # === SCENE TEMPLATES ===
            FictionTemplate(
                id="scene_structure",
                name="Scene Structure Template",
                category="scene",
                description="Template for structuring individual scenes",
                document_type=DocumentType.SCENE,
                content="""# Scene: [Scene Title/Number]

## Scene Purpose
- **Goal of this scene:** 
- **How it advances plot:** 
- **Character development:** 

## Setting
- **Location:** 
- **Time:** 
- **Atmosphere/Mood:** 
- **Weather:** 

## Characters Present
- **POV Character:** 
- **Other Characters:** 
- **Character Goals:** 
- **Character Obstacles:** 

## Scene Structure

### Opening
- **Hook:** 
- **Setting establishment:** 
- **Character state:** 

### Rising Action
- **Conflict/Tension:** 
- **Dialogue highlights:** 
- **Action beats:** 

### Climax/Turning Point
- **Key moment:** 
- **Character choice:** 
- **Revelation:** 

### Resolution
- **Outcome:** 
- **Character reaction:** 
- **Transition to next scene:** 

## Sensory Details
- **What character sees:** 
- **What character hears:** 
- **What character feels:** 
- **What character smells:** 
- **What character tastes:** 

## Emotional Journey
- **Character's emotional state at start:** 
- **Emotional changes during scene:** 
- **Character's emotional state at end:** 

## Dialogue Notes
- **Key conversations:** 
- **Subtext:** 
- **Character voice reminders:** 

## Revision Notes
""",
                tags=["scene", "structure", "writing", "craft"]
            ),
            
            # === CHAPTER TEMPLATES ===
            FictionTemplate(
                id="chapter_template",
                name="Chapter Template",
                category="chapter",
                description="Structure for writing chapters",
                document_type=DocumentType.CHAPTER,
                content="""# Chapter [Number]: [Chapter Title]

## Chapter Overview
- **POV Character:** 
- **Main Goal:** 
- **Key Events:** 
- **Word Count Target:** 

## Opening
[Start writing your chapter here...]

## Notes
- **Character arcs in this chapter:** 
- **Plot threads advanced:** 
- **Foreshadowing planted:** 
- **Themes explored:** 

---

*Chapter Word Count: [Track your progress]*
*Status: [Draft/Revision/Final]*
""",
                tags=["chapter", "novel", "structure"]
            ),
            
            # === RESEARCH TEMPLATES ===
            FictionTemplate(
                id="research_notes",
                name="Research Notes",
                category="research",
                description="Template for organizing research materials",
                document_type=DocumentType.RESEARCH_NOTES,
                content="""# Research Notes: [Topic]

## Research Question/Purpose
**What I'm researching:** 
**Why I need this information:** 
**How it applies to my story:** 

## Sources
1. **Source Name:** 
   - **Type:** (Book/Article/Website/Interview/etc.)
   - **Author:** 
   - **Date:** 
   - **URL/Location:** 
   - **Credibility:** 
   - **Notes:** 

## Key Findings
- **Important Facts:** 
- **Surprising Discoveries:** 
- **Contradictory Information:** 
- **Gaps in Research:** 

## Story Applications
- **How this affects my plot:** 
- **Character implications:** 
- **World building elements:** 
- **Dialogue/terminology:** 

## Questions for Further Research
- 
- 
- 

## Visual References
[Links to images, maps, diagrams, etc.]

## Research Timeline
- **Started:** 
- **Completed:** 
- **Last Updated:** 

## Fact-Checking Notes
""",
                tags=["research", "notes", "reference", "accuracy"]
            )
        ]
    
    def get_all_templates(self) -> List[FictionTemplate]:
        """Get all available templates"""
        return self.templates
    
    def get_template_by_id(self, template_id: str) -> Optional[FictionTemplate]:
        """Get a specific template by ID with caching"""
        # PERFORMANCE: Check cache first
        if template_id in self._template_cache:
            return self._template_cache[template_id]
        
        template = next((t for t in self.templates if t.id == template_id), None)
        
        # Cache the result (both hits and misses)
        self._template_cache[template_id] = template
        return template
    
    def get_templates_by_category(self, category: str) -> List[FictionTemplate]:
        """Get templates by category"""
        return [t for t in self.templates if t.category == category]
    
    def get_templates_by_document_type(self, doc_type: DocumentType) -> List[FictionTemplate]:
        """Get templates by document type"""
        return [t for t in self.templates if t.document_type == doc_type]
    
    def get_categories(self) -> List[str]:
        """Get all available template categories with caching"""
        # PERFORMANCE: Cache categories since they don't change often
        if self._category_cache is None:
            self._category_cache = list(set(t.category for t in self.templates))
        return self._category_cache
    
    def search_templates(self, query: str) -> List[FictionTemplate]:
        """Search templates by name, description, or tags with caching"""
        query_lower = query.lower()
        
        # PERFORMANCE: Cache search results
        if query_lower in self._search_cache:
            return self._search_cache[query_lower]
        
        results = [
            t for t in self.templates
            if (query_lower in t.name.lower() or 
                query_lower in t.description.lower() or
                any(query_lower in tag.lower() for tag in t.tags))
        ]
        
        # Cache the search results (limit cache size)
        if len(self._search_cache) > 100:  # Prevent memory bloat
            self._search_cache.clear()
        
        self._search_cache[query_lower] = results
        return results

# Global instance
fiction_template_service = FictionTemplateService() 