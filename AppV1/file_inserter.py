"""
InsertFile 기반 파일 삽입 모듈

전처리 + InsertFile 순차 방식
"""
import time
from pathlib import Path
from typing import List, Tuple
from tempfile import mkdtemp
import shutil

from src.automation.client import AutomationClient
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
        time.sleep(0.1)

        # 정리
        client.close_document()
        client.cleanup()

        return (True, temp_file, f"Para:{len(paras)} 빈:{removed}")

    except Exception as e:
        return (False, None, str(e)[:50])


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

                # InsertFile
                target_hwp.HAction.GetDefault("InsertFile", target_hwp.HParameterSet.HInsertFile.HSet)
                insert_params = target_hwp.HParameterSet.HInsertFile
                insert_params.HSet.SetItem("FileName", str(temp_file.absolute()))
                insert_params.HSet.SetItem("FileFormat", "HWP")
                insert_params.HSet.SetItem("KeepSection", 0)

                if target_hwp.HAction.Execute("InsertFile", insert_params.HSet):
                    inserted += 1
                    print(f' ✅')
                else:
                    print(f' ❌')

                # BreakColumn (마지막 제외)
                if i < len(processed_files):
                    target_hwp.Run("BreakColumn")
                    time.sleep(0.15)  # 칼럼 구분 완료 대기

            except Exception as e:
                print(f' ❌ {str(e)[:30]}')

        insert_time = time.time() - start_time
        print('-' * 70)
        print(f'✅ InsertFile 완료: {inserted}개 삽입 ({insert_time:.1f}초)')

        # 저장
        print(f'\n[3단계] 저장 중...')
        output_path.parent.mkdir(parents=True, exist_ok=True)
        target_hwp.SaveAs(str(output_path.absolute()))
        time.sleep(0.5)

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
