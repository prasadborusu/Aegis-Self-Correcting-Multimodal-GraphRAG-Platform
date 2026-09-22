# Aegis: Implemented Architecture & Demonstrated Scope

> **Transparency Statement**: This document explicitly defines the **demonstrated and verified components** of Aegis versus roadmap/scaffolding components, providing full technical clarity for hackathon judges, evaluators, and production reviewers.

---

## 🏛️ The Proven Core Technical Flow

The core technical achievement demonstrated in Aegis is an evidence-first, self-correcting retrieval and generation pipeline:

```
[Document Ingestion]
   │  (PDF Resumes, Grade Cards, Markdown Guides)
   ▼
[Structure-Aware Extraction (PyMuPDF / fitz)]
   │  (Preserves headings, font sizes, tabular rows, page numbers)
   ▼
[Provenance-Preserving Chunking]
   │  (Chunks linked to doc_id, filename, page_number, section)
   ▼
[Vector & Lexical Indexing]
   │  (Bedrock Titan Text Embeddings v2 [1024-dim] + BM25 Lexical Inverted Index)
   ▼
[Hybrid Multi-Stage Retrieval]
   │  (Semantic similarity + exact keyword matching)
   ▼
[Evidence-Grounded Generation]
   │  (Bedrock Claude / Titan with strict factual claim-tagging rules)
   ▼
[Atomic Claim Verification Engine]
   │  (Claim decomposition -> NLI grounding evaluation against evidence)
   ▼
[Autonomous Self-Correction Loop]
   │  ├─ Grounding >= 75%: Finalized with inline [VERIFIED] tags & citations
   │  └─ Grounding < 75%: Trigger Query Reformulation -> Pass 2 Retrieval
   ▼
[Traceability & Auditability]
   │  (Interactive citation drawers + multi-pass reasoning trace modal)
```

---

## 🔍 Verified vs Scaffolding Inventory

| Architectural Layer | Demonstrated & Implemented Status | Implementation Details |
| :--- | :--- | :--- |
| **Document Extraction** | ✅ **Implemented & Verified** | PyMuPDF (`fitz`) structure-aware extraction with page-level tracking, heading heuristics, and layout retention for complex PDFs. |
| **Provenance Chunking** | ✅ **Implemented & Verified** | `StructureAwareChunker` generates chunks with deterministic hashes, section hierarchy, and source page bounds. |
| **Embedding Generation** | ✅ **Implemented & Verified** | Amazon Bedrock Titan Text Embeddings v2 (`amazon.titan-embed-text-v2:0`) with 1024 dimensions and normalized cosine distance. |
| **Hybrid Retrieval** | ✅ **Implemented & Verified** | Dense vector similarity combined with BM25 lexical keyword matching and document-level candidate filtering. |
| **Self-Correction Engine** | ✅ **Implemented & Verified** | Multi-pass retrieval orchestrator: detects insufficient evidence on Pass 1 (<75% threshold), rewrites query, triggers Pass 2, and records multi-pass audit history. |
| **Claim Verification** | ✅ **Implemented & Verified** | Decomposes answers into individual sentences; audits lexical and semantic overlap against retrieved chunks with confidence scoring. |
| **Interactive Auditability** | ✅ **Implemented & Verified** | Clickable citation badges opening source excerpts; *"How Aegis reached this answer"* modal displaying latency breakdowns and multi-pass history. |
| **Cloud Infrastructure (IaC)**| ✅ **Implemented & Verified** | AWS SAM template (`infrastructure/sam/template.yaml`) declaring S3 buckets, DynamoDB metadata/conversations tables, Lambda backend, and Bedrock IAM permissions. |
| **Image OCR (Textract)** | 🚧 *MVP Scaffolding* | Current image extractor registers image entities and metadata; full Amazon Textract multimodal visual layout is scaffolded for Phase 2. |
| **Graph Database Storage** | 🚧 *MVP Scaffolding* | Graph reasoning concepts and entity models defined; full Amazon Neptune / Neo4j graph traversal engine planned for Phase 2. |

---

## 🛡️ Hackathon Submission Alignment

- **Innovation**: Real-time closed-loop self-correction where the RAG engine refuses to output unverified claims.
- **Completeness**: Full-stack application with React 18 / Tailwind frontend, FastAPI backend, local persistent storage fallback, and complete test suite.
- **Auditability**: Zero "black-box" answers. Every fact maps to an inspectable chunk, page number, and confidence score.
