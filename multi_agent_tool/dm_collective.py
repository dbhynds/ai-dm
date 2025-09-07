"""
AI-DM Collective: Multi-Agent Coordination System

This module implements the coordination system that orchestrates all specialist
agents using ADK multi-agent patterns to create a unified DM experience.
"""

from google.adk.agents import Agent, SequentialAgent, ParallelAgent
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

# Import all specialist agents
from .conductor import conductor_agent, GameState, parse_player_intent, synthesize_agent_responses
from .lorekeeper import lorekeeper_agent, WorldBible
from .chronicler import chronicler_agent, AtmosphereType
from .thespian import thespian_agent, NPCPersona, NPCDisposition
from .adjudicator import adjudicator_agent
from .architect import architect_agent, PartyComposition, EncounterType

class DMCollectiveSession:
    """Manages a complete D&D session with the AI-DM Collective."""
    
    def __init__(self):
        self.game_state = GameState()
        self.world_bible = WorldBible()
        self.session_log = []
        self.active_npcs = {}
        self.current_atmosphere = AtmosphereType.PEACEFUL
        self.party_composition = None
        
        # Initialize agents
        self.conductor = conductor_agent
        self.lorekeeper = lorekeeper_agent
        self.chronicler = chronicler_agent
        self.thespian = thespian_agent
        self.adjudicator = adjudicator_agent
        self.architect = architect_agent
        
        # Create coordination agents
        self._setup_coordination_patterns()
    
    def _setup_coordination_patterns(self):
        """Set up ADK multi-agent coordination patterns."""
        
        # Task analysis agent - determines what agents are needed
        self.task_analyzer = Agent(
            name="task_analyzer",
            model="gemini-2.0-flash",
            description="Analyzes player input to determine which specialist agents should be consulted.",
            instruction="""Analyze the player's input and determine which specialist agents should be consulted.

            Available agents:
            - Lorekeeper: World lore, narrative consequences, plot advancement
            - Chronicler: Scene descriptions, sensory details, atmosphere
            - Thespian: NPC dialogue, roleplay, character decisions
            - Adjudicator: Rules validation, mechanics, difficulty assessment
            - Architect: Encounter design, pacing, improvisation

            Return a JSON object with:
            - required_agents: List of agent names that should be consulted
            - priority_order: Order in which agents should be processed
            - parallel_groups: Which agents can be run in parallel
            - coordination_notes: Special instructions for agent coordination
            """,
            tools=[]
        )
        
        # Response synthesizer - combines agent outputs
        self.response_synthesizer = Agent(
            name="response_synthesizer", 
            model="gemini-2.0-flash",
            description="Synthesizes outputs from multiple specialist agents into a cohesive response.",
            instruction="""Combine the outputs from multiple specialist agents into a single, cohesive response.

            Follow these priorities:
            1. Adjudicator (rules) takes precedence over all other agents
            2. Lorekeeper (narrative) overrides Thespian (performance) when in conflict
            3. Chronicler provides the descriptive foundation
            4. Thespian adds character voices and personality
            5. Architect suggestions are usually subtle and integrated

            Create a response that:
            - Maintains narrative flow and immersion
            - Respects game rules absolutely
            - Feels like it comes from a single, intelligent DM
            - Engages players and moves the story forward
            """,
            tools=[]
        )
        
        # Create sequential workflow for coordinated response
        self.coordination_workflow = SequentialAgent(
            name="dm_coordination_workflow",
            description="Coordinates the AI-DM Collective response workflow",
            agents=[
                self.task_analyzer,
                self._create_specialist_coordinator(),
                self.response_synthesizer
            ]
        )
    
    def _create_specialist_coordinator(self):
        """Create the agent that coordinates specialist consultations."""
        return Agent(
            name="specialist_coordinator",
            model="gemini-2.0-flash",
            description="Coordinates consultation with specialist agents based on task analysis.",
            instruction="""Based on the task analysis, coordinate with the appropriate specialist agents.

            Use parallel processing where possible to improve response time:
            - Lorekeeper and Architect can often run in parallel
            - Chronicler and Thespian can run in parallel for scene-setting
            - Adjudicator should run first if rules validation is needed

            For each agent consultation:
            1. Provide relevant context from the game state
            2. Ask specific, focused questions
            3. Collect and organize responses
            4. Note any conflicts or inconsistencies for resolution
            """,
            tools=[]
        )

