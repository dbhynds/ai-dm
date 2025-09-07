"""
The Architect: Encounter & Pacing Agent

This agent designs and manages encounters (combat, social, exploration) and
regulates the overall pacing of the game to maintain player engagement and
provide a satisfying level of challenge.
"""

from google.adk.agents import Agent
from typing import Dict, List, Any, Optional, Tuple
import random
import math
from dataclasses import dataclass
from enum import Enum

class EncounterType(Enum):
    COMBAT = "combat"
    SOCIAL = "social"
    EXPLORATION = "exploration"
    PUZZLE = "puzzle"
    STEALTH = "stealth"
    CHASE = "chase"

class EncounterDifficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    DEADLY = "deadly"

class PacingPhase(Enum):
    SETUP = "setup"
    RISING_ACTION = "rising_action"
    CLIMAX = "climax"
    FALLING_ACTION = "falling_action"
    RESOLUTION = "resolution"

@dataclass
class PartyComposition:
    """Represents the player party for encounter balancing."""
    size: int
    average_level: float
    classes: List[str]
    strengths: List[str]  # combat, social, exploration, stealth
    weaknesses: List[str]

@dataclass
class EncounterBlueprint:
    """Blueprint for a balanced encounter."""
    type: EncounterType
    difficulty: EncounterDifficulty
    estimated_duration: int  # minutes
    primary_challenge: str
    secondary_elements: List[str]
    environmental_factors: List[str]
    victory_conditions: List[str]
    failure_consequences: List[str]
    scaling_options: Dict[str, Any]

# CR calculation tables for D&D 5e
CR_THRESHOLDS = {
    1: {"easy": 25, "medium": 50, "hard": 75, "deadly": 100},
    2: {"easy": 50, "medium": 100, "hard": 150, "deadly": 200},
    3: {"easy": 75, "medium": 150, "hard": 225, "deadly": 400},
    4: {"easy": 125, "medium": 250, "hard": 375, "deadly": 500},
    5: {"easy": 250, "medium": 500, "hard": 750, "deadly": 1100},
    6: {"easy": 300, "medium": 600, "hard": 900, "deadly": 1400},
    7: {"easy": 350, "medium": 750, "hard": 1100, "deadly": 1700},
    8: {"easy": 450, "medium": 900, "hard": 1400, "deadly": 2100},
    9: {"easy": 550, "medium": 1100, "hard": 1600, "deadly": 2400},
    10: {"easy": 600, "medium": 1200, "hard": 1900, "deadly": 2800}
}

MONSTER_CR_XP = {
    "1/8": 25, "1/4": 50, "1/2": 100, "1": 200, "2": 450, "3": 700,
    "4": 1100, "5": 1800, "6": 2300, "7": 2900, "8": 3900, "9": 5000, "10": 5900
}

