import logging
import random
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from prompt_library import BarranaPromptLibrary

class SEOManager:
    """
    Manages SEO keywords, rotation, and optimization based on the prompt library
    """
    
    def __init__(self, prompt_library: BarranaPromptLibrary):
        self.library = prompt_library
        self.seo_config = prompt_library.library.get('seo', {})
        self.refresh_policy = self.seo_config.get('refresh_policy', {})
    
    def get_keywords(self, category: str = None, count: int = None) -> Dict[str, List[str]]:
        """
        Get primary and secondary keywords
        
        Args:
            category: Specific category of keywords (optional)
            count: Number of keywords to return (optional)
        
        Returns:
            Dictionary with primary and secondary keywords
        """
        try:
            primary_keywords = self.seo_config.get('primary_keywords', [])
            secondary_keywords = self.seo_config.get('secondary_keywords', [])
            
            # Filter by category if specified
            if category:
                # This would be extended for category-specific keywords
                pass
            
            # Limit count if specified
            if count:
                primary_keywords = primary_keywords[:count]
                secondary_keywords = secondary_keywords[:count]
            
            return {
                'primary': primary_keywords,
                'secondary': secondary_keywords
            }
            
        except Exception as e:
            logging.error(f"Error getting keywords: {e}")
            return {'primary': [], 'secondary': []}
    
    def get_rotated_keywords(self, platform: str, count: int = 3) -> Dict[str, List[str]]:
        """
        Get rotated keywords for a specific platform
        
        Args:
            platform: Target platform
            count: Number of keywords to return
        
        Returns:
            Rotated keywords for the platform
        """
        try:
            all_keywords = self.get_keywords()
            primary = all_keywords['primary']
            secondary = all_keywords['secondary']
            
            # Get platform-specific keywords if available
            platform_config = self.library.get_platform_config(platform)
            platform_keywords = platform_config.get('keywords', [])
            
            # Combine and rotate
            combined_primary = list(set(primary + platform_keywords))
            combined_secondary = list(set(secondary + platform_keywords))
            
            # Rotate based on current time or other factors
            rotation_seed = datetime.now().day  # Changes daily
            random.seed(rotation_seed)
            
            rotated_primary = random.sample(combined_primary, min(count, len(combined_primary)))
            rotated_secondary = random.sample(combined_secondary, min(count, len(combined_secondary)))
            
            return {
                'primary': rotated_primary,
                'secondary': rotated_secondary
            }
            
        except Exception as e:
            logging.error(f"Error rotating keywords: {e}")
            return self.get_keywords(count=count)
    
    def should_refresh_keywords(self) -> bool:
        """
        Check if keywords should be refreshed based on refresh policy
        
        Returns:
            True if keywords should be refreshed
        """
        try:
            frequency = self.refresh_policy.get('frequency', 'monthly')
            last_refresh_str = self.refresh_policy.get('last_refresh', '2024-01-01')
            
            # Parse last refresh date
            last_refresh = datetime.strptime(last_refresh_str, '%Y-%m-%d')
            now = datetime.now()
            
            if frequency == 'daily':
                return (now - last_refresh).days >= 1
            elif frequency == 'weekly':
                return (now - last_refresh).days >= 7
            elif frequency == 'monthly':
                return (now - last_refresh).days >= 30
            elif frequency == 'quarterly':
                return (now - last_refresh).days >= 90
            
            return False
            
        except Exception as e:
            logging.error(f"Error checking refresh policy: {e}")
            return False
    
    def update_keywords(self, new_primary: List[str], new_secondary: List[str]) -> bool:
        """
        Update keywords in the library (this would typically update the JSON file)
        
        Args:
            new_primary: New primary keywords
            new_secondary: New secondary keywords
        
        Returns:
            True if update was successful
        """
        try:
            # Update the in-memory library
            self.library.library['seo']['primary_keywords'] = new_primary
            self.library.library['seo']['secondary_keywords'] = new_secondary
            self.library.library['seo']['refresh_policy']['last_refresh'] = datetime.now().strftime('%Y-%m-%d')
            
            logging.info("Keywords updated successfully")
            return True
            
        except Exception as e:
            logging.error(f"Error updating keywords: {e}")
            return False
    
    def get_keyword_suggestions(self, content: str, platform: str) -> List[str]:
        """
        Suggest additional keywords based on content and platform
        
        Args:
            content: The content to analyze
            platform: Target platform
        
        Returns:
            List of suggested keywords
        """
        try:
            suggestions = []
            
            # Get platform-specific keywords
            platform_config = self.library.get_platform_config(platform)
            platform_keywords = platform_config.get('keywords', [])
            
            # Get current SEO keywords
            current_keywords = self.get_keywords()
            all_keywords = current_keywords['primary'] + current_keywords['secondary']
            
            # Simple keyword extraction from content
            content_words = content.lower().split()
            word_frequency = {}
            
            for word in content_words:
                # Clean word (remove punctuation)
                clean_word = ''.join(c for c in word if c.isalnum())
                if len(clean_word) > 3:  # Only consider words longer than 3 characters
                    word_frequency[clean_word] = word_frequency.get(clean_word, 0) + 1
            
            # Find frequent words not already in keywords
            for word, freq in word_frequency.items():
                if freq > 1 and word not in all_keywords and word not in platform_keywords:
                    suggestions.append(word)
            
            # Limit suggestions
            return suggestions[:5]
            
        except Exception as e:
            logging.error(f"Error generating keyword suggestions: {e}")
            return []
    
    def get_platform_optimized_keywords(self, platform: str, content_type: str = "general") -> Dict[str, List[str]]:
        """
        Get keywords optimized for a specific platform and content type
        
        Args:
            platform: Target platform
            content_type: Type of content
        
        Returns:
            Platform-optimized keywords
        """
        try:
            # Get base keywords
            base_keywords = self.get_rotated_keywords(platform, count=5)
            
            # Get platform-specific keywords
            platform_config = self.library.get_platform_config(platform)
            platform_keywords = platform_config.get('keywords', [])
            
            # Combine and optimize based on content type
            optimized_primary = list(set(base_keywords['primary'] + platform_keywords))
            optimized_secondary = list(set(base_keywords['secondary'] + platform_keywords))
            
            # Content type specific optimizations
            if content_type == "technical":
                # Add technical keywords
                technical_keywords = ["implementation", "integration", "optimization", "automation"]
                optimized_primary.extend(technical_keywords)
            elif content_type == "promotional":
                # Add promotional keywords
                promotional_keywords = ["solution", "benefits", "results", "success"]
                optimized_primary.extend(promotional_keywords)
            
            return {
                'primary': optimized_primary[:5],  # Limit to 5 primary keywords
                'secondary': optimized_secondary[:5]  # Limit to 5 secondary keywords
            }
            
        except Exception as e:
            logging.error(f"Error getting platform-optimized keywords: {e}")
            return self.get_keywords(count=5)
    
    def analyze_keyword_performance(self, content: str, target_keywords: List[str]) -> Dict[str, Any]:
        """
        Analyze how well keywords are used in content
        
        Args:
            content: The content to analyze
            target_keywords: Keywords that should be present
        
        Returns:
            Analysis results
        """
        try:
            content_lower = content.lower()
            total_words = len(content.split())
            
            analysis = {
                "total_words": total_words,
                "keyword_usage": {},
                "density": {},
                "coverage": 0,
                "recommendations": []
            }
            
            # Analyze each keyword
            for keyword in target_keywords:
                keyword_lower = keyword.lower()
                count = content_lower.count(keyword_lower)
                density = count / total_words if total_words > 0 else 0
                
                analysis["keyword_usage"][keyword] = count
                analysis["density"][keyword] = density
            
            # Calculate coverage (percentage of keywords used)
            used_keywords = sum(1 for count in analysis["keyword_usage"].values() if count > 0)
            analysis["coverage"] = (used_keywords / len(target_keywords)) * 100 if target_keywords else 0
            
            # Generate recommendations
            if analysis["coverage"] < 50:
                analysis["recommendations"].append("Increase keyword usage - less than 50% of target keywords are used")
            
            for keyword, density in analysis["density"].items():
                if density > 0.05:  # More than 5% density
                    analysis["recommendations"].append(f"Reduce usage of '{keyword}' - density too high ({density:.3f})")
                elif density == 0:
                    analysis["recommendations"].append(f"Consider using '{keyword}' - not found in content")
            
            return analysis
            
        except Exception as e:
            logging.error(f"Error analyzing keyword performance: {e}")
            return {
                "error": str(e),
                "total_words": 0,
                "keyword_usage": {},
                "density": {},
                "coverage": 0,
                "recommendations": ["Error in analysis"]
            }
