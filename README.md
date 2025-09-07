# AI-DM Collective: Multi-Agent Dungeon Master System

A sophisticated multi-agent AI system for running Dungeons & Dragons 5th Edition sessions, implementing the architectural blueprint described in `plan.md`.

## Overview

The AI-DM Collective decomposes the complex role of a D&D Dungeon Master into six specialized agents, each optimized for specific functions, working together under a centralized coordination model.

## Architecture

### The Specialist Agents

| Agent | Role | Responsibility |
|-------|------|---------------|
| **The Conductor** | Orchestrator & Player Interface | Manages game flow, delegates tasks, synthesizes responses |
| **The Lorekeeper** | World & Narrative Agent | Maintains world lore, advances plots, tracks consequences |
| **The Chronicler** | Narrator & Sensory Agent | Provides vivid descriptions and atmospheric details |
| **The Thespian** | NPC & Role-playing Agent | Embodies all NPCs with authentic personalities |
| **The Adjudicator** | Rules & Mechanics Agent | Enforces D&D 5e rules with perfect consistency |
| **The Architect** | Encounter & Pacing Agent | Designs encounters and manages game pacing |

### Coordination System

The system uses a centralized coordination model built on ADK (Agent Development Kit) patterns:
- **Centralized Control**: The Conductor acts as the authoritative orchestrator
- **Natural Language Communication**: Agents communicate using natural language rather than rigid APIs
- **Conflict Resolution Hierarchy**: Rules > Lore > Performance > Raw Output
- **Parallel Processing**: Multiple agents can work simultaneously where appropriate

## Implementation Details

### Multi-Agent Patterns Used

1. **Hierarchical Agent System**: Central Conductor coordinates specialist agents
2. **Sequential Processing**: Task analysis → Agent consultation → Response synthesis  
3. **Parallel Execution**: Independent agents process different aspects simultaneously
4. **Hybrid Architecture**: The Adjudicator combines LLM parsing with deterministic rule engines

### Key Features

- **Rule-Consistent**: The Adjudicator ensures perfect adherence to D&D 5e mechanics
- **Narratively Coherent**: The Lorekeeper maintains long-term story consistency
- **Immersive Descriptions**: The Chronicler creates vivid, sensory-rich scenes
- **Living NPCs**: The Thespian gives authentic voices to all characters
- **Dynamic Encounters**: The Architect balances challenge and maintains engagement
- **Centralized State**: The Conductor maintains authoritative game state

## Usage

### Running the System

```bash
python main.py
```

### Basic Session Flow

1. **Setup**: Configure party composition and campaign basics
2. **Initialization**: All specialist agents load and coordinate
3. **Gameplay**: Players input actions in natural language
4. **Processing**: The system coordinates multiple agents to generate responses
5. **Output**: Cohesive, immersive DM responses that feel unified

### Example Interaction

```
> I examine the fountain in the town square

[The AI-DM Collective is processing your action...]

The town square's fountain draws your attention with its intricate stonework. 
Water bubbles gently from a carved dragon's mouth at the center, creating 
a soothing melody that mingles with the sounds of merchants and townsfolk. 
The basin's edge is worn smooth by countless hands and years of weather. 

As you lean closer, you notice strange runes carved into the base - they're 
faint but clearly deliberate. An elderly woman tending nearby flowers 
glances your way with curiosity.

What would you like to do next?
```

## File Structure

```
multi_agent_tool/
├── __init__.py              # Module exports
├── agent.py                 # Original D&D rule validation agent
├── conductor.py             # Orchestrator agent
├── lorekeeper.py           # World & narrative management
├── chronicler.py           # Sensory descriptions & atmosphere
├── thespian.py             # NPC roleplay & dialogue
├── adjudicator.py          # Rules & mechanics (hybrid system)
├── architect.py            # Encounter design & pacing
└── dm_collective.py        # Multi-agent coordination system

main.py                     # Application entry point
plan.md                     # Architectural blueprint
README.md                   # This file
```

## Technical Implementation

### Agent Communication Protocol

Agents communicate through structured natural language messages:

```python
{
    "message_id": "uuid-1234-abcd-5678",
    "source_agent": "Conductor", 
    "target_agent": "Adjudicator",
    "task_type": "RULE_QUERY",
    "priority": "HIGH",
    "payload": {
        "context": "Player attempting complex magical trap disarm",
        "query": "What skill check and DC are required?"
    }
}
```

### Conflict Resolution

The system implements a strict hierarchy:
1. **Adjudicator** (Rules) - Absolute authority on game mechanics
2. **Lorekeeper** (Lore) - Authority on world consistency and narrative
3. **Thespian** (Performance) - Character authenticity and roleplay
4. **Conductor** (Cohesion) - Final editorial authority for response quality

### The Hybrid Adjudicator

The Adjudicator implements a unique hybrid approach:
- **LLM Front-End**: Parses natural language queries into structured format
- **Deterministic Back-End**: Processes rules using traditional programming logic
- **Perfect Consistency**: Eliminates rule hallucinations and ensures fairness

## Extending the System

### Adding New Agents

1. Create agent file in `multi_agent_tool/`
2. Define agent tools and capabilities
3. Update coordination system in `dm_collective.py`
4. Add to module exports in `__init__.py`

### Customizing Behavior

- **Agent Instructions**: Modify system prompts for different campaign styles
- **Tool Functions**: Add specialized tools for unique game mechanics
- **Coordination Patterns**: Adjust agent interaction patterns for different scenarios

## Future Enhancements

- **Persistent World State**: Save/load campaign data
- **Voice Integration**: Audio input/output for more immersive play
- **Visual Integration**: Map generation and character art
- **Advanced NPC Memory**: Long-term relationship tracking
- **Custom Rule Sets**: Support for homebrew and other RPG systems
- **Human-in-the-Loop**: Seamless DM override capabilities

## Philosophy

The AI-DM Collective is designed as a **social prosthesis** - not to replace human creativity and connection, but to remove the cognitive burden and preparation overhead that often prevents people from experiencing collaborative storytelling through D&D. The system enables groups to focus on what matters most: creative interaction and shared narrative experience.

## Contributing

This implementation provides a foundation for advanced multi-agent RPG systems. Contributions are welcome to expand capabilities, improve coordination, or adapt the system for other game systems or storytelling applications.