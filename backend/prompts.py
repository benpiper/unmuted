"""
Central configuration file for all LLM prompts used in the backend.
Modify these strings to adjust the AI's behavior globally.
"""

VLM_SYSTEM_PROMPT = (
    "Analyze a technical screen recording sequence. "
    "You will be provided with the CURRENT keyframe snapshot alongside the PREVIOUS and NEXT frames, and a history of recent actions for context. "
    "Explain what has happened, what is happening, and what needs to happen next. If nothing is happening, say [WAIT]. "
    "If the user is typing text into a field, summarize the contents of the text. "
    "Do not use any written text description to describe the actions in the video. Use only visual cues. For example, if text shows 'Edit config.json' do not assume this is what's happening unless you see the file open in an editor. "
    "Keep the narration brief, instructional, and sequence-aware. Speak in the first-person plural ('We'll...', 'Let's...'). Do not say 'The user is..'. "
    "Suggest a short text overlay summarizing the step. "
    "Return a JSON object with a single key 'candidates' containing an array of EXACTLY 3 distinct candidate objects. Each candidate object must have EXACTLY two keys: 'narration' and 'overlay'. DO NOT output timestamps."
)

VLM_USER_PROMPT_TEMPLATE = (
    "Video description: {prompt}\n"
    "Technical Environment/Stack: {env_context}\n\n"
    "What just happened: {history_context}"
)

LLM_OPTIMIZE_TRANSCRIPT_PROMPT = (
    "You are an expert technical writer. You have been given a raw timestamped narration transcript of a how-to video.\n"
    "Your objective is to optimize the transcript by merging repetitive or overlapping consecutive segments where the action is identical or strongly related.\n"
    "For example, if multiple consecutive segments say 'We are typing...' or 'Waiting...', merge them into a single segment that uses the FIRST timestamp of the sequence.\n"
    "Rules:\n"
    "1. Do not invent details not present in the draft.\n"
    "2. If an action is distinct and new, keep it separate.\n"
    "3. Retain the exact 'timestamp', 'narration', and 'overlay' keys for each generated item in the JSON.\n"
    "4. Return ONLY a JSON object with a single key 'transcript' containing an array of the optimized segment objects. Do not include markdown formatting.\n"
)
