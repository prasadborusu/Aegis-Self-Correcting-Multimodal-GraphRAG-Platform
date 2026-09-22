"""
Evidence-Grounded Generation Client for Aegis.
Invokes Amazon Bedrock Converse API with strict evidence-grounding constraints.
"""

import logging
from typing import List, Tuple, Optional, Dict, Any
import boto3
from botocore.exceptions import ClientError

from backend.app.models.document import Chunk
from backend.app.config.settings import Settings, get_settings

logger = logging.getLogger("aegis.generator")


class GroundedGenerator:
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self.model_id = self.settings.bedrock_generation_model_id
        self.region = self.settings.bedrock_generation_region or self.settings.aws_region

        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = boto3.client("bedrock-runtime", region_name=self.region)
        return self._client

    def generate_answer(
        self,
        query: str,
        evidence_chunks: List[Tuple[Chunk, float]],
    ) -> str:
        """
        Generate a verifiable, cited answer strictly over retrieved evidence context.
        """
        if not evidence_chunks:
            return "I couldn't find sufficient evidence in the uploaded sources to answer this confidently."

        # Format retrieved evidence context blocks
        context_blocks = []
        for i, (chunk, score) in enumerate(evidence_chunks):
            heading_info = f" | Heading: {chunk.metadata.heading}" if chunk.metadata.heading else ""
            page_info = f" | Page: {chunk.metadata.page}" if chunk.metadata.page else ""
            context_blocks.append(
                f"--- EVIDENCE EXCERPT {i+1} ---\n"
                f"Chunk ID: {chunk.chunk_id}\n"
                f"Document: {chunk.metadata.filename}{page_info}{heading_info}\n"
                f"Content:\n{chunk.text}\n"
            )

        evidence_context = "\n\n".join(context_blocks)

        system_instruction = (
            "You are Aegis, an enterprise evidence-first knowledge intelligence engine built on AWS.\n"
            "CRITICAL INSTRUCTIONS:\n"
            "1. Answer the user question using ONLY the provided evidence excerpts below.\n"
            "2. For every factual statement or claim you make, explicitly append its supporting chunk tag in brackets, "
            "for example: '...as specified in the documentation [Chunk: <chunk_id>]'.\n"
            "3. If the provided evidence excerpts do NOT contain enough information to answer the question accurately, "
            "you MUST reply with: 'I couldn't find sufficient evidence in the uploaded sources to answer this confidently.'\n"
            "4. NEVER fabricate citations, page numbers, or facts not present in the excerpts."
        )

        user_prompt = (
            f"EVIDENCE SOURCES:\n{evidence_context}\n\n"
            f"QUESTION: {query}\n\n"
            f"GROUNDED ANSWER:"
        )

        try:
            response = self.client.converse(
                modelId=self.model_id,
                system=[{"text": system_instruction}],
                messages=[
                    {
                        "role": "user",
                        "content": [{"text": user_prompt}],
                    }
                ],
                inferenceConfig={
                    "maxTokens": 1024,
                    "temperature": 0.1,  # Low temperature to prioritize factual accuracy
                    "topP": 0.9,
                },
            )
            output_text = response["output"]["message"]["content"][0]["text"]
            return output_text.strip()

        except ClientError as e:
            logger.error(f"Bedrock Converse API call failed ({e.response.get('Error', {}).get('Code')}): {e}")
            if evidence_chunks:
                top_chunk, _ = evidence_chunks[0]
                return f"According to {top_chunk.metadata.filename or 'the verified evidence'}: {top_chunk.text.strip()} [Chunk: {top_chunk.chunk_id}]"
            return "I couldn't find sufficient evidence in the uploaded sources to answer this confidently."
        except Exception as e:
            logger.error(f"Generation error: {e}")
            if evidence_chunks:
                top_chunk, _ = evidence_chunks[0]
                return f"According to {top_chunk.metadata.filename or 'the verified evidence'}: {top_chunk.text.strip()} [Chunk: {top_chunk.chunk_id}]"
            return "I couldn't find sufficient evidence in the uploaded sources to answer this confidently."
