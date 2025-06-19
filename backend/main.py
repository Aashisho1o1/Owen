# Backend API - DOG Writer Document Management System
# Version 2.0.0 - Railway Deployment [FORCE-DEPLOY-2024-TEMPLATE-FIX]
"""
DOG Writer Backend - Google Docs-Like Document Management System
Comprehensive document editor with PostgreSQL database, folders, versions, sharing, and collaboration
Production-ready with proper database persistence
"""

import os
import logging
import uuid
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from contextlib import asynccontextmanager
from enum import Enum

from fastapi import FastAPI, HTTPException, Depends, status, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

import jwt
import bcrypt

# Import our PostgreSQL services
from services.database import db_service, DatabaseError
from services.auth_service import auth_service, AuthenticationError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Enums for better type safety
class DocumentStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class PermissionLevel(str, Enum):
    OWNER = "owner"
    EDITOR = "editor"
    VIEWER = "viewer"

class ActivityType(str, Enum):
    CREATED = "created"
    EDITED = "edited"
    SHARED = "shared"
    VIEWED = "viewed"
    COMMENTED = "commented"

# JWT Configuration from auth service
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here-please-change-in-production")
security = HTTPBearer()

# Story Writing Templates - Beautiful Templates for Creative Writers
templates_store = [
    {
        "id": "romance",
        "title": "Romance Novel",
        "description": "A passionate love story template with character arcs and emotional depth",
        "content": """# Romance Novel: [Your Story Title]

💕 **Genre:** Romance | **Target Length:** 50,000-80,000 words | **Theme:** [Love conquers all/Second chances/Enemies to lovers]

---

## ✨ Main Characters

### 💖 Protagonist
- **Name:** [Character Name]
- **Age:** [Age]
- **Occupation:** [Job/Career]
- **Personality:** [3-4 key traits]
- **Backstory:** [What shaped them?]
- **Romantic History:** [Past relationships/heartbreak]
- **Internal Conflict:** [What holds them back from love?]
- **Character Arc:** [How will love change them?]

### 💕 Love Interest
- **Name:** [Character Name]
- **Age:** [Age]
- **Occupation:** [Job/Career]
- **Personality:** [3-4 key traits that complement/contrast protagonist]
- **Backstory:** [What shaped them?]
- **What Makes Them Irresistible:** [Specific traits that attract protagonist]
- **Internal Conflict:** [Their own barriers to love]

## 🎭 Romance Plot Structure

### 📖 Chapter 1-3: The Meet-Cute
- **First Encounter:** [How do they meet? What's the immediate impression?]
- **Initial Attraction:** [What draws them to each other?]
- **First Obstacle:** [What creates tension/conflict?]

### 💫 Chapter 4-8: Building Tension
- **Growing Attraction:** [Moments of connection and chemistry]
- **Romantic Obstacles:** [External/internal conflicts keeping them apart]
- **First Kiss:** [When and how does it happen?]
- **Deepening Bond:** [How do they get to know each other?]

### 💔 Chapter 9-12: The Crisis
- **Dark Moment:** [What threatens to tear them apart?]
- **Misunderstanding/Conflict:** [The big fight or revelation]
- **Separation:** [Physical or emotional distance]
- **Internal Growth:** [What each character learns about themselves]

### 💕 Chapter 13-15: Resolution
- **Grand Gesture:** [How is love declared/proven?]
- **Reconciliation:** [How do they overcome the obstacles?]
- **Happy Ever After:** [How does their love story conclude?]

---

## 🌟 Chapter 1: [Chapter Title]

[Start with a compelling hook that introduces your protagonist in a moment of vulnerability, strength, or change. Show their world before love enters it.]

The morning light filtered through [setting details], casting shadows that reminded [protagonist] of everything they were trying to forget. [Describe their current emotional state and what they want/need]...

[Continue with the scene that will lead to meeting the love interest, or set up their world compellingly]

---

## 💝 Romance Writing Prompts
- What's the one thing your protagonist swore they'd never do again?
- What secret could destroy their budding relationship?
- What does your love interest do that no one else has ever done for your protagonist?
- What's the most romantic gesture in your story?

## 🎯 Key Themes to Explore
- [ ] Vulnerability and trust
- [ ] Growth through love
- [ ] Overcoming past trauma
- [ ] Finding self-worth
- [ ] The courage to love again""",
        "category": "Romance",
        "word_count_target": 65000,
        "estimated_time": "3-6 months"
    },
    {
        "id": "fantasy",
        "title": "Fantasy Epic",
        "description": "A magical world-building template for epic fantasy adventures",
        "content": """# Fantasy Epic: [Your World's Name]

🐉 **Genre:** Epic Fantasy | **Target Length:** 80,000-120,000 words | **Magic Level:** [High/Low Fantasy]

---

## 🌍 World Building

### ⚡ Magic System
- **How Magic Works:** [Energy source, mechanics, visualization]
- **Rules & Limitations:** [What can't magic do? What's the cost?]
- **Who Can Use Magic:** [Bloodlines, training, artifacts, born ability]
- **Magic Types:** [Elemental, divine, arcane, nature, etc.]
- **Forbidden Magic:** [What's dangerous or banned?]

### 🏰 Geography & Realms
- **Main Kingdom/Empire:** [Name, culture, government]
- **Other Regions:** [At least 3 distinct areas with unique features]
- **Important Locations:** [Capital cities, sacred sites, dangerous zones]
- **Climate & Terrain:** [How geography affects story and characters]

### 👑 Cultures & Peoples
- **Main Race/Culture:** [Humans, elves, etc. - their customs, values]
- **Other Peoples:** [At least 2-3 distinct cultures with conflicts/alliances]
- **Languages:** [Do you have unique languages or naming conventions?]
- **Religions/Beliefs:** [Gods, creation myths, afterlife beliefs]
- **Political Structure:** [How are these societies governed?]

## ⚔️ Main Characters

### 🌟 The Hero/Heroine
- **Name:** [Character Name]
- **Age:** [Age]
- **Origin:** [Where are they from? What's their background?]
- **Special Abilities:** [Magical powers, skills, unique traits]
- **Greatest Fear:** [What terrifies them most?]
- **Fatal Flaw:** [What weakness could destroy them?]
- **The Call to Adventure:** [What forces them to leave their ordinary world?]
- **Character Arc:** [How will they grow throughout the journey?]

### 🛡️ The Mentor
- **Name:** [Character Name]
- **Relationship to Hero:** [How do they know each other?]
- **Wisdom/Powers:** [What can they teach the hero?]
- **Dark Secret:** [What are they hiding?]

### ⚔️ Companions/Fellowship
- **Warrior:** [Name, fighting style, motivation for joining]
- **Mage/Healer:** [Name, magical abilities, personal quest]
- **Rogue/Scout:** [Name, skills, what they're running from]
- **[Additional Companion]:** [Name, role, unique contribution]

### 🖤 The Dark Lord/Antagonist
- **Name:** [Character Name]
- **Origin Story:** [How did they become evil? Were they always?]
- **Powers:** [What makes them formidable?]
- **Army/Followers:** [Who serves them and why?]
- **Ultimate Goal:** [World domination? Revenge? Destruction?]
- **Connection to Hero:** [Personal stakes beyond good vs. evil]

## 🗡️ The Epic Quest

### 🌅 Call to Adventure
- **The Ordinary World:** [Hero's life before adventure]
- **Inciting Incident:** [What changes everything?]
- **Refusal of the Call:** [Why don't they want to go?]
- **Crossing the Threshold:** [What forces them to begin?]

### 🏔️ Trials & Challenges
- **Trial 1:** [First major obstacle - physical/mental/spiritual test]
- **Trial 2:** [Character development challenge]
- **Trial 3:** [Team building/trust challenge]
- **The Midpoint Crisis:** [Major setback/revelation changes everything]
- **Trial 4:** [Personal sacrifice required]
- **Trial 5:** [Face their greatest fear]

### ⚡ Magical Items & Artifacts
- **The [Weapon/Tool] of [Power]:** [Description, powers, history]
- **Ancient Relic:** [What it does, where it's hidden]
- **Protective Charm:** [Who gives it, what it protects against]

### 🏰 Final Confrontation
- **The Dark Fortress:** [Where the final battle takes place]
- **Ultimate Test:** [How is the villain defeated?]
- **Hero's Sacrifice:** [What must they give up to win?]
- **Resolution:** [How is peace restored?]

---

## ⭐ Chapter 1: The Ordinary World

[Begin with your hero in their normal life, but hint at the larger destiny awaiting them. Show us their character through action.]

The ancient oak had stood guard over [location] for a thousand years, its roots drinking from the same spring that [protagonist] visited each morning. Today, however, something was different. The water tasted of copper and starlight, and [protagonist] could swear they heard whispers in the wind...

[Continue with a scene that establishes your world's magic and your hero's life before adventure calls]

---

## 🎯 Fantasy Elements Checklist
- [ ] Unique magic system with clear rules
- [ ] Rich world history and mythology
- [ ] Distinct cultures with their own customs
- [ ] Political conflicts and alliances
- [ ] Ancient prophecies or legends
- [ ] Magical creatures and beings
- [ ] Epic battles and personal growth
- [ ] Themes of power, responsibility, and sacrifice""",
        "category": "Fantasy",
        "word_count_target": 100000,
        "estimated_time": "6-12 months"
    },
    {
        "id": "mystery",
        "title": "Mystery Thriller",
        "description": "A suspenseful mystery template with clues, red herrings, and shocking revelations",
        "content": """# Mystery Thriller: [Your Mystery Title]

🔍 **Genre:** Mystery/Thriller | **Target Length:** 60,000-80,000 words | **Setting:** [Time & Place]

---

## 🕵️ Main Characters

### 🎯 The Detective/Protagonist
- **Name:** [Character Name]
- **Profession:** [Police detective, private investigator, amateur sleuth]
- **Age:** [Age]
- **Special Skills:** [Deduction, forensics, psychology, local knowledge]
- **Personal Stakes:** [Why is this case personal? What do they have to lose?]
- **Fatal Flaw:** [Obsessiveness, trust issues, past trauma]
- **Unique Method:** [How do they approach solving crimes differently?]

### 💀 The Victim
- **Name:** [Character Name]
- **Background:** [Who were they? Why were they targeted?]
- **Secrets:** [What were they hiding?]
- **Connections:** [How do they link to other characters?]
- **The Hook:** [What makes their death compelling/mysterious?]

### 🎭 The Killer/Antagonist
- **Identity:** [Keep this secret until the reveal!]
- **Motive:** [Why did they kill? Revenge, money, love, power?]
- **Method:** [How do they operate? Signature elements?]
- **Psychology:** [What drives them? Are they calculating or impulsive?]
- **Connection to Protagonist:** [How are they linked to the detective?]

### 🧩 Key Suspects (3-5 people)
**Suspect 1:** [Name] - [Relationship to victim] - [Apparent motive] - [Secret they're hiding]
**Suspect 2:** [Name] - [Relationship to victim] - [Apparent motive] - [Secret they're hiding]  
**Suspect 3:** [Name] - [Relationship to victim] - [Apparent motive] - [Secret they're hiding]
**Suspect 4:** [Name] - [Relationship to victim] - [Apparent motive] - [Secret they're hiding]

## 🧩 The Mystery Structure

### 🚨 The Crime (Chapters 1-2)
- **The Discovery:** [Who finds the body? How?]
- **First Impressions:** [What does the scene reveal?]
- **Initial Questions:** [What immediately seems strange/wrong?]
- **Stakes Established:** [Why must this be solved quickly?]

### 🔍 Investigation Phase 1 (Chapters 3-8)
- **Key Clue 1:** [Physical evidence found]
- **Key Clue 2:** [Witness testimony/information]
- **Key Clue 3:** [Discovery about victim's past]
- **Red Herring 1:** [False lead that misdirects]
- **Character Development:** [What personal demons does protagonist face?]

### 💡 Revelation & Escalation (Chapters 9-12)
- **Major Discovery:** [Game-changing information revealed]
- **Second Crime/Attempt:** [Killer strikes again or threatens to]
- **Red Herring 2:** [Another false lead]
- **Personal Danger:** [Protagonist becomes target]
- **Breakthrough:** [Crucial clue that starts unraveling truth]

### ⚡ Resolution (Chapters 13-15)
- **The Confrontation:** [Detective faces the killer]
- **The Reveal:** [How/why the crime was committed]
- **Justice:** [How is the killer caught/punished?]
- **Resolution:** [How are loose ends tied up?]

## 🔍 Clues & Evidence

### 🧩 Physical Evidence
1. **[Clue Name]:** [Description] - [What it reveals] - [When discovered]
2. **[Clue Name]:** [Description] - [What it reveals] - [When discovered]
3. **[Clue Name]:** [Description] - [What it reveals] - [When discovered]

### 🗣️ Witness Testimony
- **Witness 1:** [Name] - [What they saw/know] - [Why they're important]
- **Witness 2:** [Name] - [What they saw/know] - [Why they're important]

### 🎭 Red Herrings (False Clues)
1. **[False Lead]:** [What it suggests] - [Why it's wrong] - [When revealed]
2. **[False Lead]:** [What it suggests] - [Why it's wrong] - [When revealed]

---

## 🔍 Chapter 1: The Discovery

[Start with the discovery of the crime in a way that immediately hooks the reader. Show your protagonist's expertise and personality.]

The call came at 3:47 AM, dragging Detective [Name] from the first decent sleep they'd had in weeks. "[Victim's name] is dead," the voice on the phone announced without preamble. "[Location]." 

[Continue with the protagonist arriving at the scene, their first observations, and what immediately strikes them as wrong or unusual about this case...]

---

## 🎯 Mystery Writing Checklist
- [ ] All clues necessary for solution are presented fairly to reader
- [ ] Red herrings mislead without cheating
- [ ] Multiple viable suspects with clear motives
- [ ] Solution is surprising but inevitable in hindsight  
- [ ] Protagonist uses logical deduction
- [ ] Personal stakes for detective beyond just "doing their job"
- [ ] Escalating tension and danger
- [ ] Satisfying confrontation and resolution

## 💭 Themes to Explore
- Truth vs. perception
- Justice vs. revenge  
- Past sins catching up
- The cost of secrets
- Obsession and its dangers""",
        "category": "Mystery",
        "word_count_target": 70000,
        "estimated_time": "4-8 months"
    },
    {
        "id": "scifi",
        "title": "Science Fiction",
        "description": "A futuristic sci-fi template exploring technology, humanity, and the unknown",
        "content": """# Science Fiction: [Your Future Vision]

🚀 **Genre:** Science Fiction | **Target Length:** 70,000-100,000 words | **Time:** [Year/Era] | **Setting:** [Planet/Space/Dimension]

---

## 🌌 World Building

### 🔬 Scientific Foundation
- **Core Technology:** [AI, genetic engineering, space travel, time manipulation, etc.]
- **How It Works:** [Explain the science - real or imagined]
- **Societal Impact:** [How has this technology changed humanity?]
- **Limitations:** [What can't this technology do? What are the costs?]
- **Ethical Questions:** [What moral dilemmas does it raise?]

### 🌍 Setting & Society
- **Time Period:** [How far in the future? Alternate timeline?]
- **Location:** [Earth, colony planets, space stations, other dimensions]
- **Government:** [How is society organized? Corporate rule? Democracy? AI governance?]
- **Social Classes:** [How is society stratified? Rich/poor? Human/AI? Enhanced/natural?]
- **Daily Life:** [How do ordinary people live in this world?]

### 🤖 Technology & Science
- **Transportation:** [How do people travel? Teleportation? FTL ships? Time travel?]
- **Communication:** [Brain implants? Quantum networks? AI translators?]
- **Medicine:** [Life extension? Genetic modification? Consciousness transfer?]
- **Energy:** [Fusion? Dark matter? Zero-point? Environmental impact?]
- **Computing:** [AI consciousness? Quantum computers? Neural interfaces?]

## 👥 Main Characters

### 🌟 The Protagonist
- **Name:** [Character Name]
- **Profession:** [Scientist, pilot, explorer, rebel, ordinary person]
- **Background:** [Where are they from? What's their history?]
- **Relationship to Technology:** [Enhanced? Natural? Resistant? Dependent?]
- **Personal Stakes:** [What do they have to lose/gain?]
- **Character Flaw:** [Pride in science? Fear of change? Nostalgia for the past?]
- **The Question They Face:** [What forces them to examine their beliefs?]

### 🤖 The Other (AI/Alien/Enhanced Human)
- **Nature:** [Artificial intelligence, alien species, genetically modified human]
- **Capabilities:** [What can they do that humans can't?]
- **Motivation:** [What do they want? How do they think differently?]
- **Relationship to Protagonist:** [Ally, enemy, mysterious guide?]
- **The Mirror:** [How do they reflect or challenge human nature?]

### 🏢 The Institution/Corporation/Government
- **Name:** [Organization Name]
- **Power:** [What do they control? Technology? Information? Lives?]
- **Goals:** [Profit? Control? Human advancement? Survival?]
- **Methods:** [How do they maintain power?]
- **Corruption:** [What are they hiding? What lines have they crossed?]

## 🚀 Science Fiction Plot Structure

### 🌌 Opening: The New World (Chapters 1-3)
- **Establish the Science:** [Show your technology/world in action]
- **Normal Life:** [How does your protagonist live in this world?]
- **The Inciting Incident:** [Discovery, malfunction, first contact, rebellion]
- **The Question:** [What big issue will your story explore?]

### 🔬 Exploration & Discovery (Chapters 4-8)
- **Deeper Understanding:** [Protagonist learns more about the technology/aliens/situation]
- **Complications:** [The science/situation is more complex than expected]
- **Ethical Dilemmas:** [Characters must make difficult choices]
- **Growing Stakes:** [Personal becomes universal, or vice versa]

### ⚡ Crisis & Confrontation (Chapters 9-12)  
- **The Problem Escalates:** [Technology fails, aliens attack, society collapses]
- **Impossible Choices:** [Science vs. humanity, safety vs. freedom, etc.]
- **Personal Cost:** [What must the protagonist sacrifice?]
- **The Solution:** [How science/understanding provides a way forward]

### 🌟 Resolution & New Understanding (Chapters 13-15)
- **The New Normal:** [How has the world changed?]
- **Human Growth:** [What have characters learned about humanity?]
- **Future Implications:** [What questions remain? What comes next?]

---

## 🌌 Chapter 1: [Chapter Title]

[Start by dropping the reader into your futuristic world. Show the technology and society in action through your protagonist's eyes.]

The morning neural-sync alert chimed softly in [protagonist's] mind at exactly 0600 hours, as it had every day for the past [time period]. Outside the biodome's transparent walls, [planet/setting] stretched endlessly, its [color] horizon broken only by the geometric patterns of the terraforming arrays.

[Continue with a scene that establishes your world's technology and the protagonist's role/feelings about it, leading to the inciting incident...]

---

## 🎯 Science Fiction Themes to Explore
- [ ] What makes us human?
- [ ] The consequences of technological advancement
- [ ] Individual vs. collective good
- [ ] The nature of consciousness and identity
- [ ] Humanity's place in the universe
- [ ] The ethics of scientific progress
- [ ] Communication across different forms of intelligence
- [ ] Evolution and adaptation

## 🔬 Scientific Elements Checklist
- [ ] Core scientific concept is explained clearly
- [ ] Technology feels both advanced and believable
- [ ] Scientific elements drive the plot forward
- [ ] Ethical implications are explored
- [ ] Characters represent different viewpoints on science
- [ ] World-building supports the scientific themes
- [ ] Resolution addresses the central scientific question""",
        "category": "Science Fiction", 
        "word_count_target": 85000,
        "estimated_time": "5-10 months"
    },
    {
        "id": "horror",
        "title": "Horror Story",
        "description": "A spine-chilling horror template with psychological terror and supernatural elements",
        "content": """# Horror Story: [Your Nightmare Title]

👻 **Genre:** Horror | **Target Length:** 50,000-75,000 words | **Horror Type:** [Psychological/Supernatural/Body Horror/Cosmic]

---

## 😨 Horror Elements

### 👻 The Fear Factor
- **Primary Fear:** [Death, isolation, loss of control, the unknown, body horror, madness]
- **Horror Subgenre:** [Psychological, supernatural, slasher, cosmic, folk horror]
- **Atmosphere:** [Oppressive, claustrophobic, dreamlike, decay, wrongness]
- **The Unknown:** [What are you keeping hidden from readers?]
- **Escalation:** [How does the horror intensify throughout the story?]

### 🏚️ Setting & Atmosphere  
- **Location:** [Haunted house, small town, isolated cabin, urban decay, otherworldly realm]
- **Time Period:** [Modern day, historical, timeless/eternal]
- **Weather/Season:** [Perpetual winter, oppressive heat, eternal storms]
- **Physical Decay:** [How does the environment reflect the horror?]
- **Isolation Factor:** [What cuts characters off from help/escape?]

### 👹 The Horror/Monster/Threat
- **Nature:** [Ghost, demon, alien, human killer, psychological break, ancient evil]
- **Origin:** [Where did it come from? Why is it here now?]
- **Rules:** [What can it do? What are its limitations?]
- **Symbolism:** [What deeper fear does it represent?]
- **Connection to Characters:** [How is it tied to the protagonist's past/psyche?]

## 😱 Main Characters

### 🎯 The Protagonist 
- **Name:** [Character Name]
- **Age:** [Age]
- **Background:** [What's their history? Any trauma/guilt?]
- **Fatal Flaw:** [Pride, denial, guilt, curiosity, isolation]
- **Connection to Horror:** [How are they specifically vulnerable?]
- **Arc:** [Do they survive? How are they changed?]
- **Sanity Level:** [Stable to start? Gradual breakdown? Already fragile?]

### 👥 Supporting Characters (The Victims/Allies)
- **Character 1:** [Name] - [Role] - [How they die/what they represent]
- **Character 2:** [Name] - [Role] - [How they die/what they represent]  
- **Character 3:** [Name] - [Role] - [How they die/what they represent]
- **The Skeptic:** [Who doesn't believe until it's too late?]
- **The Believer:** [Who understands the threat first?]

### 🔍 The Investigator/Expert
- **Name:** [Character Name]
- **Expertise:** [Occult, psychology, history, science]
- **Personal Connection:** [Why do they care about this case?]
- **Fate:** [Do they help or become another victim?]

## 👻 Horror Story Structure

### 🌙 Setup: The Normal World (Chapters 1-2)
- **Establish Normalcy:** [Show life before horror intrudes]
- **First Signs:** [Subtle wrongness, minor disturbances]
- **Character Introduction:** [Show personalities before they're tested]
- **The Hook:** [First genuinely scary/unsettling moment]

### 😰 Rising Dread (Chapters 3-6)
- **Escalating Events:** [Supernatural occurrences become undeniable]
- **Isolation Begins:** [Characters cut off from help/escape]
- **First Victim:** [Someone dies/disappears - establishes real danger]
- **Attempts to Rationalize:** [Characters try to explain away the horror]
- **Research/Investigation:** [Learning about the threat's history]

### 😱 Full Horror (Chapters 7-10)
- **Point of No Return:** [Characters realize they're truly trapped]
- **Major Losses:** [Multiple deaths, hope lost]
- **Truth Revealed:** [The full nature of the threat is understood]
- **Protagonist's Breaking Point:** [Their defenses/sanity crumble]
- **Desperate Measures:** [Characters attempt increasingly risky solutions]

### 🌅 Climax & Resolution (Chapters 11-12)
- **Final Confrontation:** [Face the horror directly]
- **Ultimate Sacrifice:** [What must be given up to survive/win?]
- **Resolution:** [Is the horror defeated? Escaped? Does it win?]
- **New Normal:** [How are survivors changed? Is it really over?]

## 👻 Horror Scenes & Setpieces

### 😨 Key Scare Moments
1. **The First Real Scare:** [When horror becomes undeniable]
2. **The False Relief:** [Moment when characters think they're safe]
3. **The Revelation:** [Terrifying truth is revealed]
4. **The Chase:** [Characters flee from the horror]
5. **The Final Scare:** [Last moment of terror]

### 🩸 Death Scenes (If Applicable)
- **Death 1:** [Who, how, what it represents]
- **Death 2:** [Who, how, what it represents]
- **Death 3:** [Who, how, what it represents]

---

## 🌙 Chapter 1: The Calm Before

[Begin with a sense of normalcy that will be shattered. Establish your characters and setting, but let unease creep in at the edges.]

The house on Elm Street had stood empty for three years, and [protagonist] had driven past it every day on the way to work, never giving it a second thought. Until today. Today, there was a light in the upstairs window—a warm, yellow glow that seemed to pulse like a heartbeat.

[Continue with subtle wrongness building. Show character's normal life, but plant seeds of the horror to come...]

---

## 😱 Horror Writing Techniques
- [ ] **Show, Don't Tell:** Let readers discover horror through details
- [ ] **Less is More:** Sometimes what's not shown is scarier
- [ ] **Sensory Details:** Use all five senses to create dread
- [ ] **Pacing:** Build tension slowly, release in sharp bursts
- [ ] **Vulnerability:** Put characters in helpless situations
- [ ] **The Uncanny:** Make familiar things seem wrong/threatening
- [ ] **Escalation:** Each scare should top the last

## 🎭 Themes to Explore
- The price of curiosity
- Guilt and punishment
- The thin line between sanity and madness
- What we fear says about who we are
- The past coming back to haunt us
- Isolation and helplessness
- The corruption of innocence""",
        "category": "Horror",
        "word_count_target": 62500,
        "estimated_time": "3-6 months"
    }
]

