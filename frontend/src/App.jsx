import React, { useState, useEffect, useCallback } from 'react';
import './App.css';
import AdminDashboard from './AdminDashboard';
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
  LinearProgress,
  Grid,
  Card,
  CardContent,
  CardHeader,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Link as MuiLink,
  alpha,
  Select,
  MenuItem
} from '@mui/material';
import {
  Brightness4 as DarkModeIcon,
  Brightness7 as LightModeIcon,
  RestartAlt as RestartIcon,
  Logout as LogoutIcon,
  Delete as DeleteIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import getDesignTokens from './theme';

const API_BASE = import.meta.env.VITE_API_BASE || '';

function SetupScreen({ onSetupComplete, theme }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email.trim() || !password.trim()) return;

    setError(null);
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/api/auth/setup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim(), password }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || 'Setup failed');
        return;
      }

      onSetupComplete(data.access_token);
    } catch {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', p: 2 }}>
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
          Initialize your admin account
        </Typography>
        <form onSubmit={handleSubmit}>
          <Stack spacing={2}>
            <Typography variant="body2" color="textSecondary">
              This is the first time Unmuted is being set up. Create your admin account:
            </Typography>
            <TextField
              type="email"
              label="Admin Email"
              value={email}
              onChange={e => { setEmail(e.target.value); setError(null); }}
              fullWidth
              autoFocus
            />
            <TextField
              type="password"
              label="Password"
              value={password}
              onChange={e => { setPassword(e.target.value); setError(null); }}
              fullWidth
              error={!!error}
              helperText={error || ''}
            />
            <Button
              type="submit"
              variant="contained"
              fullWidth
              disabled={!email.trim() || !password.trim() || loading}
            >
              {loading ? <CircularProgress size={24} color="inherit" /> : 'Create Admin Account'}
            </Button>
          </Stack>
        </form>
      </Paper>
    </Box>
  );
}

function LoginScreen({ onLogin, theme }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isRegister, setIsRegister] = useState(false);
  const [error, setError] = useState(null);
  const [creditsDialogOpen, setCreditsDialogOpen] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email.trim() || !password.trim()) return;

    setError(null);
    const endpoint = isRegister ? '/api/auth/register' : '/api/auth/login';

    try {
      const res = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: email.trim(), password }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || 'Authentication failed');
        return;
      }

      onLogin(data.access_token);
    } catch {
      setError('Network error. Please try again.');
    }
  };

  return (
    <>
      <Box sx={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', p: 2 }}>
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
            {isRegister ? 'Create an account to get started' : 'Sign in to your account'}
          </Typography>
          <form onSubmit={handleSubmit}>
            <Stack spacing={2}>
              <TextField
                type="email"
                label="Email"
                value={email}
                onChange={e => { setEmail(e.target.value); setError(null); }}
                fullWidth
                autoFocus
              />
              <TextField
                type="password"
                label="Password"
                value={password}
                onChange={e => { setPassword(e.target.value); setError(null); }}
                fullWidth
                error={!!error}
                helperText={error || ''}
              />
              <Button type="submit" variant="contained" fullWidth disabled={!email.trim() || !password.trim()}>
                {isRegister ? 'Sign Up' : 'Sign In'}
              </Button>
              <Button
                variant="text"
                onClick={() => { setIsRegister(!isRegister); setError(null); }}
                sx={{ textTransform: 'none' }}
              >
                {isRegister ? 'Already have an account? Sign In' : "Don't have an account? Sign Up"}
              </Button>
            </Stack>
          </form>
        </Paper>

        <Box sx={{ mt: 4, textAlign: 'center' }}>
          <Typography variant="body2" color="textSecondary">
            Created by{' '}
            <MuiLink href="https://benpiper.com" target="_blank" rel="noopener noreferrer" sx={{ textDecoration: 'none' }}>
              Ben Piper
            </MuiLink>
            {' • '}
            <MuiLink href="https://github.com/benpiper/unmuted" target="_blank" rel="noopener noreferrer" sx={{ textDecoration: 'none' }}>
              GitHub
            </MuiLink>
            {' • '}
            <MuiLink component="button" onClick={() => setCreditsDialogOpen(true)} sx={{ textDecoration: 'none', cursor: 'pointer' }}>
              About
            </MuiLink>
          </Typography>
        </Box>
      </Box>

      <Dialog open={creditsDialogOpen} onClose={() => setCreditsDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ fontWeight: 700 }}>About Unmuted</DialogTitle>
        <DialogContent sx={{ pt: 3 }}>
          <Typography variant="h6" gutterBottom sx={{ fontWeight: 700 }}>
            AI-Powered Technical Video Narrations
          </Typography>
          <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
            Unmuted is designed to turn your screen recording captures into polished, technical how-to videos fit for public consumption using Vision-Language Models.
          </Typography>

          <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1 }}>
            Created by
          </Typography>
          <Typography variant="body2" sx={{ mb: 2 }}>
            <MuiLink href="https://benpiper.com" target="_blank" rel="noopener noreferrer">
              Ben Piper
            </MuiLink>
          </Typography>

          <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1 }}>
            Open Source
          </Typography>
          <Typography variant="body2">
            <MuiLink href="https://github.com/benpiper/unmuted" target="_blank" rel="noopener noreferrer">
              View on GitHub
            </MuiLink>
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreditsDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </>
  );
}

