"""
AppV1: 문항 파일 합병 애플리케이션

기능: 여러 개의 HWP 문항 파일을 하나의 2단 레이아웃 문서로 합병
기반: Tests/E2E/test_merge_40_problems_clean.py (가장 깔끔한 결과)
명세: HwpIdris/AppV1/MergeProblemFiles.idr
"""

from .types import ProblemFile, ParaInfo, ProcessResult, MergeConfig
from .merger import ProblemMerger

__all__ = [
    'ProblemFile',
    'ParaInfo',
    'ProcessResult',
    'MergeConfig',
    'ProblemMerger',
]
