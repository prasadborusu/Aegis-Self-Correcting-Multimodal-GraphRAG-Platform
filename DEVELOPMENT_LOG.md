# Aegis — Development Log

This log chronicles the disciplined development of **Aegis**, an evidence-first knowledge intelligence platform built for the **AWS Zero to Shipped Hackathon**, documenting the development process facilitated by autonomous coding agent **OpenCode**.

---

## Log Entry 001 — Environment Inspection & Project Scaffolding

* **Date**: 2026-09-22
* **Objective**: Perform initial repository and environment inspection, verify toolchains and AWS CLI credentials safely, scaffold project architecture (backend, frontend, infrastructure, configuration, docs), implement basic health probes and enterprise dashboard, and run verification test suites.
* **OpenCode Task**: Milestone 1 — Environment & Repository Inspection, Foundation Scaffolding.
* **Files Modified / Created**:
  * `.gitignore`
  * `.env.example`
  * `README.md`
  * `DEVELOPMENT_LOG.md`
  * `ROADMAP.md`
  * `backend/requirements.txt`
  * `backend/app/main.py`
  * `backend/app/config/settings.py`
  * `backend/app/config/__init__.py`
  * `backend/app/api/v1/router.py`
  * `backend/app/api/v1/health.py`
  * `backend/tests/test_health.py`
  * `backend/tests/test_config.py`
  * `frontend/package.json`
  * `frontend/vite.config.ts`
  * `frontend/tsconfig.json`
  * `frontend/tsconfig.node.json`
  * `frontend/tailwind.config.js`
  * `frontend/postcss.config.js`
  * `frontend/index.html`
  * `frontend/public/shield.svg`
  * `frontend/src/index.css`
  * `frontend/src/types/index.ts`
  * `frontend/src/services/api.ts`
  * `frontend/src/components/Header.tsx`
  * `frontend/src/components/MetricsCards.tsx`
  * `frontend/src/pages/DashboardPage.tsx`
  * `frontend/src/pages/DocumentsPage.tsx`
  * `frontend/src/pages/AskAegisPage.tsx`
  * `frontend/src/app/App.tsx`
  * `frontend/src/main.tsx`
  * `infrastructure/template.yaml`
* **AWS Services Involved**:
  * AWS CLI v2 / STS (Identity and Region Verification: `ap-south-1`)
  * Amazon Bedrock (Configuration scaffolding for Titan Embeddings v2 & Nova Pro LLM)
  * Amazon S3 (Bucket definitions in SAM template & config)
  * Amazon DynamoDB (Table definitions in SAM template & config)
  * Amazon OpenSearch Serverless (Vector index definitions & settings)
* **Commands Executed**:
  * `node -v`, `npm -v`, `python --version`, `git --version`, `aws --version`, `docker --version`
  * `aws configure get region` (safely detected `ap-south-1`)
  * `aws sts get-caller-identity` (safely validated STS profile authentication without printing secrets)
  * `git init` (initialized git repository)
  * `npm install` (installed frontend dependencies)
  * `python -m pytest backend/tests -v` (ran backend unit tests)
  * `npm run build` (compiled and type-checked frontend bundle)
* **Tests**:
  * Backend: 4 pytest tests in `backend/tests/test_health.py` and `backend/tests/test_config.py` (4 passed, 0 failed).
  * Frontend: Full TypeScript compile and Vite production bundling (1,899 modules transformed, 0 errors).
* **Result**:
  * Complete repository scaffolded according to project specification.
  * Backend health endpoint `GET /health` and `GET /api/v1/health` operational.
  * Frontend enterprise dashboard with live metrics cards, "No data yet" states, documents management view, and query view functional.
* **Problem**:
  * Initial TypeScript build failed due to strict `noUnusedLocals: true` catching unused icon imports.
* **Solution**:
  * Cleaned unused icon imports and unused state variables in `Header.tsx`, `DashboardPage.tsx`, `DocumentsPage.tsx`, and `AskAegisPage.tsx`. The build then passed with 100% clean output.

---

## Log Entry 002 — Document Ingestion Engine, Structure-Aware Chunking, & Bedrock Embeddings

* **Date**: 2026-09-22
* **Objective**: Build non-blocking asynchronous document upload, DynamoDB document processing state machine (`UPLOADED` → `PROCESSING` → `EXTRACTING` → `CHUNKING` → `EMBEDDING` → `INDEXING` → `COMPLETED` / `FAILED`), multi-format layout-preserving extraction (PDF, TXT, images), structure-aware chunking preserving provenance metadata, and live Amazon Bedrock Titan Text Embeddings v2 generation.
* **OpenCode Task**: Milestone 2 — S3 Document Upload, DynamoDB State Lifecycle, Structure-Aware Extraction, and Bedrock Embeddings.
* **Files Modified / Created**:
  * `backend/app/config/settings.py` (added granular Bedrock region routing)
  * `backend/app/models/document.py` (DocumentRecord, Chunk, ChunkMetadata, ProcessingState)
  * `backend/app/models/__init__.py`
  * `backend/app/services/s3_storage.py` (S3 upload, magic byte validation, fallback store)
  * `backend/app/services/dynamo_db.py` (DynamoDB state machine with local persistent store)
  * `backend/app/extraction/extractor.py` (PyMuPDF & plain text layout extractor)
  * `backend/app/chunking/structure_aware.py` (Structure-aware chunker splitting on headings & paragraphs)
  * `backend/app/embeddings/bedrock_embeddings.py` (Bedrock Titan v2 1024-dim client)
  * `backend/app/ingestion/pipeline.py` (asynchronous pipeline orchestration)
  * `backend/app/api/v1/documents.py` (upload, list, get, delete endpoints)
  * `backend/app/api/v1/router.py` (registered documents router)
  * `backend/tests/test_chunking.py` (unit tests for extraction & chunking)
  * `backend/tests/test_documents_api.py` (integration tests for upload & lifecycle)
  * `backend/tests/test_embeddings.py` (tests for Bedrock embeddings)
  * `frontend/src/services/api.ts` (uploadDocument, deleteDocument, document mapper)
  * `frontend/src/pages/DocumentsPage.tsx` (drag-and-drop upload, active status polling, deletion)
  * `.gitignore` (added .storage/ exclusion)
* **AWS Services Involved**:
  * Amazon S3 (raw document storage and validation)
  * Amazon DynamoDB (document metadata and state transitions)
  * Amazon Bedrock (Live invocation of `amazon.titan-embed-text-v2:0` in `us-east-1` yielding 1024-dim dense vectors)
* **Commands Executed**:
  * `python -m pytest backend/tests -v` (12 tests passed)
  * `npm run typecheck` (passed with 0 errors)
  * `npm run build` (production build compiled successfully in 3.97s)
* **Tests**:
  * Total 12 backend unit and integration tests executed: 12 passed, 0 failed.
  * Live Amazon Bedrock Titan v2 embedding invocation test executed: passed.
* **Result**:
  * Asynchronous document upload functional.
  * Complete state machine progression implemented and verified.
  * Structure-aware chunking preserving headings, page numbers, and provenance tags verified.
  * Frontend document management interface wired with live upload, polling, and status badges.
* **Problem**:
  * Headings test failed initially because sample text was smaller than `chunk_size`.
* **Solution**:
  * Refined `StructureAwareChunker` so encountering a new section heading automatically completes the preceding chunk, enforcing natural semantic boundaries between distinct sections. All tests passed.
