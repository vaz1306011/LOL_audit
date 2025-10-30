import sys
from pathlib import Path


def resource_path(relative_path) -> str:
    """獲取打包後的檔案路徑"""
    if hasattr(sys, "_MEIPASS"):
        path = Path(sys._MEIPASS, relative_path)  # type: ignore
        return str(path)  # type: ignore
    return relative_path
