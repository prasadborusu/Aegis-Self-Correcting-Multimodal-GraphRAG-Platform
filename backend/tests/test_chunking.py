"""
Tests for Aegis Document Extraction and Structure-Aware Chunking.
"""

from backend.app.extraction.extractor import DocumentExtractor
from backend.app.chunking.structure_aware import StructureAwareChunker
from backend.app.config.settings import Settings


def test_txt_extraction_and_chunking():
    extractor = DocumentExtractor()
    chunker = StructureAwareChunker(Settings(chunk_size=200, chunk_overlap=30))

    sample_text = (
        "# Introduction to Aegis\n\n"
        "Aegis is an evidence-first knowledge intelligence platform built for technical accuracy.\n\n"
        "## Architecture Overview\n\n"
        "The architecture combines structure-aware document parsing, Bedrock embeddings, and vector search.\n\n"
        "## Verification Engine\n\n"
        "Answers are decomposed into atomic claims and cross-checked against source citations."
    )

    doc_id = "test-doc-001"
    filename = "intro.txt"
    content = sample_text.encode("utf-8")

    # Extraction
    extracted = extractor.extract(doc_id, filename, content, "txt")
    assert extracted.document_id == doc_id
    assert extracted.filename == filename
    assert extracted.total_pages == 1
    assert len(extracted.pages) == 1
    assert "Introduction to Aegis" in extracted.pages[0].headings[0]

    # Chunking
    chunks = chunker.chunk_document(extracted)
    assert len(chunks) >= 2

    # Verify provenance metadata preservation on every chunk
    for i, chunk in enumerate(chunks):
        assert chunk.document_id == doc_id
        assert chunk.metadata.filename == filename
        assert chunk.metadata.page == 1
        assert chunk.metadata.chunk_index == i
        assert chunk.metadata.source_type == "txt"
        assert chunk.chunk_id.startswith(f"{doc_id}#p1_c{i}")
        assert len(chunk.text) > 0
        assert chunk.metadata.char_count == len(chunk.text)


def test_chunking_honors_heading_context():
    extractor = DocumentExtractor()
    chunker = StructureAwareChunker(Settings(chunk_size=300, chunk_overlap=50))

    sample_text = (
        "## Policy Section A\n\n"
        "All employees must complete compliance training within 30 days of employment.\n\n"
        "## Policy Section B\n\n"
        "Annual leave requires supervisor approval 14 days in advance."
    )

    extracted = extractor.extract("doc-headings", "policy.txt", sample_text.encode("utf-8"), "txt")
    chunks = chunker.chunk_document(extracted)

    assert len(chunks) >= 2
    # Verify that headings are captured in metadata
    heading_names = [c.metadata.heading for c in chunks if c.metadata.heading]
    assert any("Policy Section A" in h for h in heading_names)
