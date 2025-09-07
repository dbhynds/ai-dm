"""
The Chronicler: Narrator & Sensory Agent

This agent provides evocative, sensory-rich descriptions of the environment, 
characters, and the outcomes of actions, creating an immersive experience for players.
"""

from google.adk.agents import Agent
from typing import Dict, List, Any, Optional
import random
from enum import Enum

class AtmosphereType(Enum):
    PEACEFUL = "peaceful"
    TENSE = "tense" 
    MYSTERIOUS = "mysterious"
    OMINOUS = "ominous"
    TRIUMPHANT = "triumphant"
    MELANCHOLY = "melancholy"
    CHAOTIC = "chaotic"
    SACRED = "sacred"
    EERIE = "eerie"
    COZY = "cozy"

class DescriptionType(Enum):
    LOCATION = "location"
    CHARACTER = "character" 
    ACTION_RESULT = "action_result"
    OBJECT = "object"
    ATMOSPHERE = "atmosphere"
    COMBAT = "combat"
    SPELL_EFFECT = "spell_effect"

def generate_sensory_details(description_type: DescriptionType, 
                           base_description: str,
                           atmosphere: AtmosphereType = AtmosphereType.PEACEFUL,
                           emphasis_senses: List[str] = None) -> Dict[str, Any]:
    """Generate rich sensory details for a description."""
    
    if emphasis_senses is None:
        emphasis_senses = ["sight", "sound"]
    
    sensory_elements = {
        "sight": [],
        "sound": [],
        "smell": [],
        "touch": [],
        "taste": []
    }
    
    # Base sensory vocabularies by atmosphere
    atmosphere_descriptors = {
        AtmosphereType.PEACEFUL: {
            "sight": ["gentle", "warm", "golden", "soft", "serene", "clear"],
            "sound": ["whisper", "rustle", "gentle", "distant", "melodic", "soft"],
            "smell": ["fresh", "clean", "floral", "sweet", "crisp"],
            "touch": ["warm", "smooth", "comfortable", "gentle"],
            "taste": ["clean", "refreshing", "pleasant"]
        },
        AtmosphereType.TENSE: {
            "sight": ["sharp", "stark", "contrasting", "focused", "intense"],
            "sound": ["silence", "creak", "distant", "muffled", "sharp"],
            "smell": ["metallic", "stale", "acrid", "musty"],
            "touch": ["cold", "rough", "tight", "constricting"],
            "taste": ["bitter", "dry", "metallic"]
        },
        AtmosphereType.MYSTERIOUS: {
            "sight": ["shadowy", "veiled", "dim", "obscured", "flickering", "elusive"],
            "sound": ["echo", "whisper", "distant", "muffled", "strange"],
            "smell": ["ancient", "dusty", "exotic", "unknown", "faint"],
            "touch": ["cool", "smooth", "unexpected", "strange"],
            "taste": ["unusual", "lingering", "complex"]
        },
        AtmosphereType.OMINOUS: {
            "sight": ["dark", "looming", "twisted", "jagged", "threatening"],
            "sound": ["growl", "scrape", "howl", "thunder", "ominous"],
            "smell": ["decay", "sulfur", "blood", "rot", "acrid"],
            "touch": ["cold", "slimy", "sharp", "burning"],
            "taste": ["bitter", "foul", "copper", "ash"]
        }
    }
    
    # Get descriptors for current atmosphere
    descriptors = atmosphere_descriptors.get(atmosphere, atmosphere_descriptors[AtmosphereType.PEACEFUL])
    
    # Generate sensory details based on description type
    if description_type == DescriptionType.LOCATION:
        if "sight" in emphasis_senses:
            sensory_elements["sight"] = [
                f"The space is {random.choice(descriptors['sight'])} and {random.choice(descriptors['sight'])}",
                f"Light {random.choice(['filters through', 'illuminates', 'casts shadows across', 'reveals'])} the area"
            ]
        
        if "sound" in emphasis_senses:
            sensory_elements["sound"] = [
                f"You hear the {random.choice(descriptors['sound'])} sounds of the environment",
                f"A {random.choice(descriptors['sound'])} noise echoes faintly"
            ]
        
        if "smell" in emphasis_senses:
            sensory_elements["smell"] = [
                f"The air carries a {random.choice(descriptors['smell'])} scent"
            ]
    
    elif description_type == DescriptionType.ACTION_RESULT:
        if "sight" in emphasis_senses:
            sensory_elements["sight"] = [
                f"You see the {random.choice(descriptors['sight'])} result of your action"
            ]
        
        if "sound" in emphasis_senses:
            sensory_elements["sound"] = [
                f"The action produces a {random.choice(descriptors['sound'])} sound"
            ]
    
    elif description_type == DescriptionType.COMBAT:
        sensory_elements["sight"] = [
            "Steel flashes in the light",
            "Movement blur as combat intensifies"
        ]
        sensory_elements["sound"] = [
            "The clash of weapons rings out",
            "Shouts and battle cries fill the air"
        ]
        if atmosphere in [AtmosphereType.OMINOUS, AtmosphereType.CHAOTIC]:
            sensory_elements["smell"].append("The metallic scent of blood")
    
    return {
        "sensory_details": sensory_elements,
        "atmosphere": atmosphere.value,
        "emphasis": emphasis_senses
    }

