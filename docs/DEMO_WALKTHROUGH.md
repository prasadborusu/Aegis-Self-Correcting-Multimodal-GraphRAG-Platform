# Aegis: Demonstration Video Walkthrough & Transcription

This guide documents the scenes, questions, and verified outputs featured in the official walkthrough recording: `recordings/aegis_demo_walkthrough.mp4`.

---

## 🎬 Video Summary
- **Format**: MP4 (H.264 / AAC, 1280x720 720p HD) & WebM (VP8)
- **Duration**: 01:11
- **File Location**: `recordings/aegis_demo_walkthrough.mp4` (9.5MB)

---

## ⏱️ Scene-by-Scene Timeline

### 00:00 – 00:15: Capability Overview
- **Question**: `"Hello Aegis, who are you and what can you do?"`
- **Behavior**: Conversational routing identifies meta-query. Returns platform mission, grounding coverage badge, and architecture summary without firing wasteful vector searches.

### 00:15 – 00:27: Factual Extraction (Resume Skills)
- **Question**: `"What technical skills and programming languages are listed in his resume?"`
- **Behavior**: Retrieves from `Durga_Prasad_Paytm_Python_Developer_Intern_Resume.pdf`, outputs exact programming languages, frameworks, cloud services, and tools with `[VERIFIED]` tags and supporting chunk IDs.

### 00:27 – 00:39: Hallucination Defense Explanation
- **Question**: `"What is Aegis and how does it prevent hallucinations?"`
- **Behavior**: Outlines the 3-tier defense: Atomic Claim Decomposition, 75% Grounding Threshold, and Autonomous Self-Correction Query Rewriting.

### 00:39 – 00:52: The Difficult Query (Self-Correction in Action)
- **Question**: `"Cross-reference Durga Prasad's academic percentage with his projects from his resume"`
- **Behavior**:
  - **Pass 1**: Initial retrieval only captures academic records (60% coverage, insufficient).
  - **Autonomous Action**: Query is rewritten to target projects and technical experience.
  - **Pass 2**: Augmented retrieval incorporates resume chunks, achieving consensus grounding with dual citations.
  - **Visual Indicator**: Amber `Self-Corrected (2 Passes)` badge appears on the message.

### 00:52 – 01:00: Reasoning Trace Modal Inspection
- **Action**: Opens *"How Aegis reached this answer >"*.
- **Display**: Highlights the multi-pass audit card showing Pass 1 insufficiency, autonomous query rewrite, Pass 2 consensus, candidate counts, and latency breakdowns.

### 01:00 – 01:05: Citation Context Drawer
- **Action**: Clicks citation badge.
- **Display**: Displays original source document excerpt, relevance score (`94.2%`), and page number.

### 01:05 – 01:11: Repository & Dashboard Telemetry
- **Action**: Smoothly reviews conversation thread, inspects Documents repository, and reviews live cluster telemetry on the Dashboard.
