#!/usr/bin/env python3
"""
Token Calculator for AI Content Agent
Calculates and monitors token usage for cost optimization
"""

import tiktoken
import json
from typing import Dict, List, Tuple

class TokenCalculator:
    def __init__(self, model: str = "gpt-4"):
        """Initialize token calculator for specified model"""
        self.model = model
        self.encoding = tiktoken.encoding_for_model(model)
        
        # Pricing (as of 2024)
        self.input_price_per_1k = 0.03
        self.output_price_per_1k = 0.06
        
    def count_tokens(self, text: str) -> int:
        """Count exact tokens in text"""
        return len(self.encoding.encode(text))
    
    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for input and output tokens"""
        input_cost = (input_tokens / 1000) * self.input_price_per_1k
        output_cost = (output_tokens / 1000) * self.output_price_per_1k
        return input_cost + output_cost
    
    def analyze_prompt(self, prompt: str) -> Dict:
        """Analyze prompt and return token count and cost estimate"""
        tokens = self.count_tokens(prompt)
        estimated_output = min(tokens * 2, 800)  # Estimate 2x input tokens, max 800
        estimated_cost = self.estimate_cost(tokens, estimated_output)
        
        return {
            "input_tokens": tokens,
            "estimated_output_tokens": estimated_output,
            "estimated_cost": estimated_cost,
            "character_count": len(prompt),
            "word_count": len(prompt.split())
        }
    
    def analyze_content_generation(self, topic: str, description: str, platforms: List[str]) -> Dict:
        """Analyze full content generation request"""
        total_input_tokens = 0
        total_estimated_cost = 0
        platform_analysis = {}
        
        for platform in platforms:
            # Simulate prompt construction
            prompt = f"""
Generate {platform} content for topic: {topic}
Description: {description}
Platform: {platform}
Word count: 280-320 words
Include: CTA, hashtags, engagement elements
"""
            
            analysis = self.analyze_prompt(prompt)
            platform_analysis[platform] = analysis
            
            total_input_tokens += analysis["input_tokens"]
            total_estimated_cost += analysis["estimated_cost"]
        
        return {
            "total_platforms": len(platforms),
            "total_input_tokens": total_input_tokens,
            "total_estimated_cost": total_estimated_cost,
            "average_cost_per_platform": total_estimated_cost / len(platforms),
            "platform_analysis": platform_analysis
        }
    
    def optimize_prompt(self, prompt: str) -> str:
        """Optimize prompt to reduce token usage"""
        # Remove extra whitespace
        optimized = " ".join(prompt.split())
        
        # Replace verbose phrases with concise ones
        replacements = {
            "Generate content for the topic": "Topic",
            "Description:": "Desc:",
            "Word count:": "Words:",
            "Include:": "Include:",
            "engagement elements": "engagement"
        }
        
        for old, new in replacements.items():
            optimized = optimized.replace(old, new)
        
        return optimized
    
    def batch_analysis(self, requests: List[Dict]) -> Dict:
        """Analyze batch processing benefits"""
        regular_cost = sum(req["estimated_cost"] for req in requests)
        batch_cost = regular_cost * 0.5  # 50% discount
        
        return {
            "total_requests": len(requests),
            "regular_api_cost": regular_cost,
            "batch_api_cost": batch_cost,
            "savings": regular_cost - batch_cost,
            "savings_percentage": ((regular_cost - batch_cost) / regular_cost) * 100
        }

def main():
    """Example usage"""
    calculator = TokenCalculator()
    
    # Example topic and platforms
    topic = "AI Native"
    description = "Not all disruption comes from throw-away AI tools. It comes from businesses that are AI-native—and the rest risk becoming commoditized."
    platforms = ["linkedin", "twitter", "medium", "substack"]
    
    # Analyze content generation
    analysis = calculator.analyze_content_generation(topic, description, platforms)
    
    print("🔢 Token Analysis for AI Content Agent")
    print("=" * 50)
    print(f"Topic: {topic}")
    print(f"Platforms: {', '.join(platforms)}")
    print(f"Total Platforms: {analysis['total_platforms']}")
    print(f"Total Input Tokens: {analysis['total_input_tokens']}")
    print(f"Total Estimated Cost: ${analysis['total_estimated_cost']:.4f}")
    print(f"Average Cost per Platform: ${analysis['average_cost_per_platform']:.4f}")
    
    print("\n📊 Platform Breakdown:")
    for platform, data in analysis['platform_analysis'].items():
        print(f"  {platform}: {data['input_tokens']} tokens, ${data['estimated_cost']:.4f}")
    
    # Batch analysis
    requests = [analysis['platform_analysis'][platform] for platform in platforms]
    batch_analysis = calculator.batch_analysis(requests)
    
    print(f"\n💰 Batch Processing Benefits:")
    print(f"Regular API Cost: ${batch_analysis['regular_api_cost']:.4f}")
    print(f"Batch API Cost: ${batch_analysis['batch_api_cost']:.4f}")
    print(f"Savings: ${batch_analysis['savings']:.4f} ({batch_analysis['savings_percentage']:.1f}%)")

if __name__ == "__main__":
    main()