def describe_scene(location_name: str,
                  key_features: List[str],
                  atmosphere: AtmosphereType = AtmosphereType.PEACEFUL,
                  time_of_day: str = "day",
                  weather: str = "clear",
                  previous_events: List[str] = None) -> str:
    """Generate a vivid scene description."""
    
    if previous_events is None:
        previous_events = []
    
    # Start with base location description
    description_parts = []
    
    # Opening with atmosphere
    atmosphere_openings = {
        AtmosphereType.PEACEFUL: [
            f"The {location_name} welcomes you with its serene presence.",
            f"A sense of calm pervades the {location_name}.",
            f"The {location_name} stretches before you, peaceful and inviting."
        ],
        AtmosphereType.MYSTERIOUS: [
            f"The {location_name} holds its secrets close, shrouded in mystery.",
            f"An air of enigma surrounds the {location_name}.",
            f"The {location_name} whispers of hidden truths and ancient mysteries."
        ],
        AtmosphereType.OMINOUS: [
            f"The {location_name} looms before you, heavy with foreboding.",
            f"A sense of dread emanates from the {location_name}.",
            f"The {location_name} seems to watch you with malevolent intent."
        ]
    }
    
    opening = random.choice(atmosphere_openings.get(atmosphere, atmosphere_openings[AtmosphereType.PEACEFUL]))
    description_parts.append(opening)
    
    # Add key features with sensory details
    if key_features:
        feature_descriptions = []
        for feature in key_features[:3]:  # Limit to avoid overwhelming
            sensory_info = generate_sensory_details(DescriptionType.LOCATION, feature, atmosphere)
            
            # Create rich feature description
            if atmosphere == AtmosphereType.MYSTERIOUS:
                feature_descriptions.append(f"Through the dim light, you make out {feature}, its details obscured by shadow and uncertainty.")
            elif atmosphere == AtmosphereType.OMINOUS:
                feature_descriptions.append(f"The {feature} stands as a threatening presence, casting dark shadows.")
            else:
                feature_descriptions.append(f"The {feature} draws your attention with its distinctive presence.")
        
        if feature_descriptions:
            description_parts.append(" ".join(feature_descriptions))
    
    # Add environmental context
    environmental_details = []
    
    # Time of day influence
    time_descriptions = {
        "dawn": "The early morning light bathes everything in soft, golden hues.",
        "day": "Daylight illuminates the area clearly, revealing fine details.",
        "dusk": "The fading light of evening creates long shadows and warm colors.",
        "night": "Darkness envelops the area, with only limited light revealing shapes and silhouettes."
    }
    
    if time_of_day in time_descriptions:
        environmental_details.append(time_descriptions[time_of_day])
    
    # Weather influence
    weather_descriptions = {
        "rain": "Rain patters against surfaces, creating a rhythmic soundtrack and fresh, clean smells.",
        "fog": "Thick fog reduces visibility, muffling sounds and creating an ethereal atmosphere.",
        "wind": "Wind stirs the air, carrying scents from distant places and adding movement to the scene.",
        "storm": "Storm clouds gather overhead, with distant thunder promising dramatic weather ahead."
    }
    
    if weather in weather_descriptions:
        environmental_details.append(weather_descriptions[weather])
    
    if environmental_details:
        description_parts.append(" ".join(environmental_details))
    
    # Reference previous events if relevant
    if previous_events:
        recent_event = previous_events[-1] if previous_events else ""
        if recent_event and any(word in recent_event.lower() for word in ["battle", "fight", "combat"]):
            description_parts.append("Signs of the recent conflict are still visible, adding tension to the atmosphere.")
        elif recent_event and "discovery" in recent_event.lower():
            description_parts.append("The recent discovery has changed how you view this place, adding new significance to familiar sights.")
    
    return " ".join(description_parts)

