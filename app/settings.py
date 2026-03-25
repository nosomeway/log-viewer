import os
from pathlib import Path


def repo_root() -> Path:
    """log-viewer 仓库根目录（与 app 同级）。"""
    return Path(__file__).resolve().parent.parent


def log_dir() -> Path:
    raw = os.environ.get("LOG_DIR")
    if raw:
        return Path(raw).expanduser().resolve()
    return (repo_root() / "logs").resolve()


def max_read_bytes() -> int:
    return int(os.environ.get("LOG_MAX_READ_BYTES", "2_000_000"))


def log_encoding() -> str:
    return os.environ.get("LOG_ENCODING", "utf-8").strip() or "utf-8"