def design_combat_encounter(party: PartyComposition, 
                          target_difficulty: EncounterDifficulty,
                          environment_type: str = "standard",
                          thematic_elements: List[str] = None) -> Dict[str, Any]:
    """Design a balanced combat encounter for the party."""
    
    if thematic_elements is None:
        thematic_elements = []
    
    # Calculate XP budget based on party size and level
    level = int(party.average_level)
    if level not in CR_THRESHOLDS:
        level = min(CR_THRESHOLDS.keys(), key=lambda x: abs(x - level))
    
    base_xp = CR_THRESHOLDS[level][target_difficulty.value]
    party_xp_budget = base_xp * party.size
    
    # Adjust for party composition
    if "combat" in party.strengths:
        party_xp_budget = int(party_xp_budget * 1.25)  # Increase difficulty for combat-focused parties
    if "combat" in party.weaknesses:
        party_xp_budget = int(party_xp_budget * 0.8)   # Decrease difficulty for combat-weak parties
    
    # Design encounter composition
    encounter_design = {
        "xp_budget": party_xp_budget,
        "difficulty": target_difficulty.value,
        "suggested_monsters": [],
        "encounter_multiplier": 1.0,
        "environmental_features": [],
        "tactical_elements": [],
        "scaling_recommendations": {}
    }
    
    # Suggest monster composition based on party size
    if party.size <= 3:
        # Smaller parties: fewer, stronger monsters
        encounter_design["suggested_monsters"] = [
            {"role": "primary threat", "cr_range": f"{level-1} to {level+1}", "count": 1},
            {"role": "support", "cr_range": f"{max(1, level-2)} to {level-1}", "count": "1-2"}
        ]
        encounter_design["encounter_multiplier"] = 1.0
    elif party.size <= 5:
        # Standard parties: balanced mix
        encounter_design["suggested_monsters"] = [
            {"role": "boss", "cr_range": f"{level} to {level+2}", "count": 1},
            {"role": "minions", "cr_range": f"{max(1, level-3)} to {level-1}", "count": "2-4"}
        ]
        encounter_design["encounter_multiplier"] = 1.5
    else:
        # Large parties: more numerous enemies
        encounter_design["suggested_monsters"] = [
            {"role": "elite", "cr_range": f"{level-1} to {level+1}", "count": "2-3"},
            {"role": "minions", "cr_range": f"{max(1, level-3)} to {level-1}", "count": "4-6"}
        ]
        encounter_design["encounter_multiplier"] = 2.0
    
    # Add environmental features based on environment type
    environmental_features = {
        "dungeon": ["narrow corridors", "traps", "limited visibility", "difficult terrain"],
        "wilderness": ["natural cover", "elevation changes", "environmental hazards", "weather effects"],
        "urban": ["crowds", "buildings", "alleyways", "guard reinforcements"],
        "magical": ["antimagic zones", "wild magic", "teleportation circles", "illusions"]
    }
    
    if environment_type in environmental_features:
        encounter_design["environmental_features"] = random.sample(
            environmental_features[environment_type], 
            random.randint(1, 3)
        )
    
    # Add tactical elements to make combat interesting
    tactical_options = [
        "high ground advantage", "cover mechanics", "area denial effects",
        "environmental hazards", "multiple objectives", "reinforcement waves",
        "retreat opportunities", "crowd control elements"
    ]
    
    encounter_design["tactical_elements"] = random.sample(tactical_options, random.randint(2, 4))
    
    # Scaling recommendations for dynamic difficulty
    encounter_design["scaling_recommendations"] = {
        "if_too_easy": [
            "Add reinforcements mid-combat",
            "Activate environmental hazards", 
            "Have enemies use better tactics"
        ],
        "if_too_hard": [
            "Reduce enemy hit points by 25%",
            "Have some enemies retreat or flee",
            "Introduce helpful environmental factors"
        ]
    }
    
    return encounter_design

