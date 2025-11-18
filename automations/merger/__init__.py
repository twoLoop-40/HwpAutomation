"""
Merger Plugin

문제 파일 병합 플러그인 (기존 AppV1)
HWP 문항 파일들을 2단 편집 양식으로 병합
"""

from .plugin import MergerPlugin
from .types import ProblemFile, ParaInfo, ProcessResult, MergeConfig

# ProblemMerger는 lazy import (실제 사용 시에만 import)
def __getattr__(name):
    if name == 'ProblemMerger':
        from .merger import ProblemMerger
        return ProblemMerger
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    'MergerPlugin',
    'ProblemFile',
    'ParaInfo',
    'ProcessResult',
    'MergeConfig',
    'ProblemMerger',
]