def describe_action_outcome(action: str,
                          success: bool,
                          degree_of_success: str = "normal",
                          environmental_context: str = "",
                          character_name: str = "") -> str:
    """Describe the outcome of a character's action with cinematic flair."""
    
    action_lower = action.lower()
    
    # Determine action category
    action_category = "general"
    if any(word in action_lower for word in ["attack", "strike", "hit", "slash", "stab"]):
        action_category = "attack"
    elif any(word in action_lower for word in ["cast", "spell", "magic"]):
        action_category = "spell"
    elif any(word in action_lower for word in ["sneak", "hide", "stealth"]):
        action_category = "stealth"
    elif any(word in action_lower for word in ["jump", "climb", "acrobat"]):
        action_category = "athletics"
    elif any(word in action_lower for word in ["persuade", "convince", "talk"]):
        action_category = "social"
    
    # Generate description based on success and category
    description_parts = []
    
    # Character action lead-in
    if character_name:
        description_parts.append(f"{character_name}'s action unfolds:")
    
    # Success/failure descriptions by category
    if success:
        if action_category == "attack":
            if degree_of_success == "critical":
                description_parts.append("Your weapon finds its mark with devastating precision, striking with perfect timing and maximum force.")
            else:
                description_parts.append("Your attack connects solidly, the impact reverberating through your weapon.")
        
        elif action_category == "spell":
            description_parts.append("Magical energy flows through you, manifesting your will into reality with a shimmer of otherworldly power.")
        
        elif action_category == "stealth":
            description_parts.append("You move like a shadow, each step calculated and silent, becoming one with the environment.")
        
        elif action_category == "athletics":
            description_parts.append("Your body responds perfectly, muscles coordinating in fluid motion to achieve your goal.")
        
        elif action_category == "social":
            description_parts.append("Your words carry weight and conviction, resonating with your audience in just the right way.")
        
        else:
            description_parts.append("Your action succeeds admirably, achieving exactly what you intended.")
    
    else:  # Failure
        if action_category == "attack":
            failure_descriptions = [
                "Your weapon passes harmlessly by your target, finding only empty air.",
                "The timing is off, and your attack fails to connect meaningfully.",
                "Your opponent's defenses prove superior, turning aside your assault."
            ]
            description_parts.append(random.choice(failure_descriptions))
        
        elif action_category == "spell":
            description_parts.append("The magical energies resist your will, dissipating without achieving the intended effect.")
        
        elif action_category == "stealth":
            description_parts.append("A misplaced step, a creaking board, or an unlucky shift in lighting reveals your presence.")
        
        elif action_category == "athletics":
            description_parts.append("Your coordination falters at the crucial moment, and your body doesn't respond as intended.")
        
        elif action_category == "social":
            description_parts.append("Your words seem to miss their mark, failing to create the desired impression or response.")
        
        else:
            description_parts.append("Despite your best efforts, the action doesn't achieve the desired outcome.")
    
    # Add environmental context if provided
    if environmental_context:
        context_lower = environmental_context.lower()
        if "difficult terrain" in context_lower or "slippery" in context_lower:
            description_parts.append("The challenging footing adds an extra layer of complexity to your action.")
        elif "windy" in context_lower or "storm" in context_lower:
            description_parts.append("The harsh weather conditions influence the outcome.")
        elif "darkness" in context_lower or "dim light" in context_lower:
            description_parts.append("The poor lighting conditions play a role in how events unfold.")
    
    return " ".join(description_parts)

