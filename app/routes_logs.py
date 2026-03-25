from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query

from .settings import log_dir, log_encoding, max_read_bytes

router = APIRouter(prefix="/api", tags=["logs"])


def _under_log_root(path: Path) -> bool:
    base = log_dir().resolve()
    try:
        path.resolve().relative_to(base)
        return True
    except ValueError:
        return False


def _decode(raw: bytes, encoding: str) -> str:
    enc = encoding.lower()
    if enc in ("utf-8", "utf8"):
        return raw.decode("utf-8", errors="replace")
    return raw.decode(encoding, errors="replace")


def _read_head(path: Path, cap: int) -> tuple[bytes, bool]:
    size = path.stat().st_size
    if size <= cap:
        return path.read_bytes(), False
    with path.open("rb") as f:
        return f.read(cap), True


def _read_tail(path: Path, cap: int) -> tuple[bytes, bool]:
    size = path.stat().st_size
    if size <= cap:
        return path.read_bytes(), False
    with path.open("rb") as f:
        f.seek(size - cap)
        return f.read(cap), True


@router.get("/files")
def list_files() -> list[dict]:
    base = log_dir()
    if not base.is_dir():
        raise HTTPException(status_code=404, detail="LOG_DIR 不存在或不是目录")

    out: list[dict] = []
    for p in sorted(base.rglob("*")):
        if p.is_file() and p.name != ".gitkeep":
            rel = p.relative_to(base).as_posix()
            st = p.stat()
            out.append(
                {
                    "path": rel,
                    "size": st.st_size,
                    "mtime": datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat(),
                }
            )
    return out


@router.get("/logs/{filepath:path}")
def read_log(
    filepath: str,
    tail: int | None = Query(default=None, ge=1, le=50_000),
    offset: int | None = Query(default=None, ge=0),
    limit: int | None = Query(default=None, ge=1, le=50_000),
) -> dict:
    base = log_dir()
    target = (base / filepath).resolve()
    if not _under_log_root(target) or not target.is_file():
        raise HTTPException(status_code=404, detail="文件不存在或路径非法")

    enc = log_encoding()
    cap = max_read_bytes()

    if (offset is None) != (limit is None):
        raise HTTPException(status_code=400, detail="分页需同时提供 offset 与 limit")

    if offset is not None and limit is not None:
        raw, byte_trunc = _read_head(target, cap)
        text = _decode(raw, enc)
        lines = text.splitlines()
        end = offset + limit
        sliced = lines[offset:end]
        return {
            "path": filepath,
            "lines": sliced,
            "mode": "page",
            "offset": offset,
            "limit": limit,
            "truncated": byte_trunc,
            "total_lines_in_chunk": len(lines),
            "encoding": enc,
        }

    t = tail if tail is not None else 500
    raw, byte_trunc = _read_tail(target, cap)
    text = _decode(raw, enc)
    lines = text.splitlines()
    if len(lines) > t:
        lines = lines[-t:]
    return {
        "path": filepath,
        "lines": lines,
        "mode": "tail",
        "tail": t,
        "truncated": byte_trunc,
        "encoding": enc,
    }
