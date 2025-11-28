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
    문서 끝에서 빈 Para 제거 (루프 방식)

    math-collector 검증된 방식:
    - GetPos()로 빈 Para 판단 (end_pos[2] == 0)
    - 루프 방식: 빈 Para가 없을 때까지 반복
    - 페이지 경계를 넘어 모든 빈 Para 제거
    - 공백 문자만 있는 Para는 제거하지 않음 (안전)

    Returns:
        제거된 Para 개수
    """
    if not paras:
        return 0

    removed = 0
    max_iterations = 100  # 안전 장치

    for i in range(max_iterations):
        try:
            # 문서 끝으로 이동
            hwp.Run("MoveDocEnd")
            time.sleep(0.02)

            # Para 시작으로 이동
            hwp.Run("MoveParaBegin")
            time.sleep(0.02)

            # Para 끝으로 이동
            hwp.Run("MoveParaEnd")
            time.sleep(0.02)

            # Para 끝 위치 확인
            end_pos = hwp.GetPos()

            # 빈 Para 판단: end_pos[2] == 0 (완전히 빈 Para만)
            is_empty = (end_pos[2] == 0)

            if is_empty:
                # 빈 Para - 삭제
                hwp.Run("MoveDocEnd")
                time.sleep(0.02)

                hwp.Run("Select")
                time.sleep(0.01)
                hwp.Run("MoveLeft")
                time.sleep(0.01)
                hwp.Run("Delete")
                time.sleep(0.02)

                removed += 1
            else:
                # 내용 있는 Para - 종료
                break

        except Exception as e:
            try:
                hwp.Run("Cancel")
            except:
                pass
            break

    # 최종 위치를 문서 시작으로 (Copy 준비)
    hwp.Run("MoveDocBegin")
    time.sleep(0.02)

    return removed
