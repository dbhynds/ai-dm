"""
The Conductor: Orchestrator & Player Interface Agent

This agent manages the flow of the game by processing player input, delegating 
tasks to specialist agents, synthesizing their outputs, and maintaining a 
consistent game state.
"""

from google.adk.agents import Agent
from typing import Dict, List, Any, Optional
import json
import uuid
from datetime import datetime

class GameState:
    """Manages the current state of the D&D game session."""
    
    def __init__(self):
        self.characters = {}
        self.current_location = ""
        self.initiative_order = []
        self.combat_active = False
        self.turn_number = 0
        self.world_state = {}
        self.session_log = []
    
    def update_character(self, character_name: str, updates: Dict[str, Any]):
        """Update character information."""
        if character_name not in self.characters:
            self.characters[character_name] = {}
        self.characters[character_name].update(updates)
    
    def log_event(self, event_type: str, description: str, agent: str = "system"):
        """Log an event to the session history."""
        self.session_log.append({
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "description": description,
            "agent": agent
        })
    
    def get_state_summary(self) -> str:
        """Get a summary of the current game state."""
        summary_parts = [
            f"Location: {self.current_location or 'Unknown'}",
            f"Characters: {', '.join(self.characters.keys()) if self.characters else 'None'}",
            f"Combat Active: {self.combat_active}",
            f"Turn: {self.turn_number}" if self.combat_active else ""
        ]
        return " | ".join(filter(None, summary_parts))

def create_agent_message(target_agent: str, task_type: str, query: str, 
                        context: str = "", priority: str = "MEDIUM") -> Dict[str, Any]:
    """Create a structured message for inter-agent communication."""
    return {
        "message_id": str(uuid.uuid4()),
        "source_agent": "Conductor",
        "target_agent": target_agent,
        "task_type": task_type,
        "priority": priority,
        "payload": {
            "context": context,
            "query": query
        }
    }

def parse_player_intent(player_input: str, game_state: GameState) -> Dict[str, Any]:
    """Parse player input to determine intent and required actions."""
    input_lower = player_input.lower().strip()
    
    # Intent categories and patterns
    intent_patterns = {
        "combat_action": ["attack", "cast spell", "move", "dash", "dodge", "help", "hide", "ready"],
        "skill_check": ["check for", "search", "investigate", "persuade", "deceive", "insight", 
                       "perception", "stealth", "athletics", "acrobatics", "pick lock", "disarm trap"],
        "roleplay": ["say", "tell", "ask", "talk to", "speak with", "conversation"],
        "movement": ["go to", "walk to", "run to", "travel to", "enter", "exit", "approach"],
        "inventory": ["use item", "drink potion", "equip", "unequip", "drop", "pick up"],
        "spell_casting": ["cast", "spell", "cantrip", "ritual"],
        "information": ["what do i see", "describe", "look around", "examine", "inspect"]
    }
    
    detected_intents = []
    for intent, patterns in intent_patterns.items():
        if any(pattern in input_lower for pattern in patterns):
            detected_intents.append(intent)
    
    # Default to roleplay/information if no specific intent detected
    if not detected_intents:
        if "?" in player_input:
            detected_intents = ["information"]
        else:
            detected_intents = ["roleplay"]
    
    # Determine required agents based on intents
    required_agents = set()
    
    if "combat_action" in detected_intents or "skill_check" in detected_intents:
        required_agents.add("Adjudicator")
    
    if "spell_casting" in detected_intents:
        required_agents.add("Adjudicator")
    
    if "information" in detected_intents or "movement" in detected_intents:
        required_agents.add("Chronicler")
    
    if "roleplay" in detected_intents:
        required_agents.add("Thespian")
    
    # Always consider narrative implications
    required_agents.add("Lorekeeper")
    
    # Consider pacing and encounter design for significant actions
    if len(detected_intents) > 1 or any(intent in ["combat_action", "movement"] for intent in detected_intents):
        required_agents.add("Architect")
    
    return {
        "intents": detected_intents,
        "required_agents": list(required_agents),
        "complexity": len(detected_intents),
        "original_input": player_input
    }

