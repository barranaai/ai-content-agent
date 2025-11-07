import json
import logging
import re
from typing import Dict, List, Optional, Any
import os
from datetime import datetime

class BarranaPromptLibrary:
    """
    Manages the Barrana prompt library JSON file and provides methods
    for building dynamic prompts and accessing platform configurations.
    """
    
    def __init__(self, json_path: str = "Barrana-Merged-Prompt-Library-v3.1.json", comments_engine_path: str = "comments-engine.json"):
        self.json_path = json_path
        self.comments_engine_path = comments_engine_path
        self.library = None
        self.comments_engine = None
        self.load_library()
        self.load_comments_engine()
    
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
    
    def load_comments_engine(self) -> None:
        """Load comments engine JSON with comprehensive error handling"""
        try:
            if not os.path.exists(self.comments_engine_path):
                logging.warning(f"Comments engine file not found: {self.comments_engine_path}")
                self.comments_engine = None
                return
            
            with open(self.comments_engine_path, 'r', encoding='utf-8') as f:
                self.comments_engine = json.load(f)
            
            logging.info(f"Comments engine loaded successfully from {self.comments_engine_path}")
            
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in comments engine: {e}")
            self.comments_engine = None
        except Exception as e:
            logging.error(f"Failed to load comments engine: {e}")
            self.comments_engine = None
    
    def _validate_library_structure(self) -> None:
        """Validate that the library has the required structure"""
        # Check for either v3.0 structure (meta.version) or v3.1 structure (version)
        if "meta" in self.library and "version" in self.library["meta"]:
            # v3.1 structure
            required_keys = ['meta', 'seo', 'platforms']
        else:
            # v3.0 structure
            required_keys = ['version', 'globals', 'seo', 'platforms', 'guardrails', 'runtime']
        
        for key in required_keys:
            if key not in self.library:
                raise ValueError(f"Missing required key in prompt library: {key}")
        
        # Validate platforms
        if not self.library['platforms']:
            raise ValueError("No platforms defined in prompt library")
        
        # Validate each platform has required fields
        for platform, config in self.library['platforms'].items():
            # Different required fields for different JSON versions
            if 'meta' in self.library:
                # v3.1 structure - more flexible
                required_platform_keys = ['voice', 'word_count']
            else:
                # v3.0 structure - strict
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
                    secondary_keywords: List[str] = None,
                    rag_context: str = None) -> str:
        """
        Build dynamic prompt with variable injection and optional RAG context
        
        Args:
            description: The main content description
            platform: Target platform (linkedin, medium, etc.)
            primary_keywords: List of primary keywords
            secondary_keywords: List of secondary keywords
            rag_context: Optional RAG context to enhance the prompt
        
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
            # Handle different JSON structures
            if 'meta' in self.library:
                # v3.1 structure
                cta = self.library['globals']['cta']
            else:
                # v3.0 structure
                cta = self.library['globals']['cta']
            
            prompt = config['prompt_template'].format(
                description=description,
                primary_keywords=', '.join(primary_keywords),
                secondary_keywords=', '.join(secondary_keywords),
                cta=cta,
                word_count_min=config['word_count']['min'],
                word_count_max=config['word_count']['max']
            )
            
            # Add explicit keyword inclusion requirements
            prompt += f"""

