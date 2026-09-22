# Aegis: Hackathon Submission & Evaluation Guide

## 🏆 Project Information
- **Project Name**: Aegis — Self-Correcting Multimodal GraphRAG Platform
- **Track**: Enterprise AI / Document Intelligence / Amazon Bedrock
- **Tagline**: The evidence-first knowledge engine that verifies every factual claim and self-corrects before answering.
- **Repository**: [https://github.com/prasadborusu/Aegis-Self-Correcting-Multimodal-GraphRAG-Platform](https://github.com/prasadborusu/Aegis-Self-Correcting-Multimodal-GraphRAG-Platform)

---

## 🎯 The Core Problem Solved
Traditional Retrieval-Augmented Generation (RAG) suffers from **silent hallucinations**:
1. Top-k vector search frequently misses multi-aspect or cross-document evidence.
2. The LLM generates fluent but fabricated assertions.
3. Users receive no citation transparency or confidence breakdown.

Aegis solves this with **Closed-Loop Self-Correction**:
- Atomic Claim Decomposition: Answers are audited sentence by sentence.
- Strict 75% Grounding Threshold: Answers below threshold are blocked from user presentation.
- Autonomous Query Reformulation: Aegis identifies which claim lacked evidence, rewrites the query, and performs a second retrieval pass to pull in the missing proof.

---

## ⏱️ The 60-Second Demo Pitch
> *"Aegis is built for high-stakes enterprise knowledge tasks where hallucinations cannot be tolerated.
> When a user asks a complex question like 'Cross-reference Durga Prasad's academic percentage with his projects from his resume', standard RAG only retrieves one document and guesses the rest.
> Aegis detects that initial grounding is incomplete (Pass 1: 60%), triggers an autonomous query rewrite, executes Pass 2 to pull in the resume chunks, and achieves 100% consensus grounding.
> Every answer is tagged with inline claim verification tags, interactive citation drawers linking to original PDF and image sources, and a complete multi-step reasoning trace for absolute auditability."*

---

## 📊 Judging Criteria Alignment

| Criteria | Aegis Demonstration & Verification |
| :--- | :--- |
| **Technical Innovation** | Closed-loop self-correction engine that mathematically audits grounding and re-retrieves autonomously. |
| **AWS Service Integration** | Amazon Bedrock (Titan Text Embeddings v2, Claude 3 Converse API), S3, DynamoDB, AWS SAM. |
| **Design & User Experience** | Sleek enterprise UI with Tailwind CSS, real-time cluster telemetry, citation drawer, and trace modal. |
| **Completeness & Auditability**| Zero black-box outputs. Full latency breakdown (retrieval, generation, verification) and multi-pass audit history. |
| **Code Quality & Testing** | Comprehensive pytest test suite covering chunking, embeddings, health routes, traces, and self-correction. |
