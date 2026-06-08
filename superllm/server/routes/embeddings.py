from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class EmbeddingRequest(BaseModel):
    model: str = "bge-small"
    input: str | list[str]
    encoding_format: str = "float"


class EmbeddingData(BaseModel):
    object: str = "embedding"
    index: int = 0
    embedding: list[float]


class EmbeddingUsage(BaseModel):
    prompt_tokens: int = 0
    total_tokens: int = 0


class EmbeddingResponse(BaseModel):
    object: str = "list"
    data: list[EmbeddingData] = []
    model: str
    usage: EmbeddingUsage = EmbeddingUsage()


_EMBEDDING_CACHE: dict[str, list[float]] = {}


@router.post("/embeddings")
@router.post("/v1/embeddings")
async def create_embeddings(request: EmbeddingRequest):
    texts = [request.input] if isinstance(request.input, str) else request.input

    try:
        from superllm.models.library import ModelLibrary
        card = ModelLibrary.get_model(request.model)
        if not card or not card.capabilities.get("embeddings", False):
            raise HTTPException(
                status_code=400,
                detail=f"Model '{request.model}' is not an embedding model or not found in library",
            )

        import numpy as np

        try:
            from sentence_transformers import SentenceTransformer
            model_key = f"st_{request.model}"
            if model_key not in _EMBEDDING_CACHE:
                _EMBEDDING_CACHE[model_key] = None

            st_model = SentenceTransformer(
                f"BAAI/{request.model}" if "bge" in request.model else request.model,
                trust_remote_code=True,
            )
            embeddings = st_model.encode(texts, normalize_embeddings=True)
            data = []
            for i, emb in enumerate(embeddings):
                data.append(EmbeddingData(
                    object="embedding",
                    index=i,
                    embedding=emb.tolist() if isinstance(emb, np.ndarray) else emb,
                ))
            return EmbeddingResponse(
                data=data,
                model=request.model,
                usage=EmbeddingUsage(
                    prompt_tokens=sum(len(t.split()) for t in texts),
                    total_tokens=sum(len(t.split()) for t in texts),
                ),
            )
        except ImportError:
            try:
                from llama_cpp import Llama
                model_path = f"~/.superllm/models/{request.model}.gguf"
                import os
                expanded_path = os.path.expanduser(model_path)
                if not os.path.exists(expanded_path):
                    raise HTTPException(
                        status_code=404,
                        detail=f"Embedding model '{request.model}' not found locally. Pull it first.",
                    )
                llm = Llama(
                    model_path=expanded_path,
                    embedding=True,
                    n_ctx=512,
                )
                data = []
                for i, text in enumerate(texts):
                    emb = llm.create_embedding(text)
                    data.append(EmbeddingData(
                        object="embedding",
                        index=i,
                        embedding=emb["data"][0]["embedding"],
                    ))
                return EmbeddingResponse(
                    data=data,
                    model=request.model,
                    usage=EmbeddingUsage(
                        prompt_tokens=sum(len(t.split()) for t in texts),
                        total_tokens=sum(len(t.split()) for t in texts),
                    ),
                )
            except ImportError:
                raise HTTPException(
                    status_code=500,
                    detail="No embedding backend available. Install: pip install sentence-transformers",
                )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding generation failed: {e}")


@router.get("/embeddings/models")
async def list_embedding_models():
    from superllm.models.library import ModelLibrary
    emb_models = ModelLibrary.get_by_capability("embeddings")
    return {
        "models": [
            {
                "name": m.name,
                "display_name": m.display_name,
                "parameter_count": m.parameter_count,
                "context_length": m.context_length,
                "recommended_ram": m.recommended_ram,
                "tags": m.tags,
            }
            for m in emb_models
        ],
        "total": len(emb_models),
    }