function usePersistentState(key, defaultValue) {
  const [state, setState] = useState(() => {
    const saved = localStorage.getItem(key);
    if (saved !== null) {
      try {
        return JSON.parse(saved);
      } catch {
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
  const [planningStatus, setPlanningStatus] = useState(''); // Tracks current phase during planning
  const [toolContext, setToolContext] = usePersistentState('unmuted_toolContext', '');
  const [transcriptData, setTranscriptData] = usePersistentState('unmuted_transcriptData', []);
  const [isSaved, setIsSaved] = usePersistentState('unmuted_isSaved', false);
  const [optimizing, setOptimizing] = useState(false);
  const [generateOverlay, setGenerateOverlay] = usePersistentState('unmuted_generateOverlay', false);
  const [token, setToken] = useState(() => localStorage.getItem('unmuted_token'));
  const [isAdmin, setIsAdmin] = useState(false);
  const [creditsDialogOpen, setCreditsDialogOpen] = useState(false);
  const [initialized, setInitialized] = useState(null);
  const [ttsStatus, setTtsStatus] = useState('idle');
  const [ttsVoice, setTtsVoice] = useState('nova');
  const [isThrottled, setIsThrottled] = useState(false);
  const throttleTimeoutRef = React.useRef(null);

  const apiFetch = useCallback((url, options = {}) => {
    const stored = localStorage.getItem('unmuted_token');
    return fetch(url, {
      ...options,
      headers: {
        ...(options.headers || {}),
        ...(stored ? { 'Authorization': `Bearer ${stored}` } : {}),
      },
    }).then(res => {
      if (res.status === 401) setToken(null);
      if (res.status === 429 || res.headers.get('X-Throttled') === 'true') {
        setIsThrottled(true);
        clearTimeout(throttleTimeoutRef.current);
        throttleTimeoutRef.current = setTimeout(() => setIsThrottled(false), 3000);
      }
      return res;
    });
  }, []);

  useEffect(() => {
    if (token) {
      localStorage.setItem('unmuted_token', token);
      // Fetch profile to check if admin
      apiFetch(`${API_BASE}/api/auth/me`).then(res => res.json()).then(data => {
        if (data.is_admin) setIsAdmin(true);
        else setIsAdmin(false);
      }).catch(() => { });
    } else {
      localStorage.removeItem('unmuted_token');
      setIsAdmin(false);
    }
  }, [token, apiFetch]);

  useEffect(() => {
    const checkInitialization = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/auth/status`);
        const data = await res.json();
        setInitialized(data.initialized);
      } catch (e) {
        console.error('Error checking initialization:', e);
        setInitialized(false);
      }
    };
    checkInitialization();
  }, []);


  const mediaUrl = useCallback((url) => url, []);

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
    } catch {
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
          use_rag: false,
          rag_max_frames: 10,
          generate_overlay: generateOverlay,
          synopsis: synopsisOverride || selectedSynopsis,
          tools_context: toolContext
        })
      });
      const data = await res.json();

      if (!abortRef.current && data.success && data.job_id) {
        // Poll for job completion
        await pollJobCompletion(data.job_id);
      } else if (!abortRef.current) {
        alert("Error running auto-finish via backend.");
        setMode('done');
      }
    } catch (e) {
      console.error(e);
      if (!abortRef.current) setMode('done');
    }
  };

  const pollJobCompletion = useCallback(async (jobId) => {
    const maxAttempts = 600; // 10 minutes with 1s polling
    let attempts = 0;

    while (!abortRef.current && attempts < maxAttempts) {
      try {
        const res = await apiFetch(`${API_BASE}/api/jobs/${jobId}/status`, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
        });
        const jobStatus = await res.json();

        // Show throttle indicator if API is rate-limited
        if (jobStatus.throttled) {
          setIsThrottled(true);
          clearTimeout(throttleTimeoutRef.current);
          throttleTimeoutRef.current = setTimeout(() => setIsThrottled(false), 3000);
        }

        if (jobStatus.status === 'complete') {
          if (!abortRef.current && jobStatus.result) {
            setTranscriptData(jobStatus.result.transcript || []);
            setHistory((jobStatus.result.transcript || []).map(t => t.narration));
            setMode('done');
          }
          return;
        } else if (jobStatus.status === 'failed') {
          if (!abortRef.current) {
            alert(`Auto-finish job failed: ${jobStatus.error || 'Unknown error'}`);
            setMode('done');
          }
          return;
        } else if (jobStatus.status === 'cancelled') {
          if (!abortRef.current) {
            setMode('done');
          }
          return;
        }
      } catch (e) {
        console.error('Error checking job status:', e);
      }

      // Wait before polling again
      await new Promise(resolve => setTimeout(resolve, 1000));
      attempts++;
    }

    if (!abortRef.current) {
      alert('Auto-finish job timed out.');
      setMode('done');
    }
  }, [apiFetch, setTranscriptData, setHistory, setMode]);

  const generateSynopsises = async (plan, workDir, total, _fps, autoFinish, tools = '') => {
    console.log('[generateSynopsises] Starting, mode should be planning_loading');
    setGeneratingSynopsis(true);
    setPlanningStatus('Generating narrative synopsises...');
    try {
      console.log('[generateSynopsises] Calling /api/project/synopsises...');
      const synopsisStart = Date.now();
      const res = await apiFetch(`${API_BASE}/api/project/synopsises`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ story_plan: plan, prompt, tool_context: tools })
      });
      const synopsisDuration = Date.now() - synopsisStart;
      console.log(`[generateSynopsises] Synopsises call completed in ${synopsisDuration}ms`);
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
        console.log('[generateSynopsises] Auto-finishing with synopsis');
        startAutoFinishAll(workDir, total, _fps, plan, data.synopsises[0]);
      } else if (autoFinish) {
        console.log('[generateSynopsises] Auto-finishing without synopsis');
        startAutoFinishAll(workDir, total, _fps, plan);
      } else {
        console.log('[generateSynopsises] Setting mode to planning');
        setMode('planning');
        setPlanningStatus('');
      }
    } catch (e) {
      console.error("Error generating synopsises:", e);
      setSynopsises([]);
      if (autoFinish) {
        console.log('[generateSynopsises] Error - auto-finishing anyway');
        startAutoFinishAll(workDir, total, _fps, plan);
      } else {
        console.log('[generateSynopsises] Error - setting mode to planning');
        setMode('planning');
        setPlanningStatus('');
      }
    } finally {
      setGeneratingSynopsis(false);
    }
  };

  const generateStrategicPlan = async (workDir, total, _fps, autoFinish, tools = '') => {
    console.log('[generateStrategicPlan] Setting mode to planning_loading');
    setMode('planning_loading');
    setPlanningStatus('Generating outline from video...');
    try {
      console.log('[generateStrategicPlan] Calling /api/project/plan...');
      const planStart = Date.now();
      const res = await apiFetch(`${API_BASE}/api/project/plan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ directory_path: workDir, prompt, context, tool_context: tools })
      });
      const planDuration = Date.now() - planStart;
      console.log(`[generateStrategicPlan] Plan call completed in ${planDuration}ms`);
      const data = await res.json();
      if (data.success) {
        console.log('[generateStrategicPlan] Plan successful, calling generateSynopsises...');
        setStoryPlan(data.plan || []);
        setPlanningStatus('Generating narrative synopsises...');
        generateSynopsises(data.plan || [], workDir, total, _fps, autoFinish, tools);
      } else {
        console.error('[generateStrategicPlan] Plan failed:', data);
        alert("Error analyzing video for story plan");
        setMode('setup');
        setPlanningStatus('');
      }
    } catch (e) {
      console.error('[generateStrategicPlan] Exception:', e);
      alert("Error generating plan");
      setMode('setup');
      setPlanningStatus('');
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
    } catch {
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
          use_rag: false,
          rag_max_frames: 10,
          generate_overlay: generateOverlay,
          synopsis: selectedSynopsis,
          tools_context: toolContext
        })
      });
      const data = await res.json();
      if (data.success) {
        let cands = data.data.candidates;

        setCandidates(cands);
        setCurrentTimestamp(data.data.timestamp);

        // Use existing transcript data if available, otherwise fallback to first candidate
        if (currentTranscript && currentTranscript.length > index) {
          setCustomNarration(currentTranscript[index].narration);
          setCustomOverlay(currentTranscript[index].overlay);
        } else if (cands.length > 0) {
          setCustomNarration(cands[0].narration || '');
          setCustomOverlay(cands[0].overlay || '');
        }

        setCandidatesCache(prev => ({ ...prev, [index]: { candidates: cands, timestamp: data.data.timestamp } }));
        setFrameIndex(index);
      }
    } catch {
      alert("Error fetching candidates for frame.");
    } finally {
      setLoading(false);
    }
  };

  const resumeAutoFinish = useCallback(async () => {
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
          use_rag: false,
          rag_max_frames: 10,
          generate_overlay: generateOverlay,
          synopsis: selectedSynopsis,
          tools_context: toolContext
        })
      });
      const data = await res.json();

      if (!abortRef.current && data.success && data.job_id) {
        // Poll for job completion
        await pollJobCompletion(data.job_id);
      } else if (!abortRef.current) {
        alert("Error running auto-finish via backend.");
        setMode('done');
      }
    } catch (e) {
      console.error("Error resuming auto finish", e);
      if (!abortRef.current) setMode('done');
    }
  }, [directory, prompt, context, frameIndex, history, fps, transcriptData, storyPlan, generateOverlay, selectedSynopsis, toolContext, apiFetch, pollJobCompletion, setMode]);

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
  }, [mode, resumeAutoFinish, setMode]);

  const commitNext = () => {
    const item = { timestamp: currentTimestamp, narration: customNarration, overlay: customOverlay };

    let newTranscript = [...transcriptData];
    let newHistory = [...history];

    if (frameIndex < newTranscript.length) {
      // Overwrite existing commit if user went backwards and edited
      newTranscript[frameIndex] = item;
      newHistory[frameIndex] = customNarration;
    } else {
      // Append new commit
      newTranscript.push(item);
      newHistory.push(customNarration);
    }

    setTranscriptData(newTranscript);
    setHistory(newHistory);

    if (frameIndex + 1 < totalFrames) {
      const nextIndex = frameIndex + 1;
      setFrameIndex(nextIndex);

      const cached = candidatesCache[nextIndex];
      if (cached) {
        setCandidates(cached.candidates);
        setCurrentTimestamp(cached.timestamp);

        // Restore user's previous selection if they already committed this frame
        if (nextIndex < newTranscript.length) {
          setCustomNarration(newTranscript[nextIndex].narration);
          setCustomOverlay(newTranscript[nextIndex].overlay);
        } else if (cached.candidates.length > 0) {
          setCustomNarration(cached.candidates[0].narration || '');
          setCustomOverlay(cached.candidates[0].overlay || '');
        }
      } else {
        fetchCandidates(nextIndex, newHistory, newTranscript);
      }
    } else {
      setMode('done');
    }
  };

  const goBack = () => {
    if (frameIndex > 0) {
      const newIndex = frameIndex - 1;
      setFrameIndex(newIndex);

      const cached = candidatesCache[newIndex];
      if (cached) {
        setCandidates(cached.candidates);
        setCurrentTimestamp(cached.timestamp);

        // Load the user's previously committed text instead of candidate 0
        if (newIndex < transcriptData.length) {
          setCustomNarration(transcriptData[newIndex].narration);
          setCustomOverlay(transcriptData[newIndex].overlay);
        } else if (cached.candidates.length > 0) {
          setCustomNarration(cached.candidates[0].narration || '');
          setCustomOverlay(cached.candidates[0].overlay || '');
        }
      } else {
        fetchCandidates(newIndex, history.slice(0, newIndex), transcriptData);
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
            use_rag: false,
            rag_max_frames: 10,
            generate_overlay: generateOverlay,
            synopsis: selectedSynopsis,
            tools_context: toolContext
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
    } catch {
      alert("Error checking connection.");
    } finally {
      setLoading(false);
    }
  };

  const synthesizeVoiceover = async () => {
    if (!directory || !isSaved) return;
    setTtsStatus('running');
    try {
      const res = await apiFetch(`${API_BASE}/api/project/synthesize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ directory_path: directory, voice: ttsVoice })
      });
      const data = await res.json();
      if (!data.success || !data.job_id) {
        setTtsStatus('failed');
        return;
      }
      await pollTtsJob(data.job_id);
    } catch (e) {
      console.error('TTS synthesis error', e);
      setTtsStatus('failed');
    }
  };

  const pollTtsJob = async (jobId) => {
    const maxAttempts = 600;
    let attempts = 0;
    while (attempts < maxAttempts) {
      try {
        const res = await apiFetch(`${API_BASE}/api/jobs/${jobId}/status`);
        const s = await res.json();
        if (s.throttled) {
          setIsThrottled(true);
          clearTimeout(throttleTimeoutRef.current);
          throttleTimeoutRef.current = setTimeout(() => setIsThrottled(false), 3000);
        }
        if (s.status === 'complete') { setTtsStatus('done'); return; }
        if (s.status === 'failed') { setTtsStatus('failed'); return; }
        if (s.status === 'cancelled') { setTtsStatus('idle'); return; }
      } catch (e) {
        console.error('TTS poll error', e);
      }
      await new Promise(r => setTimeout(r, 1000));
      attempts++;
    }
    setTtsStatus('failed');
  };

  if (initialized === null) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
          <CircularProgress />
        </Box>
      </ThemeProvider>
    );
  }

  if (!initialized && !token) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <SetupScreen onSetupComplete={setToken} theme={theme} />
      </ThemeProvider>
    );
  }

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
              {isAdmin && (
                <Button
                  color="inherit"
                  onClick={() => setMode(mode === 'admin' ? 'setup' : 'admin')}
                  sx={{ fontWeight: 'bold' }}
                >
                  {mode === 'admin' ? 'Back to Projects' : 'Admin Panel'}
                </Button>
              )}
              <Tooltip title="About & Credits">
                <IconButton onClick={() => setCreditsDialogOpen(true)} color="inherit">
                  <InfoIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title={`Switch to ${themeMode === 'dark' ? 'light' : 'dark'} mode`}>
                <IconButton onClick={() => setThemeMode(themeMode === 'dark' ? 'light' : 'dark')} color="inherit">
                  {themeMode === 'dark' ? <LightModeIcon /> : <DarkModeIcon />}
                </IconButton>
              </Tooltip>
              <Tooltip title="Sign out">
                <IconButton onClick={async () => {
                  if (token) {
                    try {
                      await apiFetch(`${API_BASE}/api/auth/logout`, { method: 'POST' });
                    } catch (e) {
                      console.error('Logout error:', e);
                    }
                  }
                  setToken(null);
                }} color="inherit">
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

        {isThrottled && (
          <Box sx={{ backgroundColor: theme.palette.mode === 'dark' ? '#5a4a00' : '#fff3cd', p: 2, borderBottom: '1px solid', borderColor: theme.palette.mode === 'dark' ? '#9d8c00' : '#ffc107' }}>
            <Typography variant="body2" sx={{ color: theme.palette.mode === 'dark' ? '#ffeb3b' : '#856404' }}>
              ⚠️ Server is temporarily throttled. Requests may be slower than usual.
            </Typography>
          </Box>
        )}

        {mode === 'setup' && (
          <Container maxWidth="md" sx={{ py: 4 }} className="fade-in-up">
            <Paper sx={{ p: 4, borderRadius: '24px' }}>
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

                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mt: 2, pt: 2 }}>
                  <Box>
                    <Typography variant="subtitle1" fontWeight="bold">Generate Overlay Text</Typography>
                    <Typography variant="body2" color="textSecondary">Generate overlay text for each segment.</Typography>
                  </Box>
                  <input type="checkbox" checked={generateOverlay} onChange={e => setGenerateOverlay(e.target.checked)} style={{ width: 24, height: 24 }} />
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
              <Box sx={{ mb: 4, display: 'flex', justifyContent: 'center' }}>
                <div className="custom-spinner" />
              </Box>
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
              <Box sx={{ mb: 4, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 3 }}>
                <div className="custom-spinner" />
                <Box>
                  <Typography variant="body2" color="textSecondary" sx={{ fontSize: '0.75rem', mb: 1 }}>
                    {generatingSynopsis ? 'Step 2/2' : 'Step 1/2'}
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={generatingSynopsis ? 75 : 40}
                    sx={{ width: 80, height: 6, borderRadius: 1 }}
                  />
                </Box>
              </Box>
              <Typography variant="h5" gutterBottom sx={{ fontWeight: 700 }}>
                Generating Outline...
              </Typography>
              <Typography variant="body1" color="textSecondary" sx={{ mb: 2 }}>
                The AI is analyzing the entire video to build a high-level narrative outline before frame-by-frame processing begins.
              </Typography>
              {planningStatus && (
                <Typography variant="body2" sx={{ p: 2, bgcolor: 'action.hover', borderRadius: 1, mb: 2 }}>
                  {planningStatus}
                </Typography>
              )}
              {generatingSynopsis && (
                <Box sx={{ mt: 3, pt: 3, borderTop: '1px solid', borderColor: 'divider' }}>
                  <Typography variant="body2" color="textSecondary">
                    ✓ Plan generated • Now generating synopsises...
                  </Typography>
                </Box>
              )}
            </Paper>
          </Container>
        )}

        {mode === 'planning' && (
          <Container maxWidth="md" sx={{ py: 4 }} className="fade-in-up">
            <Paper sx={{ p: 4 }}>
              <Typography variant="h5" gutterBottom sx={{ fontWeight: 700 }}>
                Outline
              </Typography>
              <Typography variant="body1" color="textSecondary" sx={{ mb: 3 }}>
                The AI has generated a high-level outline of the task based on keyframes. This plan will guide the frame-by-frame narration and self-correction engine. You can edit this plan before proceeding.
              </Typography>

              <Stack spacing={2} sx={{ mb: 4 }}>
                {storyPlan.map((step, idx) => (
                  <Box key={idx} sx={{ display: 'flex', gap: 1, alignItems: 'flex-start' }}>
                    <TextField
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
                    <Tooltip title="Delete task">
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => {
                          const newPlan = storyPlan.filter((_, i) => i !== idx);
                          setStoryPlan(newPlan);
                        }}
                        sx={{ mt: 0.5 }}
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </Box>
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

          <Container maxWidth="xl" sx={{ py: 3 }} className="fade-in-up">
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
                      <Paper variant="outlined" sx={{ p: 3, background: theme.palette.customTimeline.bg, maxHeight: '300px', overflowY: 'auto' }}>
                        <Stack spacing={0}>
                          {transcriptData.map((t, idx) => (
                            <Box key={idx} sx={{ display: 'flex', position: 'relative' }}>
                              {/* Line connecting nodes */}
                              {idx < transcriptData.length - 1 && (
                                <Box sx={{ position: 'absolute', left: '11px', top: '24px', bottom: '-8px', width: '2px', bgcolor: 'primary.main', opacity: 0.2 }} />
                              )}
                              {/* Timeline Node */}
                              <Box sx={{ mt: '6px', mr: 2, zIndex: 1 }}>
                                <Box sx={{ width: 24, height: 24, borderRadius: '50%', bgcolor: 'primary.main', color: 'primary.contrastText', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.65rem', fontWeight: 'bold', boxShadow: `0 0 0 4px ${alpha(theme.palette.primary.main, 0.1)}` }}>
                                  {idx + 1}
                                </Box>
                              </Box>
                              {/* Content */}
                              <Box sx={{ pb: 3, flex: 1 }}>
                                <Typography variant="caption" sx={{ color: 'primary.main', fontWeight: 800 }}>{t.timestamp}</Typography>
                                <Typography variant="body2" sx={{ mt: 0.5, lineHeight: 1.5 }}>{t.narration}</Typography>
                              </Box>
                            </Box>
                          ))}
                        </Stack>
                        {transcriptData.length === 0 && (
                          <Box sx={{ textAlign: 'center', py: 4, opacity: 0.5 }}>
                            <Typography variant="body2">No events recorded yet.</Typography>
                            <Typography variant="caption" sx={{ display: 'block' }}>Complete the first frame to see your timeline build.</Typography>
                          </Box>
                        )}
                      </Paper>
                    </Box>

                    {loading ? (
                      <Box sx={{ py: 6, textAlign: 'center' }}>
                        <Box sx={{ mb: 2, display: 'flex', justifyContent: 'center' }}>
                          <div className="custom-spinner" style={{ width: 40, height: 40, borderWidth: 3 }} />
                        </Box>
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

        {mode === 'admin' && (
          <Container maxWidth="xl">
            <AdminDashboard apiFetch={apiFetch} apiBase={API_BASE} />
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
              <div className="custom-spinner" style={{ width: 40, height: 40, borderWidth: 3, margin: '0 auto' }} />
            </Paper>
          </Container>
        )}

        {mode === 'done' && (
          <Container maxWidth="xl" sx={{ py: 3 }} className="fade-in-up">
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
                  <Stack direction="row" spacing={1} sx={{ alignItems: 'center' }}>
                    <Select
                      value={ttsVoice}
                      onChange={(e) => setTtsVoice(e.target.value)}
                      size="small"
                      disabled={ttsStatus === 'running'}
                      sx={{ minWidth: 120 }}
                    >
                      <MenuItem value="echo">Echo</MenuItem>
                      <MenuItem value="fable">Fable</MenuItem>
                      <MenuItem value="onyx">Onyx</MenuItem>
                      <MenuItem value="nova">Nova</MenuItem>
                      <MenuItem value="shimmer">Shimmer</MenuItem>
                    </Select>
                    <Button
                      variant="outlined"
                      size="large"
                      onClick={synthesizeVoiceover}
                      disabled={!isSaved || ttsStatus === 'running'}
                      startIcon={ttsStatus === 'running' ? <CircularProgress size={18} color="inherit" /> : null}
                    >
                      {ttsStatus === 'running' ? 'Synthesizing...' : 'Synthesize Voiceover'}
                    </Button>
                  </Stack>

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
                  {ttsStatus === 'done' && (
                    <Button
                      component="a"
                      href={mediaUrl(`${API_BASE}/api/project/download/audio?directory_path=${encodeURIComponent(directory)}`)}
                      download="narration.mp3"
                      startIcon={<span>⬇️</span>}
                      variant="outlined"
                      color="secondary"
                    >
                      Download Audio
                    </Button>
                  )}
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

        <Dialog open={creditsDialogOpen} onClose={() => setCreditsDialogOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle sx={{ fontWeight: 700 }}>About Unmuted</DialogTitle>
          <DialogContent sx={{ pt: 3 }}>
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 700 }}>
              AI-Powered Technical Video Narrations
            </Typography>
            <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
              Unmuted is designed to turn your screen recording captures into polished, technical how-to videos fit for public consumption using Vision-Language Models.
            </Typography>

            <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1 }}>
              Created by
            </Typography>
            <Typography variant="body2" sx={{ mb: 2 }}>
              <MuiLink href="https://benpiper.com" target="_blank" rel="noopener noreferrer">
                Ben Piper
              </MuiLink>
            </Typography>

            <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1 }}>
              Open Source
            </Typography>
            <Typography variant="body2">
              <MuiLink href="https://github.com/benpiper/unmuted" target="_blank" rel="noopener noreferrer">
                View on GitHub
              </MuiLink>
            </Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setCreditsDialogOpen(false)}>Close</Button>
          </DialogActions>
        </Dialog>

      </div>
    </ThemeProvider>
  );
}

export default App;