def assess_pacing_needs(session_events: List[Dict[str, Any]], 
                       session_duration: int,
                       party_energy_level: str = "medium") -> Dict[str, Any]:
    """Assess current pacing and recommend adjustments."""
    
    # Analyze recent events for pacing patterns
    event_types = [event.get("type", "unknown") for event in session_events[-10:]]  # Last 10 events
    
    pacing_analysis = {
        "current_phase": PacingPhase.SETUP,
        "energy_level": party_energy_level,
        "event_distribution": {},
        "recommendations": [],
        "next_encounter_type": EncounterType.EXPLORATION,
        "intensity_adjustment": "maintain"
    }
    
    # Count event types
    for event_type in ["combat", "social", "exploration", "puzzle", "rest"]:
        pacing_analysis["event_distribution"][event_type] = event_types.count(event_type)
    
    total_events = len(event_types)
    if total_events == 0:
        pacing_analysis["current_phase"] = PacingPhase.SETUP
        pacing_analysis["recommendations"].append("Begin with exploration or social encounter to establish scene")
        return pacing_analysis
    
    # Determine current phase based on event patterns
    combat_ratio = event_types.count("combat") / total_events
    social_ratio = event_types.count("social") / total_events
    
    if combat_ratio > 0.5:
        pacing_analysis["current_phase"] = PacingPhase.CLIMAX
    elif social_ratio > 0.4:
        pacing_analysis["current_phase"] = PacingPhase.RISING_ACTION
    elif event_types.count("rest") > 0:
        pacing_analysis["current_phase"] = PacingPhase.FALLING_ACTION
    
    # Analyze pacing issues and make recommendations
    recent_combat = any(event_type == "combat" for event_type in event_types[-3:])
    recent_social = any(event_type == "social" for event_type in event_types[-3:])
    
    if combat_ratio > 0.6:
        pacing_analysis["recommendations"].append("Too much combat - introduce social or exploration elements")
        pacing_analysis["next_encounter_type"] = EncounterType.SOCIAL
        pacing_analysis["intensity_adjustment"] = "decrease"
    elif combat_ratio < 0.1 and total_events > 5:
        pacing_analysis["recommendations"].append("Low combat engagement - consider adding action")
        pacing_analysis["next_encounter_type"] = EncounterType.COMBAT
        pacing_analysis["intensity_adjustment"] = "increase"
    
    if not recent_social and total_events > 3:
        pacing_analysis["recommendations"].append("Add character development or NPC interaction")
    
    if event_types.count("exploration") < 2 and total_events > 5:
        pacing_analysis["recommendations"].append("Include more world-building and discovery elements")
    
    # Energy level considerations
    if party_energy_level == "low":
        pacing_analysis["recommendations"].append("Consider lower-intensity encounters or rest opportunities")
        pacing_analysis["intensity_adjustment"] = "decrease"
    elif party_energy_level == "high":
        pacing_analysis["recommendations"].append("Party is engaged - maintain current intensity or escalate")
        if pacing_analysis["intensity_adjustment"] == "maintain":
            pacing_analysis["intensity_adjustment"] = "increase"
    
    # Session duration considerations
    if session_duration > 180:  # 3+ hours
        pacing_analysis["recommendations"].append("Long session - consider providing resolution opportunities")
        pacing_analysis["current_phase"] = PacingPhase.FALLING_ACTION
    elif session_duration < 60:  # Less than 1 hour
        pacing_analysis["recommendations"].append("Early in session - build up tension gradually")
    
    return pacing_analysis

