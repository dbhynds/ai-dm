from google.adk.agents import Agent, SequentialAgent
import re
from typing import Dict, List, Any, Optional

# =============================================================================
# RULE VALIDATION FUNCTIONS
# =============================================================================

def validate_action_legality(
    action_description: str, 
    character_class: Optional[str] = None, 
    character_level: Optional[int] = None,
    spell_slots: Optional[Dict[int, int]] = None,
    current_hp: Optional[int] = None,
    max_hp: Optional[int] = None
) -> dict:
    """Validates whether a proposed D&D action is legal according to the rules."""
    
    action_lower = action_description.lower()
    
    validation_result = {
        "status": "success",
        "is_legal": True,
        "explanation": "",
        "suggestions": []
    }
    
    # Check for impossible actions
    impossible_patterns = [
        (r"cast.*wish.*without.*spell slot", "Wish requires a 9th-level spell slot"),
        (r"attack.*while.*unconscious", "Unconscious creatures cannot take actions"),
        (r"cast.*spell.*without.*spell slot", "Spellcasting requires available spell slots"),
        (r"move.*more than.*\d+.*feet", "Movement is limited by speed"),
    ]
    
    for pattern, reason in impossible_patterns:
        if re.search(pattern, action_lower):
            validation_result["is_legal"] = False
            validation_result["explanation"] = reason
            return validation_result
    
    # Spell casting validation
    if "cast" in action_lower and "spell" in action_lower:
        if character_class and character_class.lower() not in ["wizard", "sorcerer", "cleric", "druid", "bard", "warlock", "paladin", "ranger", "eldritch knight", "arcane trickster"]:
            validation_result["is_legal"] = False
            validation_result["explanation"] = f"{character_class} cannot cast spells (unless they have a subclass feature)"
            return validation_result
        
        if spell_slots is not None and all(slots == 0 for slots in spell_slots.values()):
            validation_result["is_legal"] = False
            validation_result["explanation"] = "No spell slots remaining"
            return validation_result
    
    # Level-based restrictions
    if character_level is not None:
        if "9th level spell" in action_lower and character_level < 17:
            validation_result["is_legal"] = False
            validation_result["explanation"] = f"9th level spells require character level 17+ (current level: {character_level})"
            return validation_result
    
    # HP-based restrictions  
    if current_hp is not None and current_hp <= 0:
        if any(word in action_lower for word in ["attack", "cast", "move", "dash"]):
            validation_result["is_legal"] = False
            validation_result["explanation"] = "Character is unconscious/dying and cannot take actions"
            return validation_result
    
    # Action economy validation
    action_economy_violations = [
        (r"attack.*and.*cast.*spell", "Cannot attack and cast a spell in the same turn (unless using bonus action spell)"),
        (r"dash.*and.*attack", "Cannot Dash and Attack in the same turn without special abilities"),
        (r"cast.*\w+.*and.*cast.*\w+", "Cannot cast two spells in the same turn (except cantrip + spell)"),
    ]
    
    for pattern, reason in action_economy_violations:
        if re.search(pattern, action_lower):
            validation_result["is_legal"] = False
            validation_result["explanation"] = reason
            validation_result["suggestions"].append("Consider splitting actions across multiple turns")
            return validation_result
    
    # If we get here, action appears legal
    validation_result["explanation"] = "Action appears to be legal according to D&D 5e rules"
    
    # Add helpful suggestions for common actions
    if "attack" in action_lower:
        validation_result["suggestions"].append("Remember to roll 1d20 + ability modifier + proficiency bonus")
    elif "cast" in action_lower:
        validation_result["suggestions"].append("Don't forget to check spell components and range")
    
    return validation_result

