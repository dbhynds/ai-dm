#!/usr/bin/env python3
"""
AI-DM Collective - Main Application

This is the main entry point for the AI-DM Collective system, demonstrating
how to use the multi-agent D&D Dungeon Master system.
"""

import asyncio
import sys
from typing import Dict, Any
from multi_agent_tool import dm_collective_agent, initialize_dm_session, DMCollectiveSession

def print_banner():
    """Print the AI-DM Collective banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                    AI-DM COLLECTIVE                          ║
    ║           A Multi-Agent D&D Dungeon Master System           ║
    ╚══════════════════════════════════════════════════════════════╝
    
    The AI-DM Collective consists of six specialized agents:
    • The Conductor - Orchestrates the entire system
    • The Lorekeeper - Maintains world lore and narrative
    • The Chronicler - Provides vivid descriptions  
    • The Thespian - Embodies all NPCs and characters
    • The Adjudicator - Enforces rules with perfect consistency
    • The Architect - Designs encounters and manages pacing
    """
    print(banner)

def get_party_info() -> Dict[str, Any]:
    """Get basic party information for session setup."""
    print("\n=== PARTY SETUP ===")
    
    try:
        party_size = int(input("Enter party size (1-8): ").strip() or "4")
        party_size = max(1, min(8, party_size))
        
        avg_level = float(input("Enter average party level (1-20): ").strip() or "3")
        avg_level = max(1, min(20, avg_level))
        
        print("Enter party classes (comma-separated):")
        print("Examples: fighter,wizard,cleric,rogue")
        classes_input = input("Classes: ").strip() or "fighter,wizard,cleric,rogue"
        classes = [cls.strip().lower() for cls in classes_input.split(",")]
        
        print("Enter party strengths (comma-separated):")
        print("Options: combat, social, exploration, stealth")
        strengths_input = input("Strengths: ").strip() or "combat"
        strengths = [s.strip().lower() for s in strengths_input.split(",")]
        
        return {
            "size": party_size,
            "average_level": avg_level,
            "classes": classes,
            "strengths": strengths,
            "weaknesses": []
        }
        
    except (ValueError, KeyboardInterrupt):
        print("Using default party setup...")
        return {
            "size": 4,
            "average_level": 3,
            "classes": ["fighter", "wizard", "cleric", "rogue"],
            "strengths": ["combat"],
            "weaknesses": []
        }

async def run_dm_session(session: DMCollectiveSession):
    """Run an interactive DM session."""
    
    print("\n=== SESSION STARTED ===")
    print("Type 'help' for commands, 'quit' to exit")
    print("=" * 50)
    
    # Welcome message
    welcome_msg = """
    Welcome, brave adventurers! You find yourselves at the edge of a small 
    frontier town called Millbrook. The cobblestone streets are busy with 
    merchants and travelers, and the air carries the scent of fresh bread 
    from the local bakery. To the north, dark woods stretch toward distant 
    mountains where ancient ruins are said to lie hidden.
    
    What would you like to do?
    """
    
    print(welcome_msg)
    
    # Set initial game state
    session.game_state.current_location = "Millbrook Town Square"
    session.game_state.log_event("location_change", "Party arrived in Millbrook", "system")
    
    while True:
        try:
            # Get player input
            player_input = input("\n> ").strip()
            
            if not player_input:
                continue
            
            # Handle special commands
            if player_input.lower() in ['quit', 'exit']:
                print("\nThanks for playing! May your adventures continue...")
                break
            elif player_input.lower() == 'help':
                show_help()
                continue
            elif player_input.lower().startswith('status'):
                show_game_status(session)
                continue
            elif player_input.lower().startswith('save'):
                save_session(session)
                continue
            
            # Process input through the AI-DM Collective
            print("\n[The AI-DM Collective is processing your action...]\n")
            
            # For this demo, we'll simulate the async processing
            # In a full implementation, this would be:
            # response = await process_player_input(session, player_input)
            
            # Simulate processing time
            import time
            time.sleep(1)
            
            # Generate a demo response
            demo_response = generate_demo_response(player_input, session)
            print(demo_response)
            
        except KeyboardInterrupt:
            print("\n\nSession interrupted. Thanks for playing!")
            break
        except Exception as e:
            print(f"\nError occurred: {e}")
            print("The DM collective is recovering...")

