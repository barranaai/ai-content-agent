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

def validate_platform_content(content, platform, config):
    """Validate content against platform-specific requirements"""
    
    print(f"\n🔍 Validating {platform.upper()} Content:")
    print("=" * 60)
    
    # Extract word count
    word_count = len(content.split())
    
    # Get platform requirements
    word_min = config.get('word_count', {}).get('min', 0)
    word_max = config.get('word_count', {}).get('max', 9999)
    voice = config.get('voice', 'Unknown')
    style = config.get('style', 'Unknown')
    
    print(f"📊 Content Statistics:")
    print(f"  - Word count: {word_count} (required: {word_min}-{word_max})")
    print(f"  - Voice: {voice}")
    print(f"  - Style: {style}")
    
    # Check word count (special handling for TikTok and Instagram)
    if platform == "tiktok":
        # For TikTok, we need to extract caption word count, not total word count
        caption_match = re.search(r'CAPTION.*?:(.*?)(?=\n\n|\Z)', content, re.DOTALL)
        if caption_match:
            caption_words = len(caption_match.group(1).strip().split())
            word_count_valid = 70 <= caption_words <= 120  # TikTok caption requirements
            status_word = "✅" if word_count_valid else "❌"
            print(f"  {status_word} Caption word count compliance: {caption_words} words (required: 70-120)")
        else:
            word_count_valid = False
            status_word = "❌"
            print(f"  {status_word} Caption word count compliance: No caption found")
    elif platform == "instagram":
        # For Instagram, we need to extract caption word count, not total word count
        caption_match = re.search(r'CAPTION.*?:(.*?)(?=\n\n|\Z)', content, re.DOTALL)
        if caption_match:
            caption_words = len(caption_match.group(1).strip().split())
            word_count_valid = word_min <= caption_words <= word_max
            status_word = "✅" if word_count_valid else "❌"
            print(f"  {status_word} Caption word count compliance: {caption_words} words (required: {word_min}-{word_max})")
        else:
            word_count_valid = False
            status_word = "❌"
            print(f"  {status_word} Caption word count compliance: No caption found")
    else:
        # Standard word count validation for other platforms
        word_count_valid = word_min <= word_count <= word_max
        status_word = "✅" if word_count_valid else "❌"
        print(f"  {status_word} Word count compliance")
    
    # Check voice compliance
    voice_valid = True
    if voice == "I (Ikram)":
        if "I " not in content and "I'm" not in content and "I've" not in content:
            voice_valid = False
            print(f"  ❌ Voice compliance: Missing first-person 'I' perspective")
        else:
            print(f"  ✅ Voice compliance: First-person 'I' perspective found")
    elif voice == "We (Barrana)":
        if "We " not in content and "we " not in content:
            voice_valid = False
            print(f"  ❌ Voice compliance: Missing 'We' perspective")
        else:
            print(f"  ✅ Voice compliance: 'We' perspective found")
    elif voice == "Flexible":
        print(f"  ✅ Voice compliance: Flexible voice (no specific check)")
    elif voice == "Technical":
        print(f"  ✅ Voice compliance: Technical voice")
    
    # Check for CTA
    cta_required = platform != "stackoverflow"
    cta_present = "barrana.ai" in content.lower() or "contact us" in content.lower()
    status_cta = "✅" if (cta_present and cta_required) or (not cta_required) else "❌"
    print(f"  {status_cta} CTA compliance: {'Present' if cta_present else 'Missing'}")
    
    # Check for hashtags (if required)
    hashtag_count = len(re.findall(r'#\w+', content))
    if 'hashtags' in config:
        hashtag_config = config['hashtags']
        if isinstance(hashtag_config, dict) and 'count' in hashtag_config:
            hashtag_req = hashtag_config['count']
            try:
                if isinstance(hashtag_req, str) and '-' in hashtag_req:
                    min_hashtags, max_hashtags = map(int, hashtag_req.split('-'))
                    hashtag_valid = min_hashtags <= hashtag_count <= max_hashtags
                elif isinstance(hashtag_req, str) and 'max' in hashtag_req.lower():
                    # Handle cases like "2-3 max", "5 trending + brand"
                    numbers = re.findall(r'\d+', hashtag_req)
                    if numbers:
                        max_hashtags = int(numbers[-1])  # Take the last number as max
                        hashtag_valid = hashtag_count <= max_hashtags
                    else:
                        hashtag_valid = True  # Skip validation if can't parse
                else:
                    hashtag_valid = hashtag_count >= int(hashtag_req.split()[0])
                status_hashtag = "✅" if hashtag_valid else "❌"
                print(f"  {status_hashtag} Hashtag compliance: {hashtag_count} hashtags (required: {hashtag_req})")
            except (ValueError, IndexError):
                print(f"  ⚠️  Hashtag compliance: {hashtag_count} hashtags (could not parse requirement: {hashtag_req})")
    
    # Platform-specific validations
    if platform == "twitter":
        validate_twitter_thread(content)
    elif platform == "tiktok":
        validate_tiktok_content(content)
    elif platform == "instagram":
        validate_instagram_content(content)
    elif platform == "barrana_blog":
        validate_barrana_blog_content(content)
    elif platform == "substack":
        validate_substack_content(content)
    elif platform == "stackoverflow":
        validate_stackoverflow_content(content)
    
    # Overall compliance
    overall_valid = word_count_valid and voice_valid and (cta_present if cta_required else True)
    print(f"\n📋 Overall Compliance: {'✅ PASS' if overall_valid else '❌ FAIL'}")
    
    return overall_valid

