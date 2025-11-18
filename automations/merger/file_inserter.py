"""
InsertFile 기반 파일 삽입 모듈

전처리 + InsertFile 순차 방식
"""
import time
from pathlib import Path
from typing import List, Tuple
from tempfile import mkdtemp
import shutil

from core.automation_client import AutomationClient
from core.sync import wait_for_hwp_ready
from .types import ProblemFile
from .column import convert_to_single_column
from .para_scanner import scan_paras, remove_empty_paras


def preprocess_and_save(problem: ProblemFile, temp_dir: Path) -> Tuple[bool, Path, str]:
    """
    단일 파일 전처리 후 임시 저장

    Returns: (success, temp_file_path, message)
    """
    try:
        # 독립 클라이언트
        client = AutomationClient()
        hwp = client.hwp
        hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")

        # 창 숨기기
        try:
            hwp.XHwpWindows.Item(0).Visible = False
        except:
            pass

        # 1. 파일 열기
        result = client.open_document(str(problem.path))
        if not result.success:
            client.cleanup()
            return (False, None, f"열기 실패")

        # 2. 1단 변환
        convert_to_single_column(hwp)

        # 3. Para 스캔 및 빈 Para 제거
        paras = scan_paras(hwp)
        removed = remove_empty_paras(hwp, paras)

        # 4. 임시 파일로 저장
        temp_file = temp_dir / f"processed_{problem.index:03d}.hwp"
        hwp.SaveAs(str(temp_file.absolute()))

        # 저장 완료 대기 (동기화)
        if not wait_for_hwp_ready(hwp, timeout=5.0):
            client.cleanup()
            return (False, None, "저장 시간 초과")

        # 정리
        client.close_document()
        client.cleanup()

        return (True, temp_file, f"Para:{len(paras)} 빈:{removed}")

    except Exception as e:
        return (False, None, str(e)[:50])


def insert_file_and_break_column(hwp, file_path: Path, is_last: bool, keep_section: int = 1) -> bool:
    """
    InsertFile + BreakColumn 결합 시퀀스 (원자적 작업)

    HwpIdris 명세 기반: ParameterSet InsertFile
    - KeepSection=1: 끼워 넣을 문서를 구역으로 나누어 쪽 모양을 유지

    Args:
        hwp: HWP COM 객체
        file_path: 삽입할 파일 경로
        is_last: 마지막 파일 여부 (BreakColumn 생략)
        keep_section: 구역 정보 유지 (0: 무시, 1: 유지)

    Returns:
        성공 여부
    """
    try:
        # 1. InsertFile 실행
        hwp.HAction.GetDefault("InsertFile", hwp.HParameterSet.HInsertFile.HSet)
        insert_params = hwp.HParameterSet.HInsertFile
        insert_params.HSet.SetItem("FileName", str(file_path.absolute()))
        insert_params.HSet.SetItem("FileFormat", "HWP")
        insert_params.HSet.SetItem("KeepSection", keep_section)  # HwpIdris ParameterSet 명세

        if not hwp.HAction.Execute("InsertFile", insert_params.HSet):
            return False

        # 2. InsertFile 완료 대기
        if not wait_for_hwp_ready(hwp, timeout=5.0):
            return False

        # 3. 문서 끝으로 이동 (InsertFile은 커서를 움직이지 않음)
        hwp.Run("MoveDocEnd")
        if not wait_for_hwp_ready(hwp, timeout=2.0):
            return False

        # 4. BreakColumn (마지막 파일 제외)
        if not is_last:
            hwp.Run("BreakColumn")
            # BreakColumn은 더 긴 대기 시간 필요
            if not wait_for_hwp_ready(hwp, timeout=3.0):
                return False

        return True

    except Exception as e:
        print(f' ❌ 오류: {str(e)[:30]}')
        return False