# Pydantic Models
class UserCreate(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    name: str = Field(..., min_length=2, description="User's full name")

class UserLogin(BaseModel):
    email: str
    password: str

class FolderCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[str] = None
    color: Optional[str] = "#3B82F6"

class FolderUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None

class DocumentCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = ""
    template_id: Optional[str] = None
    folder_id: Optional[str] = None
    status: DocumentStatus = DocumentStatus.DRAFT
    tags: List[str] = []

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    status: Optional[DocumentStatus] = None
    tags: Optional[List[str]] = None
    folder_id: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

class DocumentFromTemplateCreate(BaseModel):
    template_id: str = Field(..., description="Template ID to use")
    title: str = Field(..., min_length=1, max_length=200, description="Document title")
    folder_id: Optional[str] = None

# Helper functions
def get_user_id_from_email(email: str) -> Optional[int]:
    """Get user ID from email"""
    try:
        result = db_service.execute_query(
            "SELECT id FROM users WHERE email = %s AND is_active = TRUE",
            (email,),
            fetch='one'
        )
        return result['id'] if result else None
    except Exception:
        return None

def get_user_by_id(user_id: int) -> Optional[dict]:
    """Get user details by ID"""
    try:
        result = db_service.execute_query(
            "SELECT id, username, name, email, created_at, last_login, preferences FROM users WHERE id = %s AND is_active = TRUE",
            (user_id,),
            fetch='one'
        )
        return dict(result) if result else None
    except Exception:
        return None

def calculate_reading_time(content: str) -> int:
    """Calculate reading time in minutes (average 200 words per minute)"""
    word_count = len(content.split()) if content else 0
    return max(1, word_count // 200)

def calculate_word_count(content: str) -> int:
    """Calculate word count"""
    return len(content.split()) if content else 0

def calculate_character_count(content: str) -> int:
    """Calculate character count"""
    return len(content) if content else 0

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(user_id: int) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(weeks=1),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """Get current user ID from JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# App initialization
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    try:
        logger.info("Initializing database...")
        db_service.init_database()
        logger.info("Database initialized successfully")
        yield
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        yield
    finally:
        logger.info("Closing database connections...")
        db_service.close()

app = FastAPI(
    title="DOG Writer",
    description="Google Docs-Like Document Management System with PostgreSQL",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health endpoints
@app.get("/")
async def root():
    db_health = db_service.health_check()
    return {
        "message": "DOG Writer - Google Docs-Like Document Management System",
        "version": "2.0.0",
        "status": "healthy",
        "database": db_health['status'],
        "features": [
            "postgresql_database",
            "document_management",
            "folder_organization", 
            "version_control",
            "analytics_tracking",
            "template_system",
            "auto_save",
            "favorites",
            "search_and_filter"
        ],
        "statistics": {
            "total_users": db_health.get('total_users', 0),
            "total_documents": db_health.get('total_documents', 0),
            "total_templates": len(templates_store)
        }
    }

@app.get("/api/health")
async def health_check():
    db_health = db_service.health_check()
    
    # Get additional metrics
    try:
        folder_count = db_service.execute_query("SELECT COUNT(*) as count FROM folders", fetch='one')
        version_count = db_service.execute_query("SELECT COUNT(*) as count FROM document_versions", fetch='one')
    except:
        folder_count = {"count": 0}
        version_count = {"count": 0}
    
    return {
        "status": db_health['status'],
        "timestamp": datetime.utcnow().isoformat(),
        "database": db_health,
        "metrics": {
            "users_count": db_health.get('total_users', 0),
            "documents_count": db_health.get('total_documents', 0),
            "folders_count": folder_count['count'],
            "templates_count": len(templates_store),
            "document_versions_count": version_count['count']
        }
    }


# Authentication endpoints
@app.post("/api/auth/register")
async def register(user_data: UserCreate) -> TokenResponse:
    try:
        logger.info(f"Registration attempt for email: {user_data.email}")
        logger.info(f"Registration data: name='{user_data.name}', email='{user_data.email}', password_length={len(user_data.password)}")
        
        # Use auth service for registration
        result = auth_service.register_user(
            username=user_data.email.split('@')[0],  # Use email prefix as username
            email=user_data.email,
            password=user_data.password,
            name=user_data.name
        )
        
        user_info = result['user']
        access_token = create_access_token(user_info['id'])
        
        logger.info(f"New user registered: {user_data.email}")
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user={
                "id": user_info['id'],
                "name": user_info['name'],
                "email": user_info['email'],
                "created_at": user_info['created_at']
            }
        )
    except AuthenticationError as e:
        logger.error(f"Authentication error during registration: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except DatabaseError as e:
        logger.error(f"Database error during registration: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected registration error: {type(e).__name__}: {e}")
        import traceback
        logger.error(f"Registration traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/api/auth/login")
async def login(login_data: UserLogin) -> TokenResponse:
    try:
        # Use auth service for login
        result = auth_service.login_user(login_data.email, login_data.password)
        
        user_info = result['user']
        access_token = create_access_token(user_info['id'])
        
        logger.info(f"User logged in: {login_data.email}")
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user={
                "id": user_info['id'],
                "name": user_info['name'],
                "email": user_info['email'],
                "last_login": user_info.get('last_login')
            }
        )
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.get("/api/auth/profile")
async def get_profile(user_id: int = Depends(get_current_user_id)):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user statistics
    try:
        doc_stats = db_service.execute_query(
            "SELECT COUNT(*) as total_documents, COALESCE(SUM(word_count), 0) as total_words, COUNT(CASE WHEN is_favorite THEN 1 END) as favorite_documents FROM documents WHERE user_id = %s",
            (user_id,),
            fetch='one'
        )
        
        folder_stats = db_service.execute_query(
            "SELECT COUNT(*) as total_folders FROM folders WHERE user_id = %s",
            (user_id,),
            fetch='one'
        )
        
        user['statistics'] = {
            "total_documents": doc_stats['total_documents'] if doc_stats else 0,
            "total_words": doc_stats['total_words'] if doc_stats else 0,
            "total_folders": folder_stats['total_folders'] if folder_stats else 0,
            "favorite_documents": doc_stats['favorite_documents'] if doc_stats else 0
        }
    except Exception as e:
        logger.error(f"Error getting user statistics: {e}")
        user['statistics'] = {"total_documents": 0, "total_words": 0, "total_folders": 0, "favorite_documents": 0}
    
    return user

# Templates endpoints
@app.get("/api/templates")
async def get_templates():
    return templates_store

@app.get("/api/templates/{template_id}")
async def get_template(template_id: str):
    template = next((t for t in templates_store if t['id'] == template_id), None)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

# Folder management endpoints
@app.get("/api/folders")
async def get_folders(user_id: int = Depends(get_current_user_id)):
    try:
        folders = db_service.execute_query(
            """SELECT f.*, 
               (SELECT COUNT(*) FROM documents d WHERE d.folder_id = f.id) as document_count
               FROM folders f 
               WHERE f.user_id = %s 
               ORDER BY f.created_at DESC""",
            (user_id,),
            fetch='all'
        )
        return folders
    except DatabaseError as e:
        logger.error(f"Error fetching folders: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch folders")

@app.post("/api/folders")
async def create_folder(folder_data: FolderCreate, user_id: int = Depends(get_current_user_id)):
    try:
        folder_id = str(uuid.uuid4())
        
        result = db_service.execute_query(
            """INSERT INTO folders (id, user_id, name, parent_id, color, created_at, updated_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s)
               RETURNING id, name, parent_id, color, created_at""",
            (folder_id, user_id, folder_data.name, folder_data.parent_id, folder_data.color, datetime.utcnow(), datetime.utcnow()),
            fetch='one'
        )
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create folder")
            
        return {
            "id": result['id'],
            "name": result['name'],
            "parent_id": result['parent_id'],
            "color": result['color'],
            "created_at": result['created_at'].isoformat() if result['created_at'] else None,
            "document_count": 0
        }
        
    except DatabaseError as e:
        logger.error(f"Error creating folder: {e}")
        raise HTTPException(status_code=500, detail="Failed to create folder")

@app.put("/api/folders/{folder_id}")
async def update_folder(folder_id: str, folder_data: FolderUpdate, user_id: int = Depends(get_current_user_id)):
    try:
        # Check if folder exists and belongs to user
        folder = db_service.execute_query(
            "SELECT id, name, color FROM folders WHERE id = %s AND user_id = %s",
            (folder_id, user_id),
            fetch='one'
        )
        
        if not folder:
            raise HTTPException(status_code=404, detail="Folder not found")
        
        # Update fields
        updates = []
        params = []
        
        if folder_data.name is not None:
            updates.append("name = %s")
            params.append(folder_data.name)
        if folder_data.color is not None:
            updates.append("color = %s")
            params.append(folder_data.color)
        
        if not updates:
            return folder
        
        updates.append("updated_at = %s")
        params.extend([datetime.utcnow(), folder_id, user_id])
        
        result = db_service.execute_query(
            f"UPDATE folders SET {', '.join(updates)} WHERE id = %s AND user_id = %s RETURNING id, name, color, updated_at",
            params,
            fetch='one'
        )
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to update folder")
        
        return result
        
    except DatabaseError as e:
        logger.error(f"Error updating folder: {e}")
        raise HTTPException(status_code=500, detail="Failed to update folder")

@app.delete("/api/folders/{folder_id}")
async def delete_folder(folder_id: str, user_id: int = Depends(get_current_user_id)):
    try:
        # Check if folder exists and belongs to user
        folder = db_service.execute_query(
            "SELECT id FROM folders WHERE id = %s AND user_id = %s",
            (folder_id, user_id),
            fetch='one'
        )
        
        if not folder:
            raise HTTPException(status_code=404, detail="Folder not found")
        
        # Move documents out of this folder
        db_service.execute_query(
            "UPDATE documents SET folder_id = NULL WHERE folder_id = %s AND user_id = %s",
            (folder_id, user_id)
        )
        
        # Delete the folder
        result = db_service.execute_query(
            "DELETE FROM folders WHERE id = %s AND user_id = %s",
            (folder_id, user_id)
        )
        
        return {"message": "Folder deleted successfully"}
        
    except DatabaseError as e:
        logger.error(f"Error deleting folder: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete folder")

# Document management endpoints
@app.get("/api/documents")
async def get_documents(
    user_id: int = Depends(get_current_user_id),
    folder_id: Optional[str] = Query(None),
    status: Optional[DocumentStatus] = Query(None),
    search: Optional[str] = Query(None),
    limit: Optional[int] = Query(50),
    offset: Optional[int] = Query(0)
):
    try:
        # Build query conditions
        conditions = ["user_id = %s"]
        params = [user_id]
        
        if folder_id:
            conditions.append("folder_id = %s")
            params.append(folder_id)
        
        if status:
            conditions.append("status = %s")
            params.append(status.value)
        
        if search:
            conditions.append("(title ILIKE %s OR content ILIKE %s)")
            search_term = f"%{search}%"
            params.extend([search_term, search_term])
        
        # Get total count
        count_query = f"SELECT COUNT(*) as count FROM documents WHERE {' AND '.join(conditions)}"
        total_count = db_service.execute_query(count_query, params, fetch='one')['count']
        
        # Get documents
        query = f"""
            SELECT id, title, content, status, tags, is_favorite, word_count, 
                   created_at, updated_at, folder_id, series_id
            FROM documents 
            WHERE {' AND '.join(conditions)}
            ORDER BY updated_at DESC
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        
        documents = db_service.execute_query(query, params, fetch='all')
        
        # Format response
        for doc in documents:
            # Parse tags from JSON if needed
            if isinstance(doc['tags'], str):
                try:
                    doc['tags'] = json.loads(doc['tags'])
                except:
                    doc['tags'] = []
            
            doc['created_at'] = doc['created_at'].isoformat() if doc['created_at'] else None
            doc['updated_at'] = doc['updated_at'].isoformat() if doc['updated_at'] else None
        
        return {
            "documents": documents,
            "total_count": total_count,
            "page_info": {
                "has_next": offset + limit < total_count,
                "has_previous": offset > 0,
                "current_offset": offset,
                "limit": limit
            }
        }
    except DatabaseError as e:
        logger.error(f"Error fetching documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch documents")

@app.post("/api/documents/from-template")
async def create_document_from_template(doc_data: DocumentFromTemplateCreate, user_id: int = Depends(get_current_user_id)):
    try:
        logger.info(f"🎯 TEMPLATE ENDPOINT CALLED: template_id={doc_data.template_id}, title={doc_data.title}, user_id={user_id}")
        
        # Find the template
        template = next((t for t in templates_store if t['id'] == doc_data.template_id), None)
        if not template:
            logger.error(f"❌ Template not found: {doc_data.template_id}")
            raise HTTPException(status_code=404, detail="Template not found")
        
        logger.info(f"✅ Template found: {template['title']}")
        
        doc_id = str(uuid.uuid4())
        content = template['content']
        
        # Calculate analytics
        word_count = calculate_word_count(content)
        
        logger.info(f"📝 Creating document with content length: {len(content)} characters, {word_count} words")
        
        result = db_service.execute_query(
            """INSERT INTO documents (id, user_id, title, content, folder_id, status, tags, word_count, created_at, updated_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
               RETURNING id, title, content, folder_id, status, tags, word_count, created_at, updated_at""",
            (doc_id, user_id, doc_data.title, content, doc_data.folder_id, 'draft', json.dumps([]), word_count, datetime.utcnow(), datetime.utcnow()),
            fetch='one'
        )
        
        if not result:
            logger.error(f"❌ Failed to create document from template")
            raise HTTPException(status_code=500, detail="Failed to create document from template")
        
        # Format response
        document = dict(result)
        document['tags'] = json.loads(document['tags']) if document['tags'] else []
        document['created_at'] = document['created_at'].isoformat() if document['created_at'] else None
        document['updated_at'] = document['updated_at'].isoformat() if document['updated_at'] else None
        
        logger.info(f"🎉 TEMPLATE DOCUMENT CREATED SUCCESSFULLY: {document['title']} (ID: {document['id']}) by user {user_id}")
        return document
        
    except DatabaseError as e:
        logger.error(f"❌ Database error creating document from template: {e}")
        raise HTTPException(status_code=500, detail="Failed to create document from template")

@app.post("/api/documents")
async def create_document(doc_data: DocumentCreate, user_id: int = Depends(get_current_user_id)):
    try:
        logger.info(f"🔵 REGULAR DOCUMENT ENDPOINT CALLED: title={doc_data.title}, template_id={doc_data.template_id}, user_id={user_id}")
        
        doc_id = str(uuid.uuid4())
        
        # Use template content if provided
        content = doc_data.content
        if doc_data.template_id:
            logger.info(f"⚠️  USING TEMPLATE IN REGULAR ENDPOINT: {doc_data.template_id}")
            template = next((t for t in templates_store if t['id'] == doc_data.template_id), None)
            if template:
                content = template['content']
                logger.info(f"📝 Template content applied: {len(content)} characters")
        
        # Calculate analytics
        word_count = calculate_word_count(content)
        
        result = db_service.execute_query(
            """INSERT INTO documents (id, user_id, title, content, folder_id, status, tags, word_count, created_at, updated_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
               RETURNING id, title, content, folder_id, status, tags, word_count, created_at, updated_at""",
            (doc_id, user_id, doc_data.title, content, doc_data.folder_id, doc_data.status.value, json.dumps(doc_data.tags), word_count, datetime.utcnow(), datetime.utcnow()),
            fetch='one'
        )
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create document")
        
        # Format response
        document = dict(result)
        document['tags'] = json.loads(document['tags']) if document['tags'] else []
        document['created_at'] = document['created_at'].isoformat() if document['created_at'] else None
        document['updated_at'] = document['updated_at'].isoformat() if document['updated_at'] else None
        
        logger.info(f"🔵 REGULAR DOCUMENT CREATED: {document['title']} (ID: {document['id']}) by user {user_id}")
        return document
        
    except DatabaseError as e:
        logger.error(f"Error creating document: {e}")
        raise HTTPException(status_code=500, detail="Failed to create document")

@app.get("/api/documents/{document_id}")
async def get_document(document_id: str, user_id: int = Depends(get_current_user_id)):
    try:
        document = db_service.execute_query(
            """SELECT id, title, content, status, tags, is_favorite, word_count, 
                      created_at, updated_at, folder_id, series_id
               FROM documents 
               WHERE id = %s AND user_id = %s""",
            (document_id, user_id),
            fetch='one'
        )
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Format response
        doc = dict(document)
        doc['tags'] = json.loads(doc['tags']) if doc['tags'] else []
        doc['created_at'] = doc['created_at'].isoformat() if doc['created_at'] else None
        doc['updated_at'] = doc['updated_at'].isoformat() if doc['updated_at'] else None
        
        return doc
        
    except DatabaseError as e:
        logger.error(f"Error fetching document: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch document")

@app.put("/api/documents/{document_id}")
async def update_document(document_id: str, doc_data: DocumentUpdate, user_id: int = Depends(get_current_user_id)):
    try:
        # Check if document exists
        existing = db_service.execute_query(
            "SELECT id, content FROM documents WHERE id = %s AND user_id = %s",
            (document_id, user_id),
            fetch='one'
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Build update query
        updates = []
        params = []
        
        if doc_data.title is not None:
            updates.append("title = %s")
            params.append(doc_data.title)
        
        if doc_data.content is not None:
            # Create version for significant changes
            if abs(len(doc_data.content) - len(existing['content'] or '')) > 50:
                version_id = str(uuid.uuid4())
                db_service.execute_query(
                    """INSERT INTO document_versions (id, document_id, content, title, created_at, version_number)
                       VALUES (%s, %s, %s, %s, %s, 
                               (SELECT COALESCE(MAX(version_number), 0) + 1 FROM document_versions WHERE document_id = %s))""",
                    (version_id, document_id, existing['content'], 
                     db_service.execute_query("SELECT title FROM documents WHERE id = %s", (document_id,), fetch='one')['title'],
                     datetime.utcnow(), document_id)
                )
            
            updates.append("content = %s")
            params.append(doc_data.content)
            updates.append("word_count = %s")
            params.append(calculate_word_count(doc_data.content))
        
        if doc_data.status is not None:
            updates.append("status = %s")
            params.append(doc_data.status.value)
        
        if doc_data.tags is not None:
            updates.append("tags = %s")
            params.append(json.dumps(doc_data.tags))
        
        if doc_data.folder_id is not None:
            updates.append("folder_id = %s")
            params.append(doc_data.folder_id)
        
        if not updates:
            return await get_document(document_id, user_id)
        
        updates.append("updated_at = %s")
        params.extend([datetime.utcnow(), document_id, user_id])
        
        result = db_service.execute_query(
            f"""UPDATE documents SET {', '.join(updates)} 
                WHERE id = %s AND user_id = %s
                RETURNING id, title, content, status, tags, is_favorite, word_count, created_at, updated_at, folder_id""",
            params,
            fetch='one'
        )
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to update document")
        
        # Format response
        doc = dict(result)
        doc['tags'] = json.loads(doc['tags']) if doc['tags'] else []
        doc['created_at'] = doc['created_at'].isoformat() if doc['created_at'] else None
        doc['updated_at'] = doc['updated_at'].isoformat() if doc['updated_at'] else None
        
        return doc
        
    except DatabaseError as e:
        logger.error(f"Error updating document: {e}")
        raise HTTPException(status_code=500, detail="Failed to update document")

@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str, user_id: int = Depends(get_current_user_id)):
    try:
        # Check if document exists
        document = db_service.execute_query(
            "SELECT id, title FROM documents WHERE id = %s AND user_id = %s",
            (document_id, user_id),
            fetch='one'
        )
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete document versions first (foreign key constraint)
        db_service.execute_query(
            "DELETE FROM document_versions WHERE document_id = %s",
            (document_id,)
        )
        
        # Delete the document
        db_service.execute_query(
            "DELETE FROM documents WHERE id = %s AND user_id = %s",
            (document_id, user_id)
        )
        
        logger.info(f"Document deleted: {document['title']} by user {user_id}")
        return {"message": "Document deleted successfully"}
        
    except DatabaseError as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete document")

# Document versions
@app.get("/api/documents/{document_id}/versions")
async def get_document_versions(document_id: str, user_id: int = Depends(get_current_user_id)):
    try:
        # Verify document ownership
        document = db_service.execute_query(
            "SELECT id FROM documents WHERE id = %s AND user_id = %s",
            (document_id, user_id),
            fetch='one'
        )
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        versions = db_service.execute_query(
            """SELECT id, content, title, created_at, version_number, change_summary
               FROM document_versions 
               WHERE document_id = %s 
               ORDER BY version_number DESC""",
            (document_id,),
            fetch='all'
        )
        
        # Format response
        for version in versions:
            version['created_at'] = version['created_at'].isoformat() if version['created_at'] else None
        
        return {"versions": versions}
        
    except DatabaseError as e:
        logger.error(f"Error fetching document versions: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch document versions")

# Document favorites
@app.post("/api/documents/{document_id}/favorite")
async def toggle_document_favorite(document_id: str, user_id: int = Depends(get_current_user_id)):
    try:
        # Check if document exists
        document = db_service.execute_query(
            "SELECT id, is_favorite FROM documents WHERE id = %s AND user_id = %s",
            (document_id, user_id),
            fetch='one'
        )
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Toggle favorite status
        new_status = not document['is_favorite']
        
        db_service.execute_query(
            "UPDATE documents SET is_favorite = %s WHERE id = %s AND user_id = %s",
            (new_status, document_id, user_id)
        )
        
        return {
            "document_id": document_id,
            "is_favorite": new_status,
            "message": f"Document {'added to' if new_status else 'removed from'} favorites"
        }
        
    except DatabaseError as e:
        logger.error(f"Error toggling favorite: {e}")
        raise HTTPException(status_code=500, detail="Failed to toggle favorite")

@app.get("/api/documents/favorites")
async def get_favorite_documents(user_id: int = Depends(get_current_user_id)):
    try:
        documents = db_service.execute_query(
            """SELECT id, title, content, status, tags, word_count, created_at, updated_at, folder_id
               FROM documents 
               WHERE user_id = %s AND is_favorite = TRUE
               ORDER BY updated_at DESC""",
            (user_id,),
            fetch='all'
        )
        
        # Format response
        for doc in documents:
            doc['tags'] = json.loads(doc['tags']) if doc['tags'] else []
            doc['created_at'] = doc['created_at'].isoformat() if doc['created_at'] else None
            doc['updated_at'] = doc['updated_at'].isoformat() if doc['updated_at'] else None
            doc['is_favorite'] = True
        
        return documents
        
    except DatabaseError as e:
        logger.error(f"Error fetching favorite documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch favorite documents")

# Analytics endpoints
@app.get("/api/analytics/overview")
async def get_analytics_overview(user_id: int = Depends(get_current_user_id)):
    try:
        # Get overview statistics
        overview_stats = db_service.execute_query(
            """SELECT 
                COUNT(*) as total_documents,
                COALESCE(SUM(word_count), 0) as total_words,
                COUNT(CASE WHEN is_favorite THEN 1 END) as favorite_documents
               FROM documents 
               WHERE user_id = %s""",
            (user_id,),
            fetch='one'
        )
        
        folder_stats = db_service.execute_query(
            "SELECT COUNT(*) as total_folders FROM folders WHERE user_id = %s",
            (user_id,),
            fetch='one'
        )
        
        # Status distribution
        status_stats = db_service.execute_query(
            """SELECT status, COUNT(*) as count 
               FROM documents 
               WHERE user_id = %s 
               GROUP BY status""",
            (user_id,),
            fetch='all'
        )
        
        status_counts = {stat['status']: stat['count'] for stat in status_stats}
        
        # Recent documents
        recent_docs = db_service.execute_query(
            """SELECT id, title, updated_at, word_count
               FROM documents 
               WHERE user_id = %s 
               ORDER BY updated_at DESC 
               LIMIT 5""",
            (user_id,),
            fetch='all'
        )
        
        # Format recent docs
        for doc in recent_docs:
            doc['updated_at'] = doc['updated_at'].isoformat() if doc['updated_at'] else None
        
        return {
            "overview": {
                "total_words": overview_stats['total_words'] or 0,
                "total_documents": overview_stats['total_documents'] or 0,
                "total_folders": folder_stats['total_folders'] if folder_stats else 0,
                "favorite_documents": overview_stats['favorite_documents'] or 0
            },
            "status_distribution": status_counts,
            "recent_documents": recent_docs
        }
        
    except DatabaseError as e:
        logger.error(f"Error fetching analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch analytics")

# Auto-save endpoint
@app.put("/api/documents/{document_id}/auto-save")
async def auto_save_document(document_id: str, content: str = Query(...), user_id: int = Depends(get_current_user_id)):
    """Auto-save document content without creating versions"""
    try:
        # Check if document exists and belongs to user
        existing = db_service.execute_query(
            "SELECT id, content FROM documents WHERE id = %s AND user_id = %s",
            (document_id, user_id),
            fetch='one'
        )
        
        if not existing:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Only save if content changed
        if existing['content'] != content:
            word_count = calculate_word_count(content)
            
            db_service.execute_query(
                """UPDATE documents 
                   SET content = %s, word_count = %s, updated_at = %s 
                   WHERE id = %s AND user_id = %s""",
                (content, word_count, datetime.utcnow(), document_id, user_id)
            )
        
        return {"status": "auto_saved", "timestamp": datetime.utcnow().isoformat()}
        
    except DatabaseError as e:
        logger.error(f"Error auto-saving document: {e}")
        raise HTTPException(status_code=500, detail="Failed to auto-save document")

# Simple endpoints for compatibility
@app.get("/api/series")
async def get_series(user_id: int = Depends(get_current_user_id)):
    try:
        series = db_service.execute_query(
            "SELECT id, name, description, total_chapters, total_words, created_at FROM series WHERE user_id = %s ORDER BY created_at DESC",
            (user_id,),
            fetch='all'
        )
        # Format dates
        for s in series:
            s['created_at'] = s['created_at'].isoformat() if s['created_at'] else None
        return series
    except:
        return []

@app.get("/api/goals")
async def get_goals():
    return []

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False) 