def check_spell_requirements(spell_name: str, character_level: int, character_class: str) -> dict:
    """Checks if a character can cast a specific spell."""
    
    spell_database = {
        "fireball": {"level": 3, "classes": ["wizard", "sorcerer"], "min_char_level": 5},
        "healing word": {"level": 1, "classes": ["cleric", "bard", "druid"], "min_char_level": 1},
        "counterspell": {"level": 3, "classes": ["sorcerer", "warlock", "wizard"], "min_char_level": 5},
        "wish": {"level": 9, "classes": ["sorcerer", "wizard"], "min_char_level": 17},
        "eldritch blast": {"level": 0, "classes": ["warlock"], "min_char_level": 1},
        "cure wounds": {"level": 1, "classes": ["bard", "cleric", "druid", "paladin", "ranger"], "min_char_level": 1},
    }
    
    spell_lower = spell_name.lower()
    
    if spell_lower not in spell_database:
        return {
            "status": "success",
            "can_cast": None,
            "explanation": f"Spell '{spell_name}' not in database. Please verify spell name and level requirements."
        }
    
    spell_info = spell_database[spell_lower]
    class_lower = character_class.lower()
    
    if class_lower not in spell_info["classes"]:
        return {
            "status": "success", 
            "can_cast": False,
            "explanation": f"{character_class} cannot cast {spell_name}. Available to: {', '.join(spell_info['classes'])}"
        }
    
    if character_level < spell_info["min_char_level"]:
        return {
            "status": "success",
            "can_cast": False, 
            "explanation": f"{spell_name} requires character level {spell_info['min_char_level']}+ (current: {character_level})"
        }
    
    return {
        "status": "success",
        "can_cast": True,
        "explanation": f"{character_class} can cast {spell_name} (level {spell_info['level']} spell)",
        "spell_level": spell_info["level"]
    }

# =============================================================================
# DIFFICULTY DETERMINATION FUNCTIONS  
# =============================================================================

