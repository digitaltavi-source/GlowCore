from __future__ import annotations
from typing import Optional

def gemini_generate(prompt: str, api_key: Optional[str] = None) -> str:
    """
    Minimal safe stub.
    - Nếu bạn chưa muốn tích hợp thư viện Gemini thật, hàm này vẫn chạy.
    - Khi có API thật, bạn thay phần TODO bằng SDK chính thức.
    """
    if not api_key:
        return ""  # no-op -> engine sẽ fallback offline

    # TODO: integrate official Gemini SDK later
    # For now: return empty to keep system stable
    return ""
