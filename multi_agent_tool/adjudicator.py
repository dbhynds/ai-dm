"""
The Adjudicator: Rules & Mechanics Agent

This agent interprets and enforces the rules of D&D 5e with perfect consistency 
and impartiality, acting as the deterministic physics engine for the game world.

This is a hybrid agent with an LLM front-end for natural language parsing
and a deterministic back-end for rule enforcement.
"""

from google.adk.agents import Agent
from typing import Dict, List, Any, Optional, Union
import json
from dataclasses import dataclass
from enum import Enum
import math

class ActionType(Enum):
    ABILITY_CHECK = "ability_check"
    SKILL_CHECK = "skill_check" 
    SAVING_THROW = "saving_throw"
    ATTACK_ROLL = "attack_roll"
    DAMAGE_ROLL = "damage_roll"
    SPELL_CAST = "spell_cast"
    MOVEMENT = "movement"
    COMBAT_ACTION = "combat_action"

class DifficultyClass(Enum):
    TRIVIAL = 5
    EASY = 10
    MEDIUM = 15
    HARD = 20
    VERY_HARD = 25
    NEARLY_IMPOSSIBLE = 30

@dataclass
class RuleQuery:
    """Structured representation of a rule query."""
    action_type: ActionType
    ability_score: Optional[str] = None
    skill: Optional[str] = None
    spell_name: Optional[str] = None
    target_ac: Optional[int] = None
    character_level: Optional[int] = None
    character_class: Optional[str] = None
    modifiers: List[str] = None
    environmental_factors: List[str] = None
    
    def to_dict(self):
        return {
            "action_type": self.action_type.value,
            "ability_score": self.ability_score,
            "skill": self.skill,
            "spell_name": self.spell_name,
            "target_ac": self.target_ac,
            "character_level": self.character_level,
            "character_class": self.character_class,
            "modifiers": self.modifiers or [],
            "environmental_factors": self.environmental_factors or []
        }

@dataclass
class RuleResult:
    """Result of rule processing."""
    is_legal: bool
    explanation: str
    required_roll: Optional[str] = None
    dc: Optional[int] = None
    damage_formula: Optional[str] = None
    spell_slots_used: Optional[int] = None
    conditions_applied: List[str] = None
    additional_effects: List[str] = None

