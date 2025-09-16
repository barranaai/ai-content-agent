"""
Platform-Specific Quality Metrics System
Based on Final Verdict Prompt Elements for Each Platform
"""

import re
from typing import Dict, List, Any, Tuple

class PlatformSpecificMetrics:
    """Calculate platform-specific quality metrics based on unique platform elements"""
    
    def __init__(self):
        self.platform_configs = {
            # Personal Voice Platforms (I Ikram)
            'linkedin': {
                'voice': 'personal',
                'voice_text': 'I Ikram',
                'word_range': (280, 320),
                'keywords_range': (3, 5),
                'hashtags_range': (3, 5),
                'structure_steps': (3, 5),
                'tone': 'professional',
                'cta_type': 'explicit',
                'special_rules': ['no_links'],
                'unique_features': ['thought_leadership', 'contrarian_insights', 'professional_networking'],
                'content_type': 'medium_form'
            },
            'ikramrana_blog': {
                'voice': 'personal',
                'voice_text': 'I Ikram',
                'word_range': (800, 1200),
                'keywords_range': (5, 7),
                'hashtags_range': (5, 7),
                'structure_steps': (5, 7),
                'tone': 'educational',
                'cta_type': 'explicit',
                'special_rules': [],
                'unique_features': ['personal_pov', 'storytelling', 'educational_content'],
                'content_type': 'long_form'
            },
            'linkedin_quick': {
                'voice': 'personal',
                'voice_text': 'I Ikram',
                'word_range': (80, 150),
                'keywords_range': (2, 3),
                'hashtags_range': (2, 3),
                'structure_steps': (2, 3),
                'tone': 'professional',
                'cta_type': 'soft',
                'special_rules': ['no_links', 'minimal_emojis'],
                'unique_features': ['quick_engagement', 'bold_contrarian_opening', 'open_ended_question'],
                'content_type': 'ultra_short_form'
            },
            
            # Corporate Voice Platforms (We Barrana)
            'medium': {
                'voice': 'corporate',
                'voice_text': 'We Barrana',
                'word_range': (900, 1200),
                'keywords_range': (5, 7),
                'hashtags_range': (5, 7),
                'structure_steps': (5, 7),
                'tone': 'educational',
                'cta_type': 'explicit',
                'special_rules': [],
                'unique_features': ['seo_optimized', 'comprehensive_articles', 'educational_content'],
                'content_type': 'long_form'
            },
            'substack': {
                'voice': 'corporate',
                'voice_text': 'We Barrana',
                'word_range': (1000, 1500),
                'keywords_range': (5, 7),
                'hashtags_range': (5, 7),
                'structure_steps': (5, 7),
                'tone': 'educational',
                'cta_type': 'explicit',
                'special_rules': [],
                'unique_features': ['newsletter_narrative', 'educational_content', 'comprehensive_articles'],
                'content_type': 'long_form'
            },
            'barrana_blog': {
                'voice': 'corporate',
                'voice_text': 'We Barrana',
                'word_range': (1500, 2000),
                'keywords_range': (5, 7),
                'hashtags_range': (5, 7),
                'structure_steps': (5, 7),
                'tone': 'educational',
                'cta_type': 'explicit',
                'special_rules': [],
                'unique_features': ['comprehensive_guides', 'detailed_analysis', 'educational_content'],
                'content_type': 'long_form'
            },
            'slideshare': {
                'voice': 'corporate',
                'voice_text': 'We Barrana',
                'word_range': (100, 300),
                'keywords_range': (1, 2),
                'hashtags_range': (1, 2),
                'structure_steps': (1, 2),
                'tone': 'professional',
                'cta_type': 'explicit',
                'special_rules': ['visual_content'],
                'unique_features': ['professional_presentations', 'business_focus', 'visual_content'],
                'content_type': 'visual_content'
            },
            'product_hunt': {
                'voice': 'corporate',
                'voice_text': 'We Barrana',
                'word_range': (200, 400),
                'keywords_range': (2, 3),
                'hashtags_range': (2, 3),
                'structure_steps': (2, 3),
                'tone': 'professional',
                'cta_type': 'explicit',
                'special_rules': [],
                'unique_features': ['product_positioning', 'launch_strategy', 'startup_community'],
                'content_type': 'short_form'
            },
            'crunchbase': {
                'voice': 'corporate',
                'voice_text': 'We Barrana',
                'word_range': (100, 300),
                'keywords_range': (2, 3),
                'hashtags_range': (2, 3),
                'structure_steps': (2, 3),
                'tone': 'professional',
                'cta_type': 'explicit',
                'special_rules': [],
                'unique_features': ['company_positioning', 'business_intelligence', 'company_data'],
                'content_type': 'short_form'
            },
            'substack_quick': {
                'voice': 'corporate',
                'voice_text': 'We Barrana',
                'word_range': (200, 300),
                'keywords_range': (2, 3),
                'hashtags_range': (2, 3),
                'structure_steps': (2, 3),
                'tone': 'educational',
                'cta_type': 'soft',
                'special_rules': [],
                'unique_features': ['quick_notes', 'seed_ideas', 'provocative_tone'],
                'content_type': 'ultra_short_form'
            },
            
            # Flexible Voice Platforms
            'twitter': {
                'voice': 'flexible',
                'voice_text': 'Flexible',
                'word_range': (8, 12),  # tweets
                'keywords_range': (1, 2),
                'hashtags_range': (1, 2),
                'structure_steps': (1, 2),
                'tone': 'conversational',
                'cta_type': 'discussion_invitation',
                'special_rules': ['no_links', '280_chars_per_tweet'],
                'unique_features': ['thread_format', 'conversational', '8_12_tweets'],
                'content_type': 'micro_content'
            },
            'tiktok': {
                'voice': 'flexible',
                'voice_text': 'Flexible',
                'word_range': (70, 120),  # caption words
                'keywords_range': (2, 3),
                'hashtags_range': (2, 3),
                'structure_steps': (2, 3),
                'tone': 'entertainment',
                'cta_type': 'soft',
                'special_rules': ['video_script', '30_60_sec_video'],
                'unique_features': ['video_script_caption', 'entertainment', '30_60_sec_video'],
                'content_type': 'video_content'
            },
            'instagram': {
                'voice': 'flexible',
                'voice_text': 'Flexible',
                'word_range': (100, 150),
                'keywords_range': (2, 3),
                'hashtags_range': (2, 3),
                'structure_steps': (2, 3),
                'tone': 'entertainment',
                'cta_type': 'soft',
                'special_rules': ['visual_content'],
                'unique_features': ['visual_content_caption', 'lifestyle', 'visual_content'],
                'content_type': 'visual_content'
            },
            'facebook': {
                'voice': 'flexible',
                'voice_text': 'Flexible',
                'word_range': (100, 150),
                'keywords_range': (2, 3),
                'hashtags_range': (2, 3),
                'structure_steps': (2, 3),
                'tone': 'conversational',
                'cta_type': 'soft',
                'special_rules': [],
                'unique_features': ['community_focused', 'social_engagement', 'community_driven'],
                'content_type': 'short_form'
            },
            'pinterest': {
                'voice': 'flexible',
                'voice_text': 'Flexible',
                'word_range': (100, 150),
                'keywords_range': (2, 3),
                'hashtags_range': (2, 3),
                'structure_steps': (2, 3),
                'tone': 'inspirational',
                'cta_type': 'soft',
                'special_rules': ['visual_content'],
                'unique_features': ['seo_optimized_pins', 'visual_discovery', 'visual_content'],
                'content_type': 'visual_content'
            },
            'skool': {
                'voice': 'flexible',
                'voice_text': 'Flexible',
                'word_range': (200, 600),
                'keywords_range': (3, 5),
                'hashtags_range': (3, 5),
                'structure_steps': (3, 5),
                'tone': 'conversational',
                'cta_type': 'explicit',
                'special_rules': [],
                'unique_features': ['educational_lessons', 'community_learning', 'educational_community'],
                'content_type': 'medium_form'
            },
            'twitter_quick': {
                'voice': 'flexible',
                'voice_text': 'Flexible',
                'word_range': (1, 3),  # tweets
                'keywords_range': (2, 3),
                'hashtags_range': (2, 3),
                'structure_steps': (2, 3),
                'tone': 'conversational',
                'cta_type': 'discussion_invitation',
                'special_rules': ['no_links', '280_chars_per_tweet', '1_emoji_max'],
                'unique_features': ['mini_thread', 'quick_engagement', '1_3_tweets'],
                'content_type': 'micro_content'
            },
            
            # Technical Voice Platforms
            'stackoverflow': {
                'voice': 'technical',
                'voice_text': 'Technical',
                'word_range': (150, 400),
                'keywords_range': (1, 2),
                'hashtags_range': (1, 2),
                'structure_steps': (1, 2),
                'tone': 'technical',
                'cta_type': 'explicit',
                'special_rules': [],
                'unique_features': ['direct_answers', 'code_focused', 'technical_qa'],
                'content_type': 'medium_form'
            },
            'dev_to': {
                'voice': 'flexible',
                'voice_text': 'Flexible',
                'word_range': (400, 800),
                'keywords_range': (3, 5),
                'hashtags_range': (3, 5),
                'structure_steps': (3, 5),
                'tone': 'educational',
                'cta_type': 'explicit',
                'special_rules': [],
                'unique_features': ['technical_tutorials', 'developer_community', 'technical_content'],
                'content_type': 'medium_form'
            },
            
            # Conversational Voice Platforms
            'reddit': {
                'voice': 'personal',
                'voice_text': 'I Ikram',
                'word_range': (400, 600),
                'keywords_range': (3, 5),
                'hashtags_range': (3, 5),
                'structure_steps': (3, 5),
                'tone': 'conversational',
                'cta_type': 'discussion_invitation',
                'special_rules': [],
                'unique_features': ['conversational_discussion', 'community_engagement', 'community_driven'],
                'content_type': 'medium_form'
            },
            'quora': {
                'voice': 'personal',
                'voice_text': 'I Ikram',
                'word_range': (500, 700),
                'keywords_range': (3, 5),
                'hashtags_range': (3, 5),
                'structure_steps': (3, 5),
                'tone': 'educational',
                'cta_type': 'explicit',
                'special_rules': [],
                'unique_features': ['authoritative_answers', 'expertise_sharing', 'educational_qa'],
                'content_type': 'medium_form'
            }
        }
    
    def get_platform_config(self, platform: str) -> Dict[str, Any]:
        """Get platform-specific configuration"""
        return self.platform_configs.get(platform, {})
    
    def calculate_platform_specific_metrics(self, platform: str, content: str, 
                                          primary_keywords: List[str], 
                                          secondary_keywords: List[str]) -> Dict[str, Any]:
        """Calculate platform-specific quality metrics based on unique platform elements"""
        
        config = self.get_platform_config(platform)
        if not config:
            return {}
        
        metrics = {}
        
        # 1. VOICE COMPLIANCE
        metrics['voice_compliance'] = self._check_voice_compliance(platform, content, config)
        
        # 2. WORD COUNT COMPLIANCE
        metrics['word_count_compliance'] = self._check_word_count_compliance(platform, content, config)
        
        # 3. KEYWORD COMPLIANCE
        metrics['keyword_compliance'] = self._check_keyword_compliance(platform, content, config, primary_keywords, secondary_keywords)
        
        # 4. HASHTAG COMPLIANCE
        metrics['hashtag_compliance'] = self._check_hashtag_compliance(platform, content, config)
        
        # 5. STRUCTURE COMPLIANCE
        metrics['structure_compliance'] = self._check_structure_compliance(platform, content, config)
        
        # 6. TONE COMPLIANCE
        metrics['tone_compliance'] = self._check_tone_compliance(platform, content, config)
        
        # 7. CTA COMPLIANCE
        metrics['cta_compliance'] = self._check_cta_compliance(platform, content, config)
        
        # 8. SPECIAL RULES COMPLIANCE
        metrics['special_rules_compliance'] = self._check_special_rules_compliance(platform, content, config)
        
        # 9. UNIQUE FEATURES COMPLIANCE
        metrics['unique_features_compliance'] = self._check_unique_features_compliance(platform, content, config)
        
        # 10. OVERALL PLATFORM SCORE
        metrics['overall_platform_score'] = self._calculate_overall_platform_score(metrics)
        
        return metrics
    
    def _check_voice_compliance(self, platform: str, content: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check if content follows platform-specific voice requirements"""
        voice = config.get('voice', '')
        voice_text = config.get('voice_text', '')
        
        detected_voice = self._detect_voice_in_content(content)
        
        if voice == 'personal':
            # Check for "I" statements, personal pronouns, personal experiences
            personal_indicators = ['I ', 'my ', 'me ', 'myself', 'personal', 'experience', 'believe', 'think']
            personal_count = sum(1 for indicator in personal_indicators if indicator.lower() in content.lower())
            compliance_score = min(personal_count / 2, 1.0)  # At least 2 personal indicators
            
        elif voice == 'corporate':
            # Check for "We" statements, corporate language, professional tone
            corporate_indicators = ['we ', 'our ', 'us ', 'company', 'team', 'organization', 'business', 'corporate']
            corporate_count = sum(1 for indicator in corporate_indicators if indicator.lower() in content.lower())
            compliance_score = min(corporate_count / 2, 1.0)  # At least 2 corporate indicators
            
        elif voice == 'flexible':
            # Flexible voice can use either personal or corporate - give full credit
            personal_indicators = ['I ', 'my ', 'me ', 'myself']
            corporate_indicators = ['we ', 'our ', 'us ', 'company']
            personal_count = sum(1 for indicator in personal_indicators if indicator.lower() in content.lower())
            corporate_count = sum(1 for indicator in corporate_indicators if indicator.lower() in content.lower())
            
            # Flexible voice gets full credit if it uses either personal or corporate voice
            if personal_count > 0 or corporate_count > 0:
                compliance_score = 1.0
            else:
                compliance_score = 0.5  # Partial credit for neutral voice
            
        elif voice == 'technical':
            # Check for technical language, code references, technical terms
            technical_indicators = ['code', 'function', 'algorithm', 'API', 'database', 'system', 'technical', 'implementation']
            technical_count = sum(1 for indicator in technical_indicators if indicator.lower() in content.lower())
            compliance_score = min(technical_count / 2, 1.0)  # At least 2 technical indicators
            
        else:
            compliance_score = 0.0
        
        return {
            'score': compliance_score,
            'voice_required': voice_text,
            'voice_detected': detected_voice,
            'compliance_percentage': round(compliance_score * 100, 1)
        }
    
    def _check_word_count_compliance(self, platform: str, content: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check if content meets platform-specific word count requirements"""
        word_range = config.get('word_range', (0, 1000))
        min_words, max_words = word_range
        
        # Handle special cases
        if platform in ['twitter', 'twitter_quick']:
            # Count tweets instead of words
            tweet_count = self._count_tweets(content)
            compliance_score = 1.0 if min_words <= tweet_count <= max_words else 0.0
            actual_count = tweet_count
            count_type = 'tweets'
            
        elif platform == 'tiktok':
            # Count caption words only
            caption_words = self._extract_caption_words(content)
            compliance_score = 1.0 if min_words <= caption_words <= max_words else 0.0
            actual_count = caption_words
            count_type = 'caption_words'
            
        elif platform == 'instagram':
            # Count caption words only
            caption_words = self._extract_caption_words(content)
            compliance_score = 1.0 if min_words <= caption_words <= max_words else 0.0
            actual_count = caption_words
            count_type = 'caption_words'
            
        else:
            # Regular word count
            word_count = len(content.split())
            compliance_score = 1.0 if min_words <= word_count <= max_words else 0.0
            actual_count = word_count
            count_type = 'words'
        
        return {
            'score': compliance_score,
            'required_range': f"{min_words}-{max_words} {count_type}",
            'actual_count': actual_count,
            'compliance_percentage': round(compliance_score * 100, 1)
        }
    
    def _check_keyword_compliance(self, platform: str, content: str, config: Dict[str, Any], 
                                 primary_keywords: List[str], secondary_keywords: List[str]) -> Dict[str, Any]:
        """Check if content includes required keywords"""
        keywords_range = config.get('keywords_range', (1, 5))
        min_keywords, max_keywords = keywords_range
        
        # Only use primary keywords for compliance (as per prompt instructions)
        all_keywords = primary_keywords
        found_keywords = []
        
        for keyword in all_keywords:
            # Check for exact phrase match (case insensitive)
            if keyword.lower() in content.lower():
                found_keywords.append(keyword)
        
        keyword_count = len(found_keywords)
        
        # More lenient scoring - give partial credit for close compliance
        if min_keywords <= keyword_count <= max_keywords:
            compliance_score = 1.0
        elif keyword_count >= min_keywords * 0.8:  # 80% of minimum
            compliance_score = 0.8
        elif keyword_count > 0:
            compliance_score = 0.5
        else:
            compliance_score = 0.0
        
        return {
            'score': compliance_score,
            'required_range': f"{min_keywords}-{max_keywords} keywords",
            'actual_count': keyword_count,
            'found_keywords': found_keywords,
            'compliance_percentage': round(compliance_score * 100, 1)
        }
    
    def _check_hashtag_compliance(self, platform: str, content: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check if content includes required hashtags"""
        hashtags_range = config.get('hashtags_range', (1, 5))
        min_hashtags, max_hashtags = hashtags_range
        
        hashtags = re.findall(r'#\w+', content)
        hashtag_count = len(hashtags)
        
        # More lenient scoring - give partial credit for close compliance
        if min_hashtags <= hashtag_count <= max_hashtags:
            compliance_score = 1.0
        elif hashtag_count >= min_hashtags * 0.8:  # 80% of minimum
            compliance_score = 0.8
        elif hashtag_count > 0:
            compliance_score = 0.5
        else:
            compliance_score = 0.0
        
        return {
            'score': compliance_score,
            'required_range': f"{min_hashtags}-{max_hashtags} hashtags",
            'actual_count': hashtag_count,
            'found_hashtags': hashtags,
            'compliance_percentage': round(compliance_score * 100, 1)
        }
    
    def _check_structure_compliance(self, platform: str, content: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check if content follows platform-specific structure requirements"""
        structure_steps = config.get('structure_steps', (1, 5))
        min_steps, max_steps = structure_steps
        
        # Count structural elements more accurately
        # For social media platforms, count main sections/points, not every paragraph
        if platform in ['instagram', 'facebook', 'pinterest', 'tiktok']:
            # Count main content sections (numbered items, bullet points, or major breaks)
            numbered_items = len(re.findall(r'\d+\.\s', content))
            bullet_points = len(re.findall(r'[-*•]\s', content))
            major_sections = len(re.findall(r'\n\n', content)) + 1  # Paragraphs + 1
            
            # Use the most appropriate count for the platform
            if numbered_items > 0:
                total_structure_elements = numbered_items
            elif bullet_points > 0:
                total_structure_elements = bullet_points
            else:
                total_structure_elements = min(major_sections, 5)  # Cap at 5 for social media
        else:
            # For long-form content, count paragraphs and lists
            paragraphs = len([p for p in content.split('\n\n') if p.strip()])
            bullet_points = len(re.findall(r'^[\s]*[-*•]\s', content, re.MULTILINE))
            numbered_lists = len(re.findall(r'^[\s]*\d+\.\s', content, re.MULTILINE))
            
            total_structure_elements = paragraphs + bullet_points + numbered_lists
        
        # More lenient scoring
        if min_steps <= total_structure_elements <= max_steps:
            compliance_score = 1.0
        elif total_structure_elements >= min_steps * 0.8:  # 80% of minimum
            compliance_score = 0.8
        elif total_structure_elements > 0:
            compliance_score = 0.5
        else:
            compliance_score = 0.0
        
        return {
            'score': compliance_score,
            'required_range': f"{min_steps}-{max_steps} structural elements",
            'actual_count': total_structure_elements,
            'compliance_percentage': round(compliance_score * 100, 1)
        }
    
    def _check_tone_compliance(self, platform: str, content: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check if content follows platform-specific tone requirements"""
        tone = config.get('tone', '')
        
        # Define tone indicators
        tone_indicators = {
            'professional': ['professional', 'business', 'industry', 'expertise', 'experience', 'leadership'],
            'conversational': ['you', 'your', 'let\'s', 'what do you think', 'share your', 'tell me'],
            'educational': ['learn', 'understand', 'explain', 'guide', 'tutorial', 'step-by-step', 'how to'],
            'entertainment': ['fun', 'exciting', 'amazing', 'incredible', 'wow', 'check this out'],
            'inspirational': ['inspire', 'motivate', 'achieve', 'success', 'dream', 'believe', 'possible'],
            'technical': ['code', 'function', 'algorithm', 'API', 'database', 'system', 'implementation']
        }
        
        indicators = tone_indicators.get(tone, [])
        if not indicators:
            return {'score': 1.0, 'tone_required': tone, 'compliance_percentage': 100.0}
        
        tone_count = sum(1 for indicator in indicators if indicator.lower() in content.lower())
        compliance_score = min(tone_count / 3, 1.0)  # At least 3 tone indicators
        
        return {
            'score': compliance_score,
            'tone_required': tone,
            'tone_indicators_found': tone_count,
            'compliance_percentage': round(compliance_score * 100, 1)
        }
    
    def _check_cta_compliance(self, platform: str, content: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check if content includes required CTA type"""
        cta_type = config.get('cta_type', 'explicit')
        
        # Define CTA indicators
        cta_indicators = {
            'explicit': ['click here', 'sign up', 'download', 'buy now', 'get started', 'learn more', 'contact us'],
            'soft': ['check out', 'explore', 'discover', 'find out', 'see more', 'try it'],
            'discussion_invitation': ['what do you think', 'share your', 'tell me', 'comment below', 'let me know'],
            'open_ended_question': ['?', 'what', 'how', 'why', 'when', 'where', 'who']
        }
        
        indicators = cta_indicators.get(cta_type, [])
        if not indicators:
            return {'score': 1.0, 'cta_type_required': cta_type, 'compliance_percentage': 100.0}
        
        cta_found = any(indicator.lower() in content.lower() for indicator in indicators)
        compliance_score = 1.0 if cta_found else 0.0
        
        return {
            'score': compliance_score,
            'cta_type_required': cta_type,
            'cta_found': cta_found,
            'compliance_percentage': round(compliance_score * 100, 1)
        }
    
    def _check_special_rules_compliance(self, platform: str, content: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check if content follows platform-specific special rules"""
        special_rules = config.get('special_rules', [])
        
        compliance_scores = {}
        overall_score = 1.0
        
        for rule in special_rules:
            if rule == 'no_links':
                # Check for absence of links
                links = re.findall(r'https?://\S+', content)
                score = 1.0 if len(links) == 0 else 0.0
                compliance_scores['no_links'] = score
                
            elif rule == 'minimal_emojis':
                # Check for minimal emoji usage
                emojis = re.findall(r'[😀-🙏🌀-🗿]', content)
                score = 1.0 if len(emojis) <= 2 else 0.0
                compliance_scores['minimal_emojis'] = score
                
            elif rule == '280_chars_per_tweet':
                # Check tweet character limits
                tweets = self._extract_tweets(content)
                char_compliance = all(len(tweet) <= 280 for tweet in tweets)
                score = 1.0 if char_compliance else 0.0
                compliance_scores['280_chars_per_tweet'] = score
                
            elif rule == '1_emoji_max':
                # Check for maximum 1 emoji
                emojis = re.findall(r'[😀-🙏🌀-🗿]', content)
                score = 1.0 if len(emojis) <= 1 else 0.0
                compliance_scores['1_emoji_max'] = score
                
            elif rule == 'video_script':
                # Check for video script elements
                video_indicators = ['video', 'script', 'scene', 'action', 'dialogue']
                score = 1.0 if any(indicator in content.lower() for indicator in video_indicators) else 0.0
                compliance_scores['video_script'] = score
                
            elif rule == 'visual_content':
                # Check for visual content references
                visual_indicators = ['image', 'photo', 'visual', 'picture', 'graphic', 'slide']
                score = 1.0 if any(indicator in content.lower() for indicator in visual_indicators) else 0.0
                compliance_scores['visual_content'] = score
        
        if compliance_scores:
            overall_score = sum(compliance_scores.values()) / len(compliance_scores)
        
        return {
            'score': overall_score,
            'special_rules_required': special_rules,
            'rule_compliance': compliance_scores,
            'compliance_percentage': round(overall_score * 100, 1)
        }
    
    def _check_unique_features_compliance(self, platform: str, content: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check if content includes platform-specific unique features"""
        unique_features = config.get('unique_features', [])
        
        compliance_scores = {}
        overall_score = 1.0
        
        for feature in unique_features:
            if feature == 'thought_leadership':
                indicators = ['insight', 'perspective', 'analysis', 'expert', 'leader', 'vision']
                score = 1.0 if any(indicator in content.lower() for indicator in indicators) else 0.0
                compliance_scores['thought_leadership'] = score
                
            elif feature == 'contrarian_insights':
                indicators = ['contrarian', 'unpopular', 'different', 'against', 'challenge', 'disagree']
                score = 1.0 if any(indicator in content.lower() for indicator in indicators) else 0.0
                compliance_scores['contrarian_insights'] = score
                
            elif feature == 'thread_format':
                indicators = ['tweet', 'thread', '1/', '2/', '3/']
                score = 1.0 if any(indicator in content.lower() for indicator in indicators) else 0.0
                compliance_scores['thread_format'] = score
                
            elif feature == 'video_script_caption':
                indicators = ['video', 'script', 'caption', 'scene', 'action']
                score = 1.0 if any(indicator in content.lower() for indicator in indicators) else 0.0
                compliance_scores['video_script_caption'] = score
                
            elif feature == 'visual_content_caption':
                indicators = ['image', 'photo', 'visual', 'caption', 'picture']
                score = 1.0 if any(indicator in content.lower() for indicator in indicators) else 0.0
                compliance_scores['visual_content_caption'] = score
                
            elif feature == 'community_driven':
                indicators = ['community', 'discussion', 'share', 'engage', 'participate']
                score = 1.0 if any(indicator in content.lower() for indicator in indicators) else 0.0
                compliance_scores['community_driven'] = score
                
            elif feature == 'educational_content':
                indicators = ['learn', 'teach', 'education', 'tutorial', 'guide', 'explain']
                score = 1.0 if any(indicator in content.lower() for indicator in indicators) else 0.0
                compliance_scores['educational_content'] = score
                
            elif feature == 'technical_content':
                indicators = ['code', 'technical', 'programming', 'development', 'API', 'system']
                score = 1.0 if any(indicator in content.lower() for indicator in indicators) else 0.0
                compliance_scores['technical_content'] = score
        
        if compliance_scores:
            overall_score = sum(compliance_scores.values()) / len(compliance_scores)
        
        return {
            'score': overall_score,
            'unique_features_required': unique_features,
            'feature_compliance': compliance_scores,
            'compliance_percentage': round(overall_score * 100, 1)
        }
    
    def _calculate_overall_platform_score(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall platform-specific score"""
        scores = []
        
        for metric_name, metric_data in metrics.items():
            if isinstance(metric_data, dict) and 'score' in metric_data:
                scores.append(metric_data['score'])
        
        if scores:
            overall_score = sum(scores) / len(scores)
        else:
            overall_score = 0.0
        
        return {
            'score': overall_score,
            'compliance_percentage': round(overall_score * 100, 1),
            'total_metrics': len(scores),
            'passed_metrics': sum(1 for score in scores if score >= 0.7)
        }
    
    def _detect_voice_in_content(self, content: str) -> str:
        """Detect the voice used in content"""
        personal_indicators = ['I ', 'my ', 'me ', 'myself']
        corporate_indicators = ['we ', 'our ', 'us ', 'company']
        
        personal_count = sum(1 for indicator in personal_indicators if indicator.lower() in content.lower())
        corporate_count = sum(1 for indicator in corporate_indicators if indicator.lower() in content.lower())
        
        if personal_count > corporate_count:
            return 'Personal (I Ikram)'
        elif corporate_count > personal_count:
            return 'Corporate (We Barrana)'
        else:
            return 'Flexible'
    
    def _count_tweets(self, content: str) -> int:
        """Count number of tweets in Twitter content"""
        # Look for tweet indicators like "Tweet 1:", "1/", etc.
        tweet_indicators = re.findall(r'(?:Tweet \d+|^\d+/|^\d+\.)', content, re.MULTILINE)
        return len(tweet_indicators) if tweet_indicators else 1
    
    def _extract_tweets(self, content: str) -> List[str]:
        """Extract individual tweets from Twitter content"""
        # Split by tweet indicators
        tweets = re.split(r'(?:Tweet \d+|^\d+/|^\d+\.)', content, flags=re.MULTILINE)
        return [tweet.strip() for tweet in tweets if tweet.strip()]
    
    def _extract_caption_words(self, content: str) -> int:
        """Extract caption words from TikTok/Instagram content"""
        # Look for caption section
        caption_match = re.search(r'(?:caption|description):\s*(.+)', content, re.IGNORECASE)
        if caption_match:
            caption_text = caption_match.group(1)
            return len(caption_text.split())
        else:
            # If no caption section found, count all words
            return len(content.split())
    
    def get_platform_metrics_summary(self, platform: str) -> Dict[str, Any]:
        """Get a summary of platform-specific metrics for display"""
        config = self.get_platform_config(platform)
        if not config:
            return {}
        
        return {
            'platform': platform,
            'voice': config.get('voice_text', ''),
            'content_type': config.get('content_type', ''),
            'word_range': config.get('word_range', (0, 1000)),
            'keywords_range': config.get('keywords_range', (1, 5)),
            'hashtags_range': config.get('hashtags_range', (1, 5)),
            'tone': config.get('tone', ''),
            'cta_type': config.get('cta_type', ''),
            'special_rules': config.get('special_rules', []),
            'unique_features': config.get('unique_features', [])
        }
