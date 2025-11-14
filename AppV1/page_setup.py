"""
페이지 설정 모듈

B4 페이지 및 2단 레이아웃 설정
"""

import time


def mili_to_hwp_unit(mili: float) -> int:
    """밀리미터를 HWP 단위로 변환"""
    return int(mili * 283.465)


def setup_b4_page(hwp) -> bool:
    """
    B4 페이지 설정

    크기: 257mm × 364mm
    여백: 좌우 30mm, 상 20mm, 하 15mm
    머리말/꼬리말: 15mm
    """
    try:
        hwp.HAction.GetDefault("PageSetup", hwp.HParameterSet.HSecDef.HSet)

        sec_def = hwp.HParameterSet.HSecDef
        sec_def.PageDef.PaperWidth = mili_to_hwp_unit(257.0)
        sec_def.PageDef.PaperHeight = mili_to_hwp_unit(364.0)
        sec_def.PageDef.LeftMargin = mili_to_hwp_unit(30.0)
        sec_def.PageDef.RightMargin = mili_to_hwp_unit(30.0)
        sec_def.PageDef.TopMargin = mili_to_hwp_unit(20.0)
        sec_def.PageDef.BottomMargin = mili_to_hwp_unit(15.0)
        sec_def.PageDef.HeaderLen = mili_to_hwp_unit(15.0)
        sec_def.PageDef.FooterLen = mili_to_hwp_unit(15.0)
        sec_def.HSet.SetItem("ApplyClass", 24)
        sec_def.HSet.SetItem("ApplyTo", 3)

        result = hwp.HAction.Execute("PageSetup", sec_def.HSet)
        time.sleep(0.1)
        return result

    except Exception:
        return False


def create_two_column_layout(hwp) -> bool:
    """
    2단 레이아웃 설정

    단 개수: 2
    단 간격: 8mm
    """
    try:
        hwp.HAction.GetDefault("MultiColumn", hwp.HParameterSet.HColDef.HSet)

        col_def = hwp.HParameterSet.HColDef
        col_def.Count = 2
        col_def.SameGap = mili_to_hwp_unit(8.0)
        col_def.HSet.SetItem("ApplyClass", 832)
        col_def.HSet.SetItem("ApplyTo", 6)

        result = hwp.HAction.Execute("MultiColumn", col_def.HSet)
        time.sleep(0.1)
        return result

    except Exception:
        return False
