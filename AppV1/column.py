"""
칼럼 조작 모듈

1단 변환 및 칼럼 구분
"""

import time
from .page_setup import mili_to_hwp_unit


def convert_to_single_column(hwp) -> bool:
    """
    1단으로 변환

    v3에서 학습한 내용: 양식 파일은 건드리지 않음
    문제 파일만 1단으로 변환
    """
    try:
        hwp.HAction.GetDefault("MultiColumn", hwp.HParameterSet.HColDef.HSet)

        col_def = hwp.HParameterSet.HColDef
        col_def.Count = 1  # 1단으로 설정
        col_def.HSet.SetItem("ApplyClass", 832)
        col_def.HSet.SetItem("ApplyTo", 6)

        result = hwp.HAction.Execute("MultiColumn", col_def.HSet)
        time.sleep(0.1)
        return result

    except Exception:
        return False


def break_column(hwp) -> bool:
    """
    칼럼 구분 (BreakColumn)

    다음 칼럼으로 이동
    """
    try:
        hwp.Run("BreakColumn")
        time.sleep(0.05)
        return True
    except Exception:
        return False
