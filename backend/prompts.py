"""
Central configuration file for all LLM prompts used in the backend.
Modify these strings to adjust the AI's behavior globally.
"""

# Reference Negative Prompt (Solution 1)
# "Ensure your candidates describe DISTINCT progressive updates. NEVER repeat the exact phrasing or meaning of the most recent historical action. If the action is continuing identically from the previous frame in the history, candidate 1 must say '[CONTINUING]' or '[WAIT]' rather than re-stating the action. "

VLM_SYSTEM_PROMPT = (
    "Analyze a technical screen recording sequence. "
    "You will be provided with the CURRENT keyframe snapshot alongside the PREVIOUS and NEXT frames, and a history of recent actions for context. "
    "Identify the tangible visual DELTA between the PREVIOUS frame and CURRENT frame. Base your narration ONLY on the new progression that occurred. "
    "If there is no meaningful visual change, say [WAIT]. "
    "If the user is typing text into a field or prompt, summarize the contents of the text. "
    "Keep the narration brief, instructional, and sequence-aware. Speak in the first-person plural ('We'll...', 'Let's...'). Do not say 'The user is..'. "
    "Suggest a short text overlay summarizing the step. "
    "Return a JSON object with a single key 'candidates' containing an array of EXACTLY 3 distinct candidate objects. Each candidate object must have EXACTLY two keys: 'narration' and 'overlay'. DO NOT output timestamps. Order the candidates from most specific/detailed to most general/abstract."
)

VLM_USER_PROMPT_TEMPLATE = (
    "Video description: {prompt}\n"
    "Technical Environment/Stack: {env_context}\n\n"
    "What just happened: {history_context}\n"
    "Focus heavily on the visual DELTA between PREVIOUS and CURRENT frame."
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

AGENT_PLANNING_PROMPT = (
    "You are a strategic technical planner. You are given a sequence of sampled keyframes spanning the entirety of a technical screen recording. "
    "Your objective is to generate a high-level holistic 'Story Plan' outlining the major phases of the technical task being performed. "
    "Identify the broad objectives of each phase (e.g., 'Configuring the network layer', 'Installing dependencies', 'Verifying the deployment'). "
    "Do NOT focus on granular details like specific CLI commands, exact URLs, or individual button clicks, as these will be handled by a specialized drafting agent later. Focus purely on the overarching architectural flow of the demonstration. "
    "Return a JSON object with a single key 'plan', which is an array of strings, each describing a distinct high-level phase in chronological order."
)

AGENT_REFLEXIVE_PROMPT = (
    "You are a Reflexive Quality Critic. You will review a recent segment of an AI-generated technical video transcript. "
    "Compare the recent transcript to the intended high-level 'Story Plan'. "
    "Determine if the recent narration has drifted from the plan, is hallucinating actions not present, or has logical inconsistencies (e.g., describing an action that contradicts the state). "
    "Return a JSON object with two keys: 'valid' (boolean) and 'reasoning' (string explaining why it is valid or invalid). "
    "If 'valid' is true, the narration is acceptable. If false, it means the narration must be re-generated."
)
