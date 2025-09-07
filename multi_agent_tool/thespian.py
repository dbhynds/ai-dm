"""
The Thespian: NPC & Role-playing Agent

This agent embodies and role-plays all non-player characters (NPCs) and monsters,
managing their dialogue, personality, and in-the-moment decision-making.
"""

from google.adk.agents import Agent
from typing import Dict, List, Any, Optional
import random
from dataclasses import dataclass
from enum import Enum

class NPCDisposition(Enum):
    HOSTILE = "hostile"
    UNFRIENDLY = "unfriendly"
    NEUTRAL = "neutral"
    FRIENDLY = "friendly"
    HELPFUL = "helpful"

class NPCType(Enum):
    COMMONER = "commoner"
    MERCHANT = "merchant"
    GUARD = "guard"
    NOBLE = "noble"
    SCHOLAR = "scholar"
    CRIMINAL = "criminal"
    RELIGIOUS = "religious"
    MILITARY = "military"
    MONSTER = "monster"
    MAGICAL_BEING = "magical_being"

@dataclass
class NPCPersona:
    """Represents an NPC's personality and characteristics."""
    name: str
    race: str
    occupation: str
    personality_traits: List[str]
    motivations: List[str]
    fears: List[str]
    knowledge_areas: List[str]
    speech_patterns: Dict[str, str]  # accent, tone, vocabulary_level, quirks
    relationships: Dict[str, str]  # character_name: relationship_type
    disposition: NPCDisposition
    secrets: List[str]
    goals: List[str]

