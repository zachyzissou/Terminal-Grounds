# -*- coding: utf-8 -*-
"""
Test script for Website Prompt Specialist Agent
Demonstrates the agent's capabilities by generating sample web content for Terminal Grounds
"""

def test_agent_examples():
    """
    Examples of how to use the website-prompt-specialist agent
    """
    
    examples = {
        "hero_section": {
            "prompt": "Create compelling hero section copy for bloom.slurpgg.net that showcases Terminal Grounds as a territorial warfare extraction shooter. We have 109+ professional assets including faction emblems, environmental concept art, and complete Bloom branding. Focus on faction-based territorial control and post-Cascade setting.",
            "expected_outputs": [
                "Safe: Traditional FPS messaging with clear value props",
                "Bold: Faction warfare emphasis with emotional hooks", 
                "Experimental: Immersive post-Cascade narrative approach"
            ]
        },
        
        "faction_showcase": {
            "prompt": "Design faction showcase content for Terminal Grounds' seven factions (Sky Bastion Directorate, Iron Scavengers, The Seventy-Seven, Corporate Hegemony, Nomad Clans, Archive Keepers, Civic Wardens) that builds emotional investment and drives faction loyalty.",
            "expected_outputs": [
                "Individual faction personality profiles",
                "Strategic gameplay implications of each choice",
                "Visual asset integration recommendations"
            ]
        },
        
        "feature_explanation": {
            "prompt": "Explain Terminal Grounds' territorial warfare system for website visitors in a way that's accessible to casual FPS players while highlighting the strategic depth for hardcore extraction shooter enthusiasts.",
            "expected_outputs": [
                "Progressive disclosure content architecture",
                "Visual storytelling integration strategy",
                "Conversion-focused feature hierarchy"
            ]
        }
    }
    
    return examples

def main():
    """
    Main test function showing agent usage patterns
    """
    print("Website Prompt Specialist Agent - Test Examples")
    print("=" * 50)
    
    examples = test_agent_examples()
    
    for test_name, test_data in examples.items():
        print(f"\n{test_name.upper()} TEST:")
        print(f"Prompt: {test_data['prompt']}")
        print("Expected Agent Capabilities:")
        for output in test_data['expected_outputs']:
            print(f"  - {output}")
    
    print("\n" + "=" * 50)
    print("Agent is ready for testing!")
    print("Use: Task tool with subagent_type='website-prompt-specialist'")

if __name__ == "__main__":
    main()