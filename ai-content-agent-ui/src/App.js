import React, { useState, useEffect } from "react";
import {
  Checkbox,
  FormControlLabel,
  Button,
  Typography,
  Box,
  Select,
  MenuItem,
  Tabs,
  Tab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  IconButton,
} from "@mui/material";
import CloseIcon from '@mui/icons-material/Close';
import PlatformSpecificMetrics from './PlatformSpecificMetrics';

export default function App() {
  const [availableTopics, setAvailableTopics] = useState([]);
  const [platformPrompts, setPlatformPrompts] = useState({});
  const [availablePlatforms, setAvailablePlatforms] = useState([]);
  const [selectedPlatforms, setSelectedPlatforms] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState("");
  const [generatedContent, setGeneratedContent] = useState({});
  const [description, setDescription] = useState(""); // The description text for selected topic
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationProgress, setGenerationProgress] = useState({
    currentPlatform: "",
    completedPlatforms: 0,
    totalPlatforms: 0,
    estimatedTimeRemaining: 0,
    status: ""
  });
  const [activeTab, setActiveTab] = useState(0);
  const [qualityMetrics, setQualityMetrics] = useState({});
  const [descriptionPopupOpen, setDescriptionPopupOpen] = useState(false);
  const [editableDescription, setEditableDescription] = useState("");
  const [selectedTopicName, setSelectedTopicName] = useState("");

  // API base URL for production
  const API_BASE_URL = 'http://191.101.233.56/ai-content-agent';

  // Fetch topics, platforms, and platform prompts when component mounts
  useEffect(() => {
    fetch(`${API_BASE_URL}/api/topics`)
      .then((res) => res.json())
      .then((data) => {
        setAvailableTopics(data);
      })
      .catch((error) => {
        console.error("Error fetching topics:", error);
      });

    fetch(`${API_BASE_URL}/api/platforms`)
      .then((res) => res.json())
      .then((data) => {
        setAvailablePlatforms(data);
      })
      .catch((error) => {
        console.error("Error fetching platforms:", error);
      });

    fetch(`${API_BASE_URL}/api/platform-prompts`)
      .then((res) => res.json())
      .then((data) => {
        setPlatformPrompts(data);
      })
      .catch((error) => {
        console.error("Error fetching platform prompts:", error);
      });
  }, []);

  // Update selected topic and its description
  const handleTopicChange = (e) => {
    const topic = e.target.value;
    setSelectedTopic(topic);
    const topicObj = availableTopics.find((t) => t.topic === topic);
    if (topicObj) {
      setSelectedTopicName(topicObj.topic);
      setEditableDescription(topicObj.description);
      setDescriptionPopupOpen(true);
    } else {
      setDescription("");
    }
  };

  const handlePlatformChange = (platform) => {
    setSelectedPlatforms((prev) =>
      prev.includes(platform)
        ? prev.filter((p) => p !== platform)
        : [...prev, platform]
    );
  };

  const handleDescriptionConfirm = () => {
    setDescription(editableDescription);
    setDescriptionPopupOpen(false);
  };

  const handleDescriptionCancel = () => {
    setDescriptionPopupOpen(false);
    setSelectedTopic(""); // Reset topic selection
  };

  // Call backend to generate content for selected topic and platforms
  const handleGenerate = async () => {
    if (!selectedTopic || !description || selectedPlatforms.length === 0) return;

    setIsGenerating(true);
    setGeneratedContent({});
    
    // Initialize progress
    setGenerationProgress({
      currentPlatform: "",
      completedPlatforms: 0,
      totalPlatforms: selectedPlatforms.length,
      estimatedTimeRemaining: selectedPlatforms.length * 8, // 8 seconds per platform
      status: "Initializing content generation..."
    });

    const body = {
      topic: selectedTopic,
      description,
      platforms: selectedPlatforms,
      prompts: platformPrompts,
    };

    try {
      // Simulate realistic progress updates
      const progressInterval = setInterval(() => {
        setGenerationProgress(prev => {
          const newCompleted = Math.min(prev.completedPlatforms + 0.15, prev.totalPlatforms);
          const remaining = Math.max(0, (prev.totalPlatforms - newCompleted) * 6);
          const currentPlatformIndex = Math.floor(newCompleted);
          const currentPlatform = selectedPlatforms[currentPlatformIndex] || "Finalizing...";
          
          let status = "Initializing AI models...";
          if (newCompleted >= prev.totalPlatforms * 0.9) {
            status = "Finalizing and optimizing content...";
          } else if (newCompleted >= prev.totalPlatforms * 0.7) {
            status = "Applying quality validation...";
          } else if (newCompleted >= prev.totalPlatforms * 0.5) {
            status = "Generating SEO-optimized content...";
          } else if (newCompleted > 0) {
            status = `Creating ${currentPlatform} content...`;
          }

          return {
            ...prev,
            completedPlatforms: newCompleted,
            currentPlatform: currentPlatform,
            estimatedTimeRemaining: remaining,
            status: status
          };
        });
      }, 600);

      const response = await fetch(`${API_BASE_URL}/api/generate-content`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      const data = await response.json();
      
      clearInterval(progressInterval);
      
      // Final progress update
      setGenerationProgress(prev => ({
        ...prev,
        completedPlatforms: prev.totalPlatforms,
        currentPlatform: "Complete!",
        estimatedTimeRemaining: 0,
        status: "Content generation completed successfully!"
      }));

      // Small delay to show completion
      setTimeout(() => {
        setGeneratedContent(data.content || data);
        
        // Set quality metrics if available
        if (data.metrics) {
          setQualityMetrics(data.metrics);
        }
        
        setIsGenerating(false);
      }, 1000);

    } catch (err) {
      setIsGenerating(false);
      alert("Error generating content: " + err.message);
    }
  };

  // Regenerate content for a specific platform
  const handleRegenerate = async (platform) => {
    if (!selectedTopic || !description) return;

    setIsGenerating(true);
    setGenerationProgress({
      currentPlatform: platform,
      completedPlatforms: 0,
      totalPlatforms: 1,
      estimatedTimeRemaining: 6,
      status: "Regenerating content..."
    });

    const body = {
      topic: selectedTopic,
      description,
      platforms: [platform], // Only regenerate for the specific platform
      prompts: platformPrompts,
    };

    try {
      const response = await fetch(`${API_BASE_URL}/api/generate-content`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Update the generated content for this specific platform
      setGeneratedContent(prev => ({
        ...prev,
        [platform]: data.content[platform] || data[platform]
      }));

      // Update quality metrics if available
      if (data.metrics) {
        setQualityMetrics(prev => ({
          ...prev,
          [platform]: data.metrics[platform] || data.metrics
        }));
      }

      setIsGenerating(false);
      setGenerationProgress({
        currentPlatform: "",
        completedPlatforms: 0,
        totalPlatforms: 0,
        estimatedTimeRemaining: 0,
        status: ""
      });

    } catch (err) {
      setIsGenerating(false);
      alert("Error regenerating content: " + err.message);
    }
  };

  // Save content for a specific platform
  const handleSave = (platform) => {
    const content = generatedContent[platform];
    if (!content) return;

    // Create a blob with the content
    const blob = new Blob([content], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    
    // Create a temporary link element and trigger download
    const link = document.createElement('a');
    link.href = url;
    link.download = `${platform}_content_${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  };

  return (
    <Box 
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        padding: 4,
        position: 'relative',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'radial-gradient(circle at 20% 50%, rgba(120, 119, 198, 0.3) 0%, transparent 50%), radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%), radial-gradient(circle at 40% 80%, rgba(120, 219, 255, 0.3) 0%, transparent 50%)',
          pointerEvents: 'none'
        }
      }}
    >
      <Box maxWidth={1800} margin="auto" position="relative" zIndex={1}>
        {/* Main Header Card */}
        <Box
          sx={{
            background: 'rgba(255, 255, 255, 0.1)',
            backdropFilter: 'blur(20px)',
            borderRadius: 3,
            padding: 4,
            marginBottom: 3,
            border: '1px solid rgba(255, 255, 255, 0.2)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
            textAlign: 'center'
          }}
        >
          <Typography 
            variant="h3" 
            gutterBottom
            sx={{
              background: 'linear-gradient(45deg, #fff, #e3f2fd)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              fontWeight: 'bold',
              textShadow: '0 2px 4px rgba(0,0,0,0.1)'
            }}
          >
            ✨ AI Content Agent
          </Typography>
          <Typography 
            variant="h6" 
            sx={{ 
              color: 'rgba(255, 255, 255, 0.8)',
              fontWeight: 300
            }}
          >
            Generate professional content for 21+ platforms with AI-powered optimization
          </Typography>
        </Box>

        {/* Three Column Layout */}
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: '0.8fr 1.4fr 0.5fr',
            gap: 4,
            marginTop: 3
          }}
        >
          {/* Left Column - Controls */}
          <Box>
            {/* Topic Selection Card */}
        <Box
          sx={{
            background: 'rgba(255, 255, 255, 0.1)',
            backdropFilter: 'blur(20px)',
            borderRadius: 3,
            padding: 3,
            marginBottom: 3,
            border: '1px solid rgba(255, 255, 255, 0.2)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
            transition: 'transform 0.2s ease-in-out',
            '&:hover': {
              transform: 'translateY(-2px)',
              boxShadow: '0 12px 40px rgba(0, 0, 0, 0.15)'
            }
          }}
        >
          <Typography 
            variant="h6" 
            gutterBottom
            sx={{ 
              color: 'white',
              fontWeight: 'bold',
              marginBottom: 2,
              display: 'flex',
              alignItems: 'center',
              gap: 1
            }}
          >
            📝 Select Topic
          </Typography>
          <Select
            value={selectedTopic}
            onChange={handleTopicChange}
            fullWidth
            sx={{
              backgroundColor: 'rgba(255, 255, 255, 0.1)',
              borderRadius: 2,
              '& .MuiOutlinedInput-notchedOutline': {
                borderColor: 'rgba(255, 255, 255, 0.3)',
              },
              '&:hover .MuiOutlinedInput-notchedOutline': {
                borderColor: 'rgba(255, 255, 255, 0.5)',
              },
              '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
                borderColor: 'rgba(255, 255, 255, 0.8)',
              },
              '& .MuiSelect-select': {
                color: 'white',
                padding: '12px 14px'
              },
              '& .MuiSvgIcon-root': {
                color: 'white'
              }
            }}
          >
            {availableTopics.length === 0 ? (
              <MenuItem disabled sx={{ color: 'rgba(255, 255, 255, 0.6)' }}>
                Loading topics...
              </MenuItem>
            ) : (
              availableTopics.map((t) => (
                <MenuItem 
                  key={t.topic} 
                  value={t.topic}
                  sx={{ 
                    color: '#333',
                    '&:hover': {
                      backgroundColor: 'rgba(102, 126, 234, 0.1)'
                    }
                  }}
                >
                  {t.topic}
                </MenuItem>
              ))
            )}
          </Select>
            </Box>

            {/* Platform Selection Card */}
        <Box
          sx={{
            background: 'rgba(255, 255, 255, 0.1)',
            backdropFilter: 'blur(20px)',
            borderRadius: 3,
            padding: 3,
            marginBottom: 3,
            border: '1px solid rgba(255, 255, 255, 0.2)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
            transition: 'transform 0.2s ease-in-out',
            '&:hover': {
              transform: 'translateY(-2px)',
              boxShadow: '0 12px 40px rgba(0, 0, 0, 0.15)'
            }
          }}
        >
          <Typography 
            variant="h6" 
            gutterBottom
            sx={{ 
              color: 'white',
              fontWeight: 'bold',
              marginBottom: 2,
              display: 'flex',
              alignItems: 'center',
              gap: 1
            }}
          >
            🚀 Select Platforms
          </Typography>
          
          {availablePlatforms.length === 0 ? (
            <Typography sx={{ color: 'rgba(255, 255, 255, 0.6)' }}>
              Loading platforms...
            </Typography>
          ) : (
            <Box
              sx={{
                display: 'grid',
                gridTemplateColumns: 'repeat(3, 1fr)',
                gap: 1.5
              }}
            >
              {availablePlatforms.map((platform) => {

                return (
                  <Box
                    key={platform.key}
                    sx={{
                      background: 'rgba(255, 255, 255, 0.05)',
                      borderRadius: 2,
                      padding: 1.5,
                      border: '1px solid rgba(255, 255, 255, 0.1)',
                      transition: 'all 0.2s ease-in-out',
                      position: 'relative',
                      '&:hover': {
                        background: 'rgba(255, 255, 255, 0.1)',
                        transform: 'translateY(-1px)'
                      }
                    }}
                  >
                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={selectedPlatforms.includes(platform.key)}
                        onChange={() => handlePlatformChange(platform.key)}
                        size="small"
                        sx={{
                          color: 'rgba(255, 255, 255, 0.7)',
                          padding: '4px',
                          '&.Mui-checked': {
                            color: '#4ECDC4'
                          }
                        }}
                      />
                    }
                    label={
                      <Box>
                        <Typography 
                          variant="body2" 
                          sx={{ 
                            color: 'white',
                            fontWeight: 'bold',
                            fontSize: '0.9rem',
                            lineHeight: 1.2
                          }}
                        >
                          {platform.name}
                        </Typography>
                        <Typography 
                          variant="body2" 
                          sx={{ 
                            color: 'rgba(255, 255, 255, 0.7)',
                            fontSize: '0.75rem',
                            lineHeight: 1.2
                          }}
                        >
                          {platform.word_count.min}-{platform.word_count.max} words
                        </Typography>
                      </Box>
                    }
                    sx={{ 
                      margin: 0,
                      width: '100%',
                      '& .MuiFormControlLabel-label': {
                        width: '100%'
                      }
                    }}
                  />
                  </Box>
                );
              })}
            </Box>
          )}
            </Box>

            {/* Generate Button Card */}
        <Box
          sx={{
            background: 'rgba(255, 255, 255, 0.1)',
            backdropFilter: 'blur(20px)',
            borderRadius: 3,
            padding: 3,
            marginBottom: 3,
            border: '1px solid rgba(255, 255, 255, 0.2)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
            textAlign: 'center'
          }}
        >
          <Button
            variant="contained"
            onClick={handleGenerate}
            disabled={
              !selectedTopic || !description || selectedPlatforms.length === 0 || isGenerating
            }
            sx={{
              background: 'linear-gradient(45deg, #4ECDC4 30%, #44A08D 90%)',
              boxShadow: '0 8px 32px rgba(78, 205, 196, 0.3)',
              borderRadius: 3,
              padding: '12px 32px',
              fontSize: '1.1rem',
              fontWeight: 'bold',
              textTransform: 'none',
              minWidth: 200,
              '&:hover': {
                background: 'linear-gradient(45deg, #44A08D 30%, #4ECDC4 90%)',
                transform: 'translateY(-2px)',
                boxShadow: '0 12px 40px rgba(78, 205, 196, 0.4)',
              },
              '&:disabled': {
                background: 'rgba(255, 255, 255, 0.1)',
                color: 'rgba(255, 255, 255, 0.3)',
                boxShadow: 'none'
              }
            }}
          >
            {isGenerating ? "🔄 Generating..." : "✨ Generate Content"}
          </Button>
          
          {selectedPlatforms.length > 0 && (
            <Typography 
              variant="body2" 
              sx={{ 
                color: 'rgba(255, 255, 255, 0.7)',
                marginTop: 2
              }}
            >
              Ready to generate content for {selectedPlatforms.length} platform{selectedPlatforms.length > 1 ? 's' : ''}
            </Typography>
          )}
            </Box>
          </Box>

          {/* Right Column - Generated Content */}
          <Box>
            {/* Beautiful Progress Loader */}
        {isGenerating && (
          <Box 
            sx={{
              background: 'rgba(255, 255, 255, 0.15)',
              backdropFilter: 'blur(25px)',
              borderRadius: 3,
              padding: 4,
              marginBottom: 3,
              color: 'white',
              boxShadow: '0 12px 40px rgba(0,0,0,0.2)',
              border: '1px solid rgba(255,255,255,0.3)',
              position: 'relative',
              overflow: 'hidden',
              '&::before': {
                content: '""',
                position: 'absolute',
                top: 0,
                left: '-100%',
                width: '100%',
                height: '100%',
                background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent)',
                animation: 'shimmer 3s infinite',
                '@keyframes shimmer': {
                  '0%': { left: '-100%' },
                  '100%': { left: '100%' }
                }
              }
            }}
          >
          <Box display="flex" alignItems="center" marginBottom={2}>
            <Box
              sx={{
                width: 40,
                height: 40,
                borderRadius: '50%',
                background: 'linear-gradient(45deg, #FF6B6B, #4ECDC4)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginRight: 2,
                animation: 'spin 2s linear infinite',
                '@keyframes spin': {
                  '0%': { transform: 'rotate(0deg)' },
                  '100%': { transform: 'rotate(360deg)' }
                }
              }}
            >
              <Typography variant="h6" sx={{ color: 'white', fontWeight: 'bold' }}>
                AI
              </Typography>
            </Box>
            <Box>
              <Typography variant="h6" sx={{ fontWeight: 'bold', marginBottom: 0.5 }}>
                {generationProgress.status}
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>
                {generationProgress.currentPlatform && `Working on: ${generationProgress.currentPlatform}`}
              </Typography>
            </Box>
          </Box>

          {/* Progress Bar */}
          <Box marginBottom={2}>
            <Box
              sx={{
                width: '100%',
                height: 8,
                backgroundColor: 'rgba(255,255,255,0.2)',
                borderRadius: 4,
                overflow: 'hidden'
              }}
            >
              <Box
                sx={{
                  width: `${(generationProgress.completedPlatforms / generationProgress.totalPlatforms) * 100}%`,
                  height: '100%',
                  background: 'linear-gradient(90deg, #FF6B6B, #4ECDC4, #45B7D1)',
                  borderRadius: 4,
                  transition: 'width 0.3s ease-in-out',
                  position: 'relative',
                  '&::after': {
                    content: '""',
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent)',
                    animation: 'shimmer 2s infinite',
                    '@keyframes shimmer': {
                      '0%': { transform: 'translateX(-100%)' },
                      '100%': { transform: 'translateX(100%)' }
                    }
                  }
                }}
              />
            </Box>
          </Box>

          {/* Progress Stats */}
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Box>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>
                Progress: {Math.round((generationProgress.completedPlatforms / generationProgress.totalPlatforms) * 100)}%
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>
                {generationProgress.completedPlatforms.toFixed(1)} / {generationProgress.totalPlatforms} platforms
              </Typography>
            </Box>
            <Box textAlign="right">
              <Typography variant="body2" sx={{ opacity: 0.9 }}>
                {generationProgress.estimatedTimeRemaining > 0 
                  ? `~${Math.round(generationProgress.estimatedTimeRemaining)}s remaining`
                  : 'Almost done!'
                }
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>
                ✨ AI-powered content generation
              </Typography>
            </Box>
          </Box>

          {/* Animated Dots */}
          <Box display="flex" justifyContent="center" marginTop={2}>
            <Box
              sx={{
                display: 'flex',
                gap: 1,
                '& > div': {
                  width: 8,
                  height: 8,
                  borderRadius: '50%',
                  backgroundColor: 'rgba(255,255,255,0.6)',
                  animation: 'pulse 1.5s ease-in-out infinite',
                  '&:nth-of-type(1)': { animationDelay: '0s' },
                  '&:nth-of-type(2)': { animationDelay: '0.2s' },
                  '&:nth-of-type(3)': { animationDelay: '0.4s' },
                  '@keyframes pulse': {
                    '0%, 100%': { opacity: 0.3, transform: 'scale(1)' },
                    '50%': { opacity: 1, transform: 'scale(1.2)' }
                  }
                }
              }}
            >
              <div></div>
              <div></div>
              <div></div>
            </Box>
          </Box>
        </Box>
      )}

            {/* Generated Content Results */}
            {Object.keys(generatedContent).length > 0 && (
              <Box 
                sx={{
                  animation: 'fadeInUp 0.6s ease-out',
                  '@keyframes fadeInUp': {
                    '0%': { opacity: 0, transform: 'translateY(20px)' },
                    '100%': { opacity: 1, transform: 'translateY(0)' }
                  }
                }}
              >
                <Box
                  sx={{
                    background: 'rgba(255, 255, 255, 0.1)',
                    backdropFilter: 'blur(20px)',
                    borderRadius: 3,
                    padding: 3,
                    marginBottom: 3,
                    border: '1px solid rgba(255, 255, 255, 0.2)',
                    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
                    textAlign: 'center'
                  }}
                >
                  <Typography variant="h5" gutterBottom sx={{ 
                    background: 'linear-gradient(45deg, #fff, #e3f2fd)',
                    backgroundClip: 'text',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                    fontWeight: 'bold'
                  }}>
                    ✨ Generated Content
                  </Typography>
                  <Typography 
                    variant="body2" 
                    sx={{ 
                      color: 'rgba(255, 255, 255, 0.7)'
                    }}
                  >
                    AI-powered content optimized for each platform
                  </Typography>
                </Box>

                {/* Tabs for Multiple Platforms */}
                {Object.keys(generatedContent).length > 1 ? (
                  <Box
                    sx={{
                      background: 'rgba(255, 255, 255, 0.1)',
                      backdropFilter: 'blur(20px)',
                      borderRadius: 3,
                      border: '1px solid rgba(255, 255, 255, 0.2)',
                      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
                      overflow: 'hidden'
                    }}
                  >
                    <Box
                      sx={{
                        overflowX: 'auto',
                        overflowY: 'hidden',
                        '&::-webkit-scrollbar': {
                          height: '6px',
                        },
                        '&::-webkit-scrollbar-track': {
                          background: 'rgba(255, 255, 255, 0.1)',
                          borderRadius: '3px',
                        },
                        '&::-webkit-scrollbar-thumb': {
                          background: 'rgba(255, 255, 255, 0.3)',
                          borderRadius: '3px',
                          '&:hover': {
                            background: 'rgba(255, 255, 255, 0.5)',
                          },
                        },
                      }}
                    >
                      <Tabs
                        value={activeTab}
                        onChange={(e, newValue) => setActiveTab(newValue)}
                        variant="scrollable"
                        scrollButtons="auto"
                        sx={{
                          minHeight: '48px',
                          '& .MuiTab-root': {
                            color: 'rgba(255, 255, 255, 0.7)',
                            minWidth: '120px',
                            fontSize: '0.85rem',
                            fontWeight: 'medium',
                            textTransform: 'none',
                            padding: '8px 12px',
                            '&.Mui-selected': {
                              color: 'white',
                              fontWeight: 'bold'
                            },
                            '&:hover': {
                              color: 'rgba(255, 255, 255, 0.9)',
                            }
                          },
                          '& .MuiTabs-indicator': {
                            backgroundColor: '#4ECDC4',
                            height: '3px',
                            borderRadius: '2px'
                          },
                          '& .MuiTabs-scrollButtons': {
                            color: 'rgba(255, 255, 255, 0.7)',
                            '&.Mui-disabled': {
                              opacity: 0.3
                            }
                          }
                        }}
                      >
                        {Object.keys(generatedContent).map((platform, index) => (
                          <Tab 
                            key={platform}
                            label={platform.charAt(0).toUpperCase() + platform.slice(1).replace('_', ' ')}
                          />
                        ))}
                      </Tabs>
                    </Box>
                    
                    {Object.entries(generatedContent).map(([platform, content], index) => (
                      <Box
                        key={platform}
                        sx={{
                          display: activeTab === index ? 'block' : 'none',
                          padding: 3
                        }}
                      >
                        <Typography 
                          style={{ 
                            whiteSpace: "pre-wrap",
                            lineHeight: 1.6,
                            color: 'white'
                          }}
                          sx={{
                            backgroundColor: 'rgba(255, 255, 255, 0.1)',
                            padding: 3,
                            borderRadius: 2,
                            border: '1px solid rgba(255, 255, 255, 0.2)',
                            backdropFilter: 'blur(10px)',
                            marginBottom: 3
                          }}
                        >
                          {content}
                        </Typography>
                        
                        <Box display="flex" gap={2} justifyContent="center">
                          <Button
                            size="medium"
                            variant="outlined"
                            onClick={() => handleRegenerate(platform)}
                            sx={{
                              borderColor: 'rgba(255, 255, 255, 0.5)',
                              color: 'white',
                              borderRadius: 2,
                              padding: '8px 16px',
                              '&:hover': {
                                borderColor: 'rgba(255, 255, 255, 0.8)',
                                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                                transform: 'translateY(-1px)'
                              }
                            }}
                          >
                            🔄 Regenerate
                          </Button>
                          <Button 
                            size="medium" 
                            variant="contained"
                            onClick={() => handleSave(platform)}
                            sx={{
                              background: 'linear-gradient(45deg, #4ECDC4 30%, #44A08D 90%)',
                              borderRadius: 2,
                              padding: '8px 16px',
                              '&:hover': {
                                background: 'linear-gradient(45deg, #44A08D 30%, #4ECDC4 90%)',
                                transform: 'translateY(-1px)',
                                boxShadow: '0 6px 20px rgba(78, 205, 196, 0.4)'
                              }
                            }}
                          >
                            💾 Save
                          </Button>
                        </Box>
                      </Box>
                    ))}
                  </Box>
                ) : (
                  /* Single Platform - No Tabs */
                  Object.entries(generatedContent).map(([platform, content], index) => (
                    <Box
                      key={platform}
                      sx={{
                        background: 'rgba(255, 255, 255, 0.1)',
                        backdropFilter: 'blur(20px)',
                        borderRadius: 3,
                        padding: 3,
                        border: '1px solid rgba(255, 255, 255, 0.2)',
                        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
                        transition: 'all 0.3s ease-in-out',
                        '&:hover': {
                          transform: 'translateY(-4px)',
                          boxShadow: '0 12px 40px rgba(0, 0, 0, 0.2)',
                          background: 'rgba(255, 255, 255, 0.15)'
                        },
                        animation: `fadeInUp 0.6s ease-out ${index * 0.1}s both`
                      }}
                    >
                      <Box display="flex" alignItems="center" marginBottom={2}>
                        <Box
                          sx={{
                            width: 32,
                            height: 32,
                            borderRadius: '50%',
                            background: 'linear-gradient(45deg, #FF6B6B, #4ECDC4)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            marginRight: 2
                          }}
                        >
                          <Typography variant="body2" sx={{ color: 'white', fontWeight: 'bold' }}>
                            {platform.charAt(0).toUpperCase()}
                          </Typography>
                        </Box>
                        <Typography variant="h6" sx={{ fontWeight: 'bold', color: 'white' }}>
                          {platform.charAt(0).toUpperCase() + platform.slice(1).replace('_', ' ')}
                        </Typography>
                      </Box>
                      
                      <Typography 
                        style={{ 
                          whiteSpace: "pre-wrap",
                          lineHeight: 1.6,
                          color: 'white'
                        }}
                        sx={{
                          backgroundColor: 'rgba(255, 255, 255, 0.1)',
                          padding: 3,
                          borderRadius: 2,
                          border: '1px solid rgba(255, 255, 255, 0.2)',
                          backdropFilter: 'blur(10px)',
                          marginBottom: 3
                        }}
                      >
                        {content}
                      </Typography>
                      
                      <Box display="flex" gap={2} justifyContent="center">
                        <Button
                          size="medium"
                          variant="outlined"
                          onClick={() => handleRegenerate(platform)}
                          sx={{
                            borderColor: 'rgba(255, 255, 255, 0.5)',
                            color: 'white',
                            borderRadius: 2,
                            padding: '8px 16px',
                            '&:hover': {
                              borderColor: 'rgba(255, 255, 255, 0.8)',
                              backgroundColor: 'rgba(255, 255, 255, 0.1)',
                              transform: 'translateY(-1px)'
                            }
                          }}
                        >
                          🔄 Regenerate
                        </Button>
                        <Button 
                          size="medium" 
                          variant="contained"
                          onClick={() => handleSave(platform)}
                          sx={{
                            background: 'linear-gradient(45deg, #4ECDC4 30%, #44A08D 90%)',
                            borderRadius: 2,
                            padding: '8px 16px',
                            '&:hover': {
                              background: 'linear-gradient(45deg, #44A08D 30%, #4ECDC4 90%)',
                              transform: 'translateY(-1px)',
                              boxShadow: '0 6px 20px rgba(78, 205, 196, 0.4)'
                            }
                          }}
                        >
                          💾 Save
                        </Button>
                      </Box>
                    </Box>
                  ))
                )}
              </Box>
            )}
          </Box>

          {/* Third Column - Quality Metrics */}
          <Box>
            {/* Quality Metrics Card */}
            <Box
              sx={{
                background: 'rgba(255, 255, 255, 0.1)',
                backdropFilter: 'blur(20px)',
                borderRadius: 3,
                padding: 3,
                border: '1px solid rgba(255, 255, 255, 0.2)',
                boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
                transition: 'all 0.3s ease-in-out',
                '&:hover': {
                  transform: 'translateY(-2px)',
                  boxShadow: '0 12px 40px rgba(0, 0, 0, 0.15)',
                  background: 'rgba(255, 255, 255, 0.15)'
                }
              }}
            >
              <Typography variant="h6" gutterBottom sx={{ 
                background: 'linear-gradient(45deg, #fff, #e3f2fd)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                fontWeight: 'bold',
                display: 'flex',
                alignItems: 'center',
                gap: 1
              }}>
                📊 Quality Metrics
              </Typography>
              
              <Typography 
                variant="body2" 
                sx={{ 
                  color: 'rgba(255, 255, 255, 0.7)',
                  marginBottom: 3
                }}
              >
                Real-time content quality analysis
              </Typography>

              {/* Platform-Specific Metrics Display */}
              {(() => {
                // Get the active platform based on the active tab
                const platforms = Object.keys(generatedContent);
                const activePlatform = platforms[activeTab] || platforms[0]; // Fallback to first platform if no active tab
                const metrics = qualityMetrics[activePlatform];
                
                return (
                  <PlatformSpecificMetrics 
                    platform={activePlatform} 
                    metrics={metrics} 
                  />
                );
              })()}

            </Box>
          </Box>
        </Box>
      </Box>

      {/* Description Edit Popup */}
      <Dialog
        open={descriptionPopupOpen}
        onClose={handleDescriptionCancel}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            background: 'rgba(255, 255, 255, 0.1)',
            backdropFilter: 'blur(20px)',
            borderRadius: 3,
            border: '1px solid rgba(255, 255, 255, 0.2)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
          }
        }}
      >
        <DialogTitle
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            color: 'white',
            background: 'linear-gradient(45deg, #667eea 0%, #764ba2 100%)',
            borderRadius: '12px 12px 0 0',
            padding: 2
          }}
        >
          <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
            📝 Edit Topic Description
          </Typography>
          <IconButton
            onClick={handleDescriptionCancel}
            sx={{ color: 'white' }}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        
        <DialogContent sx={{ padding: 3, backgroundColor: 'rgba(255, 255, 255, 0.05)' }}>
          <Box sx={{ marginBottom: 2 }}>
            <Typography 
              variant="h6" 
              sx={{ 
                color: 'white', 
                fontWeight: 'bold',
                marginBottom: 1
              }}
            >
              Selected Topic: {selectedTopicName}
            </Typography>
            <Typography 
              variant="body2" 
              sx={{ 
                color: 'rgba(255, 255, 255, 0.7)',
                marginBottom: 2
              }}
            >
              Review and edit the description below before generating content. This description will be used as the main context for AI content generation.
            </Typography>
          </Box>
          
          <TextField
            multiline
            rows={12}
            fullWidth
            value={editableDescription}
            onChange={(e) => setEditableDescription(e.target.value)}
            variant="outlined"
            placeholder="Enter your topic description here..."
            sx={{
              '& .MuiOutlinedInput-root': {
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                borderRadius: 2,
                '& fieldset': {
                  borderColor: 'rgba(255, 255, 255, 0.3)',
                },
                '&:hover fieldset': {
                  borderColor: 'rgba(255, 255, 255, 0.5)',
                },
                '&.Mui-focused fieldset': {
                  borderColor: '#4ECDC4',
                },
              },
              '& .MuiInputBase-input': {
                color: 'white',
                fontSize: '0.95rem',
                lineHeight: 1.6,
              },
              '& .MuiInputBase-input::placeholder': {
                color: 'rgba(255, 255, 255, 0.5)',
                opacity: 1,
              },
            }}
          />
          
          <Box sx={{ marginTop: 2, padding: 2, backgroundColor: 'rgba(78, 205, 196, 0.1)', borderRadius: 2, border: '1px solid rgba(78, 205, 196, 0.3)' }}>
            <Typography variant="body2" sx={{ color: '#4ECDC4', fontWeight: 'bold', marginBottom: 1 }}>
              💡 Tips for better content generation:
            </Typography>
            <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)', fontSize: '0.85rem' }}>
              • Be specific about your target audience<br/>
              • Include key benefits or value propositions<br/>
              • Mention any unique features or approaches<br/>
              • Keep it clear and concise for better AI understanding
            </Typography>
          </Box>
        </DialogContent>
        
        <DialogActions sx={{ padding: 3, backgroundColor: 'rgba(255, 255, 255, 0.05)' }}>
          <Button
            onClick={handleDescriptionCancel}
            variant="outlined"
            sx={{
              borderColor: 'rgba(255, 255, 255, 0.5)',
              color: 'white',
              borderRadius: 2,
              padding: '8px 24px',
              '&:hover': {
                borderColor: 'rgba(255, 255, 255, 0.8)',
                backgroundColor: 'rgba(255, 255, 255, 0.1)',
              }
            }}
          >
            Cancel
          </Button>
          <Button
            onClick={handleDescriptionConfirm}
            variant="contained"
            sx={{
              background: 'linear-gradient(45deg, #4ECDC4 30%, #44A08D 90%)',
              borderRadius: 2,
              padding: '8px 24px',
              '&:hover': {
                background: 'linear-gradient(45deg, #44A08D 30%, #4ECDC4 90%)',
                transform: 'translateY(-1px)',
                boxShadow: '0 6px 20px rgba(78, 205, 196, 0.4)'
              }
            }}
          >
            Confirm & Continue
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