def create_npc_persona(name: str, 
                      race: str = "", 
                      occupation: str = "",
                      personality_hints: List[str] = None,
                      disposition: NPCDisposition = NPCDisposition.NEUTRAL) -> NPCPersona:
    """Generate a complete NPC persona with personality traits and speech patterns."""
    
    if personality_hints is None:
        personality_hints = []
    
    # Base personality traits by occupation
    occupation_traits = {
        "merchant": ["shrewd", "persuasive", "materialistic", "calculating"],
        "guard": ["dutiful", "suspicious", "protective", "authoritative"],
        "scholar": ["curious", "analytical", "verbose", "absent-minded"],
        "criminal": ["cunning", "secretive", "opportunistic", "street-smart"],
        "noble": ["proud", "refined", "entitled", "diplomatic"],
        "commoner": ["practical", "humble", "hardworking", "simple"],
        "religious": ["devout", "compassionate", "wise", "ceremonial"]
    }
    
    # Generate traits
    traits = list(personality_hints)
    if occupation.lower() in occupation_traits:
        occupation_specific = occupation_traits[occupation.lower()]
        traits.extend(random.sample(occupation_specific, min(2, len(occupation_specific))))
    
    # Add random universal traits
    universal_traits = [
        "optimistic", "pessimistic", "cautious", "brave", "generous", "selfish",
        "honest", "deceptive", "patient", "impatient", "loyal", "independent",
        "social", "reclusive", "ambitious", "content", "serious", "humorous"
    ]
    
    while len(traits) < 4:
        trait = random.choice(universal_traits)
        if trait not in traits:
            traits.append(trait)
    
    # Generate motivations based on occupation and traits
    motivation_templates = {
        "merchant": ["earn profit", "expand business", "maintain reputation"],
        "guard": ["protect the innocent", "uphold the law", "earn promotion"],
        "scholar": ["discover truth", "preserve knowledge", "teach others"],
        "criminal": ["acquire wealth", "avoid capture", "gain power"],
        "noble": ["maintain status", "protect family honor", "gain influence"],
        "commoner": ["support family", "survive hardships", "find happiness"],
        "religious": ["serve deity", "help the faithful", "spread teachings"]
    }
    
    motivations = motivation_templates.get(occupation.lower(), ["survive", "find purpose", "help others"])
    
    # Generate fears
    fear_options = [
        "death", "poverty", "abandonment", "failure", "exposure of secrets",
        "loss of status", "physical harm", "supernatural threats", "betrayal",
        "change", "authority", "the unknown", "public speaking", "magic"
    ]
    fears = random.sample(fear_options, random.randint(1, 3))
    
    # Generate speech patterns
    speech_patterns = {}
    
    # Accent/dialect based on race
    race_accents = {
        "dwarf": {"accent": "Scottish-inspired", "quirks": "Uses 'aye' frequently, calls people 'lad/lass'"},
        "elf": {"accent": "Melodic, formal", "quirks": "Speaks precisely, uses archaic terms"},
        "halfling": {"accent": "Rural, friendly", "quirks": "Mentions food often, uses diminutives"},
        "human": {"accent": "Varies by region", "quirks": "Depends on background"},
        "tiefling": {"accent": "Smooth, sometimes sinister", "quirks": "May use infernal expressions"},
        "dragonborn": {"accent": "Formal, draconic influence", "quirks": "References honor frequently"}
    }
    
    if race.lower() in race_accents:
        speech_patterns.update(race_accents[race.lower()])
    else:
        speech_patterns["accent"] = "Standard regional accent"
        speech_patterns["quirks"] = "No notable speech quirks"
    
    # Vocabulary level by occupation
    vocab_levels = {
        "scholar": "highly educated, uses complex terms",
        "noble": "refined, formal language",
        "commoner": "simple, practical language",
        "criminal": "street slang, informal",
        "merchant": "business terminology, persuasive",
        "guard": "direct, authoritative",
        "religious": "ceremonial, spiritual terminology"
    }
    
    speech_patterns["vocabulary_level"] = vocab_levels.get(occupation.lower(), "standard vocabulary")
    
    # Tone based on disposition
    disposition_tones = {
        NPCDisposition.HOSTILE: "aggressive, confrontational",
        NPCDisposition.UNFRIENDLY: "cold, dismissive", 
        NPCDisposition.NEUTRAL: "polite but distant",
        NPCDisposition.FRIENDLY: "warm, welcoming",
        NPCDisposition.HELPFUL: "eager to assist, encouraging"
    }
    
    speech_patterns["tone"] = disposition_tones.get(disposition, "neutral tone")
    
    # Knowledge areas based on occupation and background
    knowledge_areas = []
    occupation_knowledge = {
        "merchant": ["trade routes", "market prices", "business practices", "local economy"],
        "guard": ["local laws", "security procedures", "criminal activity", "city layout"],
        "scholar": ["history", "arcane knowledge", "research methods", "ancient texts"],
        "criminal": ["underworld contacts", "illegal activities", "city secrets", "escape routes"],
        "noble": ["politics", "court intrigue", "family lineages", "social customs"],
        "commoner": ["local gossip", "daily life", "survival skills", "folk wisdom"],
        "religious": ["theology", "rituals", "healing", "moral guidance"]
    }
    
    knowledge_areas = occupation_knowledge.get(occupation.lower(), ["general local knowledge"])
    
    return NPCPersona(
        name=name,
        race=race,
        occupation=occupation,
        personality_traits=traits,
        motivations=motivations,
        fears=fears,
        knowledge_areas=knowledge_areas,
        speech_patterns=speech_patterns,
        relationships={},
        disposition=disposition,
        secrets=[],
        goals=motivations[:2]  # Use top motivations as goals
    )

