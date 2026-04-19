# 041. Consolidate Vector Backends Under `_core/infrastructure/vectors/`

- Status: Accepted
- Date: 2026-04-20
- Related issue: #80 (End-to-end RAG example)
- Supersedes layout from: [ADR 034](034-s3vectors-vectorstore-pattern.md) (S3 Vectors store)
- Related ADRs: [040](040-rag-as-reusable-pattern.md) (RAG as a reusable pattern)

## Summary

Vector store backends now live in a single folder, `src/_core/infrastructure/vectors/`, instead of being split across `s3vectors/` and `in_memory_vectors/`. The shared vector model is also renamed from `S3VectorModel` / `S3VectorModelMeta` / `S3VectorData` to the neutral `VectorModel` / `VectorModelMeta` / `VectorData` (and `__s3vector_meta__` → `__vector_meta__`) so both backends own it equally. S3-specific artefacts keep their `S3Vector*` naming.

## Background

ADR 034 introduced `_core/infrastructure/s3vectors/` for the S3 Vectors backend. ADR 040 then added a second backend — an in-memory vector store used by `make quickstart` and the `docs` example domain — under a peer directory `_core/infrastructure/in_memory_vectors/`.

Two observations drove this ADR:

1. The in-memory store already imports `S3VectorModel` from the sibling package and reuses it verbatim. The "borrowed model" made the directory split misleading — there is no clean boundary between the two packages.
2. Sibling abstractions like `_core/infrastructure/embedding/` and `_core/infrastructure/storage/` already host multiple provider implementations in one folder (OpenAI + Bedrock adapters, S3 + MinIO clients). Vectors was the only cross-backend abstraction that had been split.

## Problem

Keeping two folders for one abstraction created three concrete issues:

- **Hidden coupling.** `BaseInMemoryVectorStore` depended on `S3VectorModel`, meaning the "in_memory" package was in fact a dependant of "s3vectors". The split suggested independence that did not exist.
- **Naming implied hierarchy.** The shared model `S3VectorModel` read as "the S3 type that InMemory happens to use," not "the vector model both backends share." Callers had to reason about which backend owned the contract.
- **Inconsistent with peers.** New contributors reading `_core/infrastructure/` would reasonably expect vectors to follow the same one-folder-per-abstraction convention as `embedding/` and `storage/`.

## Decision

### 1. Single folder for both backends

```
src/_core/infrastructure/vectors/
├── vector_model.py              # Shared: VectorModel, VectorModelMeta, VectorData
├── base_s3_vector_store.py      # S3-specific: BaseS3VectorStore
├── base_in_memory_vector_store.py  # InMemory-specific: BaseInMemoryVectorStore
├── s3_vector_client.py          # S3-specific: S3VectorClient (aioboto3)
├── exceptions.py                # S3-specific: S3VectorException hierarchy
└── __init__.py
```

Note: `base_s3vector_store.py` / `s3vector_client.py` filenames are kept verbatim (no rename to `base_s3_vector_store.py` etc.) to minimise churn beyond what the semantic change requires.

### 2. Neutralise only the shared surface

| Before | After | Reason |
|---|---|---|
| `S3VectorModel` | `VectorModel` | Used by both backends |
| `S3VectorModelMeta` | `VectorModelMeta` | Used by both backends |
| `S3VectorData` | `VectorData` | Used by both backends |
| `__s3vector_meta__` | `__vector_meta__` | Class-level metadata, shared |
| `DocumentChunkS3VectorModel` | `DocumentChunkVectorModel` | Consumer domain naming follows |

### 3. Keep S3-specific names S3-specific

| Kept |
|---|
| `BaseS3VectorStore` — subclass of the S3 backend only |
| `S3VectorClient` — `aioboto3` session for AWS's S3 Vectors service |
| `S3VectorException` / `S3VectorIndexNotFoundException` / `S3VectorThrottlingException` |
| `to_s3vector()` / `from_s3vector()` on `VectorModel` — serialises to the AWS S3 Vectors API shape |

`VectorModel.to_s3vector()` still carries `s3vector` in its name because the output shape (`{"key": …, "data": {"float32": [...]}, "metadata": …}`) is the AWS S3 Vectors `put_vectors` contract. The in-memory store happens to reuse that same dict shape, which is a *compatibility* choice, not a naming accident.

### 4. Settings and env vars unchanged

`S3VECTORS_ACCESS_KEY`, `S3VECTORS_BUCKET_NAME`, and `settings.s3vectors_*` stay as-is — they configure the AWS product and keep the product name.

`migrations/s3vectors/` keeps its folder name for the same reason: it is S3 Vectors index migration tooling.

## Consequences

- **One import origin.** Consumer domains write `from src._core.infrastructure.vectors import …` regardless of which backend they pick at DI time.
- **Backend swapping is configuration-only.** `DocsContainer`'s `providers.Selector` on `VECTOR_STORE_TYPE` (inmemory ↔ s3vectors) chooses the subclass; both construct the same `VectorModel` via `_to_model()`.
- **ADR 034 stays valid for the S3 Vectors design itself** — index schema, batch limits, filter contract, etc. Only the path it described (`_core/infrastructure/s3vectors/`) changed.
- **Future backends plug in here.** If a `QdrantVectorStore`, `PgVectorStore`, or `LanceVectorStore` is added, it goes under `vectors/` next to the existing two, subclasses the shared `VectorModel`, and exposes a backend key for `VECTOR_STORE_TYPE`.

## Alternatives Considered

- **Keep the two folders, rename only the model** (`S3VectorModel` → `VectorModel`) **in-place.** Rejected: this hides the coupling without fixing it — `in_memory_vectors/` would still live as a separate package that imports from `s3vectors/`.
- **Move `in_memory_vectors/` under `s3vectors/`.** Rejected: implies the in-memory backend is a variant of the S3 backend, which is the wrong mental model.
- **Fully generalise the serialisation contract** (`to_s3vector()` → `to_dict()`, extract an AWS-specific adapter). Rejected for this ADR: out of scope for #80 and the S3 Vectors API shape is already a fine de-facto interchange format. Revisit if/when a non-S3 backend is added that needs a different wire shape.