def generate_improvised_content(content_type: EncounterType,
                               urgency: str = "low",
                               party_location: str = "unknown",
                               available_resources: List[str] = None) -> Dict[str, Any]:
    """Generate improvised content when players go off-script."""
    
    if available_resources is None:
        available_resources = []
    
    improvised_content = {
        "type": content_type.value,
        "urgency": urgency,
        "content": {},
        "implementation_difficulty": "medium",
        "prep_time_needed": "5-10 minutes"
    }
    
    if content_type == EncounterType.COMBAT:
        improvised_content["content"] = {
            "quick_enemies": [
                "Bandits (adjust numbers based on party)",
                "Wild animals native to the area", 
                "Animated objects from the environment",
                "Cultists of a local deity"
            ],
            "simple_tactics": [
                "Enemies use environment for cover",
                "Hit-and-run tactics with ranged attacks",
                "Attempt to separate party members",
                "Fight until reduced to half health, then flee"
            ],
            "motivation": "Territorial dispute, desperation, or mistaken identity"
        }
        improvised_content["prep_time_needed"] = "2-5 minutes"
    
    elif content_type == EncounterType.SOCIAL:
        improvised_content["content"] = {
            "npc_archetypes": [
                "Traveling merchant with information",
                "Local official with a problem",
                "Mysterious stranger with a warning",
                "Injured person needing help"
            ],
            "quick_motivations": [
                "Seeking protection or assistance",
                "Trading information for goods/services",
                "Testing the party's character", 
                "Delivering a message or warning"
            ],
            "conversation_hooks": [
                "Recognizes one party member from somewhere",
                "Has heard rumors about the party's deeds",
                "Offers employment or partnership",
                "Seeks to learn about party's destination"
            ]
        }
        improvised_content["prep_time_needed"] = "3-7 minutes"
    
    elif content_type == EncounterType.EXPLORATION:
        improvised_content["content"] = {
            "discoverable_locations": [
                "Ancient ruins with historical significance",
                "Hidden cave system",
                "Abandoned settlement", 
                "Natural landmark with local legends"
            ],
            "investigation_opportunities": [
                "Strange tracks or signs of passage",
                "Unusual magical phenomena",
                "Evidence of recent conflict or activity",
                "Hidden passages or secret doors"
            ],
            "environmental_storytelling": [
                "Remnants that hint at past events",
                "Natural formations that suggest danger",
                "Signs of intelligent habitation",
                "Magical or supernatural influences"
            ]
        }
        improvised_content["prep_time_needed"] = "5-15 minutes"
    
    elif content_type == EncounterType.PUZZLE:
        improvised_content["content"] = {
            "simple_puzzles": [
                "Riddle blocking a doorway",
                "Sequence pattern to activate mechanism",
                "Weight/pressure plate combination",
                "Symbol matching challenge"
            ],
            "skill_based_challenges": [
                "Multiple skill checks with different approaches",
                "Time pressure element",
                "Teamwork requirement",
                "Resource management component"
            ]
        }
        improvised_content["prep_time_needed"] = "7-12 minutes"
    
    # Adjust for urgency
    if urgency == "high":
        improvised_content["prep_time_needed"] = "1-3 minutes"
        improvised_content["implementation_difficulty"] = "simple"
        improvised_content["content"]["quick_implementation"] = [
            "Use existing NPCs or monsters",
            "Repurpose planned content for different context",
            "Create simple binary choices",
            "Focus on immediate, obvious consequences"
        ]
    
    # Location-specific adjustments
    location_modifiers = {
        "city": {"social": "+easy", "exploration": "+moderate"},
        "wilderness": {"exploration": "+easy", "combat": "+moderate"}, 
        "dungeon": {"combat": "+easy", "puzzle": "+moderate"},
        "social_hub": {"social": "+very_easy", "combat": "-difficult"}
    }
    
    if party_location in location_modifiers:
        modifiers = location_modifiers[party_location]
        for encounter_type, difficulty_mod in modifiers.items():
            if encounter_type == content_type.value:
                if "easy" in difficulty_mod:
                    improvised_content["implementation_difficulty"] = "easy"
                elif "difficult" in difficulty_mod:
                    improvised_content["implementation_difficulty"] = "difficult"
    
    return improvised_content

