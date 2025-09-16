#!/usr/bin/env python3
"""
Comprehensive Platform Testing Script
Tests all platforms and elements from Barrana-Merged-Prompt-Library-v3.1.json
"""

import json
import requests
import time
from typing import Dict, List, Any
from prompt_library import BarranaPromptLibrary

class PlatformTester:
    def __init__(self):
        self.library = BarranaPromptLibrary()
        self.results = {}
        self.test_description = "AI-powered system for automated school reporting and communication"
        self.base_url = "http://localhost:5050/api/generate-content"
        
    def get_all_platforms(self) -> List[str]:
        """Get all available platforms from the JSON library"""
        return list(self.library.library['platforms'].keys())
    
    def test_platform(self, platform: str) -> Dict[str, Any]:
        """Test a single platform and return comprehensive results"""
        print(f"Testing platform: {platform}")
        
        try:
            # Generate content for the platform
            payload = {
                "topic": "School Reporting",
                "description": self.test_description,
                "platforms": [platform]
            }
            
            response = requests.post(self.base_url, json=payload, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            content = data['content'].get(platform, '')
            metrics = data['metrics'].get(platform, {})
            
            # Analyze the content and prompt
            analysis = self.analyze_platform_content(platform, content, metrics)
            
            return {
                'platform': platform,
                'success': True,
                'content_length': len(content),
                'content_preview': content[:200] + '...' if len(content) > 200 else content,
                'metrics': metrics,
                'analysis': analysis
            }
            
        except Exception as e:
            return {
                'platform': platform,
                'success': False,
                'error': str(e),
                'analysis': {}
            }
    
    def analyze_platform_content(self, platform: str, content: str, metrics: Dict) -> Dict[str, Any]:
        """Analyze content against JSON requirements"""
        config = self.library.get_platform_config(platform)
        analysis = {
            'voice_compliance': self.check_voice_compliance(platform, content),
            'evidence_sources': self.check_evidence_sources(content),
            'content_framework': self.check_content_framework(content),
            'brand_guidelines': self.check_brand_guidelines(content),
            'cta_compliance': self.check_cta_compliance(platform, content),
            'keyword_usage': self.check_keyword_usage(content),
            'structure_compliance': self.check_structure_compliance(platform, content),
            'word_count_compliance': self.check_word_count_compliance(platform, content, metrics),
            'hashtag_compliance': self.check_hashtag_compliance(platform, content),
            'visual_requirements': self.check_visual_requirements(platform, content)
        }
        
        # Calculate overall compliance score
        compliance_checks = [v for v in analysis.values() if isinstance(v, bool)]
        analysis['overall_compliance'] = sum(compliance_checks) / len(compliance_checks) if compliance_checks else 0
        
        return analysis
    
    def check_voice_compliance(self, platform: str, content: str) -> bool:
        """Check if voice rules are followed"""
        voice_rules = self.library.library['voice_rules']
        expected_voice = None
        
        for voice_type, platforms in voice_rules.items():
            if platform in platforms:
                expected_voice = voice_type
                break
        
        if expected_voice == 'ikram_first_person':
            return 'I ' in content or 'I\'m ' in content or 'I\'ve ' in content
        elif expected_voice == 'barrana_we':
            return 'We ' in content or 'we ' in content or 'Barrana' in content
        elif expected_voice == 'flexible':
            return True  # Flexible voice can be either
        
        return True
    
    def check_evidence_sources(self, content: str) -> bool:
        """Check if evidence sources (WSJ, NFX, Reddit) are referenced"""
        evidence_sources = ['WSJ', 'NFX', 'Reddit']
        content_upper = content.upper()
        return any(source in content_upper for source in evidence_sources)
    
    def check_content_framework(self, content: str) -> bool:
        """Check if Pain Point → Insight → Solution → CTA framework is followed"""
        # Look for indicators of each framework element
        pain_indicators = ['problem', 'struggle', 'challenge', 'issue', 'pain']
        insight_indicators = ['evidence', 'study', 'research', 'data', 'shows']
        solution_indicators = ['solution', 'approach', 'method', 'system', 'tool']
        cta_indicators = ['contact', 'book', 'consultation', 'visit', 'learn more']
        
        content_lower = content.lower()
        
        has_pain = any(indicator in content_lower for indicator in pain_indicators)
        has_insight = any(indicator in content_lower for indicator in insight_indicators)
        has_solution = any(indicator in content_lower for indicator in solution_indicators)
        has_cta = any(indicator in content_lower for indicator in cta_indicators)
        
        return has_pain and has_insight and has_solution and has_cta
    
    def check_brand_guidelines(self, content: str) -> bool:
        """Check if brand guidelines are followed"""
        brand_elements = ['Barrana', 'barrana.ai', 'www.barrana.ai']
        content_upper = content.upper()
        return any(element.upper() in content_upper for element in brand_elements)
    
    def check_cta_compliance(self, platform: str, content: str) -> bool:
        """Check if CTA is included (except StackOverflow)"""
        if platform == 'stackoverflow':
            return True  # CTA not required for StackOverflow
        
        cta_text = self.library.library['globals']['cta']
        return cta_text.lower() in content.lower()
    
    def check_keyword_usage(self, content: str) -> bool:
        """Check if keywords are used naturally"""
        primary_keywords = self.library.library['seo']['primary_keywords']
        content_lower = content.lower()
        
        # Check if at least one primary keyword is used
        return any(keyword.lower() in content_lower for keyword in primary_keywords)
    
    def check_structure_compliance(self, platform: str, content: str) -> bool:
        """Check if platform-specific structure is followed"""
        config = self.library.get_platform_config(platform)
        structure = config.get('structure', [])
        
        if not structure:
            return True
        
        # For Twitter, check for numbered tweets
        if platform in ['twitter', 'twitter_quick']:
            return any(f'{i}/' in content for i in range(1, 13))
        
        # For other platforms, check for basic structure elements
        return len(content.split('\n')) > 1  # Has multiple paragraphs/sections
    
    def check_word_count_compliance(self, platform: str, content: str, metrics: Dict) -> bool:
        """Check if word count requirements are met"""
        word_count = metrics.get('word_count', 0)
        config = self.library.get_platform_config(platform)
        word_limits = config.get('word_count', {})
        
        min_words = word_limits.get('min', 0)
        max_words = word_limits.get('max', 1000)
        
        return min_words <= word_count <= max_words
    
    def check_hashtag_compliance(self, platform: str, content: str) -> bool:
        """Check if hashtag requirements are met"""
        config = self.library.get_platform_config(platform)
        hashtag_config = config.get('hashtags', {})
        
        if not hashtag_config:
            return True
        
        # Count hashtags in content
        hashtag_count = content.count('#')
        
        # Parse hashtag requirements with improved logic
        count_str = hashtag_config.get('count', '0')
        
        try:
            if 'max' in count_str:
                # Extract number before 'max'
                parts = count_str.split('max')[0].strip()
                if '-' in parts:
                    min_count, max_count = map(int, parts.split('-'))
                    return min_count <= hashtag_count <= max_count
                else:
                    max_count = int(parts)
                    return hashtag_count <= max_count
            elif '-' in count_str:
                # Handle formats like "5-7 tags" or "3-5 trending + brand"
                parts = count_str.split('-')
                if len(parts) == 2:
                    min_part = parts[0].strip()
                    max_part = parts[1].strip()
                    
                    # Extract numbers from each part
                    min_count = int(''.join(filter(str.isdigit, min_part)))
                    max_count = int(''.join(filter(str.isdigit, max_part)))
                    
                    return min_count <= hashtag_count <= max_count
            else:
                # Single number
                expected_count = int(''.join(filter(str.isdigit, count_str)))
                return hashtag_count == expected_count
        except (ValueError, IndexError):
            # If parsing fails, just check if hashtags are present
            return hashtag_count > 0
        
        return True
    
    def check_visual_requirements(self, platform: str, content: str) -> bool:
        """Check if visual requirements are mentioned"""
        config = self.library.get_platform_config(platform)
        visuals = config.get('visuals', [])
        
        if not visuals:
            return True
        
        # Check if visual placeholders or mentions are in content
        visual_indicators = ['visual', 'image', 'diagram', 'infographic', 'placeholder']
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in visual_indicators)
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive test on all platforms"""
        print("Starting comprehensive platform testing...")
        platforms = self.get_all_platforms()
        
        results = {}
        for i, platform in enumerate(platforms, 1):
            print(f"Progress: {i}/{len(platforms)} - Testing {platform}")
            results[platform] = self.test_platform(platform)
            time.sleep(1)  # Rate limiting
        
        return results
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive test report"""
        report = []
        report.append("# Comprehensive Platform Testing Report")
        report.append("=" * 50)
        report.append(f"Test Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Platforms Tested: {len(results)}")
        report.append("")
        
        # Summary statistics
        successful_tests = sum(1 for r in results.values() if r['success'])
        report.append("## Executive Summary")
        report.append(f"- **Successful Tests**: {successful_tests}/{len(results)} ({successful_tests/len(results)*100:.1f}%)")
        report.append(f"- **Failed Tests**: {len(results) - successful_tests}/{len(results)}")
        report.append("")
        
        # Detailed results by platform
        report.append("## Detailed Platform Results")
        report.append("")
        
        for platform, result in results.items():
            report.append(f"### {platform.upper()}")
            report.append(f"**Status**: {'✅ PASS' if result['success'] else '❌ FAIL'}")
            
            if result['success']:
                analysis = result['analysis']
                report.append(f"**Content Length**: {result['content_length']} characters")
                report.append(f"**Overall Compliance**: {analysis['overall_compliance']*100:.1f}%")
                report.append("")
                
                # Compliance details
                report.append("**Compliance Details**:")
                compliance_items = [
                    ("Voice Compliance", analysis['voice_compliance']),
                    ("Evidence Sources", analysis['evidence_sources']),
                    ("Content Framework", analysis['content_framework']),
                    ("Brand Guidelines", analysis['brand_guidelines']),
                    ("CTA Compliance", analysis['cta_compliance']),
                    ("Keyword Usage", analysis['keyword_usage']),
                    ("Structure Compliance", analysis['structure_compliance']),
                    ("Word Count Compliance", analysis['word_count_compliance']),
                    ("Hashtag Compliance", analysis['hashtag_compliance']),
                    ("Visual Requirements", analysis['visual_requirements'])
                ]
                
                for item, status in compliance_items:
                    status_icon = "✅" if status else "❌"
                    report.append(f"- {status_icon} {item}")
                
                report.append("")
                report.append("**Content Preview**:")
                report.append(f"```")
                report.append(result['content_preview'])
                report.append("```")
                report.append("")
                
                # Metrics
                metrics = result['metrics']
                report.append("**Quality Metrics**:")
                for metric, value in metrics.items():
                    if isinstance(value, bool):
                        report.append(f"- {metric}: {'✅ Pass' if value else '❌ Fail'}")
                    elif isinstance(value, (int, float)):
                        if metric in ['word_count', 'char_count', 'faq_word_count', 'avg_sentence_length']:
                            report.append(f"- {metric}: {value}")
                        else:
                            report.append(f"- {metric}: {int(value * 100)}%")
                
            else:
                report.append(f"**Error**: {result['error']}")
            
            report.append("")
            report.append("---")
            report.append("")
        
        # Overall analysis
        report.append("## Overall Analysis")
        report.append("")
        
        # Calculate average compliance across all platforms
        compliance_scores = [r['analysis']['overall_compliance'] for r in results.values() if r['success']]
        if compliance_scores:
            avg_compliance = sum(compliance_scores) / len(compliance_scores)
            report.append(f"**Average Compliance Score**: {avg_compliance*100:.1f}%")
        
        # Identify top and bottom performers
        successful_results = {k: v for k, v in results.items() if v['success']}
        if successful_results:
            sorted_by_compliance = sorted(successful_results.items(), 
                                        key=lambda x: x[1]['analysis']['overall_compliance'], 
                                        reverse=True)
            
            report.append("")
            report.append("**Top Performers** (by compliance score):")
            for platform, result in sorted_by_compliance[:3]:
                score = result['analysis']['overall_compliance'] * 100
                report.append(f"- {platform}: {score:.1f}%")
            
            report.append("")
            report.append("**Areas for Improvement** (by compliance score):")
            for platform, result in sorted_by_compliance[-3:]:
                score = result['analysis']['overall_compliance'] * 100
                report.append(f"- {platform}: {score:.1f}%")
        
        report.append("")
        report.append("## Recommendations")
        report.append("")
        report.append("1. **Voice Consistency**: Ensure all platforms follow their designated voice rules")
        report.append("2. **Evidence Integration**: Consistently include WSJ/NFX/Reddit references")
        report.append("3. **Content Framework**: Maintain Pain Point → Solution → CTA structure")
        report.append("4. **Brand Guidelines**: Include proper brand references and CTAs")
        report.append("5. **Quality Metrics**: Monitor and improve content quality scores")
        
        return "\n".join(report)

def main():
    """Main execution function"""
    tester = PlatformTester()
    
    print("Starting comprehensive platform testing...")
    results = tester.run_comprehensive_test()
    
    print("\nGenerating comprehensive report...")
    report = tester.generate_report(results)
    
    # Save report to file
    with open('comprehensive_platform_test_report.md', 'w') as f:
        f.write(report)
    
    print("Report saved to: comprehensive_platform_test_report.md")
    print("\n" + "="*50)
    print("TESTING COMPLETE")
    print("="*50)

if __name__ == "__main__":
    main()