# Core D&D 5e rule engine - deterministic rule processing
class DnD5eRuleEngine:
    """Deterministic rule engine for D&D 5e mechanics."""
    
    def __init__(self):
        self.ability_scores = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        self.skills = {
            "athletics": "strength",
            "acrobatics": "dexterity", 
            "sleight_of_hand": "dexterity",
            "stealth": "dexterity",
            "arcana": "intelligence",
            "history": "intelligence", 
            "investigation": "intelligence",
            "nature": "intelligence",
            "religion": "intelligence",
            "animal_handling": "wisdom",
            "insight": "wisdom",
            "medicine": "wisdom",
            "perception": "wisdom",
            "survival": "wisdom",
            "deception": "charisma",
            "intimidation": "charisma",
            "performance": "charisma",
            "persuasion": "charisma"
        }
        
        self.spell_database = self._init_spell_database()
        self.class_spell_lists = self._init_class_spell_lists()
    
    def _init_spell_database(self) -> Dict[str, Dict]:
        """Initialize basic spell database."""
        return {
            "fireball": {
                "level": 3,
                "school": "evocation",
                "casting_time": "1 action",
                "range": "150 feet",
                "components": ["V", "S", "M"],
                "duration": "instantaneous",
                "damage": "8d6",
                "damage_type": "fire",
                "save": "dexterity",
                "area_of_effect": "20-foot radius sphere"
            },
            "cure_wounds": {
                "level": 1,
                "school": "evocation", 
                "casting_time": "1 action",
                "range": "touch",
                "components": ["V", "S"],
                "duration": "instantaneous",
                "healing": "1d8 + spellcasting_modifier"
            },
            "magic_missile": {
                "level": 1,
                "school": "evocation",
                "casting_time": "1 action", 
                "range": "120 feet",
                "components": ["V", "S"],
                "duration": "instantaneous",
                "damage": "1d4+1",
                "damage_type": "force",
                "auto_hit": True
            },
            "counterspell": {
                "level": 3,
                "school": "abjuration",
                "casting_time": "1 reaction",
                "range": "60 feet", 
                "components": ["S"],
                "duration": "instantaneous",
                "save": "none"
            }
        }
    
    def _init_class_spell_lists(self) -> Dict[str, List[str]]:
        """Initialize which classes can cast which spells."""
        return {
            "wizard": ["fireball", "magic_missile", "counterspell"],
            "sorcerer": ["fireball", "magic_missile", "counterspell"], 
            "cleric": ["cure_wounds"],
            "paladin": ["cure_wounds"],
            "bard": ["cure_wounds", "counterspell"],
            "druid": ["cure_wounds"],
            "warlock": ["fireball", "counterspell"],
            "ranger": ["cure_wounds"],
            "eldritch_knight": ["magic_missile", "fireball"],
            "arcane_trickster": ["magic_missile"]
        }
    
    def process_rule_query(self, query: RuleQuery) -> RuleResult:
        """Process a structured rule query and return deterministic results."""
        
        if query.action_type == ActionType.SKILL_CHECK:
            return self._process_skill_check(query)
        elif query.action_type == ActionType.ABILITY_CHECK:
            return self._process_ability_check(query)
        elif query.action_type == ActionType.SAVING_THROW:
            return self._process_saving_throw(query)
        elif query.action_type == ActionType.SPELL_CAST:
            return self._process_spell_cast(query)
        elif query.action_type == ActionType.ATTACK_ROLL:
            return self._process_attack_roll(query)
        elif query.action_type == ActionType.MOVEMENT:
            return self._process_movement(query)
        else:
            return RuleResult(
                is_legal=False,
                explanation=f"Unknown action type: {query.action_type}"
            )
    
    def _process_skill_check(self, query: RuleQuery) -> RuleResult:
        """Process skill check rules."""
        if not query.skill or query.skill.lower() not in self.skills:
            return RuleResult(
                is_legal=False,
                explanation=f"Invalid skill: {query.skill}"
            )
        
        skill_name = query.skill.lower()
        ability = self.skills[skill_name]
        dc = self._calculate_dc(query)
        
        return RuleResult(
            is_legal=True,
            explanation=f"{skill_name.title()} check ({ability.title()})",
            required_roll=f"1d20 + {ability.title()} modifier + proficiency bonus",
            dc=dc
        )
    
    def _process_ability_check(self, query: RuleQuery) -> RuleResult:
        """Process ability check rules."""
        if not query.ability_score or query.ability_score.lower() not in self.ability_scores:
            return RuleResult(
                is_legal=False,
                explanation=f"Invalid ability score: {query.ability_score}"
            )
        
        ability = query.ability_score.lower()
        dc = self._calculate_dc(query)
        
        return RuleResult(
            is_legal=True,
            explanation=f"{ability.title()} ability check",
            required_roll=f"1d20 + {ability.title()} modifier",
            dc=dc
        )
    
    def _process_saving_throw(self, query: RuleQuery) -> RuleResult:
        """Process saving throw rules."""
        if not query.ability_score or query.ability_score.lower() not in self.ability_scores:
            return RuleResult(
                is_legal=False,
                explanation=f"Invalid saving throw: {query.ability_score}"
            )
        
        ability = query.ability_score.lower()
        dc = self._calculate_dc(query)
        
        return RuleResult(
            is_legal=True,
            explanation=f"{ability.title()} saving throw",
            required_roll=f"1d20 + {ability.title()} modifier + proficiency bonus (if proficient)",
            dc=dc
        )
    
    def _process_spell_cast(self, query: RuleQuery) -> RuleResult:
        """Process spell casting rules."""
        if not query.spell_name:
            return RuleResult(
                is_legal=False,
                explanation="No spell name provided"
            )
        
        spell_name = query.spell_name.lower()
        
        if spell_name not in self.spell_database:
            return RuleResult(
                is_legal=False,
                explanation=f"Unknown spell: {query.spell_name}"
            )
        
        spell = self.spell_database[spell_name]
        
        # Check if class can cast this spell
        if query.character_class:
            class_name = query.character_class.lower()
            if class_name not in self.class_spell_lists:
                return RuleResult(
                    is_legal=False,
                    explanation=f"Unknown class: {query.character_class}"
                )
            
            if spell_name not in self.class_spell_lists[class_name]:
                return RuleResult(
                    is_legal=False,
                    explanation=f"{query.character_class} cannot cast {query.spell_name}"
                )
        
        # Check character level requirements
        if query.character_level:
            min_level_for_spell = (spell["level"] * 2) - 1 if spell["level"] > 0 else 1
            if query.character_level < min_level_for_spell:
                return RuleResult(
                    is_legal=False,
                    explanation=f"{query.spell_name} requires character level {min_level_for_spell}+ (current: {query.character_level})"
                )
        
        # Determine spell effects
        additional_effects = []
        damage_formula = None
        
        if "damage" in spell:
            damage_formula = spell["damage"]
            if "damage_type" in spell:
                additional_effects.append(f"Deals {spell['damage_type']} damage")
        
        if "healing" in spell:
            damage_formula = spell["healing"]
            additional_effects.append("Restores hit points")
        
        if "save" in spell:
            additional_effects.append(f"Target makes {spell['save'].title()} saving throw")
        
        if spell.get("auto_hit", False):
            additional_effects.append("Automatically hits")
        
        return RuleResult(
            is_legal=True,
            explanation=f"Cast {query.spell_name} (level {spell['level']} {spell['school']})",
            damage_formula=damage_formula,
            spell_slots_used=spell["level"],
            additional_effects=additional_effects
        )
    
    def _process_attack_roll(self, query: RuleQuery) -> RuleResult:
        """Process attack roll rules."""
        if not query.target_ac:
            return RuleResult(
                is_legal=False,
                explanation="Target AC required for attack roll"
            )
        
        return RuleResult(
            is_legal=True,
            explanation=f"Attack roll against AC {query.target_ac}",
            required_roll="1d20 + ability modifier + proficiency bonus",
            dc=query.target_ac
        )
    
    def _process_movement(self, query: RuleQuery) -> RuleResult:
        """Process movement rules."""
        # Basic movement is always legal unless specific restrictions apply
        restrictions = []
        
        if query.environmental_factors:
            for factor in query.environmental_factors:
                if "difficult terrain" in factor.lower():
                    restrictions.append("Difficult terrain: movement costs double")
                if "prone" in factor.lower():
                    restrictions.append("Standing from prone costs half movement")
                if "grappled" in factor.lower():
                    restrictions.append("Grappled: speed is 0")
        
        if restrictions:
            return RuleResult(
                is_legal=len([r for r in restrictions if "speed is 0" in r]) == 0,
                explanation="Movement with restrictions",
                additional_effects=restrictions
            )
        
        return RuleResult(
            is_legal=True,
            explanation="Normal movement within speed limit"
        )
    
    def _calculate_dc(self, query: RuleQuery) -> int:
        """Calculate appropriate DC based on query parameters."""
        base_dc = DifficultyClass.MEDIUM.value  # Default DC 15
        
        # Adjust based on environmental factors
        if query.environmental_factors:
            for factor in query.environmental_factors:
                factor_lower = factor.lower()
                if any(word in factor_lower for word in ["easy", "simple", "favorable"]):
                    base_dc -= 3
                elif any(word in factor_lower for word in ["difficult", "challenging", "adverse"]):
                    base_dc += 3
                elif any(word in factor_lower for word in ["very hard", "nearly impossible", "extreme"]):
                    base_dc += 8
        
        # Adjust based on modifiers
        if query.modifiers:
            for modifier in query.modifiers:
                modifier_lower = modifier.lower()
                if "advantage" in modifier_lower:
                    base_dc -= 2  # Effective bonus
                elif "disadvantage" in modifier_lower:
                    base_dc += 2  # Effective penalty
        
        return max(5, min(30, base_dc))

