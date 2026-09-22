# Aegis: Judges & Evaluators Quick Verification Guide

This guide enables hackathon judges to verify and test the running Aegis application locally in under 2 minutes.

---

## ⚡ 1-Minute Live Verification

### 1. Verify Self-Correction Engine via CLI
Run the automated verification script to observe two-pass retrieval and query reformulation:
```bash
python -c "from backend.app.rag.orchestrator import RAGOrchestrator; orch = RAGOrchestrator(); res = orch.process_query('Cross-reference Durga Prasad academic percentage with his projects from his resume'); print('Self-Corrected:', res.retrieval_trace['self_correction_triggered']); print('Iterations:', res.retrieval_trace['iterations']); print('Grounding:', res.grounding_coverage)"
```
**Expected Output**:
```text
Self-Corrected: True
Iterations: 2
Grounding: 0.8
```

---

### 2. Run the Full Automated Test Suite
Execute the pytest suite across all subsystems:
```bash
pytest backend/tests/ -v
```
**Verified Suites**:
- `test_self_correction.py` — Verifies Pass 1 insufficiency -> Pass 2 query rewrite.
- `test_trace_generation.py` — Verifies latency breakdown and multi-pass attempt history.
- `test_multi_citations.py` — Verifies dual-document citation extraction and page numbers.
- `test_chunking.py` — Verifies structure-aware PDF chunking with metadata provenance.
- `test_embeddings.py` — Verifies Amazon Bedrock Titan Text Embeddings v2 vector generation.
- `test_health.py` — Verifies AWS subsystem health status reporting.

---

### 3. Launch the Full Stack Locally

#### Backend (FastAPI):
```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```
- OpenAPI Documentation: `http://127.0.0.1:8000/docs`
- Health Endpoint: `http://127.0.0.1:8000/api/v1/health`

#### Frontend (React / Vite):
```bash
cd frontend
npm install
npm run dev
```
- Web Application: `http://localhost:5173` (or `http://localhost:5174`)

---

### 4. Watch the Walkthrough Video
The recorded HD walkthrough video is available directly in the repository:
- `recordings/aegis_demo_walkthrough.mp4` (H.264 Universal format)
- `recordings/aegis_demo_walkthrough.webm` (Web-native format)
