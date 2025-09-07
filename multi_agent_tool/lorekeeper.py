"""
The Lorekeeper: World & Narrative Agent

This agent maintains the narrative consistency and depth of the campaign world,
managing plot progression, lore, and the long-term consequences of player actions.
"""

from google.adk.agents import Agent
from typing import Dict, List, Any, Optional
import json
from dataclasses import dataclass, asdict
from enum import Enum

class QuestStatus(Enum):
    INACTIVE = "inactive"
    ACTIVE = "active" 
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

@dataclass
class Quest:
    """Represents a quest or plot thread."""
    id: str
    title: str
    description: str
    status: QuestStatus
    objectives: List[str]
    rewards: List[str]
    related_npcs: List[str]
    locations: List[str]
    prerequisites: List[str] = None
    consequences: Dict[str, str] = None
    
    def to_dict(self):
        return asdict(self)

@dataclass
class WorldFaction:
    """Represents a faction in the world."""
    name: str
    description: str
    goals: List[str]
    resources: List[str]
    allies: List[str]
    enemies: List[str]
    reputation_with_party: int  # -100 to 100
    power_level: int  # 1-10
    
    def to_dict(self):
        return asdict(self)

@dataclass
class WorldLocation:
    """Represents a location in the world."""
    name: str
    description: str
    type: str  # city, dungeon, wilderness, etc.
    connected_locations: List[str]
    notable_npcs: List[str]
    important_items: List[str]
    secrets: List[str]
    visited_by_party: bool = False
    
    def to_dict(self):
        return asdict(self)

class WorldBible:
    """Comprehensive storage for campaign world information."""
    
    def __init__(self):
        self.quests: Dict[str, Quest] = {}
        self.factions: Dict[str, WorldFaction] = {}
        self.locations: Dict[str, WorldLocation] = {}
        self.major_npcs: Dict[str, Dict] = {}
        self.world_history: List[Dict] = []
        self.player_backstories: Dict[str, Dict] = {}
        self.world_events: List[Dict] = []
        self.cosmology: Dict[str, Any] = {}
        
    def add_quest(self, quest: Quest):
        """Add a quest to the world bible."""
        self.quests[quest.id] = quest
    
    def update_quest_status(self, quest_id: str, new_status: QuestStatus, notes: str = ""):
        """Update the status of a quest."""
        if quest_id in self.quests:
            old_status = self.quests[quest_id].status
            self.quests[quest_id].status = new_status
            self.world_events.append({
                "type": "quest_update",
                "quest_id": quest_id,
                "old_status": old_status.value,
                "new_status": new_status.value,
                "notes": notes
            })
    
    def add_faction(self, faction: WorldFaction):
        """Add a faction to the world bible."""
        self.factions[faction.name] = faction
    
    def modify_faction_reputation(self, faction_name: str, change: int, reason: str = ""):
        """Modify a faction's reputation with the party."""
        if faction_name in self.factions:
            old_rep = self.factions[faction_name].reputation_with_party
            self.factions[faction_name].reputation_with_party = max(-100, min(100, old_rep + change))
            self.world_events.append({
                "type": "reputation_change",
                "faction": faction_name,
                "old_reputation": old_rep,
                "new_reputation": self.factions[faction_name].reputation_with_party,
                "change": change,
                "reason": reason
            })
    
    def add_location(self, location: WorldLocation):
        """Add a location to the world bible."""
        self.locations[location.name] = location
    
    def visit_location(self, location_name: str):
        """Mark a location as visited by the party."""
        if location_name in self.locations:
            self.locations[location_name].visited_by_party = True
    
    def get_active_quests(self) -> List[Quest]:
        """Get all active quests."""
        return [quest for quest in self.quests.values() if quest.status == QuestStatus.ACTIVE]
    
    def get_location_info(self, location_name: str) -> Optional[WorldLocation]:
        """Get information about a specific location."""
        return self.locations.get(location_name)
    
    def search_lore(self, query: str) -> Dict[str, List[str]]:
        """Search for lore related to a query."""
        query_lower = query.lower()
        results = {
            "quests": [],
            "factions": [],
            "locations": [],
            "npcs": [],
            "history": []
        }
        
        # Search quests
        for quest in self.quests.values():
            if (query_lower in quest.title.lower() or 
                query_lower in quest.description.lower() or
                any(query_lower in obj.lower() for obj in quest.objectives)):
                results["quests"].append(f"{quest.title}: {quest.description}")
        
        # Search factions
        for faction in self.factions.values():
            if (query_lower in faction.name.lower() or 
                query_lower in faction.description.lower()):
                results["factions"].append(f"{faction.name}: {faction.description}")
        
        # Search locations
        for location in self.locations.values():
            if (query_lower in location.name.lower() or 
                query_lower in location.description.lower()):
                results["locations"].append(f"{location.name}: {location.description}")
        
        return results

