#!/usr/bin/env python3

import os
import sys
import re
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append('.')

from prompt_library import BarranaPromptLibrary
from seo_manager import SEOManager

def test_platform_fixes():
    """Test the fixes for problematic platforms"""
    
    print("🔧 Testing Platform Fixes")
    print("=" * 60)
    
    # Initialize systems
    prompt_library = BarranaPromptLibrary()
    seo_manager = SEOManager(prompt_library)
    
    # Test description
    description = "A comprehensive guide to school reporting systems and AI automation for educational institutions"
    
    # Test problematic platforms
    platforms_to_test = [
        "linkedin",      # Word count issue
        "medium",        # Word count + hashtag parsing
        "twitter_quick", # CTA issue
        "tiktok",        # Word count validation
        "instagram"      # Word count validation
    ]
    
    import openai
    client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    for platform in platforms_to_test:
        print(f"\n🚀 Testing {platform.upper()}")
        print("-" * 40)
        
        # Get platform config
        config = prompt_library.get_platform_config(platform)
        
        # Get keywords
        keywords = seo_manager.get_platform_optimized_keywords(platform, "general")
        
        # Build prompt
        prompt = prompt_library.build_prompt(
            description=description,
            platform=platform,
            primary_keywords=keywords['primary'],
            secondary_keywords=keywords['secondary']
        )
        
        print(f"📝 Prompt includes word count enforcement: {'✅' if 'CRITICAL WORD COUNT' in prompt or 'CRITICAL REQUIREMENTS' in prompt else '❌'}")
        
        try:
            # Make API call with appropriate token limits
            if platform in ['medium', 'substack', 'barrana_blog']:
                max_tokens = 2000  # Longer content needs more tokens
            elif platform in ['linkedin', 'quora', 'reddit']:
                max_tokens = 800
            else:
                max_tokens = 600
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            
            # Validate content
            word_count = len(content.split())
            word_min = config['word_count']['min']
            word_max = config['word_count']['max']
            
            print(f"📊 Generated: {word_count} words (required: {word_min}-{word_max})")
            
            # Check for CTA
            cta_present = "barrana.ai" in content.lower() or "contact us" in content.lower()
            print(f"📞 CTA present: {'✅' if cta_present else '❌'}")
            
            # Check hashtags
            hashtag_count = len(re.findall(r'#\w+', content))
            print(f"🏷️  Hashtags: {hashtag_count}")
            
            # Platform-specific checks
            if platform == "linkedin":
                voice_check = "I " in content or "I'm" in content
                print(f"👤 Voice (I): {'✅' if voice_check else '❌'}")
            
            elif platform == "medium":
                voice_check = "We " in content or "we " in content
                print(f"👥 Voice (We): {'✅' if voice_check else '❌'}")
            
            elif platform == "twitter_quick":
                tweets = re.findall(r'\d+/\d+\s+(.+?)(?=\n\d+/\d+|\n---|\Z)', content, re.DOTALL)
                print(f"🐦 Tweets: {len(tweets)}")
                if tweets:
                    last_tweet = tweets[-1].strip()
                    cta_in_last = "barrana.ai" in last_tweet.lower() or "contact" in last_tweet.lower() or "discuss" in last_tweet.lower()
                    print(f"📞 CTA in last tweet: {'✅' if cta_in_last else '❌'}")
            
            elif platform == "tiktok":
                has_script = "VIDEO SCRIPT" in content
                has_caption = "CAPTION" in content
                print(f"🎬 Video script: {'✅' if has_script else '❌'}")
                print(f"📝 Caption: {'✅' if has_caption else '❌'}")
            
            elif platform == "instagram":
                has_visual = "VISUAL CONCEPT" in content
                has_caption = "CAPTION" in content
                print(f"🖼️  Visual concept: {'✅' if has_visual else '❌'}")
                print(f"📝 Caption: {'✅' if has_caption else '❌'}")
            
            print(f"📄 Content preview: {content[:200]}...")
            
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_platform_fixes()