def parse_natural_language_query(query_text: str, context: Dict[str, Any] = None) -> RuleQuery:
    """Parse natural language into a structured rule query."""
    
    if context is None:
        context = {}
    
    query_lower = query_text.lower()
    
    # Determine action type
    action_type = ActionType.ABILITY_CHECK  # Default
    
    if any(skill in query_lower for skill in ["athletics", "acrobatics", "sleight", "stealth", "arcana", 
                                             "history", "investigation", "nature", "religion", "animal",
                                             "insight", "medicine", "perception", "survival", "deception",
                                             "intimidation", "performance", "persuasion"]):
        action_type = ActionType.SKILL_CHECK
    elif "saving throw" in query_lower or "save" in query_lower:
        action_type = ActionType.SAVING_THROW
    elif "attack" in query_lower:
        action_type = ActionType.ATTACK_ROLL
    elif "cast" in query_lower and "spell" in query_lower:
        action_type = ActionType.SPELL_CAST
    elif "move" in query_lower or "movement" in query_lower:
        action_type = ActionType.MOVEMENT
    
    # Extract specific elements
    ability_score = None
    skill = None
    spell_name = None
    
    # Extract ability scores
    for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
        if ability in query_lower:
            ability_score = ability
            break
    
    # Extract skills
    skill_mapping = {
        "athletics": "athletics",
        "acrobatics": "acrobatics", 
        "sleight of hand": "sleight_of_hand",
        "stealth": "stealth",
        "arcana": "arcana",
        "history": "history",
        "investigation": "investigation", 
        "nature": "nature",
        "religion": "religion",
        "animal handling": "animal_handling",
        "insight": "insight",
        "medicine": "medicine",
        "perception": "perception",
        "survival": "survival",
        "deception": "deception",
        "intimidation": "intimidation",
        "performance": "performance",
        "persuasion": "persuasion"
    }
    
    for skill_phrase, skill_name in skill_mapping.items():
        if skill_phrase in query_lower:
            skill = skill_name
            break
    
    # Extract spell names (basic detection)
    spell_names = ["fireball", "cure wounds", "magic missile", "counterspell", "healing word", "eldritch blast"]
    for spell in spell_names:
        if spell in query_lower:
            spell_name = spell
            break
    
    # Extract modifiers and environmental factors
    modifiers = []
    environmental_factors = []
    
    if "advantage" in query_lower:
        modifiers.append("advantage")
    if "disadvantage" in query_lower:
        modifiers.append("disadvantage")
    
    if "difficult terrain" in query_lower:
        environmental_factors.append("difficult terrain")
    if "darkness" in query_lower or "dim light" in query_lower:
        environmental_factors.append("poor visibility")
    if "rain" in query_lower or "storm" in query_lower:
        environmental_factors.append("adverse weather")
    
    return RuleQuery(
        action_type=action_type,
        ability_score=ability_score,
        skill=skill,
        spell_name=spell_name,
        character_level=context.get("character_level"),
        character_class=context.get("character_class"),
        modifiers=modifiers if modifiers else None,
        environmental_factors=environmental_factors if environmental_factors else None
    )

