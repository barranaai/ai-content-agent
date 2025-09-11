#!/usr/bin/env python3
"""
Comprehensive integration test for the new Barrana prompt library system
"""

import requests
import json
import time
import sys

def test_api_endpoint(url, method='GET', data=None, expected_status=200):
    """Test an API endpoint"""
    try:
        if method == 'GET':
            response = requests.get(url, timeout=10)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == expected_status:
            return True, response.json() if response.content else {}
        else:
            return False, f"Expected {expected_status}, got {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)

def main():
    """Run comprehensive integration tests"""
    base_url = "http://localhost:5050"
    
    print("🧪 Starting Comprehensive Integration Tests\n")
    
    # Test 1: Health Check
    print("1️⃣ Testing Health Check...")
    success, result = test_api_endpoint(f"{base_url}/api/health")
    if success:
        print("✅ Health check passed")
        print(f"   Status: {result.get('status')}")
        print(f"   JSON Library: {result['systems']['json_library']}")
        print(f"   Validator: {result['systems']['validator']}")
        print(f"   SEO Manager: {result['systems']['seo_manager']}")
    else:
        print(f"❌ Health check failed: {result}")
        return False
    
    # Test 2: System Info
    print("\n2️⃣ Testing System Info...")
    success, result = test_api_endpoint(f"{base_url}/api/system-info")
    if success:
        print("✅ System info retrieved")
        print(f"   Version: {result.get('version')}")
        print(f"   JSON Library Version: {result.get('json_library_version')}")
        print(f"   Available Platforms: {len(result.get('available_platforms', []))}")
        print(f"   Features: {list(result.get('features', {}).keys())}")
    else:
        print(f"❌ System info failed: {result}")
        return False
    
    # Test 3: Topics Endpoint
    print("\n3️⃣ Testing Topics Endpoint...")
    success, result = test_api_endpoint(f"{base_url}/api/topics")
    if success:
        print("✅ Topics retrieved")
        print(f"   Number of topics: {len(result)}")
        for topic in result[:3]:  # Show first 3
            print(f"   - {topic['topic']}: {topic['description'][:50]}...")
    else:
        print(f"❌ Topics failed: {result}")
        return False
    
    # Test 4: Platform Prompts
    print("\n4️⃣ Testing Platform Prompts...")
    success, result = test_api_endpoint(f"{base_url}/api/platform-prompts")
    if success:
        print("✅ Platform prompts retrieved")
        print(f"   Number of platforms: {len(result)}")
        for platform, prompt in list(result.items())[:2]:  # Show first 2
            print(f"   - {platform}: {prompt[:50]}...")
    else:
        print(f"❌ Platform prompts failed: {result}")
        return False
    
    # Test 5: Content Generation - Single Platform
    print("\n5️⃣ Testing Content Generation (Single Platform)...")
    test_data = {
        "topic": "AI Automation",
        "description": "How AI automation can transform small business operations and increase efficiency",
        "platforms": ["linkedin"],
        "prompts": {}
    }
    success, result = test_api_endpoint(f"{base_url}/api/generate-content", 'POST', test_data)
    if success:
        print("✅ Content generation successful")
        linkedin_content = result.get('linkedin', '')
        print(f"   Content length: {len(linkedin_content)} characters")
        print(f"   Contains CTA: {'CTA' in linkedin_content}")
        print(f"   Contains quality metrics: {'Quality Metrics' in linkedin_content}")
        print(f"   Preview: {linkedin_content[:100]}...")
    else:
        print(f"❌ Content generation failed: {result}")
        return False
    
    # Test 6: Content Generation - Multiple Platforms
    print("\n6️⃣ Testing Content Generation (Multiple Platforms)...")
    test_data = {
        "topic": "AI Automation",
        "description": "How AI automation can transform small business operations and increase efficiency",
        "platforms": ["linkedin", "medium"],
        "prompts": {}
    }
    success, result = test_api_endpoint(f"{base_url}/api/generate-content", 'POST', test_data)
    if success:
        print("✅ Multi-platform content generation successful")
        print(f"   Platforms generated: {list(result.keys())}")
        for platform, content in result.items():
            print(f"   - {platform}: {len(content)} characters")
    else:
        print(f"❌ Multi-platform content generation failed: {result}")
        return False
    
    # Test 7: Error Handling
    print("\n7️⃣ Testing Error Handling...")
    # Test with missing data
    test_data = {
        "topic": "AI Automation",
        "description": "",  # Empty description
        "platforms": ["linkedin"],
        "prompts": {}
    }
    success, result = test_api_endpoint(f"{base_url}/api/generate-content", 'POST', test_data, 400)
    if success:
        print("✅ Error handling working (empty description rejected)")
    else:
        print(f"❌ Error handling failed: {result}")
        return False
    
    # Test 8: Performance Test
    print("\n8️⃣ Testing Performance...")
    start_time = time.time()
    test_data = {
        "topic": "AI Automation",
        "description": "How AI automation can transform small business operations and increase efficiency",
        "platforms": ["linkedin"],
        "prompts": {}
    }
    success, result = test_api_endpoint(f"{base_url}/api/generate-content", 'POST', test_data)
    end_time = time.time()
    
    if success:
        response_time = end_time - start_time
        print(f"✅ Performance test passed")
        print(f"   Response time: {response_time:.2f} seconds")
        if response_time < 10:
            print("   ✅ Response time is acceptable")
        else:
            print("   ⚠️ Response time is slow")
    else:
        print(f"❌ Performance test failed: {result}")
        return False
    
    print("\n🎉 All Integration Tests Passed!")
    print("\n📊 Test Summary:")
    print("   ✅ Health Check")
    print("   ✅ System Info")
    print("   ✅ Topics Endpoint")
    print("   ✅ Platform Prompts")
    print("   ✅ Single Platform Content Generation")
    print("   ✅ Multi-Platform Content Generation")
    print("   ✅ Error Handling")
    print("   ✅ Performance")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
