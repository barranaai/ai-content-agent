import json
import logging
from typing import Dict, List, Optional, Any
import os

class BarranaPromptLibrary:
    """
    Manages the Barrana prompt library JSON file and provides methods
    for building dynamic prompts and accessing platform configurations.
    """
    
    def __init__(self, json_path: str = "barrana-merged-prompt-library-v3.json"):
        self.json_path = json_path
        self.library = None
        self.load_library()
    
    def load_library(self) -> None:
        """Load JSON library with comprehensive error handling"""
        try:
            if not os.path.exists(self.json_path):
                raise FileNotFoundError(f"Prompt library file not found: {self.json_path}")
            
            with open(self.json_path, 'r', encoding='utf-8') as f:
                self.library = json.load(f)
            
            logging.info(f"Prompt library v{self.library.get('version', 'unknown')} loaded successfully")
            
            # Validate library structure
            self._validate_library_structure()
            
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in prompt library: {e}")
            raise
        except Exception as e:
            logging.error(f"Failed to load prompt library: {e}")
            raise
    
    def _validate_library_structure(self) -> None:
        """Validate that the library has the required structure"""
        required_keys = ['version', 'globals', 'seo', 'platforms', 'guardrails', 'runtime']
        for key in required_keys:
            if key not in self.library:
                raise ValueError(f"Missing required key in prompt library: {key}")
        
        # Validate platforms
        if not self.library['platforms']:
            raise ValueError("No platforms defined in prompt library")
        
        # Validate each platform has required fields
        for platform, config in self.library['platforms'].items():
            required_platform_keys = ['voice', 'word_count', 'prompt_template', 'hashtags']
            for key in required_platform_keys:
                if key not in config:
                    raise ValueError(f"Platform {platform} missing required field: {key}")
    
    def get_platform_config(self, platform: str) -> Dict[str, Any]:
        """Get platform configuration"""
        if not self.library:
            raise RuntimeError("Prompt library not loaded")
        
        platform_config = self.library['platforms'].get(platform)
        if not platform_config:
            available_platforms = list(self.library['platforms'].keys())
            raise ValueError(f"Platform '{platform}' not found. Available platforms: {available_platforms}")
        
        return platform_config
    
    def get_available_platforms(self) -> List[str]:
        """Get list of available platforms"""
        if not self.library:
            raise RuntimeError("Prompt library not loaded")
        
        return list(self.library['platforms'].keys())
    
    def build_prompt(self, description: str, platform: str, 
                    primary_keywords: List[str] = None, 
                    secondary_keywords: List[str] = None) -> str:
        """
        Build dynamic prompt with variable injection
        
        Args:
            description: The main content description
            platform: Target platform (linkedin, medium, etc.)
            primary_keywords: List of primary keywords
            secondary_keywords: List of secondary keywords
        
        Returns:
            Formatted prompt string ready for AI generation
        """
        if not self.library:
            raise RuntimeError("Prompt library not loaded")
        
        # Get platform configuration
        config = self.get_platform_config(platform)
        
        # Get keywords from SEO config if not provided
        if primary_keywords is None:
            primary_keywords = self.library['seo']['primary_keywords']
        if secondary_keywords is None:
            secondary_keywords = self.library['seo']['secondary_keywords']
        
        # Build the prompt with variable injection
        try:
            prompt = config['prompt_template'].format(
                description=description,
                primary_keywords=', '.join(primary_keywords),
                secondary_keywords=', '.join(secondary_keywords),
                cta=self.library['globals']['cta'],
                word_count_min=config['word_count']['min'],
                word_count_max=config['word_count']['max']
            )
            
            logging.info(f"Built prompt for platform: {platform}")
            return prompt
            
        except KeyError as e:
            raise ValueError(f"Missing required variable in prompt template: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to build prompt: {e}")
    
    def get_global_cta(self) -> str:
        """Get the global CTA text"""
        if not self.library:
            raise RuntimeError("Prompt library not loaded")
        
        return self.library['globals']['cta']
    
    def get_seo_keywords(self, category: str = None) -> Dict[str, List[str]]:
        """Get SEO keywords"""
        if not self.library:
            raise RuntimeError("Prompt library not loaded")
        
        seo_config = self.library['seo']
        
        if category and category in seo_config:
            return {
                'primary': seo_config[category].get('primary_keywords', []),
                'secondary': seo_config[category].get('secondary_keywords', [])
            }
        
        return {
            'primary': seo_config.get('primary_keywords', []),
            'secondary': seo_config.get('secondary_keywords', [])
        }
    
    def get_validation_rules(self) -> Dict[str, Any]:
        """Get validation rules from guardrails"""
        if not self.library:
            raise RuntimeError("Prompt library not loaded")
        
        return self.library['guardrails']['validators']
    
    def get_output_schema(self) -> Dict[str, str]:
        """Get the expected output schema"""
        if not self.library:
            raise RuntimeError("Prompt library not loaded")
        
        return self.library['runtime']['output_schema']
    
    def get_platform_hashtags(self, platform: str) -> List[str]:
        """Get hashtags for a specific platform"""
        config = self.get_platform_config(platform)
        return config.get('hashtags', [])
    
    def get_platform_voice(self, platform: str) -> str:
        """Get voice description for a specific platform"""
        config = self.get_platform_config(platform)
        return config.get('voice', '')
    
    def get_word_count_limits(self, platform: str) -> Dict[str, int]:
        """Get word count limits for a specific platform"""
        config = self.get_platform_config(platform)
        return config.get('word_count', {'min': 100, 'max': 500})
    
    def reload_library(self) -> None:
        """Reload the library from file (useful for updates)"""
        logging.info("Reloading prompt library...")
        self.load_library()
    
    def is_loaded(self) -> bool:
        """Check if library is loaded"""
        return self.library is not None
