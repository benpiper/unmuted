import React, { useState, useEffect } from 'react';
import './App.css';

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
  const [directory, setDirectory] = usePersistentState('unmuted_directory', '/home/user/unmuted');
  const [prompt, setPrompt] = usePersistentState('unmuted_prompt', 'Create a technical how-to video transcript for this screen recording.');
  const [context, setContext] = usePersistentState('unmuted_context', '');
  const [interval, setIntervalVal] = usePersistentState('unmuted_interval', 3);
  const [theme, setTheme] = usePersistentState('unmuted_theme', 'dark');
  
  const [loading, setLoading] = useState(false);
  const [videoFile, setVideoFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  
  const [totalFrames, setTotalFrames] = usePersistentState('unmuted_totalFrames', 0);
  const [fps, setFps] = usePersistentState('unmuted_fps', 1);
  const [frameIndex, setFrameIndex] = usePersistentState('unmuted_frameIndex', 0);
  const [candidates, setCandidates] = usePersistentState('unmuted_candidates', []);
  const [history, setHistory] = usePersistentState('unmuted_history', []);
  const [customNarration, setCustomNarration] = usePersistentState('unmuted_customNarration', '');
  const [customOverlay, setCustomOverlay] = usePersistentState('unmuted_customOverlay', '');
  const [currentTimestamp, setCurrentTimestamp] = usePersistentState('unmuted_currentTimestamp', '');
  
  const [transcriptData, setTranscriptData] = usePersistentState('unmuted_transcriptData', []);
  const [isSaved, setIsSaved] = usePersistentState('unmuted_isSaved', false);
  const [optimizing, setOptimizing] = useState(false);

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
      const res = await fetch('http://localhost:8000/api/project/optimize', {
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

  const startAutoFinishAll = async (workDir, total, _fps) => {
    abortRef.current = false;
    setMode('autofinish');
    setTranscriptData([]);
    setHistory([]);
    let currentIndex = 0;
    let currentT = [];
    let currentH = [];
    
    while (currentIndex < total) {
      if (abortRef.current) break;
      setFrameIndex(currentIndex);
      try {
        const res = await fetch('http://localhost:8000/api/project/frame_candidates', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            directory_path: workDir,
            prompt,
            context,
            frame_index: currentIndex,
            history: currentH,
            fps: _fps
          })
        });
        const data = await res.json();
        
        if (abortRef.current) break;

        if (data.success && data.data.candidates.length > 0) {
          const topLLM = data.data.candidates[0];
          const autoItem = {
             timestamp: data.data.timestamp,
             narration: topLLM.narration,
             overlay: topLLM.overlay
          };
          if (!(currentT.length > 0 && currentT[currentT.length - 1].narration === autoItem.narration)) {
             currentT = [...currentT, autoItem];
             currentH = [...currentH, autoItem.narration];
             setTranscriptData(currentT);
             setHistory(currentH);
          }
        }
      } catch (e) {
        console.error(e);
        break;
      }
      currentIndex++;
    }
    if (!abortRef.current) setMode('done');
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
        const uploadRes = await fetch('http://localhost:8000/api/project/upload', {
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
        
        const extractRes = await fetch('http://localhost:8000/api/project/extract', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ directory_path: workDir, interval: Number(interval) })
        });
        const extractData = await extractRes.json();
        
        if (extractData.success) {
            setTotalFrames(extractData.total_frames);
            setFps(extractData.fps);
            if (autoFinish) {
               startAutoFinishAll(workDir, extractData.total_frames, extractData.fps);
            } else {
               setMode('review');
               fetchCandidates(0, [], [], workDir);
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
      const res = await fetch('http://localhost:8000/api/project/frame_candidates', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          directory_path: activeDir,
          prompt,
          context,
          frame_index: index,
          history: currentHistory,
          fps
        })
      });
      const data = await res.json();
      if (data.success) {
        let cands = data.data.candidates;
        
        if (currentHistory.length > 0 && currentTranscript && currentTranscript.length > 0) {
          const carryOverCand = {
            narration: currentHistory[currentHistory.length - 1],
            overlay: currentTranscript[currentTranscript.length - 1].overlay
          };
          cands = [carryOverCand, ...cands];
        }

        setCandidates(cands);
        setCurrentTimestamp(data.data.timestamp);
        if (cands.length > 0) {
          setCustomNarration(cands[0].narration || '');
          setCustomOverlay(cands[0].overlay || '');
        }
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
    let currentIndex = frameIndex;
    let currentT = [...transcriptData];
    let currentH = [...history];

    while (currentIndex < totalFrames) {
      if (abortRef.current) break;
      setFrameIndex(currentIndex);
      
      try {
        const res = await fetch('http://localhost:8000/api/project/frame_candidates', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            directory_path: directory,
            prompt,
            context,
            frame_index: currentIndex,
            history: currentH,
            fps
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
        console.error("Error resuming auto finish", e);
        break;
      }
      
      currentIndex++;
    }
    
    if (!abortRef.current) setMode('done');
  };

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

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
        const res = await fetch('http://localhost:8000/api/project/frame_candidates', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            directory_path: directory,
            prompt,
            context,
            frame_index: currentIndex,
            history: currentH,
            fps
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
      const res = await fetch('http://localhost:8000/api/project/save', {
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

  return (
    <div className="app-container">
      <header className="header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '1rem' }}>
        <div style={{ flex: 1, textAlign: 'left' }}>
          <h1 style={{margin: 0}}>🎙️ unmuted</h1>
          <p style={{margin: '5px 0 0 0'}}>AI-Powered Technical Video Narrations</p>
        </div>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <button 
            className="btn-secondary" 
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            style={{ width: '45px', height: '45px', padding: 0, fontSize: '1.2rem', borderRadius: '50%' }}
            title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
          >
            {theme === 'dark' ? '☀️' : '🌙'}
          </button>
          {mode !== 'setup' && (
            <button className="btn-secondary" onClick={handleCancel} style={{ borderColor: '#ef4444', color: '#ef4444' }}>
              Cancel / Restart
            </button>
          )}
        </div>
      </header>

      {mode === 'setup' && (
        <main className="dashboard card flow">
          <h2>Project Setup</h2>
          <div className="input-group">
            <label>Upload Screen Recording (.mp4, .mov)</label>
            <input
              type="file"
              accept="video/*"
              onChange={e => setVideoFile(e.target.files[0])}
              className="glass-input"
              style={{ padding: '0.8rem', outline: 'none' }}
            />
          </div>
          <div className="input-group">
            <label>Describe the video</label>
            <textarea
              value={prompt}
              onChange={e => setPrompt(e.target.value)}
              className="glass-input"
              rows={3}
            />
          </div>
          <div className="input-group">
            <label>Technical Context / Tools (e.g. Linux, Python, React)</label>
            <input
              type="text"
              value={context}
              onChange={e => setContext(e.target.value)}
              className="glass-input"
              placeholder="Leave blank if n/a"
            />
          </div>
          <div className="input-group">
            <label>Analysis Interval (Seconds)</label>
            <input
              type="number"
              value={interval}
              onChange={e => setIntervalVal(e.target.value)}
              className="glass-input"
              min="1"
            />
          </div>

          <div className="actions" style={{display: 'flex', gap: '1rem', flexWrap: 'wrap'}}>
            <button onClick={() => handleUploadAndExtract(false)} className="btn-primary" disabled={!videoFile || uploading}>
              {uploading && !isAutoProcessAll ? 'Setting up...' : 'Upload & Start Review'}
            </button>
            <button onClick={() => handleUploadAndExtract(true)} className="btn-secondary" disabled={!videoFile || uploading} style={{ borderColor: '#10b981', color: '#10b981' }}>
              {uploading && isAutoProcessAll ? 'Extracting...' : 'Upload & Auto-Process All'}
            </button>
          </div>
        </main>
      )}

      {mode === 'extracting' && (
        <main className="card" style={{textAlign: 'center', padding: '50px'}}>
          <div className="spinner" style={{margin: '0 auto 20px'}} />
          <h2>Uploading & Initializing...</h2>
          <p>Please wait while your video is uploaded and evaluated by the vision engine.</p>
        </main>
      )}

      {mode === 'review' && (
        <main className="review-view card">
          <div className="view-header">
            <h2>Interactive Review: Frame {frameIndex + 1} of {totalFrames}</h2>
            <span style={{opacity: 0.7}}>Timestamp: {currentTimestamp}</span>
          </div>
          
          <div className="review-layout">
            <div className="frame-preview">
               <div className="media-item" style={{ textAlign: 'center', background: 'var(--media-bg)', padding: '1rem', borderRadius: '8px', resize: 'vertical', overflow: 'hidden', height: '35vh', minHeight: '15vh', flexShrink: 0, display: 'flex', flexDirection: 'column' }}>
                  <p style={{fontSize: '1.2rem', fontWeight: 'bold', margin: '0 0 10px 0', color: 'var(--accent-color)', flexShrink: 0}}>Source Video Playback</p>
                  <video 
                     controls 
                     src={`http://localhost:8000/api/project/video?directory_path=${encodeURIComponent(directory)}`} 
                     style={{ width: '100%', height: '100%', minHeight: 0, objectFit: 'contain', borderRadius: '8px', border: '1px solid var(--media-border)' }} 
                  />
               </div>
               <div className="media-item" style={{ textAlign: 'center', height: '40vh', minHeight: '15vh', flexShrink: 0, display: 'flex', flexDirection: 'column' }}>
                  <p style={{fontSize: '1.2rem', fontWeight: 'bold', margin: '0 0 5px 0', color: 'var(--accent-color)', flexShrink: 0}}>Current Analyzed Frame</p>
                  <img 
                    src={`http://localhost:8000/api/project/frame_image?directory_path=${encodeURIComponent(directory)}&frame_index=${frameIndex}`} 
                    alt="Current Frame" 
                    style={{ width: '100%', height: '100%', objectFit: 'contain', borderRadius: '8px', border: '2px solid var(--accent-color)', boxShadow: 'none' }} 
                  />
               </div>

               <div className="media-item-group" style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                  <div style={{ flex: 1, opacity: 0.7, textAlign: 'center' }}>
                     <p style={{fontSize: '0.9rem', margin: '0 0 5px 0'}}>Previous</p>
                     {frameIndex > 0 ? (
                        <img 
                          src={`http://localhost:8000/api/project/frame_image?directory_path=${encodeURIComponent(directory)}&frame_index=${frameIndex - 1}`}
                          alt="Previous Frame"
                          style={{ width: '100%', borderRadius: '4px' }}
                        />
                     ) : <div style={{width: '100%', aspectRatio: '16/9', background: 'var(--candidate-bg)', borderRadius: '4px'}} />}
                  </div>
                  
                  <div style={{ flex: 1, opacity: 0.7, textAlign: 'center' }}>
                     <p style={{fontSize: '0.9rem', margin: '0 0 5px 0'}}>Next</p>
                     {frameIndex + 1 < totalFrames ? (
                        <img 
                          src={`http://localhost:8000/api/project/frame_image?directory_path=${encodeURIComponent(directory)}&frame_index=${frameIndex + 1}`}
                          alt="Next Frame"
                          style={{ width: '100%', borderRadius: '4px' }}
                        />
                     ) : <div style={{width: '100%', aspectRatio: '16/9', background: 'var(--candidate-bg)', borderRadius: '4px'}} />}
                  </div>
               </div>
            </div>

            <div className="frame-controls flex-col flow scroll-area" style={{ overflowY: 'auto', paddingRight: '1rem' }}>
               <h3 style={{margin: '0'}}>Timeline History</h3>
               <div style={{background: 'var(--timeline-history-bg)', padding: '1rem', borderRadius: '8px'}}>
                 {transcriptData.map((t, idx) => (
                     <div key={idx} style={{marginBottom: '0.5rem', fontSize: '0.9rem', borderLeft: '2px solid var(--accent-color)', paddingLeft: '8px'}}>
                       <strong style={{color: 'var(--accent-color)'}}>{t.timestamp}</strong>: {t.narration}
                     </div>
                 ))}
                 {transcriptData.length === 0 && <span style={{opacity: 0.5}}>No events recorded yet.</span>}
               </div>
               {loading ? (
                   <div style={{ textAlign: 'center', margin: 'auto', padding: '3rem' }}>
                       <div className="spinner" style={{margin: '0 auto 10px'}} />
                       <p>Analyzing frame with LLM...</p>
                   </div>
               ) : (
                   <>
                     {history.length > 0 && (
                       <div style={{ marginBottom: '1rem', padding: '1rem', background: 'var(--info-box-bg)', borderRadius: '8px', borderLeft: '4px solid var(--accent-color)' }}>
                         <h3 style={{ margin: '0 0 0.5rem 0', fontSize: '0.9rem', color: 'var(--accent-color)' }}>Last Selected Narration</h3>
                         <p style={{ margin: 0, fontSize: '0.95rem' }}>{history[history.length - 1]}</p>
                       </div>
                     )}
                     
                     <h3>Candidates</h3>
                     <div className="candidates-list" style={{display: 'flex', flexDirection: 'column', gap: '10px'}}>
                       {candidates.map((c, i) => (
                         <div 
                           key={i} 
                           className="candidate-card"
                           onClick={() => { setCustomNarration(c.narration); setCustomOverlay(c.overlay); }}
                           style={{ 
                             padding: '10px', 
                             background: customNarration === c.narration ? 'var(--candidate-selected-bg)' : 'var(--candidate-bg)', 
                             border: customNarration === c.narration ? '1px solid var(--accent-color)' : '1px solid transparent',
                             borderRadius: '8px', 
                             cursor: 'pointer',
                             transition: '0.2s'
                           }}
                         >
                           <strong>Option {i+1}</strong>: {c.narration} <br/>
                           <span style={{opacity: 0.6, fontSize: '0.8rem'}}>Overlay: {c.overlay}</span>
                         </div>
                       ))}
                     </div>
                     
                     <h3 style={{marginTop: '1rem'}}>Active Narration</h3>
                     <textarea 
                        className="glass-input" 
                        rows={3} 
                        value={customNarration} 
                        onChange={e => setCustomNarration(e.target.value)} 
                     />
                     
                     <h3>Active Overlay</h3>
                     <input 
                        type="text" 
                        className="glass-input" 
                        value={customOverlay} 
                        onChange={e => setCustomOverlay(e.target.value)} 
                     />

                     <div className="actions" style={{marginTop: '2rem'}}>
                        <button className="btn-primary" onClick={commitNext}>Commit & Next</button>
                        <button className="btn-secondary" onClick={commitAutoFinish}>Commit & Auto Finish Rest</button>
                     </div>
                   </>
               )}
            </div>
          </div>
        </main>
      )}

      {mode === 'autofinish' && (
        <main className="card" style={{textAlign: 'center', padding: '50px'}}>
          <h2>Auto-finishing remainder of the video...</h2>
          <p>Processing frame {frameIndex + 1} of {totalFrames}</p>
          <div style={{ maxWidth: '600px', margin: '20px auto' }}>
            <img 
               src={`http://localhost:8000/api/project/frame_image?directory_path=${encodeURIComponent(directory)}&frame_index=${frameIndex}`} 
               alt="Processing Frame" 
               style={{ width: '100%', maxHeight: '40vh', objectFit: 'contain', borderRadius: '8px', border: '2px solid var(--accent-color)', boxShadow: 'none' }} 
            />
          </div>
           {history.length > 0 && (
             <div style={{ maxWidth: '800px', margin: '0 auto 20px', padding: '1rem', background: 'var(--info-box-bg)', borderRadius: '8px', borderLeft: '4px solid var(--accent-color)', textAlign: 'left' }}>
               <h3 style={{ margin: '0 0 0.5rem 0', fontSize: '0.9rem', color: 'var(--accent-color)' }}>Latest Narration (Auto-Generated)</h3>
               <p style={{ margin: 0, fontSize: '0.95rem' }}>{history[history.length - 1]}</p>
             </div>
           )}
          <div className="spinner" style={{margin: '20px auto', flexShrink: 0}} />
        </main>
      )}

      {mode === 'done' && (
        <main className="transcript-view card">
          <div className="view-header" style={{ flexShrink: 0 }}>
            <h2>Transcript Completed! ({transcriptData.length} items)</h2>
            <div style={{ display: 'flex', gap: '10px' }}>
              <button className="btn-secondary" onClick={handleOptimize} disabled={loading || optimizing}>
                {optimizing ? "Optimizing..." : "✨ AI Optimize Timeline"}
              </button>
              <button className="btn-primary" onClick={handleSave} disabled={loading || isSaved || optimizing}>
                {isSaved ? "Assets Generated ✓" : "Generate Export Artifacts"}
              </button>
            </div>
          </div>
          
           {isSaved && (
             <div style={{ display: 'flex', gap: '1rem', flexShrink: 0, marginBottom: '2rem', padding: '1rem', background: 'var(--info-box-bg)', borderRadius: '8px' }}>
                <a className="btn-secondary" href={`http://localhost:8000/api/project/download/json?directory_path=${encodeURIComponent(directory)}`} download="transcript.json" style={{textDecoration: 'none', textAlign: 'center', color: 'var(--text-primary)'}}>⬇️ Download JSON</a>
                <a className="btn-secondary" href={`http://localhost:8000/api/project/download/vtt?directory_path=${encodeURIComponent(directory)}`} download="transcript.vtt" style={{textDecoration: 'none', textAlign: 'center', color: 'var(--text-primary)'}}>⬇️ Download VTT</a>
                <a className="btn-secondary" href={`http://localhost:8000/api/project/download/chapters?directory_path=${encodeURIComponent(directory)}`} download="chapters.txt" style={{textDecoration: 'none', textAlign: 'center', color: 'var(--text-primary)'}}>⬇️ Download Chapters</a>
             </div>
           )}

          <div className="review-layout">
            <div className="frame-preview">
               <div className="media-item" style={{ textAlign: 'center', background: 'var(--media-bg)', padding: '1rem', borderRadius: '8px', resize: 'vertical', overflow: 'hidden', height: '60vh', minHeight: '20vh', flexShrink: 0, display: 'flex', flexDirection: 'column' }}>
                  <p style={{fontSize: '1.2rem', fontWeight: 'bold', margin: '0 0 10px 0', color: 'var(--accent-color)', flexShrink: 0}}>Synchronized Live Playback</p>
                  <video 
                     ref={videoRef}
                     onTimeUpdate={handleTimeUpdate}
                     controls 
                     src={`http://localhost:8000/api/project/video?directory_path=${encodeURIComponent(directory)}`} 
                     style={{ width: '100%', height: '100%', minHeight: 0, objectFit: 'contain', borderRadius: '8px', border: '1px solid var(--media-border)' }} 
                  />
               </div>
            </div>

            <div className="frame-controls timeline" style={{ overflowY: 'auto', paddingRight: '1rem' }}>
              {transcriptData.map((item, idx) => (
                <div 
                  key={idx} 
                  ref={el => timelineRefs.current[idx] = el}
                  className="timeline-item"
                  style={{
                    borderColor: activeIndex === idx ? '#10b981' : 'var(--accent-color)',
                    background: activeIndex === idx ? 'rgba(16, 185, 129, 0.1)' : 'var(--surface-color)',
                    transform: activeIndex === idx ? 'scale(1.02)' : 'none',
                    boxShadow: activeIndex === idx ? '0 4px 15px rgba(16,185,129,0.2)' : 'none',
                    zIndex: activeIndex === idx ? 10 : 1
                  }}
                >
                  <span className="timestamp" style={{ color: activeIndex === idx ? '#10b981' : 'var(--accent-color)' }}>{item.timestamp}</span>
                  <div className="content">
                    <div className="narration">
                      <label>Narration Context</label>
                      <textarea 
                        value={item.narration || item.text || item.description || ''} 
                        onChange={e => handleUpdateItem(idx, 'narration', e.target.value)}
                        className="glass-input" rows={2} 
                      />
                    </div>
                    <div className="overlay">
                      <label>Suggested Highlight Overlay</label>
                      <input 
                        type="text" 
                        value={item.overlay || item.text_overlay || ''} 
                        onChange={e => handleUpdateItem(idx, 'overlay', e.target.value)}
                        className="glass-input" 
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </main>
      )}

    </div>
  );
}

export default App;
