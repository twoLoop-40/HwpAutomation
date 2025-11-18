"""
Merger Plugin

문제 파일 병합 플러그인 (기존 AppV1)
HWP 문항 파일들을 2단 편집 양식으로 병합
"""

from .plugin import MergerPlugin
from .types import ProblemFile, ParaInfo, ProcessResult, MergeConfig
from .merger import ProblemMerger

__all__ = [
    'MergerPlugin',
    'ProblemFile',
    'ParaInfo',
    'ProcessResult',
    'MergeConfig',
    'ProblemMerger',
]