def validate_twitter_thread(content):
    """Validate Twitter thread format"""
    tweets = re.findall(r'\d+/\d+\s+(.+?)(?=\n\d+/\d+|\n---|\Z)', content, re.DOTALL)
    if tweets:
        print(f"  📱 Twitter Thread: {len(tweets)} tweets found")
        for i, tweet in enumerate(tweets[:3], 1):  # Check first 3 tweets
            char_count = len(tweet.strip())
            status = "✅" if char_count <= 280 else "❌"
            print(f"    {status} Tweet {i}: {char_count}/280 chars")

def validate_tiktok_content(content):
    """Validate TikTok content format"""
    if "VIDEO SCRIPT" in content and "CAPTION" in content:
        print(f"  📱 TikTok Format: Video script + caption structure found")
        # Extract caption
        caption_match = re.search(r'CAPTION.*?:(.*?)(?=\n\n|\Z)', content, re.DOTALL)
        if caption_match:
            caption = caption_match.group(1).strip()
            caption_words = len(caption.split())
            print(f"    📝 Caption: {caption_words} words (required: 70-120)")
    else:
        print(f"  📱 TikTok Format: Missing video script + caption structure")

def validate_instagram_content(content):
    """Validate Instagram content format"""
    if "VISUAL CONCEPT" in content and "CAPTION" in content:
        print(f"  📱 Instagram Format: Visual concept + caption structure found")
        # Extract caption
        caption_match = re.search(r'CAPTION.*?:(.*?)(?=\n\n|\Z)', content, re.DOTALL)
        if caption_match:
            caption = caption_match.group(1).strip()
            caption_words = len(caption.split())
            print(f"    📝 Caption: {caption_words} words (required: 100-150)")

def validate_barrana_blog_content(content):
    """Validate Barrana blog content"""
    # Check for SEO elements
    h2_count = len(re.findall(r'##\s+', content))
    h3_count = len(re.findall(r'###\s+', content))
    faq_count = len(re.findall(r'FAQ|Q:', content, re.IGNORECASE))
    kpi_count = len(re.findall(r'KPI|metric', content, re.IGNORECASE))
    
    print(f"  📝 SEO Elements:")
    print(f"    - H2 headings: {h2_count}")
    print(f"    - H3 headings: {h3_count}")
    print(f"    - FAQ mentions: {faq_count}")
    print(f"    - KPI mentions: {kpi_count}")

def validate_substack_content(content):
    """Validate Substack content"""
    # Check for roadmap structure
    roadmap_30 = "30 days" in content.lower() or "30-day" in content.lower()
    roadmap_60 = "60 days" in content.lower() or "60-day" in content.lower()
    roadmap_90 = "90 days" in content.lower() or "90-day" in content.lower()
    
    print(f"  📝 Roadmap Structure:")
    print(f"    - 30-day roadmap: {'✅' if roadmap_30 else '❌'}")
    print(f"    - 60-day roadmap: {'✅' if roadmap_60 else '❌'}")
    print(f"    - 90-day roadmap: {'✅' if roadmap_90 else '❌'}")