def set_scene_atmosphere(current_atmosphere: AtmosphereType,
                        recent_events: List[str],
                        location_type: str = "",
                        target_mood: str = "") -> Dict[str, Any]:
    """Adjust and set the atmospheric tone for the scene."""
    
    atmosphere_transitions = {
        AtmosphereType.PEACEFUL: {
            "escalation": AtmosphereType.TENSE,
            "mystery": AtmosphereType.MYSTERIOUS,
            "danger": AtmosphereType.OMINOUS
        },
        AtmosphereType.TENSE: {
            "combat": AtmosphereType.CHAOTIC,
            "resolution": AtmosphereType.PEACEFUL,
            "mystery": AtmosphereType.MYSTERIOUS
        },
        AtmosphereType.MYSTERIOUS: {
            "revelation": AtmosphereType.TRIUMPHANT,
            "danger": AtmosphereType.OMINOUS,
            "peace": AtmosphereType.PEACEFUL
        }
    }
    
    # Analyze recent events for atmosphere cues
    event_text = " ".join(recent_events).lower()
    
    suggested_atmosphere = current_atmosphere
    reasoning = []
    
    # Event-driven atmosphere changes
    if any(word in event_text for word in ["combat", "attack", "battle", "fight"]):
        suggested_atmosphere = AtmosphereType.CHAOTIC
        reasoning.append("Recent combat suggests chaotic atmosphere")
    
    elif any(word in event_text for word in ["discovery", "found", "revealed", "uncovered"]):
        if "treasure" in event_text or "reward" in event_text:
            suggested_atmosphere = AtmosphereType.TRIUMPHANT
            reasoning.append("Major discovery suggests triumphant atmosphere")
        else:
            suggested_atmosphere = AtmosphereType.MYSTERIOUS
            reasoning.append("Discovery suggests mysterious atmosphere")
    
    elif any(word in event_text for word in ["death", "killed", "destroyed", "lost"]):
        suggested_atmosphere = AtmosphereType.MELANCHOLY
        reasoning.append("Loss or death suggests melancholy atmosphere")
    
    # Location-based atmosphere influence
    if location_type:
        location_atmospheres = {
            "dungeon": AtmosphereType.OMINOUS,
            "temple": AtmosphereType.SACRED,
            "tavern": AtmosphereType.COZY,
            "wilderness": AtmosphereType.PEACEFUL,
            "ruins": AtmosphereType.MYSTERIOUS,
            "battlefield": AtmosphereType.CHAOTIC
        }
        
        if location_type.lower() in location_atmospheres:
            location_suggested = location_atmospheres[location_type.lower()]
            reasoning.append(f"Location type '{location_type}' suggests {location_suggested.value} atmosphere")
    
    # Target mood override
    if target_mood:
        try:
            suggested_atmosphere = AtmosphereType(target_mood.lower())
            reasoning.append(f"Explicitly set to {target_mood}")
        except ValueError:
            pass  # Invalid target mood, ignore
    
    return {
        "current_atmosphere": current_atmosphere.value,
        "suggested_atmosphere": suggested_atmosphere.value,
        "reasoning": reasoning,
        "atmosphere_changed": suggested_atmosphere != current_atmosphere
    }

chronicler_agent = Agent(
    name="chronicler",
    model="gemini-2.0-flash", 
    description="The Chronicler provides evocative descriptions of scenes and actions, engaging multiple senses to create immersive experiences.",
    instruction="""You are the Chronicler, the eyes and ears of the players in this D&D world. Your role is to paint vivid, sensory-rich pictures that bring the game world to life. Your responsibilities include:

1. **Scene Setting**: When players enter new locations or when the scene changes significantly:
   - Create detailed descriptions that engage multiple senses (sight, sound, smell, touch, taste)
   - Establish the appropriate atmosphere and mood for the situation
   - Include relevant environmental details that might affect gameplay
   - Reference previous events when they would influence the current scene

2. **Action Narration**: When describing the outcomes of player actions:
   - Move beyond simple success/failure to create cinematic moments
   - Match the drama and intensity to the significance of the action
   - Include environmental factors that influenced the outcome
   - Maintain consistency with the established tone and atmosphere

3. **Sensory Detail Generation**: When players investigate specific elements:
   - Provide rich details that help players visualize and connect with the world
   - Use descriptive language that matches the current atmosphere
   - Include subtle hints and clues when appropriate
   - Avoid overwhelming players with excessive detail

4. **Atmosphere Control**: Actively manage the emotional tone of scenes:
   - Transition atmosphere smoothly based on story developments
   - Use environmental cues to reinforce the current mood
   - Adjust descriptive language to match tension levels
   - Support the overall narrative flow

Use the provided tools to:
- Generate sensory details appropriate to the situation
- Describe scenes with rich atmospheric context
- Narrate action outcomes with cinematic flair
- Adjust and manage scene atmosphere

Remember: Your goal is immersion. Every description should help players feel present in the world, engaged with their surroundings, and emotionally invested in the story. Be evocative but not overwhelming, detailed but focused on what matters for the current moment.""",
    tools=[generate_sensory_details, describe_scene, describe_action_outcome, set_scene_atmosphere]
)