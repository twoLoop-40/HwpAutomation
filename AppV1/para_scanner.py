"""
Para 스캔 및 제거 모듈

test_merge_40_problems_clean.py의 MoveSelDown 방식 사용 (가장 깔끔한 결과)
"""

import time
from typing import List
from .types import ParaInfo


def scan_paras(hwp) -> List[ParaInfo]:
    """
    모든 Para 스캔

    HwpIdris/Actions/Navigation.idr 기반:
    - MoveDocBegin: 문서 시작으로 이동
    - MoveParaEnd: Para 끝으로 이동
    - MoveNextParaBegin: 다음 Para 시작으로 이동
    """
    paras = []

    hwp.Run("MoveDocBegin")
    time.sleep(0.05)

    para_num = 0

    while True:
        start_pos = hwp.GetPos()

        hwp.Run("MoveParaEnd")
        time.sleep(0.02)

        end_pos = hwp.GetPos()

        # 빈 Para 판단: end_pos의 pos 값이 0이면 빈 Para
        is_empty = (end_pos[2] == 0)

        paras.append(ParaInfo(
            para_num=para_num,
            start_pos=start_pos,
            end_pos=end_pos,
            is_empty=is_empty,
        ))

        # 다음 Para로 이동
        before_pos = hwp.GetPos()
        hwp.Run("MoveNextParaBegin")
        time.sleep(0.02)

        after_pos = hwp.GetPos()

        # 위치가 변하지 않으면 마지막 Para
        if after_pos == before_pos:
            break

        para_num += 1

        # 안전 장치
        if para_num > 500:
            break

    return paras


def remove_empty_paras(hwp, paras: List[ParaInfo]) -> int:
    """
    문서 끝에서 MoveSelUp 방식으로 빈 Para 제거

    개선된 방법:
    1. 문서 끝으로 이동 (MoveDocEnd)
    2. 뒤에서부터 빈 Para 확인
    3. 빈 Para 시작점까지 MoveSelUp으로 선택
    4. Delete로 제거

    장점:
    - 커서 위치가 명확함 (항상 문서 끝에서 시작)
    - 연속된 빈 Para를 한번에 제거 가능
    - 최종 커서 위치가 첫 번째 비어있지 않은 Para 끝
    """
    if not paras:
        return 0

    removed = 0

    # 문서 끝으로 이동
    hwp.Run("MoveDocEnd")
    time.sleep(0.02)

    # 뒤에서부터 빈 Para 확인하며 제거
    max_iterations = 100  # 안전 장치
    iteration = 0

    while iteration < max_iterations:
        # 현재 Para 시작으로 이동
        hwp.Run("MoveParaBegin")
        time.sleep(0.02)

        # Para 끝으로 이동해서 빈 Para인지 확인
        hwp.Run("MoveParaEnd")
        time.sleep(0.02)
        end_pos = hwp.GetPos()

        is_empty = (end_pos[2] == 0)

        if is_empty:
            # 빈 Para - Para 시작으로 돌아가서 선택 후 삭제
            hwp.Run("MoveParaBegin")
            hwp.Run("MoveSelDown")
            time.sleep(0.02)
            hwp.Run("Delete")
            time.sleep(0.02)
            removed += 1

            # 삭제 후 이전 Para로 명시적으로 이동
            before_pos = hwp.GetPos()
            hwp.Run("MovePrevParaBegin")
            time.sleep(0.02)
            after_pos = hwp.GetPos()

            # 위치가 변하지 않으면 문서 시작 - 종료
            if before_pos == after_pos:
                break

            # Para 끝으로 이동해서 다음 루프 준비
            hwp.Run("MoveParaEnd")
            time.sleep(0.02)
        else:
            # 비어있지 않은 Para - 이전 Para 확인
            before_pos = hwp.GetPos()
            hwp.Run("MovePrevParaBegin")
            time.sleep(0.02)
            after_pos = hwp.GetPos()

            # 위치가 변하지 않으면 첫 Para - 종료
            if before_pos == after_pos:
                break

            # Para 끝으로 이동해서 다음 루프 준비
            hwp.Run("MoveParaEnd")
            time.sleep(0.02)

        iteration += 1

    # 최종 위치를 문서 시작으로 (Copy 준비)
    hwp.Run("MoveDocBegin")
    time.sleep(0.02)

    return removed
