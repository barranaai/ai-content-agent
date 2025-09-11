import re
import logging
from typing import Dict, List, Any, Tuple
from prompt_library import BarranaPromptLibrary

class ContentValidator:
    """
    Validates input and output content against the prompt library rules
    """
    
    def __init__(self, prompt_library: BarranaPromptLibrary):
        self.library = prompt_library
        self.validation_rules = prompt_library.get_validation_rules()
    
    def validate_input(self, description: str, platform: str) -> Dict[str, Any]:
        """
        Validate input before AI generation
        
        Args:
            description: The content description
            platform: Target platform
        
        Returns:
            Validation result with success status and any errors
        """
        errors = []
        warnings = []
        
        # Check if description is provided and not empty
        if not description or not description.strip():
            errors.append("Description is required and cannot be empty")
        elif len(description.strip()) < 10:
            errors.append("Description too short (minimum 10 characters)")
        elif len(description.strip()) > 5000:
            warnings.append("Description is very long (over 5000 characters)")
        
        # Check if platform is supported
        try:
            available_platforms = self.library.get_available_platforms()
            if platform not in available_platforms:
                errors.append(f"Unsupported platform: {platform}. Available: {available_platforms}")
        except Exception as e:
            errors.append(f"Error checking platform support: {str(e)}")
        
        # Check for potential issues in description
        if description:
            # Check for excessive repetition
            words = description.lower().split()
            if len(words) > 10:
                word_counts = {}
                for word in words:
                    word_counts[word] = word_counts.get(word, 0) + 1
                
                max_repetition = max(word_counts.values())
                if max_repetition > len(words) * 0.3:  # More than 30% repetition
                    warnings.append("Description has high word repetition")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "platform": platform,
            "description_length": len(description) if description else 0
        }
    
    def validate_output(self, content: str, platform: str) -> Dict[str, Any]:
        """
        Validate AI-generated content against platform rules
        
        Args:
            content: Generated content
            platform: Target platform
        
        Returns:
            Validation result with issues and suggestions
        """
        if not content or not content.strip():
            return {
                "valid": False,
                "issues": ["Generated content is empty"],
                "suggestions": ["Check AI generation process"],
                "metrics": {}
            }
        
        issues = []
        suggestions = []
        metrics = {}
        
        try:
            # Get platform configuration
            config = self.library.get_platform_config(platform)
            word_count_limits = self.library.get_word_count_limits(platform)
            cta_text = self.library.get_global_cta()
            
            # Calculate metrics
            word_count = len(content.split())
            char_count = len(content)
            metrics = {
                "word_count": word_count,
                "char_count": char_count,
                "platform": platform
            }
            
            # Check word count
            min_words = word_count_limits.get('min', 100)
            max_words = word_count_limits.get('max', 500)
            
            if word_count < min_words:
                issues.append(f"Content too short: {word_count}/{min_words} words")
                suggestions.append(f"Increase content length to at least {min_words} words")
            elif word_count > max_words:
                issues.append(f"Content too long: {word_count}/{max_words} words")
                suggestions.append(f"Reduce content length to maximum {max_words} words")
            
            # Check CTA presence
            if self.validation_rules.get('cta_required', False):
                if cta_text and cta_text not in content:
                    issues.append("Required CTA not found in content")
                    suggestions.append(f"Add CTA: {cta_text}")
                else:
                    metrics["cta_included"] = True
            
            # Check keyword density
            keyword_density_min = self.validation_rules.get('keyword_density_min', 0.02)
            keyword_density_max = self.validation_rules.get('keyword_density_max', 0.05)
            
            if keyword_density_min > 0 or keyword_density_max > 0:
                primary_keywords = self.library.get_seo_keywords()['primary']
                keyword_density = self._calculate_keyword_density(content, primary_keywords)
                metrics["keyword_density"] = keyword_density
                
                if keyword_density < keyword_density_min:
                    issues.append(f"Keyword density too low: {keyword_density:.3f}/{keyword_density_min}")
                    suggestions.append("Increase use of primary keywords")
                elif keyword_density > keyword_density_max:
                    issues.append(f"Keyword density too high: {keyword_density:.3f}/{keyword_density_max}")
                    suggestions.append("Reduce keyword usage to avoid over-optimization")
            
            # Check for FAQ section if required
            if self.validation_rules.get('faq_min_words', 0) > 0:
                faq_section = self._extract_faq_section(content)
                if faq_section:
                    faq_word_count = len(faq_section.split())
                    metrics["faq_word_count"] = faq_word_count
                    if faq_word_count < self.validation_rules['faq_min_words']:
                        issues.append(f"FAQ section too short: {faq_word_count}/{self.validation_rules['faq_min_words']} words")
                else:
                    issues.append("FAQ section not found")
                    suggestions.append("Add a comprehensive FAQ section")
            
            # Check for hashtags
            hashtags = self.library.get_platform_hashtags(platform)
            if hashtags:
                found_hashtags = self._extract_hashtags(content)
                metrics["hashtags_found"] = found_hashtags
                if not found_hashtags:
                    suggestions.append(f"Consider adding hashtags: {', '.join(hashtags)}")
            
            # Check for basic content quality
            if word_count > 50:  # Only check for longer content
                # Check for excessive repetition
                sentences = content.split('.')
                if len(sentences) > 1:
                    sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
                    avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths)
                    metrics["avg_sentence_length"] = avg_sentence_length
                    
                    if avg_sentence_length > 25:
                        suggestions.append("Consider shorter sentences for better readability")
                    elif avg_sentence_length < 8:
                        suggestions.append("Consider longer, more detailed sentences")
            
        except Exception as e:
            logging.error(f"Error during content validation: {e}")
            issues.append(f"Validation error: {str(e)}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions,
            "metrics": metrics
        }
    
    def _calculate_keyword_density(self, content: str, keywords: List[str]) -> float:
        """Calculate keyword density in content"""
        if not keywords or not content:
            return 0.0
        
        content_lower = content.lower()
        total_words = len(content.split())
        keyword_count = 0
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            keyword_count += content_lower.count(keyword_lower)
        
        return keyword_count / total_words if total_words > 0 else 0.0
    
    def _extract_faq_section(self, content: str) -> str:
        """Extract FAQ section from content"""
        # Look for common FAQ patterns
        faq_patterns = [
            r'(?:FAQ|Frequently Asked Questions|Questions and Answers).*?(?=\n\n|\Z)',
            r'(?:Q:|Question:).*?(?=\n\n|\Z)',
        ]
        
        for pattern in faq_patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(0)
        
        return ""
    
    def _extract_hashtags(self, content: str) -> List[str]:
        """Extract hashtags from content"""
        hashtag_pattern = r'#\w+'
        return re.findall(hashtag_pattern, content)
    
    def validate_platform_compatibility(self, platform: str, content_type: str = "general") -> Dict[str, Any]:
        """
        Validate if a platform is suitable for the content type
        
        Args:
            platform: Target platform
            content_type: Type of content (general, technical, promotional, etc.)
        
        Returns:
            Compatibility assessment
        """
        try:
            config = self.library.get_platform_config(platform)
            word_limits = config.get('word_count', {})
            
            compatibility = {
                "platform": platform,
                "content_type": content_type,
                "suitable": True,
                "recommendations": []
            }
            
            # Platform-specific recommendations
            if platform == "linkedin":
                if content_type == "technical":
                    compatibility["recommendations"].append("Consider simplifying technical terms for broader audience")
                elif content_type == "promotional":
                    compatibility["recommendations"].append("Focus on thought leadership rather than direct promotion")
            
            elif platform == "medium":
                if content_type == "short":
                    compatibility["recommendations"].append("Medium prefers longer, in-depth content")
                elif content_type == "promotional":
                    compatibility["recommendations"].append("Use storytelling approach for promotional content")
            
            elif platform == "pinterest":
                if content_type == "text_heavy":
                    compatibility["recommendations"].append("Pinterest works best with visual-focused content")
            
            return compatibility
            
        except Exception as e:
            return {
                "platform": platform,
                "content_type": content_type,
                "suitable": False,
                "error": str(e),
                "recommendations": ["Check platform configuration"]
            }
