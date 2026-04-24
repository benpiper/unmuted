import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  Container,
  Box,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Button,
  Paper,
  TextField,
  Stack,
  CircularProgress,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Tooltip,
  useMediaQuery,
  alpha
} from '@mui/material';
import {
  Brightness4 as DarkModeIcon,
  Brightness7 as LightModeIcon,
  RestartAlt as RestartIcon,
  Logout as LogoutIcon,
} from '@mui/icons-material';
import getDesignTokens from './theme';

const API_BASE = import.meta.env.VITE_API_BASE || '';

function LoginScreen({ onLogin, theme }) {
  const [input, setInput] = useState('');
  const [error, setError] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const token = input.trim();
    if (!token) return;
    try {
      const res = await fetch(`${API_BASE}/api/project/scan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ directory_path: '.' }),
      });
      if (res.status === 401) { setError(true); return; }
    } catch (_) { }
    onLogin(token);
  };

  return (
    <Box sx={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', p: 2 }}>
      <Paper sx={{ p: 4, maxWidth: 400, width: '100%' }}>
        <Typography variant="h4" component="h1" sx={{
          background: theme.palette.mode === 'dark'
            ? 'linear-gradient(135deg, #60a5fa, #a78bfa)'
            : 'linear-gradient(135deg, #2563eb, #7c3aed)',
          backgroundClip: 'text',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          fontWeight: 800,
          mb: 0.5,
        }}>
          🎙️ unmuted
        </Typography>
        <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
          Enter your access token to continue
        </Typography>
        <form onSubmit={handleSubmit}>
          <Stack spacing={2}>
            <TextField
              type="password"
              label="Access Token"
              value={input}
              onChange={e => { setInput(e.target.value); setError(false); }}
              fullWidth
              autoFocus
              error={error}
              helperText={error ? 'Invalid token' : ''}
            />
            <Button type="submit" variant="contained" fullWidth disabled={!input.trim()}>
              Access
            </Button>
          </Stack>
        </form>
      </Paper>
    </Box>
  );
}

function usePersistentState(key, defaultValue) {
  const [state, setState] = useState(() => {
    const saved = localStorage.getItem(key);
    if (saved !== null) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        return defaultValue;
      }
    }
    return defaultValue;
  });

  useEffect(() => {
    if (state === undefined || state === null) {
      localStorage.removeItem(key);
    } else {
      localStorage.setItem(key, JSON.stringify(state));
    }
  }, [key, state]);

  return [state, setState];
}

function App() {
  const [mode, setMode] = usePersistentState('unmuted_mode', 'setup'); // setup | extracting | review | autofinish | done
  const [directory, setDirectory] = usePersistentState('unmuted_directory', '');
  const [prompt, setPrompt] = usePersistentState('unmuted_prompt', '');
  const [context, setContext] = usePersistentState('unmuted_context', '');
  const [interval, setIntervalVal] = usePersistentState('unmuted_interval', 10);
  const [themeMode, setThemeMode] = usePersistentState('unmuted_theme', 'light');

  const theme = React.useMemo(
    () => createTheme(getDesignTokens(themeMode)),
    [themeMode]
  );

  const [loading, setLoading] = useState(false);
  const [videoFile, setVideoFile] = useState(null);
  const [uploading, setUploading] = useState(false);

  const [totalFrames, setTotalFrames] = usePersistentState('unmuted_totalFrames', 0);
  const [fps, setFps] = usePersistentState('unmuted_fps', 1);
  const [frameIndex, setFrameIndex] = usePersistentState('unmuted_frameIndex', 0);
  const [candidates, setCandidates] = usePersistentState('unmuted_candidates', []);
  const [candidatesCache, setCandidatesCache] = usePersistentState('unmuted_candidatesCache', {});
  const [history, setHistory] = usePersistentState('unmuted_history', []);
  const [customNarration, setCustomNarration] = usePersistentState('unmuted_customNarration', '');
  const [customOverlay, setCustomOverlay] = usePersistentState('unmuted_customOverlay', '');
  const [currentTimestamp, setCurrentTimestamp] = usePersistentState('unmuted_currentTimestamp', '');
  const [storyPlan, setStoryPlan] = usePersistentState('unmuted_storyPlan', []);
  const [synopsises, setSynopsises] = usePersistentState('unmuted_synopsises', []);
  const [selectedSynopsis, setSelectedSynopsis] = usePersistentState('unmuted_selectedSynopsis', '');
  const [generatingSynopsis, setGeneratingSynopsis] = useState(false);
  const [toolContext, setToolContext] = usePersistentState('unmuted_toolContext', '');
  const [transcriptData, setTranscriptData] = usePersistentState('unmuted_transcriptData', []);
  const [isSaved, setIsSaved] = usePersistentState('unmuted_isSaved', false);
  const [optimizing, setOptimizing] = useState(false);
  const [useRag, setUseRag] = usePersistentState('unmuted_useRag', false);
  const [ragMaxFrames, setRagMaxFrames] = usePersistentState('unmuted_ragMaxFrames', 10);
  const [generateOverlay, setGenerateOverlay] = usePersistentState('unmuted_generateOverlay', false);
  const [token, setToken] = useState(() => localStorage.getItem('unmuted_token'));

  useEffect(() => {
    if (token) localStorage.setItem('unmuted_token', token);
    else localStorage.removeItem('unmuted_token');
  }, [token]);

  const apiFetch = React.useCallback((url, options = {}) => {
    const stored = localStorage.getItem('unmuted_token');
    return fetch(url, {
      ...options,
      headers: {
        ...(options.headers || {}),
        ...(stored ? { 'Authorization': `Bearer ${stored}` } : {}),
      },
    }).then(res => {
      if (res.status === 401) setToken(null);
      return res;
    });
  }, []);

  const mediaUrl = React.useCallback((url) => {
    const stored = localStorage.getItem('unmuted_token');
    return stored ? `${url}&token=${encodeURIComponent(stored)}` : url;
  }, []);

  const videoRef = React.useRef(null);
  const timelineRefs = React.useRef([]);
  const abortRef = React.useRef(false);
  const [activeIndex, setActiveIndex] = useState(-1);

  const handleTimeUpdate = () => {
    if (!videoRef.current || transcriptData.length === 0) return;
    const time = videoRef.current.currentTime;

    const timeToSeconds = (ts) => {
      if (!ts) return 0;
      const parts = ts.split(':').map(Number);
      if (parts.length === 3) return parts[0] * 3600 + parts[1] * 60 + parts[2];
      if (parts.length === 2) return parts[0] * 60 + parts[1];
      return 0;
    };

    let active = -1;
    for (let i = 0; i < transcriptData.length; i++) {
      const sec = timeToSeconds(transcriptData[i].timestamp);
      if (time >= sec) {
        active = i;
      } else {
        break;
      }
    }

    if (active !== activeIndex) {
      setActiveIndex(active);
      if (active >= 0 && timelineRefs.current[active]) {
        timelineRefs.current[active].scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }
  };

  const handleOptimize = async () => {
    try {
      setOptimizing(true);
      const res = await apiFetch(`${API_BASE}/api/project/optimize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ transcript: transcriptData })
      });
      const data = await res.json();
      if (data.success && data.transcript) {
        setTranscriptData(data.transcript);
        setIsSaved(false);
        alert("Transcript fully optimized! Segments merged successfully.");
      } else {
        alert("Error optimizing: " + data.detail);
      }
    } catch (e) {
      alert("Error reaching optimization endpoint.");
    } finally {
      setOptimizing(false);
    }
  };

  const handleCancel = () => {
    if (window.confirm("Are you sure you want to cancel and start over? All current progress will be lost.")) {
      abortRef.current = true;
      setMode('setup');
      setTotalFrames(0);
      setFrameIndex(0);
      setCandidates([]);
      setCandidatesCache({});
      setHistory([]);
      setTranscriptData([]);
      setCustomNarration('');
      setCustomOverlay('');
      setCurrentTimestamp('');
      setVideoFile(null);
      setIsSaved(false);
    }
  };

  const [isAutoProcessAll, setIsAutoProcessAll] = useState(false);

  const startAutoFinishAll = async (workDir, total, _fps, planOverrides = null, synopsisOverride = null) => {
    abortRef.current = false;
    setMode('autofinish');
    setTranscriptData([]);
    setHistory([]);

    try {
      const res = await apiFetch(`${API_BASE}/api/project/auto_finish`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          directory_path: workDir,
          prompt,
          context,
          start_frame_index: 0,
          history: [],
          fps: _fps,
          current_transcript: [],
          story_plan: planOverrides || storyPlan,
          use_rag: useRag,
          rag_max_frames: parseInt(ragMaxFrames) || 3,
          generate_overlay: generateOverlay,
          synopsis: synopsisOverride || selectedSynopsis
        })
      });
      const data = await res.json();

      if (!abortRef.current && data.success) {
        setTranscriptData(data.transcript);
        setHistory(data.transcript.map(t => t.narration));
        setMode('done');
      } else if (!abortRef.current) {
        alert("Error running auto-finish via backend.");
        setMode('done');
      }
    } catch (e) {
      console.error(e);
      if (!abortRef.current) setMode('done');
    }
  };

  const generateSynopsises = async (plan, workDir, total, _fps, autoFinish, tools = '') => {
    setGeneratingSynopsis(true);
    try {
      const res = await apiFetch(`${API_BASE}/api/project/synopsises`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ story_plan: plan, prompt, tool_context: tools })
      });
      const data = await res.json();
      console.log("Synopsis response:", data);

      if (data.success && data.synopsises && data.synopsises.length > 0) {
        setSynopsises(data.synopsises);
        setSelectedSynopsis(data.synopsises[0]);
        console.log("Synopsises set:", data.synopsises);
      } else {
        console.warn("No synopsises in response:", data);
        setSynopsises([]);
      }

      if (autoFinish && data.synopsises && data.synopsises.length > 0) {
        startAutoFinishAll(workDir, total, _fps, plan, data.synopsises[0]);
      } else if (autoFinish) {
        startAutoFinishAll(workDir, total, _fps, plan);
      } else {
        setMode('planning');
      }
    } catch (e) {
      console.error("Error generating synopsises:", e);
      setSynopsises([]);
      if (autoFinish) {
        startAutoFinishAll(workDir, total, _fps, plan);
      } else {
        setMode('planning');
      }
    } finally {
      setGeneratingSynopsis(false);
    }
  };

  const generateStrategicPlan = async (workDir, total, _fps, autoFinish, tools = '') => {
    setMode('planning_loading');
    try {
      const res = await apiFetch(`${API_BASE}/api/project/plan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ directory_path: workDir, prompt, context, tool_context: tools })
      });
      const data = await res.json();
      if (data.success) {
        setStoryPlan(data.plan || []);
        generateSynopsises(data.plan || [], workDir, total, _fps, autoFinish, tools);
      } else {
        alert("Error analyzing video for story plan");
        setMode('setup');
      }
    } catch (e) {
      alert("Error generating plan");
      setMode('setup');
    }
  };

  const handleUploadAndExtract = async (autoFinish = false) => {
    if (!videoFile) {
      alert("Please select a video file first.");
      return;
    }

    setUploading(true);
    setIsAutoProcessAll(autoFinish);
    setMode('extracting');

    const formData = new FormData();
    formData.append('file', videoFile);

    try {
      const uploadRes = await apiFetch(`${API_BASE}/api/project/upload`, {
        method: 'POST',
        body: formData
      });
      const uploadData = await uploadRes.json();

      if (!uploadData.success) {
        alert("Upload failed.");
        setMode('setup');
        setUploading(false);
        return;
      }

      const workDir = uploadData.directory_path;
      setDirectory(workDir);

      const extractRes = await apiFetch(`${API_BASE}/api/project/extract`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ directory_path: workDir, interval: Number(interval) })
      });
      const extractData = await extractRes.json();

      if (extractData.success) {
        setTotalFrames(extractData.total_frames);
        setFps(extractData.fps);

        // Identify tools before generating plan
        console.log("Identifying tools in video...");
        try {
          const toolsRes = await apiFetch(`${API_BASE}/api/project/identify-tools`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ directory_path: workDir })
          });
          const toolsData = await toolsRes.json();
          if (toolsData.success && toolsData.tool_context) {
            console.log("Tools identified:", toolsData.tools);
            setToolContext(toolsData.tool_context);
            generateStrategicPlan(workDir, extractData.total_frames, extractData.fps, autoFinish, toolsData.tool_context);
          } else {
            console.warn("No tools identified, proceeding without tool context");
            generateStrategicPlan(workDir, extractData.total_frames, extractData.fps, autoFinish, '');
          }
        } catch (e) {
          console.error("Error identifying tools:", e);
          generateStrategicPlan(workDir, extractData.total_frames, extractData.fps, autoFinish, '');
        }
      } else {
        alert(extractData.detail);
        setMode('setup');
      }
    } catch (e) {
      alert("Error during upload or extraction.");
      setMode('setup');
    } finally {
      setUploading(false);
    }
  };

  const fetchCandidates = async (index, currentHistory, currentTranscript, dirOverride = null) => {
    const activeDir = dirOverride || directory;
    setLoading(true);
    try {
      const res = await apiFetch(`${API_BASE}/api/project/frame_candidates`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          directory_path: activeDir,
          prompt,
          context,
          frame_index: index,
          history: currentHistory,
          fps,
          story_plan: storyPlan,
          use_rag: useRag,
          rag_max_frames: parseInt(ragMaxFrames) || 3,
          generate_overlay: generateOverlay,
          synopsis: selectedSynopsis
        })
      });
      const data = await res.json();
      if (data.success) {
        let cands = data.data.candidates;

        setCandidates(cands);
        setCurrentTimestamp(data.data.timestamp);
        if (cands.length > 0) {
          setCustomNarration(cands[0].narration || '');
          setCustomOverlay(cands[0].overlay || '');
        }
        setCandidatesCache(prev => ({ ...prev, [index]: { candidates: cands, timestamp: data.data.timestamp } }));
        setFrameIndex(index);
      }
    } catch (e) {
      alert("Error fetching candidates for frame.");
    } finally {
      setLoading(false);
    }
  };

  const resumeAutoFinish = async () => {
    abortRef.current = false;
    setMode('autofinish');

    try {
      const res = await apiFetch(`${API_BASE}/api/project/auto_finish`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          directory_path: directory,
          prompt,
          context,
          start_frame_index: frameIndex,
          history: history,
          fps: fps,
          current_transcript: transcriptData,
          story_plan: storyPlan,
          use_rag: useRag,
          rag_max_frames: parseInt(ragMaxFrames) || 3,
          generate_overlay: generateOverlay,
          synopsis: selectedSynopsis
        })
      });
      const data = await res.json();

      if (!abortRef.current && data.success) {
        setTranscriptData(data.transcript);
        setHistory(data.transcript.map(t => t.narration));
        setMode('done');
      } else if (!abortRef.current) {
        alert("Error running auto-finish via backend.");
        setMode('done');
      }
    } catch (e) {
      console.error("Error resuming auto finish", e);
      if (!abortRef.current) setMode('done');
    }
  };

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', themeMode);
  }, [themeMode]);

  useEffect(() => {
    if (mode === 'extracting') {
      setMode('setup');
    } else if (mode === 'autofinish') {
      resumeAutoFinish();
    }

    return () => {
      if (mode === 'autofinish') {
        abortRef.current = true;
      }
    };
  }, []);

  const commitNext = () => {
    const item = { timestamp: currentTimestamp, narration: customNarration, overlay: customOverlay };
    const newTranscript = [...transcriptData, item];
    const newHistory = [...history, customNarration];

    setTranscriptData(newTranscript);
    setHistory(newHistory);

    if (frameIndex + 1 < totalFrames) {
      fetchCandidates(frameIndex + 1, newHistory, newTranscript);
    } else {
      setMode('done');
    }
  };

  const goBack = () => {
    if (frameIndex > 0) {
      const newIndex = frameIndex - 1;
      const newTranscript = transcriptData.slice(0, -1);
      const newHistory = history.slice(0, -1);

      setTranscriptData(newTranscript);
      setHistory(newHistory);
      setFrameIndex(newIndex);

      const cached = candidatesCache[newIndex];
      if (cached) {
        setCandidates(cached.candidates);
        setCurrentTimestamp(cached.timestamp);
        if (cached.candidates.length > 0) {
          setCustomNarration(cached.candidates[0].narration || '');
          setCustomOverlay(cached.candidates[0].overlay || '');
        }
      } else {
        fetchCandidates(newIndex, newHistory, newTranscript);
      }
    }
  };

  const commitAutoFinish = async () => {
    const item = { timestamp: currentTimestamp, narration: customNarration, overlay: customOverlay };
    let currentT = [...transcriptData, item];
    let currentH = [...history, customNarration];
    let currentIndex = frameIndex + 1;

    if (currentIndex >= totalFrames) {
      setTranscriptData(currentT);
      setMode('done');
      return;
    }

    abortRef.current = false;
    setMode('autofinish');
    setTranscriptData(currentT);
    setHistory(currentH);

    while (currentIndex < totalFrames) {
      if (abortRef.current) break;
      setFrameIndex(currentIndex);

      try {
        const res = await apiFetch(`${API_BASE}/api/project/frame_candidates`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            directory_path: directory,
            prompt,
            context,
            frame_index: currentIndex,
            history: currentH,
            fps,
            story_plan: storyPlan,
            use_rag: useRag,
            rag_max_frames: parseInt(ragMaxFrames) || 3,
            generate_overlay: generateOverlay,
            synopsis: selectedSynopsis
          })
        });
        const data = await res.json();

        if (abortRef.current) break;

        if (data.success && data.data.candidates.length > 0) {
          const topLLMCandidate = data.data.candidates[0];
          const autoItem = {
            timestamp: data.data.timestamp,
            narration: topLLMCandidate.narration,
            overlay: topLLMCandidate.overlay
          };

          if (!(currentT.length > 0 && currentT[currentT.length - 1].narration === autoItem.narration)) {
            currentT = [...currentT, autoItem];
            currentH = [...currentH, autoItem.narration];
            setTranscriptData(currentT);
            setHistory(currentH);
          }
        }
      } catch (e) {
        console.error("Error in auto finish loop", e);
        break;
      }

      currentIndex++;
    }

    if (!abortRef.current) setMode('done');
  };

  const handleSave = async () => {
    try {
      setLoading(true);
      const res = await apiFetch(`${API_BASE}/api/project/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ directory_path: directory, transcript: transcriptData })
      });
      const data = await res.json();
      if (data.success) {
        setIsSaved(true);
        alert("Transcript artifacts generated successfully!");
      } else {
        alert("Error: " + data.detail);
      }
    } catch (e) {
      alert("Error saving transcript.");
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateItem = (idx, field, value) => {
    const updated = [...transcriptData];
    updated[idx][field] = value;
    setTranscriptData(updated);
    setIsSaved(false);
  };

  if (!token) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <LoginScreen onLogin={setToken} theme={theme} />
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <div className="app-container">
        <AppBar position="static" color="transparent" elevation={0} sx={{ py: 1, backdropFilter: 'blur(10px)', borderBottom: '1px solid', borderColor: 'divider' }}>
          <Toolbar>
            <Box sx={{ flexGrow: 1, textAlign: 'left' }}>
              <Typography variant="h4" component="h1" sx={{
                background: theme.palette.mode === 'dark'
                  ? 'linear-gradient(135deg, #60a5fa, #a78bfa)'
                  : 'linear-gradient(135deg, #2563eb, #7c3aed)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                fontWeight: 800
              }}>
                🎙️ unmuted
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.7 }}>
                AI-Powered Technical Video Narrations
              </Typography>
            </Box>

            <Stack direction="row" spacing={2} alignItems="center">
              <Tooltip title={`Switch to ${themeMode === 'dark' ? 'light' : 'dark'} mode`}>
                <IconButton onClick={() => setThemeMode(themeMode === 'dark' ? 'light' : 'dark')} color="inherit">
                  {themeMode === 'dark' ? <LightModeIcon /> : <DarkModeIcon />}
                </IconButton>
              </Tooltip>
              <Tooltip title="Sign out">
                <IconButton onClick={() => setToken(null)} color="inherit">
                  <LogoutIcon />
                </IconButton>
              </Tooltip>

              {mode !== 'setup' && (
                <Button
                  startIcon={<RestartIcon />}
                  variant="outlined"
                  color="error"
                  onClick={handleCancel}
                  sx={{ borderRadius: '20px' }}
                >
                  Cancel / Restart
                </Button>
              )}
            </Stack>
          </Toolbar>
        </AppBar>

        {mode === 'setup' && (
          <Container maxWidth="md" sx={{ py: 4 }}>
            <Paper sx={{ p: 4 }}>
              <Typography variant="h5" gutterBottom sx={{ fontWeight: 700 }}>
                Project Setup
              </Typography>

              <Stack spacing={3} sx={{ mt: 3 }}>
                <Box>
                  <Typography variant="subtitle2" gutterBottom color="textSecondary">
                    Upload Screen Recording (.mp4, .mov, .webm)
                  </Typography>
                  <TextField
                    type="file"
                    fullWidth
                    onChange={e => setVideoFile(e.target.files[0])}
                    inputProps={{ accept: "video/*" }}
                    variant="outlined"
                    size="small"
                  />
                </Box>

                <Box>
                  <Typography variant="subtitle2" gutterBottom color="textSecondary">
                    Describe the video
                  </Typography>
                  <TextField
                    value={prompt}
                    onChange={e => setPrompt(e.target.value)}
                    fullWidth
                    multiline
                    rows={3}
                    placeholder="What is happening in this video?"
                  />
                </Box>

                <Box>
                  <Typography variant="subtitle2" gutterBottom color="textSecondary">
                    Technical Context / Tools (e.g. Linux, Python, React)
                  </Typography>
                  <TextField
                    value={context}
                    onChange={e => setContext(e.target.value)}
                    fullWidth
                    placeholder="Leave blank if n/a"
                  />
                </Box>

                <Box>
                  <Typography variant="subtitle2" gutterBottom color="textSecondary">
                    Analysis Interval (Seconds)
                  </Typography>
                  <TextField
                    type="number"
                    value={interval}
                    onChange={e => setIntervalVal(e.target.value)}
                    fullWidth
                    inputProps={{ min: 10 }}
                  />
                </Box>

                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, mt: 2, p: 2, borderRadius: 1, bgcolor: 'background.paper', border: '1px solid', borderColor: 'divider' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box>
                      <Typography variant="subtitle1" fontWeight="bold">Enable Context Sequence (Agentic RAG)</Typography>
                      <Typography variant="body2" color="textSecondary">Use DuckDuckGo web search to automatically identify abstract technical commands.</Typography>
                    </Box>
                    <input type="checkbox" checked={useRag} onChange={e => setUseRag(e.target.checked)} style={{ width: 24, height: 24 }} />
                  </Box>

                  {useRag && (
                    <Box sx={{ mt: 1 }}>
                      <Typography variant="subtitle2" gutterBottom color="textSecondary">
                        Max RAG Frames (To prevent rate limits)
                      </Typography>
                      <TextField
                        type="number"
                        value={ragMaxFrames}
                        onChange={e => setRagMaxFrames(e.target.value)}
                        fullWidth
                        size="small"
                        inputProps={{ min: 1, max: 20 }}
                      />
                    </Box>
                  )}

                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mt: 2, pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
                    <Box>
                      <Typography variant="subtitle1" fontWeight="bold">Generate Overlay Text</Typography>
                      <Typography variant="body2" color="textSecondary">Generate overlay text for each segment.</Typography>
                    </Box>
                    <input type="checkbox" checked={generateOverlay} onChange={e => setGenerateOverlay(e.target.checked)} style={{ width: 24, height: 24 }} />
                  </Box>
                </Box>

                <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ pt: 2 }}>
                  <Button
                    variant="contained"
                    size="large"
                    onClick={() => handleUploadAndExtract(false)}
                    disabled={!videoFile || uploading}
                    fullWidth
                  >
                    {uploading && !isAutoProcessAll ? <CircularProgress size={24} color="inherit" /> : 'Upload & Start Review'}
                  </Button>
                  <Button
                    variant="outlined"
                    size="large"
                    color="success"
                    onClick={() => handleUploadAndExtract(true)}
                    disabled={!videoFile || uploading}
                    fullWidth
                  >
                    {uploading && isAutoProcessAll ? <CircularProgress size={24} color="inherit" /> : 'Upload & Auto-Process All'}
                  </Button>
                </Stack>
              </Stack>
            </Paper>
          </Container>
        )}

        {mode === 'extracting' && (
          <Container maxWidth="sm" sx={{ py: 10 }}>
            <Paper sx={{ p: 6, textAlign: 'center' }}>
              <CircularProgress size={60} sx={{ mb: 4 }} />
              <Typography variant="h5" gutterBottom sx={{ fontWeight: 700 }}>
                Uploading & Initializing...
              </Typography>
              <Typography variant="body1" color="textSecondary">
                Please wait while your video is uploaded and evaluated by the vision engine.
              </Typography>
            </Paper>
          </Container>
        )}

        {mode === 'planning_loading' && (
          <Container maxWidth="sm" sx={{ py: 10 }}>
            <Paper sx={{ p: 6, textAlign: 'center' }}>
              <CircularProgress size={60} sx={{ mb: 4 }} />
              <Typography variant="h5" gutterBottom sx={{ fontWeight: 700 }}>
                Generating Strategic Plan...
              </Typography>
              <Typography variant="body1" color="textSecondary" sx={{ mb: 3 }}>
                The AI is analyzing the entire video to build a high-level narrative outline before frame-by-frame processing begins.
              </Typography>
              {generatingSynopsis && (
                <Box sx={{ mt: 3, pt: 3, borderTop: '1px solid', borderColor: 'divider' }}>
                  <Typography variant="body2" color="textSecondary">
                    Also generating video synopsises...
                  </Typography>
                </Box>
              )}
            </Paper>
          </Container>
        )}

        {mode === 'planning' && (
          <Container maxWidth="md" sx={{ py: 4 }}>
            <Paper sx={{ p: 4 }}>
              <Typography variant="h5" gutterBottom sx={{ fontWeight: 700 }}>
                Strategic Story Plan
              </Typography>
              <Typography variant="body1" color="textSecondary" sx={{ mb: 3 }}>
                The AI has generated a high-level outline of the task based on keyframes. This plan will guide the frame-by-frame narration and self-correction engine. You can edit this plan before proceeding.
              </Typography>

              <Stack spacing={2} sx={{ mb: 4 }}>
                {storyPlan.map((step, idx) => (
                  <TextField
                    key={idx}
                    fullWidth
                    value={step}
                    onChange={(e) => {
                      const newPlan = [...storyPlan];
                      newPlan[idx] = e.target.value;
                      setStoryPlan(newPlan);
                    }}
                    variant="outlined"
                    size="small"
                  />
                ))}
                <Button variant="outlined" onClick={() => setStoryPlan([...storyPlan, ""])}>
                  + Add Step
                </Button>
              </Stack>

              <Box sx={{ mb: 4, p: 2, bgcolor: 'background.paper', border: '1px solid', borderColor: 'divider', borderRadius: 1 }}>
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 700 }}>
                  Video Synopsis
                </Typography>
                {synopsises.length > 0 ? (
                  <>
                    <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
                      The AI has generated synopsises that summarize the overall narrative. Select the one that best describes this video:
                    </Typography>
                    <Stack spacing={1}>
                      {synopsises.map((synopsis, idx) => (
                        <Paper
                          key={idx}
                          variant="outlined"
                          onClick={() => setSelectedSynopsis(synopsis)}
                          sx={{
                            p: 1.5,
                            cursor: 'pointer',
                            background: selectedSynopsis === synopsis ? theme.palette.action.selected : 'transparent',
                            borderColor: selectedSynopsis === synopsis ? 'primary.main' : 'divider',
                            transition: '0.2s',
                            '&:hover': { background: theme.palette.action.hover }
                          }}
                        >
                          <Typography variant="body2">{synopsis}</Typography>
                        </Paper>
                      ))}
                    </Stack>
                  </>
                ) : (
                  <Typography variant="body2" color="textSecondary">
                    Synopsises will be generated to provide narrative context for frame analysis. If they don't appear, you can proceed without them.
                  </Typography>
                )}
              </Box>

              <Button
                variant="contained"
                size="large"
                fullWidth
                onClick={() => {
                  setMode('review');
                  fetchCandidates(0, [], [], directory);
                }}
              >
                Proceed to Interactive Review
              </Button>
            </Paper>
          </Container>
        )}

        {mode === 'review' && (

          <Container maxWidth="xl" sx={{ py: 3 }}>
            <Paper sx={{ p: 3, mb: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h5" sx={{ fontWeight: 700 }}>
                  Interactive Review: Frame {frameIndex + 1} of {totalFrames}
                </Typography>
                <Typography variant="subtitle1" color="textSecondary">
                  Timestamp: {currentTimestamp}
                </Typography>
              </Box>

              <Grid container spacing={3}>
                <Grid size={{ xs: 12, lg: 7 }} sx={{ position: { lg: 'sticky' }, top: 24, alignSelf: 'flex-start' }}>
                  <Stack spacing={3}>
                    <Paper sx={{ p: 2, background: theme.palette.customMedia.bg }}>
                      <Typography variant="subtitle2" sx={{ mb: 1, color: 'primary.main', fontWeight: 'bold' }}>
                        Source Video Playback
                      </Typography>
                      <Box sx={{ position: 'relative', width: '100%', height: '35vh', minHeight: '15vh', resize: 'vertical', overflow: 'hidden' }}>
                        <video
                          controls
                          src={mediaUrl(`${API_BASE}/api/project/video?directory_path=${encodeURIComponent(directory)}`)}
                          style={{ width: '100%', height: '100%', objectFit: 'contain', borderRadius: '8px', border: `1px solid ${theme.palette.customMedia.border}` }}
                        />
                      </Box>
                    </Paper>

                    <Paper sx={{ p: 2 }}>
                      <Typography variant="subtitle2" sx={{ mb: 1, color: 'primary.main', fontWeight: 'bold' }}>
                        Current Analyzed Frame
                      </Typography>
                      <Box sx={{ width: '100%', height: '40vh', minHeight: '15vh' }}>
                        <img
                          src={mediaUrl(`${API_BASE}/api/project/frame_image?directory_path=${encodeURIComponent(directory)}&frame_index=${frameIndex}`)}
                          alt="Current Frame"
                          style={{ width: '100%', height: '100%', objectFit: 'contain', borderRadius: '8px', border: `2px solid ${theme.palette.primary.main}` }}
                        />
                      </Box>
                    </Paper>

                    <Grid container spacing={2}>
                      <Grid size={{ xs: 6 }}>
                        <Typography variant="caption" align="center" display="block" color="textSecondary" sx={{ mb: 0.5 }}>Previous</Typography>
                        <Box sx={{ width: '100%', aspectRatio: '16/9', background: theme.palette.customCandidate.bg, borderRadius: '4px', overflow: 'hidden' }}>
                          {frameIndex > 0 && (
                            <img
                              src={mediaUrl(`${API_BASE}/api/project/frame_image?directory_path=${encodeURIComponent(directory)}&frame_index=${frameIndex - 1}`)}
                              alt="Previous Frame"
                              style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                            />
                          )}
                        </Box>
                      </Grid>
                      <Grid size={{ xs: 6 }}>
                        <Typography variant="caption" align="center" display="block" color="textSecondary" sx={{ mb: 0.5 }}>Next</Typography>
                        <Box sx={{ width: '100%', aspectRatio: '16/9', background: theme.palette.customCandidate.bg, borderRadius: '4px', overflow: 'hidden' }}>
                          {frameIndex + 1 < totalFrames && (
                            <img
                              src={mediaUrl(`${API_BASE}/api/project/frame_image?directory_path=${encodeURIComponent(directory)}&frame_index=${frameIndex + 1}`)}
                              alt="Next Frame"
                              style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                            />
                          )}
                        </Box>
                      </Grid>
                    </Grid>
                  </Stack>
                </Grid>

                <Grid size={{ xs: 12, lg: 5 }}>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                    <Box>
                      <Typography variant="h6" gutterBottom>Timeline History</Typography>
                      <Paper variant="outlined" sx={{ p: 2, background: theme.palette.customTimeline.bg, maxHeight: '200px', overflowY: 'auto' }}>
                        {transcriptData.map((t, idx) => (
                          <Box key={idx} sx={{ mb: 1, borderLeft: '2px solid', borderColor: 'primary.main', pl: 1 }}>
                            <Typography variant="caption" sx={{ color: 'primary.main', fontWeight: 'bold' }}>{t.timestamp}</Typography>
                            <Typography variant="body2">{t.narration}</Typography>
                          </Box>
                        ))}
                        {transcriptData.length === 0 && <Typography variant="body2" color="textSecondary">No events recorded yet.</Typography>}
                      </Paper>
                    </Box>

                    {loading ? (
                      <Box sx={{ py: 6, textAlign: 'center' }}>
                        <CircularProgress size={40} sx={{ mb: 2 }} />
                        <Typography variant="body1">Analyzing frame with AI...</Typography>
                      </Box>
                    ) : (
                      <>
                        {history.length > 0 && (
                          <Paper sx={{ p: 2, background: theme.palette.customInfo.bg, borderLeft: '4px solid', borderColor: 'primary.main' }}>
                            <Typography variant="subtitle2" sx={{ color: 'primary.main', mb: 0.5 }}>Last Selected Narration</Typography>
                            <Typography variant="body2">{history[history.length - 1]}</Typography>
                          </Paper>
                        )}

                        <Box>
                          <Typography variant="h6" gutterBottom>Candidates</Typography>
                          <Stack spacing={1.5}>
                            {candidates.map((c, i) => (
                              <Paper
                                key={i}
                                variant="outlined"
                                onClick={() => { setCustomNarration(c.narration); setCustomOverlay(c.overlay); }}
                                sx={{
                                  p: 1.5,
                                  cursor: 'pointer',
                                  transition: '0.2s',
                                  background: customNarration === c.narration ? theme.palette.customCandidate.selected : theme.palette.customCandidate.bg,
                                  borderColor: customNarration === c.narration ? 'primary.main' : 'divider',
                                  '&:hover': { background: theme.palette.customCandidate.selected }
                                }}
                              >
                                <Typography variant="body2" sx={{ fontWeight: 600 }}>Option {i + 1}: {c.narration}</Typography>
                                <Typography variant="caption" color="textSecondary">Overlay: {c.overlay}</Typography>
                              </Paper>
                            ))}
                          </Stack>
                        </Box>

                        <Box>
                          <Typography variant="subtitle2" gutterBottom>Active Narration</Typography>
                          <TextField
                            multiline
                            rows={3}
                            fullWidth
                            value={customNarration}
                            onChange={e => setCustomNarration(e.target.value)}
                          />
                        </Box>

                        <Box>
                          <Typography variant="subtitle2" gutterBottom>Active Overlay</Typography>
                          <TextField
                            fullWidth
                            size="small"
                            value={customOverlay}
                            onChange={e => setCustomOverlay(e.target.value)}
                          />
                        </Box>

                        <Stack direction="row" spacing={2}>
                          <Button variant="outlined" fullWidth onClick={goBack} disabled={frameIndex === 0}>Go Back</Button>
                          <Button variant="contained" fullWidth onClick={commitNext}>Commit & Next</Button>
                          <Button variant="outlined" fullWidth onClick={commitAutoFinish}>Auto Finish Rest</Button>
                        </Stack>
                      </>
                    )}
                  </Box>
                </Grid>
              </Grid>
            </Paper>
          </Container>
        )}

        {mode === 'autofinish' && (
          <Container maxWidth="md" sx={{ py: 6 }}>
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="h5" gutterBottom sx={{ fontWeight: 700 }}>
                Auto-finishing remainder of the video...
              </Typography>
              <Typography variant="body1" color="textSecondary" sx={{ mb: 2 }}>
                The AI is processing the remaining frames automatically.
              </Typography>

              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" sx={{ color: 'primary.main', fontWeight: 700 }}>
                  Frame {frameIndex + 1} of {totalFrames}
                </Typography>
                <Box sx={{ width: '100%', height: 6, borderRadius: 3, bgcolor: 'divider', mt: 1 }}>
                  <Box sx={{ width: `${totalFrames > 0 ? ((frameIndex + 1) / totalFrames) * 100 : 0}%`, height: '100%', borderRadius: 3, bgcolor: 'primary.main', transition: 'width 0.3s ease' }} />
                </Box>
              </Box>

              <Box sx={{ mb: 4 }}>
                <img
                  src={mediaUrl(`${API_BASE}/api/project/frame_image?directory_path=${encodeURIComponent(directory)}&frame_index=${frameIndex}`)}
                  alt="Processing Frame"
                  style={{ width: '100%', maxHeight: '40vh', objectFit: 'contain', borderRadius: '8px', border: `2px solid ${theme.palette.primary.main}` }}
                />
              </Box>

              {history.length > 0 && (
                <Paper sx={{ p: 3, mb: 3, background: theme.palette.customInfo.bg, borderLeft: '4px solid', borderColor: 'primary.main', textAlign: 'left' }}>
                  <Typography variant="subtitle2" sx={{ color: 'primary.main', mb: 0.5 }}>Latest Narration (Auto-Generated)</Typography>
                  <Typography variant="body2">{history[history.length - 1]}</Typography>
                </Paper>
              )}
              <CircularProgress size={40} />
            </Paper>
          </Container>
        )}

        {mode === 'done' && (
          <Container maxWidth="xl" sx={{ py: 3 }}>
            <Paper sx={{ p: 4 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
                <Box>
                  <Typography variant="h4" sx={{ fontWeight: 800 }}>Processing Complete! 🎉</Typography>
                  <Typography variant="subtitle1" color="textSecondary">Your transcript and metadata are ready.</Typography>
                </Box>
                <Stack direction="row" spacing={2} alignItems="center">
                  {!isSaved && (
                    <Button
                      variant="contained"
                      color="success"
                      size="large"
                      onClick={handleSave}
                      disabled={loading}
                      startIcon={loading ? <CircularProgress size={20} color="inherit" /> : null}
                    >
                      Save & Generate Exports
                    </Button>
                  )}
                  <Button
                    variant="outlined"
                    size="large"
                    onClick={handleOptimize}
                    disabled={optimizing}
                  >
                    {optimizing ? 'Optimizing...' : 'Optimize Transcript (AI)'}
                  </Button>

                </Stack>
              </Box>

              {isSaved && (
                <Stack direction="row" spacing={2} sx={{ mb: 4, p: 2, background: theme.palette.customInfo.bg, borderRadius: '12px' }}>
                  <Button
                    component="a"
                    href={mediaUrl(`${API_BASE}/api/project/download/json?directory_path=${encodeURIComponent(directory)}`)}
                    download="transcript.json"
                    startIcon={<span>⬇️</span>}
                    variant="outlined"
                  >
                    Download JSON
                  </Button>
                  <Button
                    component="a"
                    href={mediaUrl(`${API_BASE}/api/project/download/vtt?directory_path=${encodeURIComponent(directory)}`)}
                    download="transcript.vtt"
                    startIcon={<span>⬇️</span>}
                    variant="outlined"
                  >
                    Download VTT
                  </Button>
                  <Button
                    component="a"
                    href={mediaUrl(`${API_BASE}/api/project/download/chapters?directory_path=${encodeURIComponent(directory)}`)}
                    download="chapters.txt"
                    startIcon={<span>⬇️</span>}
                    variant="outlined"
                  >
                    Download Chapters
                  </Button>
                </Stack>
              )}

              <Grid container spacing={4}>
                <Grid size={{ xs: 12, lg: 7 }}>
                  <Paper sx={{ p: 2, background: theme.palette.customMedia.bg }}>
                    <Typography variant="h6" gutterBottom sx={{ color: 'primary.main' }}>Synchronized Live Playback</Typography>
                    <Box sx={{ position: 'relative', width: '100%', height: '60vh', minHeight: '20vh', resize: 'vertical', overflow: 'hidden' }}>
                      <video
                        ref={videoRef}
                        onTimeUpdate={handleTimeUpdate}
                        controls
                        src={mediaUrl(`${API_BASE}/api/project/video?directory_path=${encodeURIComponent(directory)}`)}
                        style={{ width: '100%', height: '100%', objectFit: 'contain', borderRadius: '8px', border: `1px solid ${theme.palette.customMedia.border}` }}
                      />
                    </Box>
                  </Paper>
                </Grid>

                <Grid size={{ xs: 12, lg: 5 }}>
                  <Typography variant="h6" gutterBottom>Final Transcript</Typography>
                  <Box sx={{ height: 'calc(60vh + 40px)', overflowY: 'auto', pr: 1 }}>
                    <Stack spacing={1}>
                      {(transcriptData && transcriptData.length > 0) ? transcriptData.map((item, idx) => (
                        <Paper
                          key={idx}
                          variant="outlined"
                          sx={{
                            p: 2,
                            transition: '0.2s',
                            borderColor: activeIndex === idx ? 'primary.main' : 'divider',
                            background: activeIndex === idx ? alpha(theme.palette.primary.main, 0.1) : theme.palette.background.paper,
                            borderLeft: '4px solid',
                            borderLeftColor: activeIndex === idx ? 'primary.main' : 'primary.main',
                            boxShadow: activeIndex === idx ? `0 4px 15px ${alpha(theme.palette.primary.main, 0.2)}` : 'none',
                          }}
                        >
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                            <Typography variant="caption" sx={{ color: 'primary.main', fontWeight: 700 }}>
                              {item.timestamp}
                            </Typography>
                            {activeIndex === idx && <Typography variant="caption" color="primary.main">Active Now</Typography>}
                          </Box>
                          <Typography variant="body2" sx={{ fontWeight: 500 }}>{item.narration}</Typography>
                          <Typography variant="caption" color="textSecondary" display="block" sx={{ mt: 1 }}>Overlay: {item.overlay}</Typography>
                        </Paper>
                      )) : (
                        <Paper variant="outlined" sx={{ p: 4, textAlign: 'center', background: theme.palette.customMedia.bg }}>
                          <Typography variant="body2" color="textSecondary">
                            No transcript segments found. If this is unexpected, try processing the video again.
                          </Typography>
                        </Paper>
                      )}
                    </Stack>
                  </Box>
                </Grid>
              </Grid>
            </Paper>
          </Container>
        )}

      </div>
    </ThemeProvider>
  );
}

export default App;
