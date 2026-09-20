# Aegis Platform Roadmap

A disciplined, phased engineering roadmap for the **Aegis Evidence-First Knowledge Intelligence Platform**.

---

## Current Status: Scaffolding & Foundation Complete

All foundational project scaffolding, configuration management, initial tests, health probes, and enterprise frontend dashboard are verified.

---

## Phase 1 — MVP (Current Milestone Gate)

The MVP scope gate is strictly enforced. No advanced features are permitted until all MVP criteria pass.

### Objectives
- [x] Foundation repository structure & configuration management
- [x] Backend FastAPI application with health check probe
- [x] Frontend React + TypeScript + Tailwind dashboard
- [x] Infrastructure as Code (AWS SAM template for S3, DynamoDB, Lambda)
- [ ] Asynchronous document upload for PDF, TXT, PNG/JPG
- [ ] Document processing lifecycle state machine:
  `UPLOADED` → `PROCESSING` → `EXTRACTING` → `CHUNKING` → `EMBEDDING` → `INDEXING` → `COMPLETED` / `FAILED`
- [ ] Document extraction via Amazon Textract / PyMuPDF with layout preservation
- [ ] Structure-aware chunking preserving `document_id`, `filename`, `page`, `section`, `chunk_id`
- [ ] Embedding generation via Amazon Bedrock Titan Text Embeddings v2
- [ ] Vector indexing in Amazon OpenSearch Serverless
- [ ] Semantic vector retrieval from uploaded documents
- [ ] Bedrock answer synthesis with grounded context
- [ ] Real citation generation (`document_id`, `filename`, `page`, `chunk_id`, `excerpt`, `relevance_score`)
- [ ] Basic claim-level grounding verification and coverage calculation
- [ ] Honest fallback handling when evidence is insufficient
- [ ] MVP automated test suite (Direct question, multi-document, unknown question, similar-but-irrelevant, citation accuracy, conflicting sources)

---

## Phase 2 — Hybrid Retrieval (Post-MVP)

- [ ] `VectorRetriever` for dense semantic embeddings
- [ ] `KeywordRetriever` for BM25 exact keyword/term matching
- [ ] `MetadataRetriever` for section/page/document scoped filtering
- [ ] Reciprocal Rank Fusion (RRF) candidate fusion and deduplication
- [ ] Modular retriever pipeline architecture

---

## Phase 3 — Reranking (Post-MVP)

- [ ] Expand retrieval candidate pool (e.g. Top 30 candidates)
- [ ] Dedicated cross-encoder or neural reranker integration
- [ ] Filter down to Top 8 high-precision evidence chunks for prompt context
- [ ] Configurable reranker interface decoupled from storage layers

---

## Phase 4 — Query Decomposition (Post-MVP)

- [ ] Query classification (Simple vs. Complex / Comparative)
- [ ] Query planner decomposing multi-hop questions into atomic sub-questions
- [ ] Parallel sub-query retrieval and intermediate evidence synthesis
- [ ] Bypass planner for simple direct questions to minimize latency

---

## Phase 5 — Self-Correcting RAG (Post-MVP)

- [ ] Automated claim extraction from draft answers
- [ ] Evidence verification against retrieved chunks
- [ ] Grounding score calculation against threshold (default: 75%)
- [ ] Autonomous query rewrite on insufficient grounding
- [ ] Targeted secondary retrieval and re-generation loop
- [ ] Strict safety ceiling of 3 maximum iterations (never infinite loop)
- [ ] Retrieval trace telemetry recording each iteration

---

## Phase 6 — Knowledge Graph (Post-MVP)

- [ ] Lightweight `GraphStore` abstraction
- [ ] Entity and relationship extraction from document chunks
- [ ] Traceable source references linking graph edges to chunk IDs
- [ ] Subgraph retrieval for entity- and relationship-dense questions

---

## Phase 7 — GraphRAG (Post-MVP)

- [ ] Unified hybrid retrieval combining Vector + Keyword + Metadata + Graph
- [ ] Parallel retrieval orchestration
- [ ] Graph-enhanced evidence fusion and context building
- [ ] Grounded generation over fused graph and text context

---

## Phase 8 — Contradiction Detection (Post-MVP)

- [ ] Cross-document claim comparison
- [ ] Disagreement detection for numbers, dates, policies, and requirements
- [ ] Explicit `CONFLICT DETECTED` UI surfacing with source attribution
- [ ] Zero silent selection between contradictory sources

---

## Phase 9 — Multimodal Expansion (Post-MVP)

- [ ] Audio ingestion pipeline via Amazon Transcribe
- [ ] Audio transcript normalization and structure-aware chunking
- [ ] Video keyframe and transcript ingestion
- [ ] CSV and structured tabular data indexing

---

## Future / Long-Term

- [ ] Autonomous research agent with multi-step exploration
- [ ] Temporal RAG tracking document versions across time
- [ ] Multi-tenant organizational access control and role-based permissions
- [ ] Enterprise SSO and SAML integration
- [ ] Custom domain-specific model fine-tuning and evaluation
- [ ] Automated compliance reporting and audit export