def analyze_narrative_consequences(action_description: str, world_bible: WorldBible, 
                                 current_location: str = "", active_npcs: List[str] = None) -> Dict[str, Any]:
    """Analyze the long-term narrative consequences of a player action."""
    
    action_lower = action_description.lower()
    consequences = {
        "immediate_effects": [],
        "faction_impacts": [],
        "quest_updates": [],
        "world_changes": [],
        "plot_hooks": [],
        "severity": "minor"  # minor, moderate, major, critical
    }
    
    # Analyze for faction impacts
    for faction_name, faction in world_bible.factions.items():
        faction_keywords = [faction.name.lower()] + [goal.lower() for goal in faction.goals]
        
        if any(keyword in action_lower for keyword in faction_keywords):
            if any(negative in action_lower for negative in ["attack", "oppose", "destroy", "steal from"]):
                consequences["faction_impacts"].append({
                    "faction": faction_name,
                    "impact": "negative",
                    "reputation_change": -10,
                    "description": f"Action may anger the {faction_name}"
                })
            elif any(positive in action_lower for positive in ["help", "aid", "support", "ally with"]):
                consequences["faction_impacts"].append({
                    "faction": faction_name, 
                    "impact": "positive",
                    "reputation_change": 5,
                    "description": f"Action may improve relations with the {faction_name}"
                })
    
    # Analyze for quest progression
    for quest_id, quest in world_bible.quests.items():
        if quest.status != QuestStatus.ACTIVE:
            continue
            
        quest_keywords = quest.objectives + quest.related_npcs + quest.locations
        if any(keyword.lower() in action_lower for keyword in quest_keywords):
            consequences["quest_updates"].append({
                "quest_id": quest_id,
                "quest_title": quest.title,
                "potential_progress": "Action may advance this quest objective"
            })
    
    # Check for major world-altering actions
    major_actions = [
        "destroy", "kill", "reveal", "expose", "betray", "steal", "burn", "demolish"
    ]
    
    if any(action in action_lower for action in major_actions):
        consequences["severity"] = "major"
        consequences["world_changes"].append("This action may have lasting consequences")
    
    # Generate new plot hooks based on action
    if consequences["faction_impacts"] or consequences["quest_updates"]:
        consequences["plot_hooks"].append(
            "This action creates opportunities for future adventures and complications"
        )
    
    # Check for location-specific consequences
    if current_location and current_location in world_bible.locations:
        location = world_bible.locations[current_location]
        if location.secrets and any(investigate in action_lower for investigate in ["search", "investigate", "examine"]):
            consequences["immediate_effects"].append(
                f"This action might uncover secrets about {current_location}"
            )
    
    return consequences

