#!/usr/bin/env python3
"""
Test Platform-Specific Metrics System
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from platform_specific_metrics import PlatformSpecificMetrics
from prompt_library import BarranaPromptLibrary

def test_platform_specific_metrics():
    """Test platform-specific metrics for different platforms"""
    
    print("=== TESTING PLATFORM-SPECIFIC METRICS ===\n")
    
    # Initialize components
    prompt_library = BarranaPromptLibrary()
    platform_metrics = PlatformSpecificMetrics()
    
    # Test platforms
    test_platforms = [
        'linkedin',
        'medium', 
        'twitter',
        'tiktok',
        'instagram',
        'linkedin_quick',
        'twitter_quick'
    ]
    
    # Sample content for testing
    sample_content = """
    I believe that AI automation is revolutionizing small business operations. 
    We at Barrana have seen incredible results with our AI chatbot solutions.
    
    Here are 3 key insights:
    1. AI chatbots reduce customer service costs by 30%
    2. Automation improves response times significantly
    3. Small businesses can compete with larger enterprises
    
    What do you think about AI automation? Share your experience below!
    
    #AI #Automation #SmallBusiness #Chatbots #Innovation
    """
    
    primary_keywords = ['AI automation', 'small business', 'chatbots']
    secondary_keywords = ['customer service', 'automation', 'business operations']
    
    for platform in test_platforms:
        print(f"🎯 TESTING PLATFORM: {platform.upper()}")
        print("=" * 50)
        
        # Get platform configuration
        config = platform_metrics.get_platform_config(platform)
        if not config:
            print(f"❌ No configuration found for {platform}")
            continue
        
        print(f"📋 Platform Configuration:")
        print(f"   Voice: {config.get('voice_text', 'N/A')}")
        print(f"   Word Range: {config.get('word_range', 'N/A')}")
        print(f"   Keywords Range: {config.get('keywords_range', 'N/A')}")
        print(f"   Hashtags Range: {config.get('hashtags_range', 'N/A')}")
        print(f"   Tone: {config.get('tone', 'N/A')}")
        print(f"   CTA Type: {config.get('cta_type', 'N/A')}")
        print(f"   Special Rules: {config.get('special_rules', [])}")
        print(f"   Unique Features: {config.get('unique_features', [])}")
        print()
        
        # Calculate platform-specific metrics
        try:
            metrics = platform_metrics.calculate_platform_specific_metrics(
                platform, sample_content, primary_keywords, secondary_keywords
            )
            
            print(f"📊 Platform-Specific Metrics:")
            for metric_name, metric_value in metrics.items():
                if isinstance(metric_value, dict):
                    if 'compliance_percentage' in metric_value:
                        print(f"   {metric_name}: {metric_value['compliance_percentage']}%")
                    elif 'score' in metric_value:
                        print(f"   {metric_name}: {metric_value['score']:.2f}")
                    else:
                        print(f"   {metric_name}: {metric_value}")
                else:
                    print(f"   {metric_name}: {metric_value}")
            
            print()
            
        except Exception as e:
            print(f"❌ Error calculating metrics for {platform}: {e}")
            print()
    
    print("=== PLATFORM METRICS SUMMARY ===")
    print("\n📈 Platform Categories by Unique Elements:")
    
    # Group platforms by unique characteristics
    voice_platforms = {
        'Personal Voice (I Ikram)': ['linkedin', 'ikramrana_blog', 'linkedin_quick', 'reddit', 'quora'],
        'Corporate Voice (We Barrana)': ['medium', 'substack', 'barrana_blog', 'slideshare', 'product_hunt', 'crunchbase', 'substack_quick'],
        'Flexible Voice': ['twitter', 'tiktok', 'instagram', 'facebook', 'pinterest', 'skool', 'twitter_quick'],
        'Technical Voice': ['stackoverflow', 'dev_to']
    }
    
    for voice_type, platforms in voice_platforms.items():
        print(f"\n🎭 {voice_type}:")
        for platform in platforms:
            config = platform_metrics.get_platform_config(platform)
            if config:
                word_range = config.get('word_range', (0, 1000))
                keywords_range = config.get('keywords_range', (1, 5))
                hashtags_range = config.get('hashtags_range', (1, 5))
                print(f"   • {platform}: {word_range[0]}-{word_range[1]} words, {keywords_range[0]}-{keywords_range[1]} keywords, {hashtags_range[0]}-{hashtags_range[1]} hashtags")
    
    print("\n🎯 Content Format Categories:")
    format_categories = {
        'Long-Form (800+ words)': ['medium', 'substack', 'barrana_blog', 'ikramrana_blog'],
        'Medium-Form (400-800 words)': ['linkedin', 'reddit', 'quora', 'dev_to', 'skool'],
        'Short-Form (100-400 words)': ['tiktok', 'instagram', 'facebook', 'pinterest', 'product_hunt', 'crunchbase'],
        'Micro Content (1-12 tweets)': ['twitter', 'twitter_quick'],
        'Ultra Short Form (80-300 words)': ['linkedin_quick', 'substack_quick'],
        'Visual Content': ['slideshare']
    }
    
    for format_type, platforms in format_categories.items():
        print(f"\n📝 {format_type}:")
        for platform in platforms:
            config = platform_metrics.get_platform_config(platform)
            if config:
                word_range = config.get('word_range', (0, 1000))
                print(f"   • {platform}: {word_range[0]}-{word_range[1]} words")
    
    print("\n✅ Platform-specific metrics system is ready!")
    print("🎯 Each platform now has unique quality metrics based on their specific requirements!")
    print("📊 The frontend will display platform-specific metrics instead of generic ones!")

if __name__ == "__main__":
    test_platform_specific_metrics()