MANDATORY KEYWORD INCLUSION:
- You MUST include these EXACT keyword phrases naturally in your content:
- Primary keywords: {', '.join(primary_keywords)}
- Secondary keywords: {', '.join(secondary_keywords)}
- Use each keyword phrase at least once in the content
- Integrate keywords naturally, not as a list
- Keywords must appear as complete phrases, not just individual words
- CRITICAL: Include ALL {len(primary_keywords)} primary keywords for SEO compliance
- Distribute keywords throughout the content (title, intro, body, conclusion)
- Ensure keyword density is between 2-5% for optimal SEO
- SPECIAL NOTE: Include \"AI chatbots for SMB\" in your content as it's a key automation solution"""
            
            # Add comprehensive platform-specific enhancements
            style = config.get('style', '')
            structure = config.get('structure', [])
            visuals = config.get('visuals', [])
            seo_requirements = config.get('seo_requirements', {})
            special_rules = config.get('special_rules', '')
            rules = config.get('rules', {})
            
            # Add voice and brand guidelines
            voice = config.get('voice', 'Flexible')
            prompt += f"""

VOICE & BRAND GUIDELINES:
- Voice: {voice}
- Company: {self.library['globals']['brand']['company_name']}
- Website: {self.library['globals']['brand']['website']}
- Tone: {self.library['globals']['tone']}
- Regions: {', '.join(self.library['globals']['brand']['regions'])}"""
            
            # Add content framework
            content_framework = self.library['globals']['content_framework']
            prompt += f"""

CONTENT FRAMEWORK:
- Follow this exact structure: {' → '.join(content_framework)}
- Lead with SMB pain point
- Use evidence (WSJ/NFX/Reddit insights)
- Present solution approach
- End with clear CTA"""
            
            # Add evidence sources requirement
            evidence_sources = self.library['globals']['evidence_sources']
            prompt += f"""

EVIDENCE REQUIREMENTS:
- Reference these sources when relevant: {', '.join(evidence_sources)}
- Use evidence naturally in content
- Support claims with credible sources"""
            
            # Add style requirement
            if style:
                prompt += f"""

STYLE REQUIREMENT:
- Platform style: {style}
- Ensure content matches this specific style throughout"""
            
            # Add structure requirements
            if structure:
                if isinstance(structure, list):
                    structure_text = " → ".join(structure)
                else:
                    structure_text = structure
                prompt += f"""

STRUCTURE REQUIREMENT:
- Follow this exact structure: {structure_text}
- Ensure all structure elements are included"""
            
            # Add visual requirements
            if visuals:
                visuals_text = ", ".join(visuals)
                prompt += f"""

VISUAL REQUIREMENTS:
- Include these visual elements: {visuals_text}
- Specify visual concepts and placeholders"""
            
            # Add SEO requirements
            if seo_requirements:
                seo_items = []
                for key, value in seo_requirements.items():
                    seo_items.append(f"{key}: {value}")
                seo_text = ", ".join(seo_items)
                prompt += f"""

SEO REQUIREMENTS:
- {seo_text}
- Ensure SEO optimization throughout content"""
            
            # Add special rules
            if special_rules:
                prompt += f"""

SPECIAL RULES:
- {special_rules}
- Follow these platform-specific constraints"""
            
            # Get word count limits early
            word_min = config.get('word_count', {}).get('min', 0)
            word_max = config.get('word_count', {}).get('max', 1000)
            
            # Get hashtag count and CTA type for constraints
            hashtag_count = config.get('hashtags', {}).get('count', '3-5')
            cta_type = "standard" if platform != 'stackoverflow' else "none"
            
            # Add CRITICAL CONSTRAINTS section for platform-specific limits
            prompt += f"""

🚨 CRITICAL CONSTRAINTS - MANDATORY COMPLIANCE:
- Word Count: EXACTLY {word_min}-{word_max} words (NO EXCEPTIONS)
- Keywords: Use EXACTLY {len(primary_keywords)} primary keywords (NO MORE, NO LESS)
- Hashtags: Use EXACTLY {hashtag_count} hashtags (NO MORE, NO LESS)
- Structure: Follow EXACTLY {len(structure) if structure else 3} structural elements
- Voice: Use "{voice}" voice consistently throughout
- CTA: Include {cta_type} call-to-action

⚠️ WARNING: Content will be REJECTED if these constraints are not met exactly!"""
            
            # Add general rules
            if rules:
                rules_items = []
                for key, value in rules.items():
                    rules_items.append(f"{key}: {value}")
                rules_text = ", ".join(rules_items)
                prompt += f"""

PLATFORM RULES:
- {rules_text}
- Adhere to these specific platform requirements"""
            
            # Add guardrails and validation rules
            guardrails = self.library.get('guardrails', {})
            if guardrails:
                dos = guardrails.get('dos', [])
                donts = guardrails.get('donts', [])
                
                if dos:
                    dos_text = "\n- ".join(dos)
                    prompt += f"""

GUARDRAILS - DO:
- {dos_text}"""
                
                if donts:
                    donts_text = "\n- ".join(donts)
                    prompt += f"""

GUARDRAILS - DON'T:
- {donts_text}"""
            
            # Add SEO rules and keyword requirements
            seo_rules = self.library.get('seo', {}).get('rules', {})
            if seo_rules:
                prompt += f"""

SEO REQUIREMENTS:
- Natural placement only: {seo_rules.get('natural_placement_only', True)}
- Keywords per piece: {seo_rules.get('keywords_per_piece_min', 1)}-{seo_rules.get('keywords_per_piece_max', 3)}
- Long-form keyword placement: {', '.join(seo_rules.get('long_form_primary_keyword_placement', []))}
- MANDATORY: Include primary keywords naturally throughout content
- MANDATORY: Achieve minimum 2% keyword density
- MANDATORY: Use keywords in title, introduction, and subheadings"""
            
            # Add publishing defaults
            publishing_defaults = self.library['globals'].get('publishing_defaults', {})
            if publishing_defaults:
                brand_hashtags = publishing_defaults.get('brand_hashtags', [])
                if brand_hashtags:
                    prompt += f"""

BRAND HASHTAGS:
- Include these brand hashtags when appropriate: {', '.join(brand_hashtags)}
- Use brand hashtags naturally, not spam"""
            
            # Add post-processor requirements
            post_processors = self.library.get('runtime', {}).get('post_processors', [])
            if post_processors:
                prompt += f"""

POST-PROCESSING REQUIREMENTS:
- Ensure CTA is included (except StackOverflow)
- Enforce keyword limits and natural placement
- Validate platform adaptation and uniqueness
- Include visual suggestions where applicable
- Add FAQs for long-form content (1000+ words)
- Validate voice consistency
- Check evidence citations"""
            
            # Add FAQ requirements for long-form content
            if word_min >= 800:  # Long-form content
                prompt += f"""

FAQ REQUIREMENTS:
- MANDATORY: Include FAQ section for content {word_min}+ words
- FAQ should contain 5-7 relevant questions and answers
- Questions should address common concerns about the topic
- Answers should provide valuable insights and solutions
- FAQ section should be comprehensive and helpful"""
            
            # Add platform-specific enforcement
            if platform in ['twitter', 'twitter_quick']:
                prompt += f"""

CRITICAL REQUIREMENTS:
- Each tweet MUST be 280 characters or less
- Count characters carefully for each tweet
- Use numbered format: 1/12, 2/12, etc.
- Include exactly {config['word_count']['min']}-{config['word_count']['max']} tweets total
- Each tweet should be on a separate line
- Do NOT exceed character limits under any circumstances"""
                
                if platform == 'twitter_quick':
                    prompt += f"""
- MUST include CTA in the final tweet (Tweet 3)
- End with explicit call to action: "Contact us via www.barrana.ai or book a consultation"
- Use numbered format: 1/3, 2/3, 3/3"""
            
            elif platform in ['linkedin', 'medium', 'substack', 'barrana_blog', 'ikramrana_blog']:
                prompt += f"""

CRITICAL WORD COUNT REQUIREMENTS:
- Generate EXACTLY {word_min}-{word_max} words
- Count words carefully - this is mandatory
- Do NOT generate less than {word_min} words
- Do NOT generate more than {word_max} words
- Word count compliance is essential for platform optimization
- If content is too short, expand with more details, examples, and insights
- If content is too long, condense while maintaining quality
- MANDATORY: Content must be at least {word_min} words to pass validation
- Include detailed examples, case studies, and comprehensive explanations
- Expand on each point with supporting evidence and actionable advice"""
                
                # Add LinkedIn-specific optimizations
                if platform in ['linkedin', 'linkedin_quick']:
                    prompt += f"""

LINKEDIN-SPECIFIC OPTIMIZATIONS:
- VOICE CONSISTENCY: Use "I (Ikram)" voice consistently throughout - NEVER use "we" or "our"
- ENGAGEMENT FOCUS: End with a thought-provoking question to drive comments
- PROFESSIONAL TONE: Balance authority with approachability for SMB decision makers
- THOUGHT LEADERSHIP: Position insights as personal experience and expertise
- HASHTAG STRATEGY: Use 3-5 relevant hashtags including #AIForBusiness, #AutomationForSMBs, #Barrana
- HOOK OPTIMIZATION: Start with a bold contrarian statement or surprising insight
- EVIDENCE INTEGRATION: Reference WSJ/NFX/Reddit insights naturally in the content
- PERSONAL BRANDING: Emphasize Ikram's individual expertise and client experience"""
                    
                    if platform == 'linkedin_quick':
                        prompt += f"""

LINKEDIN QUICK SPECIFIC REQUIREMENTS:
- CHARACTER OPTIMIZATION: Maximize impact within 80-150 word limit
- NO LINKS: Keep content native and link-free for maximum reach
- PUNCHY HOOKS: Use bold, contrarian opening statements
- ENGAGEMENT QUESTIONS: End with simple, direct questions
- HASHTAG LIMIT: Use maximum 2-3 hashtags only
- QUICK IMPACT: Focus on one key insight or challenge"""
            
            elif platform in ['tiktok']:
                prompt += f"""

CRITICAL REQUIREMENTS:
- Video script: {config['word_count']['min']}-{config['word_count']['max']} seconds duration
- Caption: {config['caption_length']['min']}-{config['caption_length']['max']} words
- Structure: Video script + caption format required"""
            
            elif platform in ['instagram']:
                prompt += f"""

CRITICAL REQUIREMENTS:
- Caption: EXACTLY {config['word_count']['min']}-{config['word_count']['max']} words
- Structure: Visual concept + caption format required
- Count caption words carefully"""

            # Add RAG context if provided
            if rag_context and rag_context.strip():
                enhanced_prompt = f"""
Use the following Barrana context to ensure accuracy, brand consistency, and factual grounding:

{rag_context}

---

Now, following the platform-specific template below, generate content that incorporates the relevant information from the context above:

{prompt}

IMPORTANT: 
- Use the Barrana context to inform your content with accurate, company-specific information
- Maintain the platform-specific format and style requirements
- Ensure all facts and claims are grounded in the provided context
- Keep the brand voice and messaging consistent with Barrana's identity
"""
                logging.info(f"Built RAG-enhanced prompt for platform: {platform}")
                return enhanced_prompt
            else:
                logging.info(f"Built standard prompt for platform: {platform}")
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
        
        # Handle different JSON structures
        if 'guardrails' in self.library and 'validators' in self.library['guardrails']:
            validators = self.library['guardrails']['validators']
            # Convert array format to dict format for easier access
            rules = {}
            for validator in validators:
                if validator.get('id') == 'require_cta':
                    rules['cta_required'] = True
                elif validator.get('id') == 'keyword_density':
                    rules['keyword_density_min'] = validator.get('min', 0.02)
                    rules['keyword_density_max'] = validator.get('max', 0.05)
                elif validator.get('id') == 'faq_required':
                    rules['faq_min_words'] = validator.get('min_words', 0)
            return rules
        else:
            # Fallback to default rules
            return {
                'cta_required': True,
                'keyword_density_min': 0.02,
                'keyword_density_max': 0.05,
                'faq_min_words': 0
            }
    
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
    
    # LinkedIn-specific optimization methods
    def enforce_linkedin_voice(self, content: str, platform: str) -> str:
        """
        Ensure consistent 'I (Ikram)' voice throughout LinkedIn content
        
        Args:
            content: The generated content
            platform: Target platform (linkedin or linkedin_quick)
        
        Returns:
            Content with enforced voice consistency
        """
        if platform not in ['linkedin', 'linkedin_quick']:
            return content
        
        # Smart voice consistency rules for LinkedIn - avoid grammatical errors
        voice_rules = [
            # Replace "we" with "I" but avoid breaking questions and other contexts
            (r'\bwe are\b', 'I am'),
            (r'\bWe are\b', 'I am'),
            (r'\bwe have\b', 'I have'),
            (r'\bWe have\b', 'I have'),
            (r'\bwe can\b', 'I can'),
            (r'\bWe can\b', 'I can'),
            (r'\bwe will\b', 'I will'),
            (r'\bWe will\b', 'I will'),
            (r'\bwe do\b', 'I do'),
            (r'\bWe do\b', 'I do'),
            (r'\bwe provide\b', 'I provide'),
            (r'\bWe provide\b', 'I provide'),
            (r'\bwe offer\b', 'I offer'),
            (r'\bWe offer\b', 'I offer'),
            (r'\bwe help\b', 'I help'),
            (r'\bWe help\b', 'I help'),
            (r'\bwe bridge\b', 'I bridge'),
            (r'\bWe bridge\b', 'I bridge'),
            # Replace possessive forms
            (r'\bour\b', 'my'),
            (r'\bOur\b', 'My'),
            (r'\bour company\b', 'my company'),
            (r'\bOur company\b', 'My company'),
            # Ensure personal pronouns are used consistently
            (r'\bthe company\b', 'my company'),
            (r'\bThe company\b', 'My company'),
        ]
        
        # Apply voice consistency rules
        for pattern, replacement in voice_rules:
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        
        return content
    
    def optimize_linkedin_engagement(self, content: str, topic: str, platform: str) -> str:
        """
        Generate platform-specific engagement questions for LinkedIn
        
        Args:
            content: The generated content
            topic: The content topic
            platform: Target platform (linkedin or linkedin_quick)
        
        Returns:
            Content with optimized engagement elements
        """
        if platform not in ['linkedin', 'linkedin_quick']:
            return content
        
        # LinkedIn engagement optimization
        engagement_patterns = {
            'linkedin': [
                "What's your experience with this challenge?",
                "How has this affected your business?",
                "What strategies have worked for you?",
                "What would you add to this approach?",
                "Have you seen similar patterns in your industry?"
            ],
            'linkedin_quick': [
                "What do you think?",
                "Agree or disagree?",
                "What's your take?",
                "Have you experienced this?",
                "What would you add?"
            ]
        }
        
        # Add engagement question if not present
        if not any(q in content for q in ['?', 'What', 'How', 'Have you', 'Do you']):
            import random
            questions = engagement_patterns.get(platform, engagement_patterns['linkedin'])
            selected_question = random.choice(questions)
            
            if platform == 'linkedin_quick':
                content += f"\n\n{selected_question}"
            else:
                content += f"\n\n{selected_question} Share your thoughts below."
        
        return content
    
    def get_trending_linkedin_hashtags(self, topic: str) -> List[str]:
        """
        Get trending hashtags relevant to the topic for LinkedIn
        
        Args:
            topic: The content topic
        
        Returns:
            List of trending hashtags
        """
        # Base hashtags from configuration
        base_hashtags = [
            "#AIForBusiness",
            "#AutomationForSMBs", 
            "#Barrana",
            "#WorkflowAutomation",
            "#SmallBusiness"
        ]
        
        # Topic-specific hashtags
        topic_keywords = topic.lower().split()
        topic_hashtags = []
        
        # Map topic keywords to relevant hashtags
        hashtag_mapping = {
            'ai': ['#AI', '#ArtificialIntelligence', '#MachineLearning'],
            'automation': ['#Automation', '#ProcessAutomation', '#BusinessAutomation'],
            'workflow': ['#Workflow', '#ProcessOptimization', '#Efficiency'],
            'business': ['#Business', '#Entrepreneurship', '#BusinessGrowth'],
            'small': ['#SmallBusiness', '#SMB', '#Startup'],
            'cost': ['#CostReduction', '#ROI', '#BusinessSavings'],
            'revenue': ['#RevenueGrowth', '#BusinessGrowth', '#Profitability'],
            'chatbot': ['#Chatbots', '#CustomerService', '#AI'],
            'bookkeeping': ['#Bookkeeping', '#Accounting', '#Finance']
        }
        
        # Add relevant hashtags based on topic
        for keyword in topic_keywords:
            if keyword in hashtag_mapping:
                topic_hashtags.extend(hashtag_mapping[keyword])
        
        # Combine and deduplicate
        all_hashtags = base_hashtags + topic_hashtags
        unique_hashtags = list(dict.fromkeys(all_hashtags))  # Preserve order while removing duplicates
        
        return unique_hashtags[:5]  # Limit to 5 hashtags
    
    def calibrate_linkedin_tone(self, content: str, platform: str) -> str:
        """
        Adjust tone for optimal LinkedIn performance
        
        Args:
            content: The generated content
            platform: Target platform (linkedin or linkedin_quick)
        
        Returns:
            Content with calibrated tone
        """
        if platform not in ['linkedin', 'linkedin_quick']:
            return content
        
        # Tone calibration rules
        tone_adjustments = {
            'linkedin': {
                # Make more professional and thought-leadership focused
                'casual_words': {
                    'awesome': 'excellent',
                    'cool': 'impressive',
                    'gonna': 'going to',
                    'wanna': 'want to',
                    'yeah': 'yes',
                    'super': 'very',
                    'really': 'significantly'
                },
                # Add professional connectors
                'add_professional_connectors': True,
                # Ensure thought leadership positioning
                'thought_leadership_keywords': [
                    'insights', 'perspective', 'analysis', 'strategic',
                    'framework', 'methodology', 'approach'
                ]
            },
            'linkedin_quick': {
                # Keep punchy but professional
                'casual_words': {
                    'awesome': 'excellent',
                    'cool': 'impressive',
                    'gonna': 'going to',
                    'wanna': 'want to'
                },
                'add_professional_connectors': False,
                'thought_leadership_keywords': [
                    'insight', 'perspective', 'key point'
                ]
            }
        }
        
        adjustments = tone_adjustments.get(platform, tone_adjustments['linkedin'])
        
        # Apply casual word replacements
        for casual, professional in adjustments['casual_words'].items():
            content = re.sub(r'\b' + casual + r'\b', professional, content, flags=re.IGNORECASE)
        
        # Add professional connectors if needed
        if adjustments['add_professional_connectors']:
            connectors = ['Furthermore', 'Moreover', 'Additionally', 'Consequently', 'Therefore']
            # Add connectors where appropriate (simplified implementation)
            if len(content.split()) > 200:  # Only for longer content
                sentences = content.split('. ')
                if len(sentences) > 3:
                    # Add connector to middle sentences occasionally
                    import random
                    if random.random() < 0.3:  # 30% chance
                        connector = random.choice(connectors)
                        sentences[2] = f"{connector}, {sentences[2].lower()}"
                        content = '. '.join(sentences)
        
        return content
    
    def optimize_linkedin_quick_length(self, content: str) -> str:
        """
        Optimize content for maximum impact within LinkedIn Quick word limits
        
        Args:
            content: The generated content
        
        Returns:
            Optimized content for LinkedIn Quick
        """
        # Target: 80-150 words for LinkedIn Quick
        words = content.split()
        word_count = len(words)
        
        if word_count <= 150:
            return content  # Already within limits
        
        # Optimization strategies for LinkedIn Quick
        optimizations = [
            # Remove filler words
            (r'\b(very|really|quite|rather|somewhat|fairly)\b', ''),
            # Shorten common phrases
            (r'\bin order to\b', 'to'),
            (r'\bdue to the fact that\b', 'because'),
            (r'\bat this point in time\b', 'now'),
            (r'\bin the event that\b', 'if'),
            # Remove redundant words
            (r'\b(completely|totally|entirely) (finished|done|complete)\b', 'finished'),
            (r'\b(future) (plans|planning)\b', 'plans'),
        ]
        
        # Apply optimizations
        for pattern, replacement in optimizations:
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        
        # If still too long, truncate intelligently
        words = content.split()
        if len(words) > 150:
            # Keep first 140 words and add ellipsis
            content = ' '.join(words[:140]) + '...'
        
        return content
    
    def generate_linkedin_hooks(self, topic: str, platform: str) -> List[str]:
        """
        Generate multiple hook options for LinkedIn content
        
        Args:
            topic: The content topic
            platform: Target platform (linkedin or linkedin_quick)
        
        Returns:
            List of hook options
        """
        # Hook templates based on platform
        hook_templates = {
            'linkedin': [
                f"Most SMBs are {topic.lower()} wrong. Here's what I've learned:",
                f"I've worked with 100+ SMBs on {topic.lower()}. The pattern is clear:",
                f"Everyone talks about {topic.lower()}, but nobody mentions this:",
                f"After analyzing {topic.lower()} across industries, here's the truth:",
                f"The biggest mistake in {topic.lower()}? Thinking it's about technology."
            ],
            'linkedin_quick': [
                f"Hot take: {topic} isn't what you think.",
                f"Unpopular opinion: {topic} is overrated.",
                f"Here's what nobody tells you about {topic}:",
                f"The {topic} industry doesn't want you to know this:",
                f"Controversial: {topic} is actually hurting your business."
            ]
        }
        
        return hook_templates.get(platform, hook_templates['linkedin'])
    
    def apply_linkedin_optimizations(self, content: str, description: str, platform: str) -> str:
        """
        Apply all LinkedIn-specific optimizations to generated content
        
        Args:
            content: The generated content
            description: The original content description/topic
            platform: Target platform (linkedin or linkedin_quick)
        
        Returns:
            Optimized content for LinkedIn
        """
        if platform not in ['linkedin', 'linkedin_quick']:
            return content
        
        # Apply LinkedIn optimizations in sequence
        optimized_content = content
        
        # 1. Enforce voice consistency
        optimized_content = self.enforce_linkedin_voice(optimized_content, platform)
        
        # 2. Optimize engagement
        optimized_content = self.optimize_linkedin_engagement(optimized_content, description, platform)
        
        # 3. Calibrate tone
        optimized_content = self.calibrate_linkedin_tone(optimized_content, platform)
        
        # 4. For LinkedIn Quick, optimize length
        if platform == 'linkedin_quick':
            optimized_content = self.optimize_linkedin_quick_length(optimized_content)
        
        return optimized_content
    
    def get_engagement_config(self) -> Dict[str, Any]:
        """
        Get engagement system configuration from the library
        
        Returns:
            Engagement system configuration
        """
        if not self.library:
            raise RuntimeError("Prompt library not loaded")
        
        return self.library.get('engagement_system', {})
    
    def is_engagement_enabled_for_platform(self, platform: str) -> bool:
        """
        Check if engagement system is enabled for a specific platform
        
        Args:
            platform: Target platform name
        
        Returns:
            True if engagement is enabled for this platform
        """
        engagement_config = self.get_engagement_config()
        enabled_platforms = engagement_config.get('enabled_platforms', [])
        return platform in enabled_platforms
    
    def extract_industry_context(self, description: str) -> str:
        """
        Extract industry context from content description
        
        Args:
            description: The content description
        
        Returns:
            Detected industry name
        """
        try:
            from openai import OpenAI
            import os
            
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            
            industry_prompt = f"""
            Analyze this business description and identify the primary industry:
            "{description}"
            
            Return only the industry name from this list: restaurant, retail, e-commerce, consulting, healthcare, real_estate, fitness, beauty, automotive, technology, finance, education, manufacturing, construction, hospitality, professional_services.
            
            If the industry is not clearly identifiable, return "general_business".
            """
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": industry_prompt}],
                max_tokens=50,
                temperature=0.3
            )
            
            industry = response.choices[0].message.content.strip().lower()
            
            # Validate against known industries
            engagement_config = self.get_engagement_config()
            known_industries = engagement_config.get('industry_detection', {}).get('common_industries', [])
            
            if industry not in known_industries and industry != "general_business":
                return "general_business"
            
            return industry
            
        except Exception as e:
            logging.warning(f"Error extracting industry context: {e}")
            return "general_business"
    
    def generate_authentic_comments(self, main_content: str, platform: str, description: str) -> List[str]:
        """
        Generate authentic comments for social media engagement
        
        Args:
            main_content: The main post content
            platform: Target platform
            description: Original content description
        
        Returns:
            List of generated comments
        """
        try:
            from openai import OpenAI
            import os
            import random
            
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            engagement_config = self.get_engagement_config()
            comment_config = engagement_config.get('comment_generation', {})
            comment_types = comment_config.get('comment_types', {})
            
            # Extract industry context
            industry = self.extract_industry_context(description)
            
            # Get comment count range
            count_range = comment_config.get('count_range', [5, 7])
            comment_count = random.randint(count_range[0], count_range[1])
            
            # Select random comment types
            available_types = list(comment_types.keys())
            selected_types = random.sample(available_types, min(comment_count, len(available_types)))
            
            # Get platform-specific guidelines
            platform_guidelines = engagement_config.get('platform_specific_guidelines', {}).get(platform, "")
            uniqueness_guidelines = engagement_config.get('uniqueness_guidelines', [])
            
            comments = []
            generated_comments = []  # Track generated comments to avoid repetition
            
            for i, comment_type in enumerate(selected_types):
                try:
                    comment_config = comment_types[comment_type]
                    comment_template = comment_config['template']
                    avoid_phrases = comment_config.get('avoid_phrases', [])
                    
                    # Format template with industry and platform
                    comment_prompt = comment_template.format(industry=industry, platform=platform)
                    
                    # Build uniqueness context
                    uniqueness_context = ""
                    if generated_comments:
                        uniqueness_context = f"\n\nIMPORTANT: Avoid repeating these existing comments:\n" + "\n".join([f"- {comment}" for comment in generated_comments])
                    
                    # Add context about the main content
                    full_prompt = f"""
                    {comment_prompt}
                    
                    Platform Guidelines: {platform_guidelines}
                    
                    Uniqueness Guidelines:
                    {chr(10).join(f"- {guideline}" for guideline in uniqueness_guidelines)}
                    
                    Phrases to AVOID: {', '.join(avoid_phrases)}
                    
                    The main post content is:
                    "{main_content}"
                    {uniqueness_context}
                    
                    Generate a unique, natural comment that sounds like a real person. Make it authentic and platform-appropriate. Vary the length and style from other comments.
                    """
                    
                    response = client.chat.completions.create(
                        model="gpt-4",
                        messages=[{"role": "user", "content": full_prompt}],
                        max_tokens=120,
                        temperature=0.9
                    )
                    
                    comment = response.choices[0].message.content.strip()
                    comments.append(comment)
                    generated_comments.append(comment)  # Track for uniqueness
                    
                except Exception as e:
                    logging.warning(f"Error generating {comment_type} comment: {e}")
                    continue
            
            return comments
            
        except Exception as e:
            logging.error(f"Error generating authentic comments: {e}")
            return []
    
    def generate_barrana_response(self, comment: str, main_content: str, platform: str) -> str:
        """
        Generate professional Barrana response to a comment
        
        Args:
            comment: The comment to respond to
            main_content: The main post content
            platform: Target platform
        
        Returns:
            Professional Barrana response
        """
        try:
            from openai import OpenAI
            import os
            
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            engagement_config = self.get_engagement_config()
            response_config = engagement_config.get('response_generation', {})
            
            barrana_voice = response_config.get('barrana_voice', '')
            response_guidelines = response_config.get('response_guidelines', [])
            
            # Determine response strategy based on comment type
            response_strategy = self._determine_response_strategy(comment, response_config)
            
            response_prompt = f"""
            {barrana_voice}
            
            Response Strategy: {response_strategy}
            
            Guidelines:
            {chr(10).join(f"- {guideline}" for guideline in response_guidelines)}
            
            The original post was:
            "{main_content}"
            
            Someone commented:
            "{comment}"
            
            Generate a professional, helpful response from Barrana. Keep it 2-3 sentences and end with a question or call-to-action when appropriate.
            """
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": response_prompt}],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logging.error(f"Error generating Barrana response: {e}")
            return "Thank you for your comment! I'd love to help you further. Feel free to reach out via www.barrana.ai for a consultation."
    
    def _determine_response_strategy(self, comment: str, response_config: Dict[str, Any]) -> str:
        """
        Determine the appropriate response strategy based on comment content
        
        Args:
            comment: The comment text
            response_config: Response generation configuration
        
        Returns:
            Response strategy description
        """
        comment_lower = comment.lower()
        strategies = response_config.get('response_strategies', {})
        
        # Simple keyword-based strategy detection
        if any(word in comment_lower for word in ['question', 'how', 'what', 'when', 'where', 'why']):
            return strategies.get('questioning', 'Provide a helpful answer with specific advice.')
        elif any(word in comment_lower for word in ['tried', 'experience', 'used', 'implemented']):
            return strategies.get('sharing_experience', 'Validate their experience and offer insights.')
        elif any(word in comment_lower for word in ['concern', 'worry', 'cost', 'expensive', 'difficult']):
            return strategies.get('skeptical', 'Address their concerns with facts and examples.')
        elif any(word in comment_lower for word in ['excited', 'love', 'amazing', 'great', 'perfect']):
            return strategies.get('enthusiastic', 'Encourage their enthusiasm and provide next steps.')
        elif any(word in comment_lower for word in ['success', 'worked', 'improved', 'results', 'better']):
            return strategies.get('success_story', 'Celebrate their success and ask for more details.')
        else:
            return strategies.get('supportive', 'Acknowledge their situation and offer additional value.')
    
    def generate_engagement_package(self, main_content: str, platform: str, description: str) -> Dict[str, Any]:
        """
        Generate complete engagement package for social media platforms using comments-engine.json
        
        Args:
            main_content: The main post content
            platform: Target platform
            description: Original content description
        
        Returns:
            Complete engagement package with threaded comments and personas
        """
        if not self.is_engagement_enabled_for_platform(platform):
            return {}
        
        # Use new comments engine if available
        if self.comments_engine:
            return self.generate_threaded_engagement_cluster(main_content, platform, description)
        
        # Fallback to old system if comments engine not loaded
        try:
            # Generate authentic comments
            comments = self.generate_authentic_comments(main_content, platform, description)
            
            if not comments:
                return {}
            
            # Generate Barrana responses for each comment
            engagement_pairs = []
            for comment in comments:
                response = self.generate_barrana_response(comment, main_content, platform)
                engagement_pairs.append({
                    'comment': comment,
                    'barrana_response': response
                })
            
            return {
                'comments_count': len(comments),
                'engagement_pairs': engagement_pairs,
                'platform': platform,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error generating engagement package: {e}")
            return {}
    
    def generate_threaded_engagement_cluster(self, main_content: str, platform: str, description: str) -> Dict[str, Any]:
        """
        Generate threaded comment cluster using comments-engine.json specifications
        
        This generates 15-20 comments with 5 personas (Person A-E) + Barrana,
        with proper threading, reply logic, and timing delays.
        
        Args:
            main_content: The main post content
            platform: Target platform (linkedin, instagram, facebook, tiktok)
            description: Original content description
        
        Returns:
            Complete engagement package with threaded comments, personas, and timing
        """
        if not self.comments_engine:
            logging.warning("Comments engine not loaded, cannot generate threaded cluster")
            return {}
        
        try:
            import random
            from openai import OpenAI
            import os
            
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            
            # Get configuration from comments engine
            personas = self.comments_engine.get('personas', {})
            platform_config = self.comments_engine.get('platform_specific_addons', {}).get(platform, {})
            timing_config = self.comments_engine.get('timing_and_cadence', {}).get(platform, {})
            reply_logic = self.comments_engine.get('reply_logic_and_structure', {})
            barrana_context = self.comments_engine.get('barrana_business_context', {})
            
            # Build master prompt
            master_prompt = self._build_comments_engine_prompt(
                main_content, 
                platform, 
                description,
                personas,
                platform_config,
                barrana_context
            )
            
            # Generate the comment cluster using GPT-4
            logging.info(f"Generating threaded comment cluster for {platform}...")
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{
                    "role": "system",
                    "content": "You are an expert social media engagement strategist. Generate authentic, natural comment threads following the exact specifications provided."
                }, {
                    "role": "user",
                    "content": master_prompt
                }],
                max_tokens=3000,
                temperature=0.85
            )
            
            # Parse the JSON response
            response_text = response.choices[0].message.content.strip()
            
            # Extract JSON from markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            try:
                cluster_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                logging.error(f"Failed to parse GPT-4 response as JSON: {e}")
                logging.error(f"Response text: {response_text[:500]}...")
                return {}
            
            # Validate and enrich the cluster data
            enriched_cluster = self._enrich_comment_cluster(cluster_data, platform, timing_config)
            
            logging.info(f"✅ Generated {enriched_cluster.get('meta', {}).get('total_comments', 0)} comments for {platform}")
            
            return enriched_cluster
            
        except Exception as e:
            logging.error(f"Error generating threaded engagement cluster: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def _build_comments_engine_prompt(self, main_content: str, platform: str, description: str, 
                                     personas: Dict, platform_config: Dict, barrana_context: Dict) -> str:
        """Build the comprehensive prompt for GPT-4 based on comments-engine.json"""
        
        # Extract persona information
        person_a = personas.get('person_a', {})
        person_b = personas.get('person_b', {})
        person_c = personas.get('person_c', {})
        person_d = personas.get('person_d', {})
        person_e = personas.get('person_e', {})
        barrana = personas.get('barrana', {})
        
        # Add geographic locations for personas (expanded list)
        locations = ["New York", "London", "Toronto", "San Francisco", "Austin", "Chicago", 
                    "Boston", "Seattle", "Miami", "Dallas", "Denver", "Portland", "Atlanta", 
                    "Phoenix", "San Diego", "Vancouver", "Montreal", "Sydney", "Singapore"]
        import random
        person_a_location = random.choice(locations)
        person_b_location = random.choice([loc for loc in locations if loc != person_a_location])
        person_c_location = random.choice([loc for loc in locations if loc not in [person_a_location, person_b_location]])
        
        # Get sentence banks for variation
        sentence_banks = self.comments_engine.get('sentence_banks', {})
        uniqueness_rules = self.comments_engine.get('uniqueness_enforcement', {})
        
        # Randomly select variation examples from banks
        person_a_question_starters = sentence_banks.get('person_a_question_starters', [])
        person_a_questions = sentence_banks.get('person_a_questions', [])
        person_b_skeptical_openers = sentence_banks.get('person_b_skeptical_openers', [])
        person_b_concerns = sentence_banks.get('person_b_concerns', [])
        person_c_result_metrics = sentence_banks.get('person_c_result_metrics', [])
        person_c_testimonial_starters = sentence_banks.get('person_c_testimonial_starters', [])
        person_d_tag_phrases = sentence_banks.get('person_d_tag_phrases', [])
        person_e_reactions = sentence_banks.get('person_e_reactions', [])
        person_e_emoji_combos = sentence_banks.get('person_e_emoji_combos', [])
        
        # Barrana response variations
        barrana_security_responses = sentence_banks.get('barrana_response_security', [])
        barrana_cost_responses = sentence_banks.get('barrana_response_cost', [])
        barrana_how_it_works = sentence_banks.get('barrana_response_how_it_works', [])
        barrana_result_responses = sentence_banks.get('barrana_response_results', [])
        
        # Randomly select which persona should dominate this thread
        dominant_personas = ['Person A', 'Person B', 'Person C', 'Person D', 'Person E']
        dominant_persona = random.choice(dominant_personas)
        
        # Banned phrases to avoid
        banned_phrases = uniqueness_rules.get('banned_repetitive_phrases', [])
        
        prompt = f"""
Generate a natural, authentic comment thread for a {platform.upper()} post.

⚠️ CRITICAL: Comments MUST reference SPECIFIC content from the post below. Do NOT generate generic comments!

====================
POST CONTENT (READ CAREFULLY):
====================
{main_content}

====================
CONTENT-SPECIFIC REQUIREMENTS:
====================
✅ Quote specific phrases or statistics from the post
✅ Ask about specific features, benefits, or examples mentioned
✅ Comment on specific results, numbers, or case studies
✅ Reference exact industry examples or pain points discussed
✅ React to specific insights or contrarian points made
❌ Do NOT use generic phrases like "This is interesting" without specifics
❌ Do NOT ask generic questions - tie them to the post content
❌ Do NOT give generic praise - cite what specifically resonated

EXAMPLE:
BAD: "Great post! This is very helpful."
GOOD: "Love the point about '20% cost reduction' - is that consistent across all industries?"

====================
BARRANA CONTEXT:
====================
Identity: {barrana_context.get('identity', '')}
Services: {', '.join(barrana_context.get('services', []))}
Tone: {barrana_context.get('tone', '')}
Industries: {', '.join(barrana_context.get('industries', []))}

====================
PERSONAS (6 VOICES WITH LOCATIONS):
====================

🎯 DOMINANT PERSONA FOR THIS THREAD: {dominant_persona}
(This persona should have MORE comments than others - give them 3-4 comments/replies)

1. PERSON A ({person_a.get('name', 'The Curious One')}) - Based in {person_a_location}:
   Voice: {person_a.get('voice', '')}
   
   VARIATION BANK - Use these starters (pick different ones each time):
   {', '.join(random.sample(person_a_question_starters, min(5, len(person_a_question_starters))))}
   
   VARIATION BANK - Questions to choose from (mix and match):
   {', '.join(random.sample(person_a_questions, min(6, len(person_a_questions))))}
   
   Geographic context: Reference {person_a_location} market/regulations/pricing

2. PERSON B ({person_b.get('name', 'The Skeptic')}) - Based in {person_b_location}:
   Voice: {person_b.get('voice', '')}
   
   VARIATION BANK - Skeptical openers (rotate these):
   {', '.join(random.sample(person_b_skeptical_openers, min(5, len(person_b_skeptical_openers))))}
   
   VARIATION BANK - Concerns to raise (pick different ones):
   {', '.join(random.sample(person_b_concerns, min(6, len(person_b_concerns))))}
   
   Geographic context: Reference {person_b_location} regulations/compliance

3. PERSON C ({person_c.get('name', 'The Insider')}) - Based in {person_c_location}:
   Voice: {person_c.get('voice', '')}
   
   VARIATION BANK - Testimonial starters (use different ones):
   {', '.join(random.sample(person_c_testimonial_starters, min(5, len(person_c_testimonial_starters))))}
   
   VARIATION BANK - Result metrics (pick ONE per comment, vary the format):
   {', '.join(random.sample(person_c_result_metrics, min(6, len(person_c_result_metrics))))}
   
   REQUIREMENT: Vary metrics - use percentages, time, money, or qualitative results
   Geographic context: {person_c_location}-based business

4. PERSON D ({person_d.get('name', 'The Amplifier')}):
   Voice: {person_d.get('voice', '')}
   
   VARIATION BANK - Tag phrases (rotate):
   {', '.join(random.sample(person_d_tag_phrases, min(6, len(person_d_tag_phrases))))}
   
   REQUIREMENT: Tag 1-2 handles relevant to industry (e.g., @RestaurantOwner, @ClinicManager)
   REQUIREMENT: Vary the tag phrases - never use the same structure twice

5. PERSON E ({person_e.get('name', 'The Cheerleader')}):
   Voice: {person_e.get('voice', '')}
   
   VARIATION BANK - Reactions (mix these):
   {', '.join(random.sample(person_e_reactions, min(6, len(person_e_reactions))))}
   
   VARIATION BANK - Emoji combos (use different ones):
   {', '.join(random.sample(person_e_emoji_combos, min(5, len(person_e_emoji_combos))))}
   
   REQUIREMENT: Short, punchy, emoji-rich BUT reference specific content

6. BARRANA ({barrana.get('name', 'Barrana')}):
   Voice: {barrana.get('voice', '')}
   
   VARIATION BANK - Security responses (pick different ones for each security question):
   • {random.sample(barrana_security_responses, min(3, len(barrana_security_responses)))[0] if barrana_security_responses else 'Security response'}
   • {random.sample(barrana_security_responses, min(3, len(barrana_security_responses)))[1] if len(barrana_security_responses) > 1 else 'Security response'}
   
   VARIATION BANK - Cost responses (pick different ones for each cost question):
   • {random.sample(barrana_cost_responses, min(3, len(barrana_cost_responses)))[0] if barrana_cost_responses else 'Cost response'}
   • {random.sample(barrana_cost_responses, min(3, len(barrana_cost_responses)))[1] if len(barrana_cost_responses) > 1 else 'Cost response'}
   
   VARIATION BANK - How it works (pick different ones):
   • {random.sample(barrana_how_it_works, min(3, len(barrana_how_it_works)))[0] if barrana_how_it_works else 'How it works'}
   • {random.sample(barrana_how_it_works, min(3, len(barrana_how_it_works)))[1] if len(barrana_how_it_works) > 1 else 'How it works'}
   
   VARIATION BANK - Result acknowledgments (when replying to Person C):
   • {random.sample(barrana_result_responses, min(3, len(barrana_result_responses)))[0] if barrana_result_responses else 'Result response'}
   
   REQUIREMENT: NEVER start with "Great question!" or "Glad to hear!" - use the variation banks above

====================
PLATFORM-SPECIFIC GUIDELINES FOR {platform.upper()}:
====================
Tone: {platform_config.get('tone', '')}
Emoji Usage: {platform_config.get('emoji_usage', '')}
Delays: {platform_config.get('delays', '')}

====================
🚨 UNIQUENESS ENFORCEMENT (CRITICAL):
====================

BANNED PHRASES - NEVER use these exact phrases:
{chr(10).join(f'❌ "{phrase}"' for phrase in banned_phrases)}

RANDOMIZATION REQUIREMENTS:
✅ Use DIFFERENT question structures each time (vary "how/what/when/where/why")
✅ Rotate Barrana's opening words - USE THE VARIATION BANKS ABOVE
✅ Mix metric formats: percentages (22%), time (6 weeks), money ($8K), qualitative (significant)
✅ Use DIFFERENT cities across posts (we have 19 locations to choose from)
✅ Vary comment lengths WITHIN each persona (not all medium)
✅ Change concern order: sometimes security first, sometimes cost, sometimes usability
✅ Person C should use DIFFERENT metrics each time - never repeat "30%" or "40%"

VARIATION REQUIREMENT:
🎯 If you used "How would this work for X?" in a previous comment, try:
   • "Walk me through how X would use this"
   • "Can you break down the setup for X?"
   • "What would implementation look like for X?"
   • "Does this scale down to X size?"

====================
MANDATORY REQUIREMENTS:
====================
1. Generate 15-20 comments total
2. At least 50% of comments must be REPLIES (not top-level)
3. Barrana must reply to each persona at least once
4. Barrana must reply to Person B (The Skeptic) TWICE
5. Person D must tag 1-2 external handles (relevant to content)
6. Person C must cite at least one specific benefit/result from their experience
7. Person E must use emojis in ≥50% of their comments
8. NO duplicate text or repetitive phrasing - USE THE VARIATION BANKS
9. Vary comment lengths: short (1 line), medium (2-3 lines), long (4-5 lines)
10. Use natural, platform-appropriate language
11. Limit deep nesting (max 3 replies per parent comment)
12. 🔥 CONTENT-SPECIFIC: Every comment must tie to something SPECIFIC in the post above
13. 🎯 DOMINANT PERSONA ({dominant_persona}) should have 3-4 comments total

====================
OUTPUT FORMAT (JSON):
====================
{{
  "platform": "{platform}",
  "post_reference": "Generated for: {description[:100]}...",
  "comments": [
    {{
      "id": "c1",
      "speaker": "Person A|Person B|Person C|Person D|Person E|Barrana",
      "type": "new|reply",
      "reply_to": null or "c<number>",
      "text": "The actual comment text...",
      "tone": "curious|skeptical|enthusiastic|amplifying|cheerleading|authoritative",
      "suggested_delay_seconds": <integer>,
      "tags": ["@handle1", "@handle2"] or []
    }}
  ],
  "meta": {{
    "total_comments": <count>,
    "percent_replies": <percentage>,
    "barrana_replies_count": <count>,
    "amplifier_tags_count": <count>
  }}
}}

====================
COMMENT LENGTH VARIATION:
====================
Distribute comment lengths naturally:
- 30% SHORT (1 sentence, 5-15 words): Quick reactions, emoji responses
- 50% MEDIUM (2-3 sentences, 15-40 words): Standard comments, questions
- 20% LONG (4-5 sentences, 40-80 words): Testimonials, detailed questions, insider stories

====================
QUESTION DEPTH EXAMPLES:
====================
SHALLOW: "How does this work?"
MEDIUM: "How would this integrate with our existing CRM system?"
DEEP: "For a 50-seat restaurant doing 300 orders on weekends with Square POS, what's the typical integration timeline and any gotchas with menu syncing?"

Use a mix of shallow, medium, and deep questions!

====================
IMPORTANT REMINDERS:
====================
- Make it look natural and organic
- REFERENCE SPECIFIC CONTENT from the post (most important!)
- Avoid generic phrases and corporate speak
- Each persona should have a distinct voice AND location context
- Thread the conversation logically (replies should reference parent comments)
- Use conservative claims only (no fake testimonials)
- Soft CTAs only (e.g., "DM us", "link in bio")
- Vary comment lengths (short, medium, long)
- Include technical, business, and practical questions at different depths
- Person C should give specific numbers/results from their experience

Generate the complete JSON now:
"""
        
        return prompt
    
    def _enrich_comment_cluster(self, cluster_data: Dict, platform: str, timing_config: Dict) -> Dict:
        """Enrich cluster data with additional metadata and validation"""
        
        # Ensure meta exists
        if 'meta' not in cluster_data:
            cluster_data['meta'] = {}
        
        # Calculate meta statistics
        comments = cluster_data.get('comments', [])
        total_comments = len(comments)
        reply_count = sum(1 for c in comments if c.get('type') == 'reply' or c.get('reply_to'))
        barrana_replies = sum(1 for c in comments if c.get('speaker') == 'Barrana' and (c.get('type') == 'reply' or c.get('reply_to')))
        amplifier_tags = sum(len(c.get('tags', [])) for c in comments if c.get('speaker') == 'Person D')
        
        cluster_data['meta'].update({
            'total_comments': total_comments,
            'percent_replies': round((reply_count / total_comments * 100) if total_comments > 0 else 0, 2),
            'barrana_replies_count': barrana_replies,
            'amplifier_tags_count': amplifier_tags,
            'platform': platform,
            'generated_at': datetime.now().isoformat()
        })
        
        # Add timing configuration
        cluster_data['timing_guidelines'] = timing_config
        
        # Validate requirements
        warnings = []
        if total_comments < 15:
            warnings.append(f"Only {total_comments} comments generated (expected 15-20)")
        if reply_count / total_comments < 0.5 if total_comments > 0 else False:
            warnings.append(f"Only {cluster_data['meta']['percent_replies']}% replies (expected ≥50%)")
        if barrana_replies < 5:
            warnings.append(f"Only {barrana_replies} Barrana replies (expected at least 5)")
        
        if warnings:
            cluster_data['meta']['warnings'] = warnings
            for warning in warnings:
                logging.warning(f"Comment cluster validation: {warning}")
        
        return cluster_data