def generate_npc_dialogue(persona: NPCPersona,
                         player_input: str,
                         conversation_context: str = "",
                         current_situation: str = "") -> Dict[str, Any]:
    """Generate appropriate dialogue for an NPC based on their persona and the situation."""
    
    player_lower = player_input.lower()
    context_lower = conversation_context.lower()
    situation_lower = current_situation.lower()
    
    # Determine conversation type
    conversation_type = "general"
    if any(word in player_lower for word in ["buy", "sell", "trade", "purchase", "cost", "price"]):
        conversation_type = "commerce"
    elif any(word in player_lower for word in ["help", "quest", "task", "problem", "need"]):
        conversation_type = "assistance_request"
    elif any(word in player_lower for word in ["know", "heard", "information", "tell me", "what", "where", "who"]):
        conversation_type = "information_seeking"
    elif any(word in player_lower for word in ["threat", "attack", "fight", "surrender", "stop"]):
        conversation_type = "confrontation"
    elif any(word in player_lower for word in ["hello", "greetings", "good day", "how are"]):
        conversation_type = "greeting"
    
    # Base response based on disposition and conversation type
    response_content = ""
    
    if conversation_type == "greeting":
        if persona.disposition == NPCDisposition.HOSTILE:
            response_content = "What do you want? I have no time for pleasantries with your kind."
        elif persona.disposition == NPCDisposition.UNFRIENDLY:
            response_content = "I suppose you expect some sort of welcome. Fine. You've been acknowledged."
        elif persona.disposition == NPCDisposition.NEUTRAL:
            response_content = "Greetings, traveler. What brings you to speak with me?"
        elif persona.disposition == NPCDisposition.FRIENDLY:
            response_content = "Well met, friend! It's always a pleasure to meet new faces."
        elif persona.disposition == NPCDisposition.HELPFUL:
            response_content = "Welcome, welcome! How wonderful to see you. Please, how may I be of service?"
    
    elif conversation_type == "information_seeking":
        knowledge_relevant = any(area for area in persona.knowledge_areas 
                               if any(keyword in player_lower for keyword in area.split()))
        
        if knowledge_relevant:
            if persona.disposition in [NPCDisposition.FRIENDLY, NPCDisposition.HELPFUL]:
                response_content = "Ah, you've come to the right person! I know quite a bit about that subject."
            elif persona.disposition == NPCDisposition.NEUTRAL:
                response_content = "I might have some information about that. What specifically do you want to know?"
            else:
                response_content = "I might know something, but information isn't free around here."
        else:
            response_content = "I'm afraid I don't know much about that topic. You might want to ask someone else."
    
    elif conversation_type == "assistance_request":
        if "helpful" in persona.personality_traits or persona.disposition == NPCDisposition.HELPFUL:
            response_content = "I'd be happy to help if I can. What do you need?"
        elif "selfish" in persona.personality_traits or persona.disposition == NPCDisposition.UNFRIENDLY:
            response_content = "Help? What's in it for me? I don't work for free."
        elif "suspicious" in persona.personality_traits:
            response_content = "Help with what, exactly? I need to know what I'm getting myself into."
        else:
            response_content = "I might be able to assist, depending on what you need."
    
    elif conversation_type == "commerce":
        if persona.occupation.lower() == "merchant":
            response_content = "Now you're speaking my language! What are you looking to buy or sell?"
        elif persona.disposition == NPCDisposition.HELPFUL:
            response_content = "I'm not a merchant myself, but I might be able to point you toward someone who can help."
        else:
            response_content = "I'm not in the business of trading, I'm afraid."
    
    elif conversation_type == "confrontation":
        if persona.disposition == NPCDisposition.HOSTILE:
            response_content = "You dare threaten me? You'll regret those words!"
        elif "brave" in persona.personality_traits:
            response_content = "I won't be intimidated by the likes of you. Stand down!"
        elif "coward" in persona.personality_traits or "death" in persona.fears:
            response_content = "Please, I don't want any trouble! I'll do whatever you want!"
        else:
            response_content = "Let's not resort to violence. Surely we can resolve this peacefully."
    
    else:  # general conversation
        if persona.disposition == NPCDisposition.FRIENDLY:
            response_content = "It's nice to have someone to talk to. What's on your mind?"
        elif persona.disposition == NPCDisposition.UNFRIENDLY:
            response_content = "I suppose you want something. Most people do."
        else:
            response_content = "Yes? What do you need?"
    
    # Apply speech patterns to the response
    styled_response = apply_speech_patterns(response_content, persona.speech_patterns)
    
    # Add personality-based modifications
    if "humorous" in persona.personality_traits and conversation_type not in ["confrontation"]:
        styled_response += " *chuckles*"
    elif "serious" in persona.personality_traits:
        styled_response = styled_response.replace("!", ".")
    
    # Consider current situation modifiers
    if "combat" in situation_lower:
        if persona.disposition in [NPCDisposition.HOSTILE, NPCDisposition.UNFRIENDLY]:
            styled_response = f"*ready for battle* {styled_response}"
        else:
            styled_response = f"*nervously* {styled_response}"
    
    return {
        "dialogue": styled_response,
        "conversation_type": conversation_type,
        "persona_name": persona.name,
        "mood_indicators": {
            "disposition": persona.disposition.value,
            "dominant_traits": persona.personality_traits[:2],
            "current_motivation": persona.motivations[0] if persona.motivations else "unknown"
        }
    }