def merge_with_insertfile(
    template_path: Path,
    problem_files: List[ProblemFile],
    output_path: Path
) -> Tuple[bool, int, int]:
    """
    InsertFile 기반 파일 합병

    Returns: (success, page_count, processed_count)
    """
    print('=' * 70)
    print('InsertFile 방식 문항 합병')
    print('=' * 70)
    print(f'양식: {template_path.name}')
    print(f'문항 수: {len(problem_files)}개')

    # 임시 디렉토리 생성
    temp_dir = Path(mkdtemp(prefix="hwp_processed_"))
    print(f'임시 디렉토리: {temp_dir}')

    try:
        # 1단계: 순차 전처리
        print(f'\n[1단계] 파일 전처리 중...')
        print('-' * 70)

        processed_files = []
        failed = []
        start_time = time.time()

        for problem in problem_files:
            progress = (problem.index / len(problem_files)) * 100
            print(f'  [{problem.index:2d}/{len(problem_files)}] ({progress:5.1f}%) {problem.name[:40]}', end='')

            success, temp_file, msg = preprocess_and_save(problem, temp_dir)

            if success:
                processed_files.append((problem, temp_file))
                print(f' ✅ {msg}')
            else:
                failed.append((problem, msg))
                print(f' ❌ {msg}')

        preprocess_time = time.time() - start_time
        print('-' * 70)
        print(f'✅ 전처리 완료: {len(processed_files)}개 성공, {len(failed)}개 실패 ({preprocess_time:.1f}초)')

        if not processed_files:
            print('❌ 전처리된 파일이 없습니다')
            return (False, 0, 0)

        # 2단계: InsertFile로 합병
        print(f'\n[2단계] InsertFile로 합병 중...')
        print('-' * 70)

        target_client = AutomationClient()
        target_hwp = target_client.hwp
        target_hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")

        # 양식 열기
        result = target_client.open_document(str(template_path))
        if not result.success:
            print(f'❌ 양식 열기 실패: {result.error}')
            return (False, 0, 0)

        print(f'양식 열림: 초기 {target_hwp.PageCount}페이지')

        # 본문 시작으로
        target_hwp.Run("MoveDocBegin")
        target_hwp.Run("MoveParaBegin")
        time.sleep(0.05)

        start_time = time.time()
        inserted = 0

        for i, (problem, temp_file) in enumerate(processed_files, 1):
            try:
                progress = (i / len(processed_files)) * 100
                print(f'  [{i:2d}/{len(processed_files)}] ({progress:5.1f}%) {problem.name[:40]}', end='')

                # InsertFile + BreakColumn 결합 시퀀스 (원자적 작업)
                is_last = (i == len(processed_files))
                if insert_file_and_break_column(target_hwp, temp_file, is_last):
                    inserted += 1
                    print(f' ✅')
                else:
                    print(f' ❌')

            except Exception as e:
                print(f' ❌ {str(e)[:30]}')

        insert_time = time.time() - start_time
        print('-' * 70)
        print(f'✅ InsertFile 완료: {inserted}개 삽입 ({insert_time:.1f}초)')

        # 저장
        print(f'\n[3단계] 저장 중...')
        output_path.parent.mkdir(parents=True, exist_ok=True)
        target_hwp.SaveAs(str(output_path.absolute()))

        # 저장 완료 대기
        if not wait_for_hwp_ready(target_hwp, timeout=10.0):
            print('❌ 저장 시간 초과')
            target_client.cleanup()
            return (False, 0, 0)

        page_count = target_hwp.PageCount
        file_size = output_path.stat().st_size

        print(f'✅ 저장 완료')
        print(f'   파일: {output_path}')
        print(f'   크기: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)')
        print(f'   페이지: {page_count}')

        # 정리
        target_client.close_document()
        target_client.cleanup()

        # 결과 요약
        total_time = preprocess_time + insert_time
        print('\n' + '=' * 70)
        print('결과 요약')
        print('=' * 70)
        print(f'전처리: {len(processed_files)}개 ({preprocess_time:.1f}초)')
        print(f'삽입: {inserted}개 ({insert_time:.1f}초)')
        print(f'총 소요 시간: {total_time:.1f}초')
        print(f'문항당 평균: {total_time/len(problem_files):.2f}초')
        print('=' * 70)

        return (True, page_count, inserted)

    finally:
        # 임시 디렉토리 정리
        try:
            shutil.rmtree(temp_dir)
            print(f'임시 디렉토리 삭제: {temp_dir}')
        except:
            pass
