#!/usr/bin/env python3

import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append('.')

from prompt_library import BarranaPromptLibrary
from seo_manager import SEOManager

def estimate_token_usage():
    """Estimate token usage for all 21 platforms"""
    
    print("💰 GPT-4 Cost Estimation for All 21 Platforms")
    print("=" * 60)
    
    # Initialize systems
    prompt_library = BarranaPromptLibrary()
    seo_manager = SEOManager(prompt_library)
    
    # Test description
    description = "A comprehensive guide to school reporting systems and AI automation for educational institutions"
    
    # GPT-4 Pricing (as of 2024)
    INPUT_COST_PER_1K_TOKENS = 0.03  # $0.03 per 1K input tokens
    OUTPUT_COST_PER_1K_TOKENS = 0.06  # $0.06 per 1K output tokens
    
    # Rough token estimation (1 token ≈ 4 characters for English text)
    CHARS_PER_TOKEN = 4
    
    platforms = prompt_library.get_available_platforms()
    
    total_input_tokens = 0
    total_output_tokens = 0
    platform_costs = []
    
    print(f"📊 Analyzing {len(platforms)} platforms:")
    print("-" * 60)
    
    for platform in platforms:
        try:
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
            
            # Estimate input tokens (prompt length)
            input_tokens = len(prompt) / CHARS_PER_TOKEN
            
            # Estimate output tokens based on platform requirements
            word_count = config.get('word_count', {})
            if isinstance(word_count, dict):
                avg_words = (word_count.get('min', 100) + word_count.get('max', 200)) / 2
            else:
                avg_words = 150  # Default estimate
            
            # Convert words to tokens (1 word ≈ 1.3 tokens)
            output_tokens = avg_words * 1.3
            
            # Calculate costs
            input_cost = (input_tokens / 1000) * INPUT_COST_PER_1K_TOKENS
            output_cost = (output_tokens / 1000) * OUTPUT_COST_PER_1K_TOKENS
            total_cost = input_cost + output_cost
            
            total_input_tokens += input_tokens
            total_output_tokens += output_tokens
            
            platform_costs.append({
                'platform': platform,
                'input_tokens': int(input_tokens),
                'output_tokens': int(output_tokens),
                'total_tokens': int(input_tokens + output_tokens),
                'cost': round(total_cost, 4)
            })
            
            print(f"{platform:20} | {int(input_tokens):4} + {int(output_tokens):4} = {int(input_tokens + output_tokens):4} tokens | ${total_cost:.4f}")
            
        except Exception as e:
            print(f"{platform:20} | ERROR: {e}")
    
    # Calculate totals
    total_tokens = total_input_tokens + total_output_tokens
    total_input_cost = (total_input_tokens / 1000) * INPUT_COST_PER_1K_TOKENS
    total_output_cost = (total_output_tokens / 1000) * OUTPUT_COST_PER_1K_TOKENS
    total_cost = total_input_cost + total_output_cost
    
    print("-" * 60)
    print(f"📊 SUMMARY:")
    print(f"Total Input Tokens:  {int(total_input_tokens):,}")
    print(f"Total Output Tokens: {int(total_output_tokens):,}")
    print(f"Total Tokens:        {int(total_tokens):,}")
    print(f"")
    print(f"💰 COST BREAKDOWN:")
    print(f"Input Cost:          ${total_input_cost:.4f}")
    print(f"Output Cost:         ${total_output_cost:.4f}")
    print(f"TOTAL COST:          ${total_cost:.4f}")
    print(f"")
    print(f"💡 COST PER PLATFORM: ${total_cost/len(platforms):.4f}")
    
    # Additional scenarios
    print(f"\n🔄 SCENARIOS:")
    print(f"Daily (1x):          ${total_cost:.4f}")
    print(f"Weekly (7x):         ${total_cost * 7:.4f}")
    print(f"Monthly (30x):       ${total_cost * 30:.4f}")
    print(f"Yearly (365x):       ${total_cost * 365:.4f}")
    
    # Cost optimization tips
    print(f"\n💡 COST OPTIMIZATION TIPS:")
    print(f"• Use shorter descriptions to reduce input tokens")
    print(f"• Optimize prompts to be more concise")
    print(f"• Consider using GPT-3.5-turbo for lower costs")
    print(f"• Batch similar content requests")
    print(f"• Cache frequently used prompts")
    
    return platform_costs, total_cost

if __name__ == "__main__":
    estimate_token_usage()