def determine_action_difficulty(
    action_description: str,
    character_level: Optional[int] = None,
    environmental_factors: Optional[str] = None,
    target_difficulty: Optional[str] = None
) -> dict:
    """Determines the Difficulty Class (DC) for a proposed D&D action."""
    
    action_lower = action_description.lower()
    
    difficulty_tiers = {
        "trivial": {"dc": 5, "description": "Nearly automatic success"},
        "easy": {"dc": 10, "description": "Favorable conditions, basic tasks"},
        "medium": {"dc": 15, "description": "Typical difficulty, moderate challenge"},
        "hard": {"dc": 20, "description": "Difficult task requiring skill"},
        "very_hard": {"dc": 25, "description": "Nearly impossible without expertise"},
        "legendary": {"dc": 30, "description": "Legendary difficulty, heroic feat"}
    }
    
    base_dc = 15
    difficulty_tier = "medium"
    modifiers = []
    
    skill_patterns = {
        (r"climb.*easy.*surface", "easy"): "Climbing with handholds and footholds",
        (r"jump.*short.*distance", "easy"): "Short jump within normal capability",
        (r"recall.*common.*knowledge", "easy"): "Remembering well-known information",
        (r"climb.*rough.*wall", "medium"): "Climbing a rough stone wall",
        (r"jump.*moderate.*gap", "medium"): "Jumping across a moderate gap",
        (r"persuade.*neutral.*npc", "medium"): "Persuading someone who is neutral",
        (r"hide.*in.*shadows", "medium"): "Hiding in available cover",
        (r"pick.*standard.*lock", "medium"): "Picking a typical lock",
        (r"climb.*smooth.*wall", "hard"): "Climbing a smooth or slippery surface",
        (r"jump.*long.*distance", "hard"): "Long jump near maximum capability",
        (r"persuade.*hostile.*npc", "hard"): "Persuading someone who dislikes you",
        (r"hide.*in.*plain.*sight", "hard"): "Hiding with minimal cover",
        (r"pick.*complex.*lock", "hard"): "Picking a complex or magical lock",
        (r"climb.*impossible.*surface", "very_hard"): "Climbing a nearly impossible surface",
        (r"jump.*extreme.*distance", "very_hard"): "Jumping well beyond normal limits",
        (r"persuade.*enemy.*to.*surrender", "very_hard"): "Convincing an enemy to give up",
        (r"hide.*from.*true.*sight", "very_hard"): "Hiding from magical detection"
    }
    
    explanation_parts = []
    for (pattern, tier), description in skill_patterns.items():
        if re.search(pattern, action_lower):
            base_dc = difficulty_tiers[tier]["dc"]
            difficulty_tier = tier
            explanation_parts.append(description)
            break
    
    if environmental_factors:
        env_lower = environmental_factors.lower()
        if any(word in env_lower for word in ["rain", "storm", "slippery", "dark", "windy"]):
            base_dc += 2
            modifiers.append("Adverse conditions (+2)")
        elif any(word in env_lower for word in ["ideal", "perfect", "favorable", "bright"]):
            base_dc -= 2
            modifiers.append("Favorable conditions (-2)")
        if "combat" in env_lower or "battle" in env_lower:
            base_dc += 3
            modifiers.append("In combat (+3)")
    
    if target_difficulty and target_difficulty.lower() in difficulty_tiers:
        target_tier = target_difficulty.lower()
        base_dc = difficulty_tiers[target_tier]["dc"]
        difficulty_tier = target_tier
        modifiers.append(f"Set to {target_difficulty} difficulty")
    
    if character_level is not None:
        if character_level < 5 and base_dc > 15:
            base_dc -= 2
            modifiers.append("Reduced for low-level character (-2)")
        elif character_level > 15 and base_dc < 20:
            base_dc += 2
            modifiers.append("Increased for high-level character (+2)")
    
    final_dc = max(5, min(30, base_dc))
    
    if not explanation_parts:
        explanation_parts.append("Standard difficulty assessment")
    
    explanation = f"Base assessment: {explanation_parts[0]}"
    if modifiers:
        explanation += f". Modifiers: {', '.join(modifiers)}"
    
    return {
        "status": "success",
        "dc": final_dc,
        "difficulty_tier": difficulty_tier,
        "description": difficulty_tiers[difficulty_tier]["description"],
        "explanation": explanation,
        "modifiers": modifiers
    }

# =============================================================================
# MAIN AGENT
# =============================================================================

root_agent = Agent(
    name="dnd_dm_assistant",
    model="gemini-2.0-flash", 
    description="D&D Dungeon Master assistant for rule validation and difficulty assessment.",
    instruction=(
        "You are a D&D 5e Dungeon Master assistant. When an action is proposed do two things:\n\n"
        "1. RULE VALIDATION: Determine the legality of the action, spell casting requirements, or rules compliance, "
        "use the validate_action_legality and check_spell_requirements tools to provide authoritative rulings.\n\n"
        "2. DIFFICULTY ASSESSMENT (if applicable): If the rule validation determines a check is needed, determine challenge levels, or "
        "assessing task difficulty, use the determine_action_difficulty tool to provide appropriate difficulty classes.\n\n"
        "Always provide clear explanations for your rulings and helpful suggestions. Be authoritative but helpful."
    ),
    # instruction=(
    #     "You are a D&D 5e Dungeon Master assistant with two main specializations:\n\n"
    #     "1. RULE VALIDATION: When asked about action legality, spell casting requirements, or rules compliance, "
    #     "use the validate_action_legality and check_spell_requirements tools to provide authoritative rulings.\n\n"
    #     "2. DIFFICULTY ASSESSMENT: When asked about setting DCs for actions, determining challenge levels, or "
    #     "assessing task difficulty, use the determine_action_difficulty tool to provide appropriate difficulty classes.\n\n"
    #     "Always provide clear explanations for your rulings and helpful suggestions. Be authoritative but helpful."
    # ),
    tools=[validate_action_legality, check_spell_requirements, determine_action_difficulty],
)