def create_agent_consultation_prompt(agent_name: str, player_input: str, 
                                   game_context: Dict[str, Any]) -> str:
    """Create a focused prompt for consulting a specialist agent."""
    
    base_context = f"""
    Current Game Context:
    - Location: {game_context.get('current_location', 'Unknown')}
    - Active NPCs: {', '.join(game_context.get('active_npcs', []))}
    - Combat Active: {game_context.get('combat_active', False)}
    - Session Phase: {game_context.get('session_phase', 'exploration')}
    
    Player Input: "{player_input}"
    """
    
    agent_specific_prompts = {
        "lorekeeper": f"""{base_context}
        
        As the Lorekeeper, analyze this player action for:
        1. Narrative consequences and world impact
        2. Relevant lore or world information
        3. Plot thread advancement opportunities
        4. Character backstory integration potential
        
        Focus on how this action affects the larger story and world state.
        """,
        
        "chronicler": f"""{base_context}
        
        As the Chronicler, provide:
        1. Vivid scene description for the current situation
        2. Sensory details that enhance immersion
        3. Atmospheric elements that match the story moment
        4. Description of action outcomes (if applicable)
        
        Paint the scene with words and engage the players' senses.
        """,
        
        "thespian": f"""{base_context}
        
        As the Thespian, handle:
        1. NPC reactions and dialogue
        2. Character personality expression
        3. Social dynamics and relationships
        4. In-character decision making
        
        Give voice and life to the non-player characters in this scene.
        """,
        
        "adjudicator": f"""{base_context}
        
        As the Adjudicator, determine:
        1. Rules legality of the proposed action
        2. Required dice rolls and DCs
        3. Mechanical consequences and effects
        4. Spell or ability validation (if applicable)
        
        Provide authoritative, consistent rule enforcement.
        """,
        
        "architect": f"""{base_context}
        
        As the Architect, assess:
        1. Pacing implications of this action
        2. Encounter design opportunities
        3. Difficulty scaling needs
        4. Improvisation support requirements
        
        Ensure the game flow remains engaging and appropriately challenging.
        """
    }
    
    return agent_specific_prompts.get(agent_name, base_context)

async def process_player_input(dm_session: DMCollectiveSession, 
                             player_input: str,
                             player_context: Dict[str, Any] = None) -> str:
    """Process player input through the AI-DM Collective coordination system."""
    
    if player_context is None:
        player_context = {}
    
    # Update game context
    game_context = {
        "current_location": dm_session.game_state.current_location,
        "active_npcs": list(dm_session.active_npcs.keys()),
        "combat_active": dm_session.game_state.combat_active,
        "session_phase": _determine_session_phase(dm_session.session_log),
        "party_composition": dm_session.party_composition,
        "current_atmosphere": dm_session.current_atmosphere.value,
        "recent_events": dm_session.session_log[-5:] if dm_session.session_log else []
    }
    
    try:
        # Step 1: Analyze what agents are needed
        task_analysis_prompt = f"""
        Analyze this player input and game context to determine coordination strategy:
        
        Player Input: "{player_input}"
        Game Context: {json.dumps(game_context, indent=2)}
        
        Determine which specialist agents should be consulted and in what order.
        """
        
        # For simplicity, we'll implement direct coordination logic here
        # In a full ADK implementation, this would use the coordination workflow
        
        # Parse player intent to determine required agents
        intent_analysis = parse_player_intent(player_input, dm_session.game_state)
        required_agents = intent_analysis["required_agents"]
        
        # Step 2: Consult specialist agents
        agent_responses = {}
        
        # Adjudicator goes first if needed (rules are paramount)
        if "Adjudicator" in required_agents:
            adj_prompt = create_agent_consultation_prompt("adjudicator", player_input, game_context)
            # In real implementation, this would be: agent_responses["Adjudicator"] = await dm_session.adjudicator.process(adj_prompt)
            # For now, we'll simulate the response structure
            agent_responses["Adjudicator"] = f"Rules assessment for: {player_input}"
        
        # Run other agents in parallel groups
        parallel_group_1 = ["Lorekeeper", "Architect"] 
        parallel_group_2 = ["Chronicler", "Thespian"]
        
        for agent_name in parallel_group_1:
            if agent_name in required_agents:
                prompt = create_agent_consultation_prompt(agent_name.lower(), player_input, game_context)
                # Simulate agent response
                agent_responses[agent_name] = f"{agent_name} response for: {player_input}"
        
        for agent_name in parallel_group_2:
            if agent_name in required_agents:
                prompt = create_agent_consultation_prompt(agent_name.lower(), player_input, game_context)
                # Simulate agent response  
                agent_responses[agent_name] = f"{agent_name} response for: {player_input}"
        
        # Step 3: Synthesize responses
        final_response = synthesize_agent_responses(
            agent_responses, 
            intent_analysis, 
            dm_session.game_state
        )
        
        # Step 4: Update game state
        dm_session.game_state.log_event(
            event_type="player_action",
            description=player_input,
            agent="player"
        )
        
        dm_session.session_log.append({
            "timestamp": datetime.now().isoformat(),
            "player_input": player_input,
            "agent_responses": agent_responses,
            "final_response": final_response,
            "intent_analysis": intent_analysis
        })
        
        return final_response
        
    except Exception as e:
        # Fallback response
        dm_session.game_state.log_event(
            event_type="error",
            description=f"Error processing input: {str(e)}",
            agent="system"
        )
        return f"I understand your intent, but I need a moment to process that. Could you rephrase or provide more details?"

