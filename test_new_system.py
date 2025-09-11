#!/usr/bin/env python3
"""
Test script for the new Barrana prompt library system
"""

import sys
import logging
from prompt_library import BarranaPromptLibrary
from validation import ContentValidator
from seo_manager import SEOManager

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_prompt_library():
    """Test the prompt library functionality"""
    print("🧪 Testing Prompt Library...")
    
    try:
        # Initialize prompt library
        library = BarranaPromptLibrary()
        
        # Test basic functionality
        print(f"✅ Library loaded successfully (v{library.library.get('version', 'unknown')})")
        
        # Test platform access
        platforms = library.get_available_platforms()
        print(f"✅ Available platforms: {platforms}")
        
        # Test platform config
        linkedin_config = library.get_platform_config('linkedin')
        print(f"✅ LinkedIn config loaded: {linkedin_config['voice']}")
        
        # Test prompt building
        test_description = "How AI can transform small business operations"
        prompt = library.build_prompt(
            description=test_description,
            platform='linkedin',
            primary_keywords=['AI', 'automation'],
            secondary_keywords=['business', 'efficiency']
        )
        print(f"✅ Prompt built successfully (length: {len(prompt)} chars)")
        print(f"   Preview: {prompt[:100]}...")
        
        return library
        
    except Exception as e:
        print(f"❌ Prompt library test failed: {e}")
        return None

def test_validation(library):
    """Test the validation system"""
    print("\n🧪 Testing Validation System...")
    
    try:
        validator = ContentValidator(library)
        
        # Test input validation
        test_description = "AI automation for small businesses"
        validation_result = validator.validate_input(test_description, 'linkedin')
        print(f"✅ Input validation: {validation_result['valid']}")
        
        if not validation_result['valid']:
            print(f"   Errors: {validation_result['errors']}")
        
        # Test output validation
        test_content = "AI automation is revolutionizing small business operations. By implementing AI tools, businesses can reduce costs, increase efficiency, and improve customer service. Ready to transform your business with AI? Let's talk."
        output_validation = validator.validate_output(test_content, 'linkedin')
        print(f"✅ Output validation: {output_validation['valid']}")
        
        if output_validation['issues']:
            print(f"   Issues: {output_validation['issues']}")
        
        if output_validation['suggestions']:
            print(f"   Suggestions: {output_validation['suggestions']}")
        
        return validator
        
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
        return None

def test_seo_manager(library):
    """Test the SEO manager"""
    print("\n🧪 Testing SEO Manager...")
    
    try:
        seo_manager = SEOManager(library)
        
        # Test keyword retrieval
        keywords = seo_manager.get_keywords()
        print(f"✅ Keywords retrieved: {len(keywords['primary'])} primary, {len(keywords['secondary'])} secondary")
        
        # Test keyword rotation
        rotated = seo_manager.get_rotated_keywords('linkedin', count=3)
        print(f"✅ Rotated keywords: {rotated['primary']}")
        
        # Test refresh policy
        should_refresh = seo_manager.should_refresh_keywords()
        print(f"✅ Should refresh keywords: {should_refresh}")
        
        # Test keyword suggestions
        test_content = "AI automation tools are transforming business operations"
        suggestions = seo_manager.get_keyword_suggestions(test_content, 'linkedin')
        print(f"✅ Keyword suggestions: {suggestions}")
        
        return seo_manager
        
    except Exception as e:
        print(f"❌ SEO manager test failed: {e}")
        return None

def test_integration():
    """Test the complete integration"""
    print("\n🧪 Testing Complete Integration...")
    
    try:
        # Initialize all components
        library = BarranaPromptLibrary()
        validator = ContentValidator(library)
        seo_manager = SEOManager(library)
        
        # Simulate a complete workflow
        description = "AI automation for small business efficiency"
        platform = 'linkedin'
        
        # 1. Validate input
        input_validation = validator.validate_input(description, platform)
        if not input_validation['valid']:
            print(f"❌ Input validation failed: {input_validation['errors']}")
            return False
        
        # 2. Get optimized keywords
        keywords = seo_manager.get_platform_optimized_keywords(platform, "general")
        
        # 3. Build prompt
        prompt = library.build_prompt(
            description=description,
            platform=platform,
            primary_keywords=keywords['primary'],
            secondary_keywords=keywords['secondary']
        )
        
        # 4. Simulate AI generation (we'll skip actual OpenAI call for testing)
        simulated_content = f"AI automation is revolutionizing small business operations. {description} By implementing AI tools, businesses can reduce costs and increase efficiency. {library.get_global_cta()}"
        
        # 5. Validate output
        output_validation = validator.validate_output(simulated_content, platform)
        
        # 6. Generate final result
        result = {
            "platform": platform,
            "voice": library.get_platform_voice(platform),
            "keywords_used": keywords['primary'],
            "word_count_or_length": len(simulated_content.split()),
            "body": simulated_content,
            "visuals_suggestions": ["Cover image"],
            "hashtags": library.get_platform_hashtags(platform),
            "cta_included": library.get_global_cta() in simulated_content,
            "faq_section_if_applicable": None,
            "validation": output_validation
        }
        
        print("✅ Complete integration test successful!")
        print(f"   Platform: {result['platform']}")
        print(f"   Voice: {result['voice']}")
        print(f"   Word count: {result['word_count_or_length']}")
        print(f"   CTA included: {result['cta_included']}")
        print(f"   Validation passed: {result['validation']['valid']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Barrana Prompt Library System Tests\n")
    
    # Test individual components
    library = test_prompt_library()
    if not library:
        print("❌ Cannot continue without prompt library")
        return False
    
    validator = test_validation(library)
    if not validator:
        print("❌ Cannot continue without validator")
        return False
    
    seo_manager = test_seo_manager(library)
    if not seo_manager:
        print("❌ Cannot continue without SEO manager")
        return False
    
    # Test complete integration
    integration_success = test_integration()
    
    print(f"\n🎯 Test Results:")
    print(f"   Prompt Library: {'✅' if library else '❌'}")
    print(f"   Validation: {'✅' if validator else '❌'}")
    print(f"   SEO Manager: {'✅' if seo_manager else '❌'}")
    print(f"   Integration: {'✅' if integration_success else '❌'}")
    
    if all([library, validator, seo_manager, integration_success]):
        print("\n🎉 All tests passed! System is ready for integration.")
        return True
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
