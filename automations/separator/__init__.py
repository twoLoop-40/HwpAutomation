"""
Separator Plugin

HWPX 파일에서 EndNote 기반으로 문제를 분리하는 플러그인
Idris2 명세: Specs/Separator/
"""

from .plugin import SeparatorPlugin
from .separator import separate_problems, Separator
from .types import SeparatorConfig, OnePerFile, GroupByCount, GroupByRange

__all__ = [
    'SeparatorPlugin',
    'separate_problems',
    'Separator',
    'SeparatorConfig',
    'OnePerFile',
    'GroupByCount',
    'GroupByRange',
]