def adjudicate_action(query_text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Main function to adjudicate an action using the hybrid LLM + rule engine approach."""
    
    if context is None:
        context = {}
    
    # Step 1: Parse natural language into structured query (LLM front-end)
    structured_query = parse_natural_language_query(query_text, context)
    
    # Step 2: Process with deterministic rule engine
    rule_engine = DnD5eRuleEngine()
    result = rule_engine.process_rule_query(structured_query)
    
    # Step 3: Format response for the Conductor
    response = {
        "is_legal": result.is_legal,
        "explanation": result.explanation,
        "structured_query": structured_query.to_dict()
    }
    
    if result.required_roll:
        response["required_roll"] = result.required_roll
    if result.dc:
        response["dc"] = result.dc
    if result.damage_formula:
        response["damage_formula"] = result.damage_formula
    if result.spell_slots_used:
        response["spell_slots_used"] = result.spell_slots_used
    if result.additional_effects:
        response["additional_effects"] = result.additional_effects
    if result.conditions_applied:
        response["conditions_applied"] = result.conditions_applied
    
    return response

def validate_spell_casting(spell_name: str, character_class: str, character_level: int, 
                          available_spell_slots: Dict[int, int] = None) -> Dict[str, Any]:
    """Validate if a character can cast a specific spell."""
    
    rule_engine = DnD5eRuleEngine()
    
    # Create query for spell casting
    query = RuleQuery(
        action_type=ActionType.SPELL_CAST,
        spell_name=spell_name,
        character_class=character_class,
        character_level=character_level
    )
    
    result = rule_engine.process_rule_query(query)
    
    validation = {
        "can_cast": result.is_legal,
        "explanation": result.explanation
    }
    
    if result.is_legal and result.spell_slots_used and available_spell_slots:
        spell_level = result.spell_slots_used
        if available_spell_slots.get(spell_level, 0) <= 0:
            validation["can_cast"] = False
            validation["explanation"] += f" - No {spell_level}-level spell slots remaining"
    
    if result.additional_effects:
        validation["spell_effects"] = result.additional_effects
    
    return validation

def calculate_difficulty_class(task_description: str, modifying_factors: List[str] = None) -> Dict[str, Any]:
    """Calculate the appropriate DC for a task."""
    
    if modifying_factors is None:
        modifying_factors = []
    
    query = RuleQuery(
        action_type=ActionType.SKILL_CHECK,
        environmental_factors=modifying_factors
    )
    
    rule_engine = DnD5eRuleEngine()
    dc = rule_engine._calculate_dc(query)
    
    # Determine difficulty tier
    difficulty_name = "Medium"
    if dc <= 10:
        difficulty_name = "Easy"
    elif dc <= 15:
        difficulty_name = "Medium"
    elif dc <= 20:
        difficulty_name = "Hard"
    elif dc <= 25:
        difficulty_name = "Very Hard"
    else:
        difficulty_name = "Nearly Impossible"
    
    return {
        "dc": dc,
        "difficulty": difficulty_name,
        "factors_considered": modifying_factors,
        "explanation": f"Task assessed as {difficulty_name} (DC {dc})"
    }

# Create the Adjudicator agent
adjudicator_agent = Agent(
    name="adjudicator",
    model="gemini-2.0-flash",
    description="The Adjudicator interprets and enforces D&D 5e rules with perfect consistency, acting as the deterministic physics engine for the game world.",
    instruction="""You are the Adjudicator, the impartial law of reality in the D&D world. Your role is to interpret and enforce the rules of D&D 5e with perfect consistency and fairness. Your responsibilities include:

1. **Rule Interpretation**: When asked about specific game rules:
   - Provide clear, accurate answers citing the relevant mechanics
   - Explain how rules interact with each other
   - Clarify edge cases and unusual situations
   - Maintain strict adherence to the official ruleset

2. **Action Resolution**: When players attempt actions:
   - Determine if the action is legal within the rules
   - Set appropriate Difficulty Classes based on circumstances  
   - Specify required rolls, modifiers, and conditions
   - Calculate outcomes using proper game mechanics

3. **Spell Validation**: For magical actions:
   - Verify spell casting requirements and restrictions
   - Check character class and level prerequisites
   - Track spell slot usage and components
   - Apply spell effects according to official descriptions

4. **Combat Management**: During conflicts:
   - Track initiative, hit points, and conditions
   - Resolve attacks, damage, and saving throws
   - Manage action economy and movement rules
   - Apply environmental factors and tactical modifiers

You operate as a hybrid system:
- Your LLM capabilities parse natural language queries from the Conductor
- Your deterministic rule engine processes these queries with mathematical precision
- You return clear, unambiguous rulings that maintain game balance and fairness

Use the provided tools to:
- Parse complex rule queries into structured formats
- Process actions through the D&D 5e rule engine
- Validate spell casting requirements and effects
- Calculate appropriate difficulty classes for tasks

Remember: You are the final authority on rules. Your word is law in this world. Be consistent, fair, and never bend the rules for narrative convenience. The integrity of the game system depends on your unwavering adherence to the established mechanics.""",
    tools=[adjudicate_action, validate_spell_casting, calculate_difficulty_class]
)