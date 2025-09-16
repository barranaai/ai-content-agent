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

def debug_twitter_prompt():
    """Debug the Twitter prompt building process"""
    
    print("🔧 Initializing systems...")
    
    # Initialize systems
    prompt_library = BarranaPromptLibrary()
    seo_manager = SEOManager(prompt_library)
    
    print(f"✅ Prompt library loaded: {prompt_library.is_loaded()}")
    print(f"✅ Available platforms: {len(prompt_library.get_available_platforms())}")
    
    # Test data
    description = "A comprehensive guide to school reporting systems"
    platform = "twitter"
    
    print(f"\n📝 Testing prompt for platform: {platform}")
    print(f"📝 Description: {description}")
    
    # Get platform config
    config = prompt_library.get_platform_config(platform)
    print(f"\n🔍 Platform config:")
    print(f"  - Voice: {config.get('voice', 'N/A')}")
    print(f"  - Word count: {config.get('word_count', 'N/A')}")
    print(f"  - Style: {config.get('style', 'N/A')}")
    print(f"  - Character limit: {config.get('character_limit', 'N/A')}")
    
    # Get keywords
    keywords = seo_manager.get_platform_optimized_keywords(platform, "general")
    print(f"\n🔑 Keywords:")
    print(f"  - Primary: {keywords['primary']}")
    print(f"  - Secondary: {keywords['secondary']}")
    
    # Build prompt
    prompt = prompt_library.build_prompt(
        description=description,
        platform=platform,
        primary_keywords=keywords['primary'],
        secondary_keywords=keywords['secondary']
    )
    
    print(f"\n📋 Generated Prompt:")
    print("=" * 80)
    print(prompt)
    print("=" * 80)
    print(f"\n📊 Prompt Statistics:")
    print(f"  - Length: {len(prompt)} characters")
    print(f"  - Lines: {len(prompt.split(chr(10)))}")
    
    # Check if prompt template exists
    if 'prompt_template' in config:
        print(f"\n✅ Prompt template found in config")
        template = config['prompt_template']
        print(f"📝 Template preview: {template[:200]}...")
    else:
        print(f"\n❌ No prompt_template found in config!")
        print(f"Available keys: {list(config.keys())}")

if __name__ == "__main__":
    debug_twitter_prompt()
