"""
HWP 작업 동기화 유틸리티

HWP COM 작업은 비동기적으로 처리될 수 있어서
작업 완료를 보장하기 위한 동기화 메커니즘 제공
"""

import time
from typing import Callable, Any
from functools import wraps


def wait_for_hwp_ready(hwp, timeout: float = 5.0, check_interval: float = 0.1) -> bool:
    """
    HWP가 작업을 완료하고 준비 상태가 될 때까지 대기

    Args:
        hwp: HWP COM 객체
        timeout: 최대 대기 시간 (초)
        check_interval: 상태 확인 간격 (초)

    Returns:
        준비 완료 여부
    """
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            # HWP가 준비 상태인지 확인
            # EditMode가 정상(0 또는 1)이면 준비 완료
            if hasattr(hwp, 'EditMode'):
                _ = hwp.EditMode
                return True

            # PageCount를 읽을 수 있으면 준비 완료
            if hasattr(hwp, 'PageCount'):
                _ = hwp.PageCount
                return True

            # 속성이 없으면 바로 성공으로 간주
            return True

        except Exception:
            # COM 객체가 바쁘면 예외 발생
            time.sleep(check_interval)
            continue

    return False


def ensure_hwp_sync(delay: float = 0.2) -> Callable:
    """
    HWP 작업 후 동기화를 보장하는 데코레이터

    Args:
        delay: 작업 후 대기 시간 (초)

    Usage:
        @ensure_hwp_sync(delay=0.3)
        def insert_file(hwp, path):
            hwp.HAction.Execute("InsertFile", ...)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # 원본 함수 실행
            result = func(*args, **kwargs)

            # HWP 객체 찾기 (첫 번째 인자 또는 kwargs에서)
            hwp = None
            if args and hasattr(args[0], 'HAction'):
                hwp = args[0]
            elif 'hwp' in kwargs:
                hwp = kwargs['hwp']

            # 동기화 대기
            if hwp:
                time.sleep(delay)  # 기본 지연
                wait_for_hwp_ready(hwp, timeout=2.0)  # 추가 확인
            else:
                time.sleep(delay)

            return result
        return wrapper
    return decorator


def batch_operation_sync(hwp, operation_count: int) -> None:
    """
    여러 작업을 수행한 후 전체 동기화

    Args:
        hwp: HWP COM 객체
        operation_count: 수행한 작업 수
    """
    # 작업 수에 비례한 대기 시간 (최대 2초)
    wait_time = min(0.1 * operation_count, 2.0)
    time.sleep(wait_time)

    # HWP 준비 상태 확인
    wait_for_hwp_ready(hwp, timeout=5.0)


def verify_content_inserted(hwp, expected_min_pages: int = 1) -> bool:
    """
    내용이 실제로 삽입되었는지 검증

    Args:
        hwp: HWP COM 객체
        expected_min_pages: 최소 예상 페이지 수

    Returns:
        삽입 검증 성공 여부
    """
    try:
        # 페이지 수 확인
        page_count = hwp.PageCount
        if page_count < expected_min_pages:
            return False

        # 텍스트 내용 확인 (선택적)
        hwp.Run("MoveDocBegin")
        hwp.Run("Select")
        hwp.Run("MoveDocEnd")
        text = hwp.GetText()

        # 텍스트가 어느 정도 있으면 성공
        return len(str(text)) > 10

    except Exception:
        return False
