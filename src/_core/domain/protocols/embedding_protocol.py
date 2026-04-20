from __future__ import annotations


class BaseEmbeddingProtocol:
    """Backend-agnostic embedding protocol.

    Abstraction boundary for embedding implementations.
    Both OpenAI and Bedrock Titan implement this protocol.
    Domain services inject this protocol directly.

    ``dimension`` exposes the vector size so that callers
    (e.g. ``VectorModelMeta``) can align index configuration.
    """

    @property
    def dimension(self) -> int: ...

    async def embed_text(self, text: str) -> list[float]: ...

    async def embed_batch(self, texts: list[str]) -> list[list[float]]: ...