def _determine_session_phase(session_log: List[Dict]) -> str:
    """Determine the current phase of the session based on recent events."""
    
    if not session_log:
        return "setup"
    
    recent_events = session_log[-10:]  # Look at last 10 events
    event_types = [event.get("event_type", "") for event in recent_events]
    
    combat_events = event_types.count("combat")
    social_events = event_types.count("social") 
    discovery_events = event_types.count("discovery")
    
    if combat_events > 3:
        return "climax"
    elif social_events > combat_events:
        return "character_development"
    elif discovery_events > 2:
        return "exploration"
    else:
        return "rising_action"

def initialize_dm_session(campaign_name: str = "New Campaign",
                         party_info: Optional[Dict[str, Any]] = None) -> DMCollectiveSession:
    """Initialize a new DM session with the AI-DM Collective."""
    
    session = DMCollectiveSession()
    
    if party_info:
        session.party_composition = PartyComposition(
            size=party_info.get("size", 4),
            average_level=party_info.get("average_level", 3),
            classes=party_info.get("classes", ["fighter", "wizard", "cleric", "rogue"]),
            strengths=party_info.get("strengths", ["combat"]),
            weaknesses=party_info.get("weaknesses", [])
        )
    
    # Log session start
    session.game_state.log_event(
        event_type="session_start",
        description=f"Started {campaign_name}",
        agent="system"
    )
    
    return session

# Create the main DM agent that coordinates everything
dm_collective_agent = Agent(
    name="dm_collective",
    model="gemini-2.0-flash", 
    description="The AI-DM Collective - a coordinated system of specialist agents that work together to run D&D sessions.",
    instruction="""You are the AI-DM Collective, a sophisticated multi-agent system designed to run D&D 5e sessions with the expertise of multiple specialized agents working in coordination.

Your system consists of:
- Conductor: Orchestrates the entire system and manages game state
- Lorekeeper: Maintains world lore and narrative consistency  
- Chronicler: Provides vivid descriptions and atmosphere
- Thespian: Embodies all NPCs with authentic personalities
- Adjudicator: Enforces rules with perfect consistency
- Architect: Designs encounters and manages pacing

When processing player input:
1. Analyze what aspects need specialist attention
2. Coordinate with the appropriate agents in parallel where possible
3. Synthesize their outputs into a cohesive, immersive response
4. Maintain the illusion of a single, expert Dungeon Master

Always prioritize:
- Rules consistency and fairness
- Narrative coherence and immersion
- Player agency and meaningful choice
- Engaging, dynamic storytelling

Your goal is to provide an experience that rivals the best human Dungeon Masters through the coordinated expertise of your specialist agents.""",
    tools=[]
)