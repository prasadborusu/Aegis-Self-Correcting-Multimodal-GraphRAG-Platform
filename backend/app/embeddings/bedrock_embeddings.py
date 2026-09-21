"""
Amazon Bedrock Titan Text Embeddings Client for Aegis.
Generates 1024-dimensional dense vectors using amazon.titan-embed-text-v2:0.
"""

import json
import logging
from typing import List, Optional
import boto3
from botocore.exceptions import ClientError

from backend.app.config.settings import Settings, get_settings

logger = logging.getLogger("aegis.embeddings")


class BedrockEmbeddingsService:
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()
        self.model_id = self.settings.bedrock_embedding_model_id
        # Use verified active embedding region
        self.region = self.settings.bedrock_embedding_region or self.settings.aws_region
        self.dimension = self.settings.opensearch_vector_dimension

        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = boto3.client("bedrock-runtime", region_name=self.region)
        return self._client

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate a single 1024-dimensional vector embedding for input text.
        """
        # Titan v2 supports up to 8192 tokens; truncate if text is huge
        clean_text = text[:8000].strip()
        if not clean_text:
            return [0.0] * self.dimension

        body = json.dumps(
            {
                "inputText": clean_text,
                "dimensions": self.dimension,
                "normalize": True,
            }
        )

        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=body,
                contentType="application/json",
                accept="application/json",
            )
            response_body = json.loads(response["body"].read().decode("utf-8"))
            embedding = response_body.get("embedding", [])
            if len(embedding) == self.dimension:
                return embedding
            else:
                logger.warning(f"Unexpected embedding dimension: {len(embedding)}, expected {self.dimension}")
                return embedding
        except ClientError as e:
            logger.error(f"Bedrock embedding invocation failed ({e.response.get('Error', {}).get('Code')}): {e}")
            raise

    def generate_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings sequentially or in batches for a list of texts.
        """
        embeddings = []
        for text in texts:
            emb = self.generate_embedding(text)
            embeddings.append(emb)
        return embeddings
