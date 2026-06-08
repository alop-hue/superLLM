from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import httpx

from superllm.config.settings import settings

HF_API_BASE = "https://huggingface.co/api"
HF_DL_BASE = "https://huggingface.co"


@dataclass
class HFModelInfo:
    id: str
    author: str
    downloads: int
    likes: int
    pipeline_tag: str | None = None
    tags: list[str] = field(default_factory=list)
    created_at: str | None = None
    trending_score: int | None = None
    siblings: list[dict] = field(default_factory=list)
    card_data: dict = field(default_factory=dict)
    is_gated: bool = False
    gguf_files: list[str] = field(default_factory=list)


class HFClient:
    def __init__(self, token: str | None = None):
        self.token = token or self._resolve_token()
        self._headers = {"User-Agent": "superllm/0.1.0"}
        if self.token:
            self._headers["Authorization"] = f"Bearer {self.token}"

    @staticmethod
    def _resolve_token() -> str | None:
        if settings.hf_token:
            return settings.hf_token
        env_token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACEHUB_API_TOKEN")
        if env_token:
            return env_token
        token_path = Path.home() / ".huggingface" / "token"
        if token_path.exists():
            return token_path.read_text().strip()
        return None

    def _get(self, url: str, params: dict = None) -> dict | list:
        with httpx.Client(follow_redirects=True, timeout=30) as c:
            r = c.get(url, headers=self._headers, params=params)
            if r.status_code == 401 and not self.token:
                raise PermissionError(
                    "This model requires Hugging Face authentication.\n"
                    "Set HF_TOKEN in .env or run: superllm config set hf_token YOUR_TOKEN"
                )
            if r.status_code == 401:
                raise PermissionError(
                    "Hugging Face returned 401. Your token may be invalid or expired.\n"
                    "Run: superllm config set hf_token YOUR_TOKEN"
                )
            if r.status_code == 404:
                return None
            r.raise_for_status()
            return r.json()

    def _head(self, url: str) -> httpx.Response:
        with httpx.Client(follow_redirects=True, timeout=15) as c:
            return c.head(url, headers=self._headers)

    def validate_token(self) -> tuple[bool, str]:
        if not self.token:
            return False, "No token configured"
        try:
            data = self._get(f"{HF_API_BASE}/whoami-v2")
            if isinstance(data, dict) and "name" in data:
                return True, f"Authenticated as {data['name']}"
            return False, "Invalid token"
        except Exception as e:
            return False, str(e)

    def repo_exists(self, repo_id: str) -> bool:
        result = self._get(f"{HF_API_BASE}/models/{repo_id}")
        return result is not None

    def get_repo_info(self, repo_id: str) -> HFModelInfo | None:
        data = self._get(f"{HF_API_BASE}/models/{repo_id}")
        if data is None:
            return None
        siblings = data.get("siblings", [])
        gguf_files = sorted(
            [s["rfilename"] for s in siblings if s["rfilename"].endswith(".gguf")],
            key=lambda x: self._quant_priority(x),
        )
        return HFModelInfo(
            id=data["modelId"],
            author=data.get("author", ""),
            downloads=data.get("downloads", 0),
            likes=data.get("likes", 0),
            pipeline_tag=data.get("pipeline_tag"),
            tags=data.get("tags", []),
            created_at=data.get("createdAt"),
            siblings=siblings,
            card_data=data.get("cardData", {}),
            is_gated=data.get("gated", False) is not False,
            gguf_files=gguf_files,
        )

    def search_models(
        self,
        query: str = "",
        pipeline_tag: str = None,
        sort: str = "downloads",
        direction: int = -1,
        limit: int = 50,
        author: str = None,
    ) -> list[HFModelInfo]:
        search_term = f"{query} GGUF" if query else "GGUF"
        params = {
            "search": search_term,
            "sort": sort,
            "direction": direction,
            "limit": min(limit, 200),
        }
        if pipeline_tag:
            params["pipeline_tag"] = pipeline_tag
        if author:
            params["author"] = author

        data = self._get(f"{HF_API_BASE}/models", params=params)
        if not isinstance(data, list):
            return []

        results = []
        for item in data:
            results.append(
                HFModelInfo(
                    id=item["modelId"],
                    author=item.get("author", ""),
                    downloads=item.get("downloads", 0),
                    likes=item.get("likes", 0),
                    pipeline_tag=item.get("pipeline_tag"),
                    tags=item.get("tags", []),
                    created_at=item.get("createdAt"),
                    is_gated=item.get("gated", False) is not False,
                )
            )
        return results

    @staticmethod
    def _quant_priority(filename: str) -> int:
        name = filename.lower()
        if "q4_k_m" in name:
            return 0
        if "q4_0" in name or "q4_1" in name:
            return 1
        if "q5_k_m" in name:
            return 2
        if "q5_0" in name or "q5_1" in name:
            return 3
        if "q8_0" in name:
            return 4
        if "q3" in name:
            return 5
        if "q2" in name:
            return 6
        if "q6" in name:
            return 7
        return 8

    def resolve_gguf_url(self, model_name: str, preferred_quant: str = "Q4_K_M") -> str | None:
        if "/" in model_name and not model_name.startswith("https://"):
            repo_id = model_name
        else:
            repo_id = f"bartowski/{self._to_hf_name(model_name)}-Instruct-GGUF"

        info = self.get_repo_info(repo_id)
        if info is None:
            alt = f"bartowski/{self._to_hf_name(model_name)}-GGUF"
            info = self.get_repo_info(alt)
        if info is None:
            return None
        if info.is_gated and not self.token:
            raise PermissionError(
                f"Model '{repo_id}' is gated and requires Hugging Face authentication.\n"
                f"Set HF_TOKEN in .env or login."
            )

        if not info.gguf_files:
            return None

        preferred_lower = preferred_quant.lower()
        candidates = [f for f in info.gguf_files if preferred_lower in f.lower()]
        if candidates:
            chosen = candidates[0]
        else:
            chosen = info.gguf_files[0]

        return f"{HF_DL_BASE}/{repo_id}/resolve/main/{chosen}"

    def find_gguf_model(self, query: str, preferred_quant: str = "Q4_K_M") -> list[dict]:
        results = self.search_models(query=query, sort="downloads", limit=30)
        if not results:
            results = self.search_models(
                query=query, author="bartowski", sort="downloads", limit=10
            )
        matches = []
        for m in results:
            if not m.gguf_files:
                continue
            best_quant = None
            for f in m.gguf_files:
                if preferred_quant.lower() in f.lower():
                    best_quant = f
                    break
            if not best_quant and m.gguf_files:
                best_quant = m.gguf_files[0]
            if best_quant:
                dl_url = f"{HF_DL_BASE}/{m.id}/resolve/main/{best_quant}"
                matches.append(
                    {
                        "id": m.id,
                        "downloads": m.downloads,
                        "likes": m.likes,
                        "quant": best_quant,
                        "url": dl_url,
                        "pipeline_tag": m.pipeline_tag,
                        "is_gated": m.is_gated,
                    }
                )
        return matches

    def find_available_quants(self, repo_id: str) -> list[str]:
        info = self.get_repo_info(repo_id)
        if not info or not info.gguf_files:
            return []
        quants = set()
        for f in info.gguf_files:
            parts = f.replace(".gguf", "").split("-")
            for p in parts:
                if any(q in p.upper() for q in ["Q2", "Q3", "Q4", "Q5", "Q6", "Q8"]):
                    quants.add(p.upper())
        return sorted(quants)

    @staticmethod
    def _to_hf_name(name: str) -> str:
        name = name.replace(":cloud", "").replace(":local", "")
        name = name.replace(".", "-")
        parts = name.split("-")
        seen = set()
        cleaned = []
        for p in parts:
            if not p or p in seen:
                continue
            seen.add(p)
            if p in ("b", "vl"):
                cleaned.append(p)
            else:
                try:
                    float(p)
                    cleaned.append(p)
                except ValueError:
                    if len(p) <= 2 and not p.isdigit():
                        cleaned.append(p.upper() if not p[0].isupper() else p)
                    else:
                        cleaned.append(p[0].upper() + p[1:].lower() if p[0].islower() else p)
        return "-".join(cleaned)

    def get_suggestions(self, model_name: str) -> list[dict]:
        results = self.search_models(query=model_name, sort="downloads", limit=10)
        suggestions = []
        for m in results:
            if m.gguf_files:
                suggestions.append(
                    {
                        "id": m.id,
                        "gguf_count": len(m.gguf_files),
                        "downloads": m.downloads,
                        "is_gated": m.is_gated,
                    }
                )
        return suggestions[:5]