def generate_demo_response(player_input: str, session: DMCollectiveSession) -> str:
    """Generate a demonstration response showing multi-agent coordination."""
    
    input_lower = player_input.lower()
    
    # Simulate different types of responses based on input
    if any(word in input_lower for word in ["look", "examine", "see"]):
        return """The town square bustles with afternoon activity. Merchants hawk their 
        wares from colorful stalls, their voices creating a cheerful cacophony. The 
        scent of roasting meat from a nearby vendor mingles with the earthy smell 
        of horses and leather. To the east, a weathered inn sign creaks in the 
        gentle breeze, depicting a prancing unicorn. A group of children play near 
        a stone fountain at the square's center, their laughter echoing off the 
        surrounding buildings."""
        
    elif any(word in input_lower for word in ["attack", "fight", "draw sword"]):
        return """**Rules Check:** You cannot attack in a peaceful town square without 
        provocation. Such an action would be against local laws and likely result 
        in intervention by town guards. If you wish to engage in combat, you might 
        seek out the local training grounds, or perhaps investigate rumors of 
        monsters in the nearby woods."""
        
    elif any(word in input_lower for word in ["talk", "speak", "approach"]):
        return """A cheerful halfling merchant notices your approach and grins widely, 
        revealing a gold tooth. "Well hello there, travelers! Welcome to Millbrook! 
        Name's Pip Goldleaf, and I've got the finest goods this side of the 
        Whispering Woods. Looking for supplies for an adventure, perhaps? I've 
        heard tell of some interesting happenings up in the old ruins lately..."
        
        His eyes twinkle with the promise of potential adventure."""
        
    elif any(word in input_lower for word in ["cast", "spell", "magic"]):
        return """**Mechanics:** Casting spells in town requires consideration of local 
        laws and social norms. Minor cantrips like Prestidigitation are generally 
        acceptable for entertainment or practical purposes. More powerful magic 
        might draw unwanted attention or require official permission.
        
        The air shimmers slightly as you consider your magical options, and you 
        notice several townsfolk watching with a mixture of curiosity and caution."""
        
    else:
        # General exploration response
        return f"""You decide to {player_input.lower()}. The AI-DM Collective is 
        coordinating to provide you with the most appropriate response...
        
        **[Demo Mode]** In a full session, this would involve:
        • The Conductor parsing your intent
        • Specialist agents analyzing implications  
        • The Lorekeeper checking narrative consequences
        • The Chronicler crafting descriptions
        • The Thespian voicing any NPCs
        • The Adjudicator validating rules
        • The Architect considering pacing
        
        All working together to create an immersive D&D experience!"""

def show_help():
    """Display help information."""
    help_text = """
    AVAILABLE COMMANDS:
    
    • help         - Show this help message
    • status       - Display current game status  
    • quit/exit    - End the session
    • save         - Save current session state
    
    GAMEPLAY:
    Simply describe what your character wants to do in natural language.
    Examples:
    • "I examine the fountain in the square"
    • "I approach the merchant and ask about rumors"
    • "I cast Light on my staff" 
    • "I search for a tavern"
    
    The AI-DM Collective will coordinate multiple specialist agents to 
    provide comprehensive responses covering rules, narrative, NPCs, 
    descriptions, and pacing.
    """
    print(help_text)

def show_game_status(session: DMCollectiveSession):
    """Display current game status."""
    status = f"""
    CURRENT GAME STATUS:
    
    Location: {session.game_state.current_location}
    Combat Active: {session.game_state.combat_active}
    Turn Number: {session.game_state.turn_number}
    
    Characters: {len(session.game_state.characters)} registered
    Active NPCs: {len(session.active_npcs)}
    Session Events: {len(session.session_log)}
    
    Party Composition:
    • Size: {session.party_composition.size if session.party_composition else 'Unknown'}
    • Average Level: {session.party_composition.average_level if session.party_composition else 'Unknown'}
    • Classes: {', '.join(session.party_composition.classes) if session.party_composition else 'Unknown'}
    """
    print(status)

def save_session(session: DMCollectiveSession):
    """Save the current session state (placeholder)."""
    print("Session save functionality would be implemented here.")
    print("This would serialize the game state, world bible, and session log.")

async def main():
    """Main application entry point."""
    
    print_banner()
    
    # Get campaign setup
    campaign_name = input("Enter campaign name (or press Enter for 'Demo Campaign'): ").strip()
    if not campaign_name:
        campaign_name = "Demo Campaign"
    
    party_info = get_party_info()
    
    # Initialize the DM session
    print(f"\nInitializing {campaign_name}...")
    print("Loading AI-DM Collective agents...")
    
    session = initialize_dm_session(campaign_name, party_info)
    
    print("✓ Conductor - System orchestration ready")
    print("✓ Lorekeeper - World knowledge loaded")  
    print("✓ Chronicler - Descriptive capabilities active")
    print("✓ Thespian - Character voice system ready")
    print("✓ Adjudicator - Rules engine initialized")
    print("✓ Architect - Encounter systems online")
    
    # Run the session
    await run_dm_session(session)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        sys.exit(0)