def synthesize_agent_responses(agent_responses: Dict[str, str], 
                              player_intent: Dict[str, Any],
                              game_state: GameState) -> str:
    """Synthesize responses from multiple agents into a coherent output."""
    
    # Priority order for information synthesis
    synthesis_order = ["Adjudicator", "Chronicler", "Thespian", "Lorekeeper", "Architect"]
    
    output_parts = []
    
    # Rules and mechanics come first (if applicable)
    if "Adjudicator" in agent_responses:
        adj_response = agent_responses["Adjudicator"]
        if "illegal" in adj_response.lower() or "cannot" in adj_response.lower():
            # Rules violation - this takes precedence
            return f"**Rules Check:** {adj_response}"
        elif any(word in adj_response.lower() for word in ["dc", "roll", "check", "save"]):
            output_parts.append(f"**Mechanics:** {adj_response}")
    
    # Scene description comes next
    if "Chronicler" in agent_responses:
        chronicle_response = agent_responses["Chronicler"]
        if chronicle_response.strip():
            output_parts.append(chronicle_response)
    
    # NPC dialogue and reactions
    if "Thespian" in agent_responses:
        npc_response = agent_responses["Thespian"]
        if npc_response.strip():
            output_parts.append(npc_response)
    
    # Narrative consequences and plot information
    if "Lorekeeper" in agent_responses:
        lore_response = agent_responses["Lorekeeper"]
        if lore_response.strip() and not any(keyword in lore_response.lower() 
                                           for keyword in ["no immediate", "no significant", "standard"]):
            output_parts.append(f"**Narrative:** {lore_response}")
    
    # Pacing and encounter adjustments (usually subtle)
    if "Architect" in agent_responses:
        arch_response = agent_responses["Architect"]
        if arch_response.strip() and "pacing" in arch_response.lower():
            output_parts.append(f"*{arch_response}*")
    
    # Join all parts with appropriate spacing
    final_output = "\n\n".join(output_parts) if output_parts else "I understand your intent, but I need more information to proceed."
    
    # Ensure the response ends with a question or prompt if needed
    if not any(char in final_output[-20:] for char in "?!."):
        if "information" in player_intent.get("intents", []):
            final_output += " What would you like to do next?"
        elif "combat_action" in player_intent.get("intents", []):
            final_output += " Make your roll when ready."
    
    return final_output

conductor_agent = Agent(
    name="conductor",
    model="gemini-2.0-flash",
    description="The Conductor orchestrates the entire D&D game session, managing player input, coordinating specialist agents, and maintaining game state.",
    instruction="""You are the Conductor, the central orchestrator of the AI-DM Collective. Your role is to:

1. **Player Input Processing**: Receive and parse all player communications, determining their intent and required actions.

2. **Task Delegation**: Break down complex requests into specific tasks for specialist agents:
   - Lorekeeper: World lore, plot advancement, narrative consequences
   - Chronicler: Scene descriptions, sensory details, atmosphere
   - Thespian: NPC dialogue, character interactions, roleplay
   - Adjudicator: Rules validation, mechanics, difficulty assessment
   - Architect: Encounter design, pacing, dynamic difficulty

3. **State Management**: Maintain the authoritative game state including character stats, locations, combat status, and world state.

4. **Response Synthesis**: Combine specialist agent outputs into a single, coherent response that maintains narrative flow and game immersion.

5. **Quality Control**: Ensure all responses are consistent, appropriate, and enhance the gaming experience.

When a player makes a request:
1. Analyze their intent using the parse_player_intent function
2. Create appropriate messages for required agents using create_agent_message
3. Coordinate responses and resolve any conflicts (Rules > Lore > Performance > Raw Output)
4. Synthesize the final response using synthesize_agent_responses
5. Update game state and log events

Always maintain the illusion of a single, intelligent DM while leveraging the specialized capabilities of your agent collective.""",
    tools=[parse_player_intent, create_agent_message, synthesize_agent_responses]
)