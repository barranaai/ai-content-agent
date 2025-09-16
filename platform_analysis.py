#!/usr/bin/env python3

import json
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append('.')

from prompt_library import BarranaPromptLibrary
from seo_manager import SEOManager

def analyze_platform_json_elements():
    """Analyze all platform elements from the JSON library"""
    
    print("🔍 COMPREHENSIVE PLATFORM ANALYSIS")
    print("=" * 80)
    
    # Load the JSON library
    with open('Barrana-Merged-Prompt-Library-v3.1.json', 'r') as f:
        json_library = json.load(f)
    
    platforms = json_library['platforms']
    
    # Initialize systems
    prompt_library = BarranaPromptLibrary()
    seo_manager = SEOManager(prompt_library)
    
    # Test description
    description = "A comprehensive guide to school reporting systems and AI automation for educational institutions"
    
    for platform_name, platform_config in platforms.items():
        print(f"\n🚀 ANALYZING PLATFORM: {platform_name.upper()}")
        print("=" * 60)
        
        # Display all JSON elements for this platform
        print(f"📋 JSON CONFIGURATION ELEMENTS:")
        for key, value in platform_config.items():
            print(f"  - {key}: {value}")
        
        print(f"\n🔧 CURRENT PROMPT GENERATION:")
        
        # Get keywords
        keywords = seo_manager.get_platform_optimized_keywords(platform_name, "general")
        
        # Build current prompt
        current_prompt = prompt_library.build_prompt(
            description=description,
            platform=platform_name,
            primary_keywords=keywords['primary'],
            secondary_keywords=keywords['secondary']
        )
        
        print(f"📝 Generated Prompt Preview:")
        print("-" * 40)
        print(current_prompt[:500] + "..." if len(current_prompt) > 500 else current_prompt)
        print("-" * 40)
        
        # Analyze what's missing
        print(f"\n🔍 MISSING ELEMENT ANALYSIS:")
        
        # Check voice
        voice = platform_config.get('voice', '')
        if voice == "I (Ikram)":
            if "I (Ikram Rana)" not in current_prompt and "I (Ikram)" not in current_prompt:
                print(f"  ❌ Missing voice: {voice}")
            else:
                print(f"  ✅ Voice included: {voice}")
        elif voice == "We (Barrana)":
            if "We (Barrana)" not in current_prompt:
                print(f"  ❌ Missing voice: {voice}")
            else:
                print(f"  ✅ Voice included: {voice}")
        
        # Check word count
        word_count = platform_config.get('word_count', {})
        if word_count:
            min_words = word_count.get('min', 0)
            max_words = word_count.get('max', 9999)
            unit = word_count.get('unit', 'words')
            if f"{min_words}-{max_words}" not in current_prompt:
                print(f"  ❌ Missing word count: {min_words}-{max_words} {unit}")
            else:
                print(f"  ✅ Word count included: {min_words}-{max_words} {unit}")
        
        # Check style
        style = platform_config.get('style', '')
        if style and style.lower() not in current_prompt.lower():
            print(f"  ❌ Missing style: {style}")
        else:
            print(f"  ✅ Style included: {style}")
        
        # Check hashtags
        hashtags = platform_config.get('hashtags', {})
        if hashtags:
            count = hashtags.get('count', '')
            examples = hashtags.get('examples', [])
            if count and count not in current_prompt:
                print(f"  ❌ Missing hashtag count: {count}")
            else:
                print(f"  ✅ Hashtag count included: {count}")
            
            if examples:
                missing_examples = [ex for ex in examples if ex not in current_prompt]
                if missing_examples:
                    print(f"  ❌ Missing hashtag examples: {missing_examples}")
                else:
                    print(f"  ✅ Hashtag examples included: {examples}")
        
        # Check keywords
        keywords_config = platform_config.get('keywords', {})
        if keywords_config:
            primary_count = keywords_config.get('primary', 0)
            secondary_count = keywords_config.get('secondary', 0)
            if primary_count > 0 and "primary keyword" not in current_prompt.lower():
                print(f"  ❌ Missing primary keyword requirement: {primary_count}")
            else:
                print(f"  ✅ Primary keyword requirement included: {primary_count}")
            
            if secondary_count > 0 and "secondary keyword" not in current_prompt.lower():
                print(f"  ❌ Missing secondary keyword requirement: {secondary_count}")
            else:
                print(f"  ✅ Secondary keyword requirement included: {secondary_count}")
        
        # Check structure
        structure = platform_config.get('structure', [])
        if structure:
            missing_structure = [s for s in structure if s.lower() not in current_prompt.lower()]
            if missing_structure:
                print(f"  ❌ Missing structure elements: {missing_structure}")
            else:
                print(f"  ✅ Structure elements included: {structure}")
        
        # Check special rules
        rules = platform_config.get('rules', {})
        if rules:
            for rule_key, rule_value in rules.items():
                if rule_key == 'no_links' and rule_value:
                    if "no links" not in current_prompt.lower():
                        print(f"  ❌ Missing rule: {rule_key} = {rule_value}")
                    else:
                        print(f"  ✅ Rule included: {rule_key} = {rule_value}")
        
        # Check SEO requirements
        seo_requirements = platform_config.get('seo_requirements', {})
        if seo_requirements:
            for seo_key, seo_value in seo_requirements.items():
                if seo_key == 'title_keywords' and seo_value:
                    if "title" not in current_prompt.lower() or "keyword" not in current_prompt.lower():
                        print(f"  ❌ Missing SEO requirement: {seo_key} = {seo_value}")
                    else:
                        print(f"  ✅ SEO requirement included: {seo_key} = {seo_value}")
        
        # Check visuals
        visuals = platform_config.get('visuals', [])
        if visuals:
            missing_visuals = [v for v in visuals if v.lower() not in current_prompt.lower()]
            if missing_visuals:
                print(f"  ❌ Missing visuals: {missing_visuals}")
            else:
                print(f"  ✅ Visuals included: {visuals}")
        
        # Check special rules
        special_rules = platform_config.get('special_rules', '')
        if special_rules:
            if special_rules.lower() not in current_prompt.lower():
                print(f"  ❌ Missing special rules: {special_rules}")
            else:
                print(f"  ✅ Special rules included: {special_rules}")
        
        print(f"\n📊 ANALYSIS SUMMARY:")
        print(f"  Platform: {platform_name}")
        print(f"  Prompt length: {len(current_prompt)} characters")
        print(f"  JSON elements: {len(platform_config)}")
        
        print("\n" + "="*60)

if __name__ == "__main__":
    analyze_platform_json_elements()
