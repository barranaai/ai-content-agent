import React from 'react';
import { Box, Typography, Chip, LinearProgress } from '@mui/material';

const PlatformSpecificMetrics = ({ platform, metrics }) => {
  if (!metrics || !platform) {
    return (
      <Box sx={{ textAlign: 'center', padding: 4, color: 'rgba(255, 255, 255, 0.5)' }}>
        <Typography variant="body2">
          Generate content to see platform-specific metrics
        </Typography>
      </Box>
    );
  }

  // Platform-specific metric categories
  const getPlatformMetrics = (platform, metrics) => {
    const platformMetrics = {
      // Voice-based metrics
      voice_compliance: {
        label: 'Voice Compliance',
        description: 'Matches platform voice requirements',
        icon: '🎭',
        category: 'Voice & Brand'
      },
      
      // Content format metrics
      word_count_compliance: {
        label: 'Word Count',
        description: 'Meets platform word count requirements',
        icon: '📝',
        category: 'Content Format'
      },
      
      // SEO metrics
      keyword_compliance: {
        label: 'Keyword Compliance',
        description: 'Includes required keywords',
        icon: '🔍',
        category: 'SEO'
      },
      
      hashtag_compliance: {
        label: 'Hashtag Compliance',
        description: 'Uses appropriate hashtags',
        icon: '#️⃣',
        category: 'SEO'
      },
      
      // Structure metrics
      structure_compliance: {
        label: 'Structure Compliance',
        description: 'Follows platform structure requirements',
        icon: '🏗️',
        category: 'Structure'
      },
      
      // Tone metrics
      tone_compliance: {
        label: 'Tone Compliance',
        description: 'Matches platform tone requirements',
        icon: '🎯',
        category: 'Tone & Style'
      },
      
      // CTA metrics
      cta_compliance: {
        label: 'CTA Compliance',
        description: 'Includes required call-to-action',
        icon: '📢',
        category: 'Engagement'
      },
      
      // Special rules metrics
      special_rules_compliance: {
        label: 'Special Rules',
        description: 'Follows platform-specific rules',
        icon: '⚡',
        category: 'Platform Rules'
      },
      
      // Unique features metrics
      unique_features_compliance: {
        label: 'Unique Features',
        description: 'Includes platform-specific features',
        icon: '✨',
        category: 'Platform Features'
      },
      
      // Overall platform score
      overall_platform_score: {
        label: 'Platform Score',
        description: 'Overall platform compliance',
        icon: '🏆',
        category: 'Overall'
      }
    };

    return platformMetrics;
  };

  const platformMetricsConfig = getPlatformMetrics(platform, metrics);
  
  // Group metrics by category
  const metricsByCategory = {};
  Object.entries(platformMetricsConfig).forEach(([key, config]) => {
    if (metrics[key]) {
      const category = config.category;
      if (!metricsByCategory[category]) {
        metricsByCategory[category] = [];
      }
      metricsByCategory[category].push({ key, config, value: metrics[key] });
    }
  });

  const getScoreColor = (score) => {
    if (score >= 0.8) return '#4CAF50'; // Green
    if (score >= 0.6) return '#FF9800'; // Orange
    return '#F44336'; // Red
  };

  const getScoreLabel = (score) => {
    if (score >= 0.8) return 'Excellent';
    if (score >= 0.6) return 'Good';
    if (score >= 0.4) return 'Fair';
    return 'Poor';
  };

  const formatMetricValue = (key, value) => {
    if (typeof value === 'object' && value !== null) {
      if (value.compliance_percentage !== undefined) {
        return `${value.compliance_percentage}%`;
      }
      if (value.score !== undefined) {
        return `${Math.round(value.score * 100)}%`;
      }
      if (value.actual_count !== undefined) {
        return `${value.actual_count}`;
      }
      return 'N/A';
    }
    
    if (typeof value === 'boolean') {
      return value ? '✅' : '❌';
    }
    
    if (typeof value === 'number') {
      if (value >= 1) {
        return `${Math.round(value * 100)}%`;
      }
      return `${Math.round(value * 100)}%`;
    }
    
    return String(value);
  };

  const getMetricScore = (value) => {
    if (typeof value === 'object' && value !== null) {
      if (value.score !== undefined) {
        return value.score;
      }
      if (value.compliance_percentage !== undefined) {
        return value.compliance_percentage / 100;
      }
      return 0;
    }
    
    if (typeof value === 'boolean') {
      return value ? 1 : 0;
    }
    
    if (typeof value === 'number') {
      return value;
    }
    
    return 0;
  };

  return (
    <Box>
      {/* Platform-specific metrics by category */}
      {Object.entries(metricsByCategory).map(([category, categoryMetrics]) => (
        <Box key={category} sx={{ marginBottom: 1.5 }}>
          <Typography 
            variant="subtitle2" 
            sx={{ 
              color: 'rgba(255, 255, 255, 0.8)',
              fontWeight: 'bold',
              marginBottom: 0.5,
              textTransform: 'uppercase',
              fontSize: '0.7rem',
              letterSpacing: '0.3px'
            }}
          >
            {category}
          </Typography>
          
          {categoryMetrics.map(({ key, config, value }) => {
            const score = getMetricScore(value);
            const scoreColor = getScoreColor(score);
            const scoreLabel = getScoreLabel(score);
            const formattedValue = formatMetricValue(key, value);
            
            return (
              <Box 
                key={key}
                sx={{ 
                  marginBottom: 1,
                  padding: 1.5,
                  borderRadius: 1.5,
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  transition: 'all 0.3s ease-in-out',
                  '&:hover': {
                    background: 'rgba(255, 255, 255, 0.08)',
                    border: '1px solid rgba(255, 255, 255, 0.2)'
                  }
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 0.5 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <Typography sx={{ fontSize: '1rem' }}>
                      {config.icon}
                    </Typography>
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        color: 'rgba(255, 255, 255, 0.9)',
                        fontWeight: 'medium',
                        fontSize: '0.85rem'
                      }}
                    >
                      {config.label}
                    </Typography>
                  </Box>
                  
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        color: scoreColor,
                        fontWeight: 'bold',
                        minWidth: '35px',
                        textAlign: 'right',
                        fontSize: '0.8rem'
                      }}
                    >
                      {formattedValue}
                    </Typography>
                    <Chip 
                      label={scoreLabel}
                      size="small"
                      sx={{
                        backgroundColor: `${scoreColor}20`,
                        color: scoreColor,
                        border: `1px solid ${scoreColor}40`,
                        fontSize: '0.65rem',
                        height: '18px'
                      }}
                    />
                  </Box>
                </Box>
                
                <Typography 
                  variant="caption" 
                  sx={{ 
                    color: 'rgba(255, 255, 255, 0.6)',
                    fontSize: '0.65rem'
                  }}
                >
                  {config.description}
                </Typography>
                
                {/* Progress bar for numeric scores */}
                {typeof score === 'number' && score >= 0 && score <= 1 && (
                  <LinearProgress 
                    variant="determinate" 
                    value={score * 100}
                    sx={{
                      marginTop: 0.5,
                      height: 3,
                      borderRadius: 1.5,
                      backgroundColor: 'rgba(255, 255, 255, 0.1)',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: scoreColor,
                        borderRadius: 1.5
                      }
                    }}
                  />
                )}
                
                {/* Additional details for complex metrics */}
                {typeof value === 'object' && value !== null && (
                  <Box sx={{ marginTop: 0.5 }}>
                    {value.voice_required && (
                      <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.5)', fontSize: '0.65rem' }}>
                        Required: {value.voice_required}
                      </Typography>
                    )}
                    {value.voice_detected && (
                      <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.5)', fontSize: '0.65rem', marginLeft: 1 }}>
                        Detected: {value.voice_detected}
                      </Typography>
                    )}
                    {value.required_range && (
                      <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.5)', fontSize: '0.65rem' }}>
                        Range: {value.required_range}
                      </Typography>
                    )}
                    {value.actual_count !== undefined && (
                      <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.5)', fontSize: '0.65rem', marginLeft: 1 }}>
                        Actual: {value.actual_count}
                      </Typography>
                    )}
                    {value.found_keywords && value.found_keywords.length > 0 && (
                      <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.5)', fontSize: '0.65rem' }}>
                        Keywords: {value.found_keywords.join(', ')}
                      </Typography>
                    )}
                    {value.found_hashtags && value.found_hashtags.length > 0 && (
                      <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.5)', fontSize: '0.65rem' }}>
                        Hashtags: {value.found_hashtags.join(', ')}
                      </Typography>
                    )}
                  </Box>
                )}
              </Box>
            );
          })}
        </Box>
      ))}
      
      {/* Overall Platform Score */}
      {metrics.overall_platform_score && (
        <Box
          sx={{
            marginTop: 2,
            padding: 2,
            borderRadius: 2,
            background: 'linear-gradient(45deg, rgba(76, 175, 80, 0.2), rgba(139, 195, 74, 0.2))',
            border: '1px solid rgba(76, 175, 80, 0.3)',
            textAlign: 'center'
          }}
        >
          <Typography 
            variant="subtitle1" 
            sx={{ 
              color: '#4CAF50',
              fontWeight: 'bold',
              marginBottom: 0.5,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 0.5,
              fontSize: '0.9rem'
            }}
          >
            🏆 Overall Platform Score
          </Typography>
          <Typography 
            variant="h5" 
            sx={{ 
              color: 'white',
              fontWeight: 'bold',
              marginBottom: 0.5,
              fontSize: '1.5rem'
            }}
          >
            {metrics.overall_platform_score.compliance_percentage || 0}%
          </Typography>
          <Typography 
            variant="body2" 
            sx={{ 
              color: 'rgba(255, 255, 255, 0.7)',
              fontSize: '0.75rem'
            }}
          >
            {metrics.overall_platform_score.passed_metrics || 0} of {metrics.overall_platform_score.total_metrics || 0} metrics passed
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default PlatformSpecificMetrics;