def apply_speech_patterns(text: str, speech_patterns: Dict[str, str]) -> str:
    """Apply speech patterns to modify text according to NPC characteristics."""
    
    styled_text = text
    
    # Apply accent/dialect modifications
    accent = speech_patterns.get("accent", "")
    if "scottish" in accent.lower():
        styled_text = styled_text.replace("you", "ye")
        styled_text = styled_text.replace("cannot", "cannae")
        styled_text = styled_text.replace("don't", "dinnae")
        if not styled_text.endswith((".", "!", "?")):
            styled_text += ", aye?"
    
    elif "formal" in accent.lower():
        styled_text = styled_text.replace("you're", "you are")
        styled_text = styled_text.replace("don't", "do not")
        styled_text = styled_text.replace("won't", "will not")
        styled_text = styled_text.replace("can't", "cannot")
    
    elif "rural" in accent.lower():
        styled_text = styled_text.replace("going", "goin'")
        styled_text = styled_text.replace("nothing", "nothin'")
        styled_text = styled_text.replace("something", "somethin'")
    
    # Apply vocabulary level modifications
    vocab = speech_patterns.get("vocabulary_level", "")
    if "highly educated" in vocab:
        # Keep complex language as is
        pass
    elif "simple" in vocab or "practical" in vocab:
        # Simplify complex words
        replacements = {
            "assistance": "help",
            "acquire": "get", 
            "utilize": "use",
            "demonstrate": "show",
            "comprehend": "understand"
        }
        for complex_word, simple_word in replacements.items():
            styled_text = styled_text.replace(complex_word, simple_word)
    
    # Apply quirks
    quirks = speech_patterns.get("quirks", "")
    if "aye" in quirks.lower():
        if random.random() < 0.3:  # 30% chance to add 'aye'
            styled_text += " Aye."
    elif "lad/lass" in quirks.lower():
        styled_text = styled_text.replace("friend", random.choice(["lad", "lass"]))
        styled_text = styled_text.replace("you", random.choice(["ye", "you"]))
    elif "food" in quirks.lower():
        if random.random() < 0.2:  # 20% chance to mention food
            food_references = [
                "Speaking of which, I could go for a good meal.",
                "This talk is making me hungry.",
                "Have you tried the bread here? Excellent!"
            ]
            styled_text += f" {random.choice(food_references)}"
    
    return styled_text