def validate_stackoverflow_content(content):
    """Validate StackOverflow content"""
    # Check for technical elements
    code_blocks = len(re.findall(r'```|`[^`]+`', content))
    technical_terms = len(re.findall(r'\b(API|function|method|class|variable|algorithm|implementation)\b', content))
    
    print(f"  💻 Technical Elements:")
    print(f"    - Code blocks: {code_blocks}")
    print(f"    - Technical terms: {technical_terms}")

def test_platform(platform, description, prompt_library, seo_manager):
    """Test a specific platform"""
    
    print(f"\n🚀 Testing Platform: {platform.upper()}")
    print("=" * 80)
    
    # Get platform config
    config = prompt_library.get_platform_config(platform)
    print(f"📋 Platform Configuration:")
    print(f"  - Voice: {config.get('voice', 'N/A')}")
    print(f"  - Word count: {config.get('word_count', 'N/A')}")
    print(f"  - Style: {config.get('style', 'N/A')}")
    print(f"  - Character limit: {config.get('character_limit', 'N/A')}")
    
    # Get keywords
    keywords = seo_manager.get_platform_optimized_keywords(platform, "general")
    print(f"🔑 Keywords:")
    print(f"  - Primary: {keywords['primary']}")
    print(f"  - Secondary: {keywords['secondary']}")
    
    # Build prompt
    prompt = prompt_library.build_prompt(
        description=description,
        platform=platform,
        primary_keywords=keywords['primary'],
        secondary_keywords=keywords['secondary']
    )
    
    print(f"\n📝 Generated Prompt Preview:")
    print("-" * 40)
    print(prompt[:300] + "..." if len(prompt) > 300 else prompt)
    print("-" * 40)
    
    # Make API call
    import openai
    client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        
        print(f"\n📄 Generated Content Preview:")
        print("-" * 40)
        print(content[:500] + "..." if len(content) > 500 else content)
        print("-" * 40)
        
        # Validate content
        is_valid = validate_platform_content(content, platform, config)
        
        return {
            'platform': platform,
            'valid': is_valid,
            'content': content,
            'config': config
        }
        
    except Exception as e:
        print(f"❌ Error generating content: {e}")
        return {
            'platform': platform,
            'valid': False,
            'error': str(e),
            'config': config
        }

def main():
    """Main testing function"""
    
    print("🔧 Initializing AI Content Agent Testing Suite")
    print("=" * 80)
    
    # Initialize systems
    prompt_library = BarranaPromptLibrary()
    seo_manager = SEOManager(prompt_library)
    
    print(f"✅ Prompt library loaded: {prompt_library.is_loaded()}")
    print(f"✅ Available platforms: {len(prompt_library.get_available_platforms())}")
    
    # Test description
    description = "A comprehensive guide to school reporting systems and AI automation for educational institutions"
    
    # Platforms to test
    platforms_to_test = [
        "linkedin",
        "medium", 
        "substack",
        "barrana_blog",
        "reddit",
        "quora",
        "tiktok",
        "instagram",
        "stackoverflow",
        "twitter_quick"
    ]
    
    results = []
    
    for platform in platforms_to_test:
        try:
            result = test_platform(platform, description, prompt_library, seo_manager)
            results.append(result)
        except Exception as e:
            print(f"❌ Failed to test {platform}: {e}")
            results.append({
                'platform': platform,
                'valid': False,
                'error': str(e)
            })
    
    # Summary
    print(f"\n📊 TESTING SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for r in results if r.get('valid', False))
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total} platforms")
    print(f"❌ Failed: {total - passed}/{total} platforms")
    
    print(f"\n📋 Detailed Results:")
    for result in results:
        status = "✅ PASS" if result.get('valid', False) else "❌ FAIL"
        error = f" - {result.get('error', '')}" if 'error' in result else ""
        print(f"  {status} {result['platform']}{error}")
    
    return results

if __name__ == "__main__":
    main()
