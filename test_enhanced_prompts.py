#!/usr/bin/env python3

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append('.')

from prompt_library import BarranaPromptLibrary
from seo_manager import SEOManager

def test_enhanced_prompts():
    """Test the enhanced prompt generation with all JSON elements"""
    
    print("🔧 TESTING ENHANCED PROMPT GENERATION")
    print("=" * 80)
    
    # Initialize systems
    prompt_library = BarranaPromptLibrary()
    seo_manager = SEOManager(prompt_library)
    
    # Test description
    description = "A comprehensive guide to school reporting systems and AI automation for educational institutions"
    
    # Test key platforms that had missing elements
    test_platforms = [
        "linkedin",      # Missing style "Thought leadership"
        "medium",         # Missing style "SEO-optimized article"
        "barrana_blog",   # Missing style + visuals + SEO
        "twitter",        # Missing style "Thread format"
        "pinterest",      # Missing style + visuals + keyword requirement
        "slideshare",     # Missing voice + style + structure + keywords
        "product_hunt"    # Missing style + structure + visuals + keywords
    ]
    
    for platform in test_platforms:
        print(f"\n🚀 Testing {platform.upper()}")
        print("-" * 50)
        
        # Get keywords
        keywords = seo_manager.get_platform_optimized_keywords(platform, "general")
        
        # Build enhanced prompt
        prompt = prompt_library.build_prompt(
            description=description,
            platform=platform,
            primary_keywords=keywords['primary'],
            secondary_keywords=keywords['secondary']
        )
        
        print(f"📝 Enhanced Prompt Preview:")
        print("-" * 30)
        print(prompt[:800] + "..." if len(prompt) > 800 else prompt)
        print("-" * 30)
        
        # Check for key elements
        checks = {
            "Style Requirement": "STYLE REQUIREMENT" in prompt,
            "Structure Requirement": "STRUCTURE REQUIREMENT" in prompt,
            "Visual Requirements": "VISUAL REQUIREMENTS" in prompt,
            "SEO Requirements": "SEO REQUIREMENTS" in prompt,
            "Special Rules": "SPECIAL RULES" in prompt,
            "Platform Rules": "PLATFORM RULES" in prompt,
            "Critical Requirements": "CRITICAL REQUIREMENTS" in prompt
        }
        
        print(f"📊 Element Inclusion Check:")
        for check, included in checks.items():
            status = "✅" if included else "❌"
            print(f"  {status} {check}")
        
        print(f"📏 Prompt Length: {len(prompt)} characters")

if __name__ == "__main__":
    test_enhanced_prompts()
