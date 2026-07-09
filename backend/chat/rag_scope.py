from contextvars import ContextVar
from typing import Optional


_selected_documents: ContextVar[Optional[list[str]]] = ContextVar(
    "selected_documents",
    default=None,
)


def normalize_selected_documents(documents: Optional[list[str]]) -> Optional[list[str]]:
    """清洗本轮限定检索的文档名；空列表按“全库检索”处理。"""
    if not documents:
        return None
    seen: set[str] = set()
    normalized: list[str] = []
    for item in documents:
        filename = str(item or "").strip()
        if not filename or filename in seen:
            continue
        seen.add(filename)
        normalized.append(filename)
    return normalized or None


def set_selected_documents(documents: Optional[list[str]]):
    """设置当前请求内的文档检索范围，返回 token 供 finally 中恢复。"""
    return _selected_documents.set(normalize_selected_documents(documents))


def reset_selected_documents(token) -> None:
    _selected_documents.reset(token)


def get_selected_documents() -> Optional[list[str]]:
    return _selected_documents.get()