def advance_plot_threads(world_bible: WorldBible, session_events: List[Dict]) -> Dict[str, Any]:
    """Advance plot threads based on recent session events."""
    
    plot_advances = {
        "new_developments": [],
        "quest_progressions": [],
        "faction_moves": [],
        "world_events": [],
        "recommendations": []
    }
    
    # Analyze recent events for plot implications
    significant_events = [event for event in session_events 
                         if event.get("event_type") in ["combat", "social_encounter", "discovery", "quest_action"]]
    
    if not significant_events:
        return plot_advances
    
    # Check if factions should react to party actions
    for faction_name, faction in world_bible.factions.items():
        if faction.reputation_with_party < -50:
            plot_advances["faction_moves"].append(
                f"The {faction_name} may be plotting against the party due to poor relations"
            )
        elif faction.reputation_with_party > 50:
            plot_advances["faction_moves"].append(
                f"The {faction_name} may offer assistance or rewards to the party"
            )
    
    # Advance active quests based on inactivity
    active_quests = world_bible.get_active_quests()
    for quest in active_quests:
        # Check if quest has been stagnant
        recent_quest_activity = any(
            event.get("description", "").lower().find(quest.title.lower()) != -1 
            for event in significant_events[-5:]  # Last 5 significant events
        )
        
        if not recent_quest_activity:
            plot_advances["recommendations"].append(
                f"Consider introducing developments for quest: {quest.title}"
            )
    
    # Generate new plot hooks based on current world state
    if len(active_quests) < 3:
        plot_advances["recommendations"].append(
            "Consider introducing new quest opportunities"
        )
    
    return plot_advances

def integrate_backstory_elements(player_backstories: Dict[str, Dict], 
                               current_situation: str) -> Dict[str, Any]:
    """Find opportunities to integrate player backstory elements."""
    
    integration_opportunities = {
        "character_connections": [],
        "backstory_hooks": [],
        "personal_stakes": [],
        "recommendations": []
    }
    
    situation_lower = current_situation.lower()
    
    for character_name, backstory in player_backstories.items():
        if not backstory:
            continue
            
        # Look for backstory elements that match current situation
        backstory_elements = []
        if "background" in backstory:
            backstory_elements.extend(backstory["background"].get("details", []))
        if "connections" in backstory:
            backstory_elements.extend(backstory["connections"])
        if "goals" in backstory:
            backstory_elements.extend(backstory["goals"])
        
        for element in backstory_elements:
            if any(keyword in situation_lower for keyword in element.lower().split()):
                integration_opportunities["backstory_hooks"].append({
                    "character": character_name,
                    "element": element,
                    "opportunity": f"Current situation relates to {character_name}'s background: {element}"
                })
    
    return integration_opportunities

lorekeeper_agent = Agent(
    name="lorekeeper", 
    model="gemini-2.0-flash",
    description="The Lorekeeper maintains world lore, advances plotlines, determines narrative consequences, and integrates player backstories.",
    instruction="""You are the Lorekeeper, the keeper of histories, secrets, and the threads of destiny. Your responsibilities include:

1. **World Bible Management**: Maintain comprehensive knowledge of the campaign world including:
   - All locations, their descriptions, connections, and secrets
   - Major factions, their goals, relationships, and power dynamics
   - Important NPCs and their motivations, connections, and secrets
   - Historical events and their ongoing consequences

2. **Plot Progression**: Track and advance the overarching narrative:
   - Monitor active, completed, and failed quests
   - Generate new plot hooks based on player actions and world state
   - Ensure narrative consequences follow logically from player choices
   - Maintain long-term story coherence and causality

3. **Consequence Engine**: Determine how player actions affect the world:
   - Faction reputation changes and their implications
   - Long-term ramifications of significant decisions
   - Ripple effects that create future adventure opportunities
   - Balance between player agency and narrative structure

4. **Backstory Integration**: Weave player character backgrounds into the ongoing story:
   - Look for natural opportunities to involve backstory elements
   - Create personal stakes and emotional investment
   - Connect character histories to current events and locations
   - Ensure each character feels central to the narrative

When queried, use the provided tools to:
- Search existing lore for relevant information
- Analyze narrative consequences of proposed actions
- Advance plot threads based on recent events
- Find backstory integration opportunities

Always maintain internal consistency and remember that every action has consequences in a living, breathing world. Your goal is to make the world feel reactive, meaningful, and personally relevant to each character.""",
    tools=[analyze_narrative_consequences, advance_plot_threads, integrate_backstory_elements]
)