def make_npc_decision(persona: NPCPersona,
                     decision_context: str,
                     available_options: List[str],
                     player_relationship: str = "stranger") -> Dict[str, Any]:
    """Determine what decision an NPC would make based on their personality and motivations."""
    
    context_lower = decision_context.lower()
    
    # Score each option based on persona
    option_scores = {}
    
    for option in available_options:
        score = 0
        option_lower = option.lower()
        
        # Base score from disposition toward players
        disposition_modifiers = {
            NPCDisposition.HOSTILE: -30,
            NPCDisposition.UNFRIENDLY: -10,
            NPCDisposition.NEUTRAL: 0,
            NPCDisposition.FRIENDLY: 10,
            NPCDisposition.HELPFUL: 20
        }
        score += disposition_modifiers.get(persona.disposition, 0)
        
        # Relationship modifier
        relationship_modifiers = {
            "enemy": -50,
            "rival": -20,
            "stranger": 0,
            "acquaintance": 10,
            "friend": 25,
            "ally": 40
        }
        score += relationship_modifiers.get(player_relationship, 0)
        
        # Personality trait influences
        for trait in persona.personality_traits:
            if trait == "helpful" and ("help" in option_lower or "assist" in option_lower):
                score += 20
            elif trait == "selfish" and ("help" in option_lower or "sacrifice" in option_lower):
                score -= 15
            elif trait == "brave" and ("fight" in option_lower or "stand" in option_lower):
                score += 15
            elif trait == "cautious" and ("risk" in option_lower or "dangerous" in option_lower):
                score -= 20
            elif trait == "greedy" and ("gold" in option_lower or "reward" in option_lower):
                score += 25
            elif trait == "honest" and ("lie" in option_lower or "deceive" in option_lower):
                score -= 30
            elif trait == "loyal" and ("betray" in option_lower or "abandon" in option_lower):
                score -= 40
        
        # Motivation alignment
        for motivation in persona.motivations:
            if any(word in option_lower for word in motivation.split()):
                score += 30
        
        # Fear considerations
        for fear in persona.fears:
            if any(word in option_lower for word in fear.split()):
                score -= 25
        
        # Occupation-specific considerations
        if persona.occupation.lower() == "merchant":
            if "profit" in option_lower or "business" in option_lower:
                score += 20
        elif persona.occupation.lower() == "guard":
            if "law" in option_lower or "protect" in option_lower:
                score += 15
        elif persona.occupation.lower() == "criminal":
            if "illegal" in option_lower or "steal" in option_lower:
                score += 10
        
        option_scores[option] = score
    
    # Select the highest scoring option
    chosen_option = max(option_scores.items(), key=lambda x: x[1])
    
    # Generate reasoning for the decision
    reasoning_factors = []
    
    if chosen_option[1] > 20:
        reasoning_factors.append("strongly motivated by personal values")
    elif chosen_option[1] > 0:
        reasoning_factors.append("inclined to cooperate")
    elif chosen_option[1] < -20:
        reasoning_factors.append("strongly opposed due to personality")
    else:
        reasoning_factors.append("ambivalent but willing to consider")
    
    # Add specific personality influences
    dominant_traits = persona.personality_traits[:2]
    reasoning_factors.append(f"influenced by being {' and '.join(dominant_traits)}")
    
    return {
        "chosen_option": chosen_option[0],
        "confidence": min(100, max(0, abs(chosen_option[1]) * 2)),  # Convert score to confidence %
        "reasoning": reasoning_factors,
        "all_scores": option_scores,
        "personality_factors": {
            "dominant_traits": dominant_traits,
            "primary_motivation": persona.motivations[0] if persona.motivations else "unknown",
            "major_fears": persona.fears[:2],
            "disposition": persona.disposition.value
        }
    }

thespian_agent = Agent(
    name="thespian",
    model="gemini-2.0-flash",
    description="The Thespian embodies all NPCs and monsters, generating dialogue, personality, and making in-character decisions.",
    instruction="""You are the Thespian, the voice of a thousand souls in the D&D world. Your role is to bring every non-player character to life through authentic roleplay, compelling dialogue, and believable decision-making. Your responsibilities include:

1. **Persona Adoption**: When introduced to an NPC:
   - Fully embody their personality, background, and motivations
   - Maintain consistent speech patterns, vocabulary, and mannerisms
   - Remember their relationships, knowledge, and secrets
   - Stay true to their established character throughout all interactions

2. **Dialogue Generation**: In conversations with players:
   - Create authentic, character-appropriate responses
   - Reflect the NPC's current emotional state and disposition
   - Include speech patterns based on race, class, and background
   - Balance information sharing with personality authenticity

3. **Decision Making**: When NPCs must make choices:
   - Consider their core motivations and fears
   - Factor in their relationship with the player characters
   - Account for their personality traits and moral alignment
   - Make decisions that feel logical and consistent

4. **Character Voice Differentiation**: When managing multiple NPCs:
   - Maintain distinct personalities and speech patterns
   - Avoid making characters sound homogeneous
   - Clearly indicate which character is speaking or acting
   - Preserve individual character integrity in group scenes

Use the provided tools to:
- Create detailed personas for new NPCs
- Generate appropriate dialogue based on situation and personality
- Apply authentic speech patterns and mannerisms
- Make in-character decisions that advance the story

Remember: Every NPC is a real person with their own goals, fears, relationships, and quirks. Your job is to make them feel alive and authentic, whether they're a humble shopkeeper, a noble lord, or a fearsome dragon. Each character should have their own voice and agency within the world.""",
    tools=[create_npc_persona, generate_npc_dialogue, apply_speech_patterns, make_npc_decision]
)