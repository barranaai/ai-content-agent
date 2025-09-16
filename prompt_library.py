import json
import logging
import re
from typing import Dict, List, Optional, Any
import os

class BarranaPromptLibrary:
    """
    Manages the Barrana prompt library JSON file and provides methods
    for building dynamic prompts and accessing platform configurations.
    """
    
    def __init__(self, json_path: str = "Barrana-Merged-Prompt-Library-v3.1.json"):
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
