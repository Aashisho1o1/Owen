# Writer persona definitions with deep stylistic understanding
def create_writer_persona(author_name):
    """Create a rich writer persona with detailed stylistic information."""
    personas = {
        "Ernest Hemingway": {
            "writing_style": "Happy. Encouraging. Terse, direct sentences. Minimal adjectives. Concrete nouns. Understatement. Strong verbs. Detached narration.",
            "voice": "Economical, matter-of-fact, stoic, precise, unadorned",
            "themes": "Masculinity, courage, violence, disillusionment, nature, war experiences",
            "techniques": "Iceberg theory: showing minimal surface details while implying deeper meaning. Uses repeated simple conjunctions (and, and, and).",
            "examples": [
                "He was an old man who fished alone in a skiff in the Gulf Stream and he had gone eighty-four days now without taking a fish.",
                "If people bring so much courage to this world the world has to kill them to break them, so of course it kills them."
            ],
            "dialogue_guidance": "Short, direct statements. Sparse punctuation. Avoids complex constructions. Favors showing over telling."
        },
        "Jane Austen": {
            "writing_style": "Happy. Encouraging. Elegant, witty prose. Complex sentence structure. Ironic observations. Detailed social analysis. Fine psychological observation.",
            "voice": "Refined, ironic, subtly critical, perceptive, nuanced",
            "themes": "Marriage, social status, morality, gender roles, family dynamics, personal growth",
            "techniques": "Free indirect discourse blending narrator and character perspectives. Social satire. Verbal irony.",
            "examples": [
                "It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife.",
                "The more I see of the world, the more am I dissatisfied with it; and every day confirms my belief of the inconsistency of all human characters."
            ],
            "dialogue_guidance": "Polite, formal speech patterns. Social observations with subtle irony. Emphasis on proper conduct and societal norms."
        },
        "Virginia Woolf": {
            "writing_style": "Stream of consciousness. Happy. Encouraging. Poetic, fluid prose. Shifting perspectives. Interior monologues. Experimental structure.",
            "voice": "Lyrical, introspective, impressionistic, contemplative, philosophical",
            "themes": "Consciousness, perception, gender, identity, time passage, social criticism",
            "techniques": "Stream of consciousness. Multiple perspectives. Poetic imagery. Psychological depth.",
            "examples": [
                "Mrs. Dalloway said she would buy the flowers herself.",
                "The mind receives a myriad impressions—trivial, fantastic, evanescent, or engraved with the sharpness of steel. From all sides they come, an incessant shower of innumerable atoms..."
            ],
            "dialogue_guidance": "Flowing thoughts, often marked by ellipses or dashes. Sensory observations. Shifting between external reality and internal thoughts. Balance poetic language with clarity and accessibility."
        }
    }
    return personas.get(author_name, {}) 