#!/usr/bin/env python3

import re

def validate_twitter_thread(content):
    """Validate Twitter thread format and character limits"""
    
    print("🔍 Validating Twitter Thread:")
    print("=" * 50)
    
    # Extract tweets (numbered format)
    tweets = re.findall(r'\d+/\d+\s+(.+?)(?=\n\d+/\d+|\n---|\Z)', content, re.DOTALL)
    
    if not tweets:
        print("❌ No numbered tweets found!")
        return False
    
    print(f"📊 Found {len(tweets)} tweets")
    print()
    
    all_valid = True
    
    for i, tweet in enumerate(tweets, 1):
        # Clean up the tweet text
        tweet = tweet.strip()
        
        # Count characters
        char_count = len(tweet)
        
        # Check if under 280 characters
        is_valid = char_count <= 280
        
        if not is_valid:
            all_valid = False
        
        status = "✅" if is_valid else "❌"
        
        print(f"{status} Tweet {i}: {char_count}/280 characters")
        if char_count > 280:
            print(f"   ❌ EXCEEDS LIMIT by {char_count - 280} characters")
        print(f"   📝 Content: {tweet[:100]}{'...' if len(tweet) > 100 else ''}")
        print()
    
    print("=" * 50)
    if all_valid:
        print("✅ All tweets are within character limits!")
    else:
        print("❌ Some tweets exceed character limits!")
    
    return all_valid

# Test with the generated content
test_content = """1/12 Schools are struggling with outdated reporting systems. Imagine a world where reporting is streamlined, efficient, and truly valuable. That world is here! #AIForBusiness #AutomationForSMBs #Barrana
2/12 The problem many schools face is a convoluted, time-consuming reporting process. It's difficult to track student progress, monitor attendance, and manage grading effectively. 
3/12 Additionally, administrators are swamped with paperwork, leaving them less time to focus on the important stuff - fostering a conducive learning environment.
4/12 Here's where AI automation for small business comes in. Yes, schools too can benefit from this technology! It can simplify these processes and reduce costs significantly. 
5/12 AI automation can streamline administrative tasks, reduce errors, and provide real-time insights. It also offers the ability to track and analyze data in a more effective manner. 
6/12 Evidence shows that schools incorporating AI automation have seen increased efficiency, reduced costs, and improved decision-making. This is the future of school management.
7/12 The solution is simple - workflow automation for small business. It's time for schools to adopt this technology and transform their operations. #Barrana
8/12 Implementing AI can seem daunting, but it doesn't have to be. Start small, identify key areas that need improvement, and gradually expand your AI capabilities. 
9/12 Our products are easy to adapt and integrate into your existing systems. We provide comprehensive training and ongoing support to ensure a smooth transition.
10/12 A case in point is the City High School that adopted AI automation. They saw a 20% reduction in administrative costs and improved student tracking, all within a year. 
11/12 Another example is the Greenwood Primary School. With AI automation, they managed to reduce grading time by 30%, allowing teachers more time to focus on instruction.
12/12 Ready to transform your school's reporting system? AI can increase small business revenue and efficiency. Contact us via www.barrana.ai or book a consultation. #AIForBusiness"""

validate_twitter_thread(test_content)