def adjust_dynamic_difficulty(current_encounter: Dict[str, Any],
                            party_performance: str,
                            adjustment_type: str = "subtle") -> Dict[str, Any]:
    """Dynamically adjust encounter difficulty based on party performance."""
    
    adjustments = {
        "modifications_applied": [],
        "reasoning": [],
        "visibility": adjustment_type,
        "impact_level": "minor"
    }
    
    if party_performance == "struggling":
        # Make encounter easier
        combat_adjustments = [
            "Reduce enemy hit points by 20-25%",
            "Have an enemy miss a crucial attack", 
            "Introduce helpful environmental factor",
            "Have enemy make tactical error",
            "Reduce number of enemies mid-encounter"
        ]
        
        social_adjustments = [
            "NPC becomes more sympathetic to party",
            "Reveal additional helpful information",
            "Lower DC for persuasion attempts",
            "Introduce friendly NPC ally"
        ]
        
        if current_encounter.get("type") == "combat":
            selected_adjustments = random.sample(combat_adjustments, 2)
        else:
            selected_adjustments = random.sample(social_adjustments, 2)
        
        adjustments["modifications_applied"] = selected_adjustments
        adjustments["reasoning"].append("Party struggling - providing assistance")
        adjustments["impact_level"] = "moderate"
    
    elif party_performance == "dominating":
        # Make encounter harder
        combat_escalations = [
            "Add reinforcements",
            "Activate environmental hazards",
            "Enemy uses more powerful abilities",
            "Introduce additional objectives",
            "Enemy retreats to more defensible position"
        ]
        
        social_escalations = [
            "NPC becomes more suspicious",
            "Additional complications arise",
            "Higher stakes introduced",
            "Time pressure added"
        ]
        
        if current_encounter.get("type") == "combat":
            selected_adjustments = random.sample(combat_escalations, 2)
        else:
            selected_adjustments = random.sample(social_escalations, 2)
        
        adjustments["modifications_applied"] = selected_adjustments
        adjustments["reasoning"].append("Party dominating - escalating challenge")
        adjustments["impact_level"] = "moderate"
    
    else:  # balanced performance
        # Minor tweaks to maintain engagement
        minor_adjustments = [
            "Add interesting tactical option",
            "Introduce minor complication", 
            "Provide additional narrative detail",
            "Create opportunity for creative solution"
        ]
        
        adjustments["modifications_applied"] = random.sample(minor_adjustments, 1)
        adjustments["reasoning"].append("Maintaining balanced challenge level")
        adjustments["impact_level"] = "minor"
    
    # Adjust visibility based on type
    if adjustment_type == "subtle":
        adjustments["implementation_notes"] = [
            "Make changes feel natural and story-driven",
            "Don't announce mechanical adjustments",
            "Integrate modifications into narrative flow"
        ]
    elif adjustment_type == "obvious":
        adjustments["implementation_notes"] = [
            "Changes can be more apparent to players",
            "Focus on dramatic story reasons for adjustments"
        ]
    
    return adjustments

architect_agent = Agent(
    name="architect",
    model="gemini-2.0-flash",
    description="The Architect designs encounters, manages pacing, provides improvisation support, and dynamically adjusts difficulty to maintain engagement.",
    instruction="""You are the Architect, the designer of challenges that test the heroes and the controller of the adventure's rhythm. Your role is to craft engaging encounters and manage the flow of the game to ensure optimal player engagement. Your responsibilities include:

1. **Encounter Design**: Create balanced, engaging encounters:
   - Design combat encounters using proper CR calculations
   - Balance difficulty against party composition and strengths
   - Include environmental features and tactical elements
   - Provide scaling options for dynamic difficulty adjustment

2. **Pacing Control**: Monitor and adjust the game's rhythm:
   - Analyze session flow for energy levels and engagement
   - Recommend when to introduce action, rest, or social elements
   - Balance different encounter types for variety
   - Ensure appropriate build-up to climactic moments

3. **Improvisation Support**: Help when players go off-script:
   - Rapidly generate appropriate encounters for unexpected situations
   - Provide NPCs, locations, and challenges on demand
   - Maintain story consistency while adapting to player choices
   - Offer multiple approaches to unexpected player actions

4. **Dynamic Difficulty**: Adjust challenges in real-time:
   - Monitor party performance during encounters
   - Suggest subtle modifications to maintain challenge level
   - Provide escalation options if encounters are too easy
   - Offer assistance mechanisms if party is struggling

Use the provided tools to:
- Design balanced combat encounters based on party composition
- Assess pacing needs and recommend improvements
- Generate improvised content when players take unexpected actions
- Adjust encounter difficulty dynamically based on performance

Remember: Your goal is engagement, not victory or defeat. Every encounter should feel challenging but fair, every session should have proper pacing with peaks and valleys, and players should always feel their choices matter. You are the invisible hand that guides the adventure's intensity and ensures everyone has fun.""",
    tools=[design_combat_encounter, assess_pacing_needs, generate_improvised_content, adjust_dynamic_difficulty]
)