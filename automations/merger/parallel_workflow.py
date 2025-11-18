"""
LangGraph Send를 활용한 병렬 전처리 + InsertFile 합병 워크플로우

Idris2 명세: HwpIdris/AppV1/ParallelMerge.idr
최대 병렬 워커: 20개
"""
from typing import List, Tuple, Annotated, Literal
from pathlib import Path
import time
from tempfile import mkdtemp
import shutil
import operator

from langgraph.graph import StateGraph, END, START, Send
from typing_extensions import TypedDict

from src.automation.client import AutomationClient
from .types import ProblemFile
from .column import convert_to_single_column
from .para_scanner import scan_paras, remove_empty_paras


# ============================================================
# 상태 정의 (Idris2 명세 기반)
# ============================================================

class ProcessedFile(TypedDict):
    """전처리된 파일 정보 (Idris2: ProcessedFile)"""
    original: ProblemFile
    processed_path: str
    para_count: int
    empty_paras_removed: int


class WorkflowState(TypedDict):
    """워크플로우 전체 상태"""
    # 입력
    problem_files: List[ProblemFile]
    template_path: str
    output_path: str
    temp_dir: str

    # 병렬 전처리 결과
    processed_files: Annotated[List[ProcessedFile], operator.add]
    failed_files: Annotated[List[Tuple[ProblemFile, str]], operator.add]

    # 합병 결과
    page_count: int
    inserted_count: int

    # 상태
    status: Literal["initial", "preprocessing", "collecting", "merging", "completed", "failed"]
    error_message: str


class PreprocessTask(TypedDict):
    """개별 전처리 작업 (Send용)"""
    problem: ProblemFile
    temp_dir: str


# ============================================================
# 노드: 전처리 워커 (병렬 실행)
# ============================================================

def preprocess_worker(task: PreprocessTask) -> dict:
    """
    단일 파일 전처리 워커 (병렬 실행)

    Idris2 스펙: preprocessSingleFile
    """
    problem = task["problem"]
    temp_dir = task["temp_dir"]

    try:
        # 독립 HWP 클라이언트 생성
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
            return {
                "processed_files": [],
                "failed_files": [(problem, "Failed to open file")]
            }

        # 2. 1단 변환
        convert_to_single_column(hwp)

        # 3. Para 스캔 및 빈 Para 제거
        paras = scan_paras(hwp)
        removed = remove_empty_paras(hwp, paras)

        # 4. 임시 파일 저장
        processed_path = Path(temp_dir) / f"processed_{problem.index:03d}.hwp"
        hwp.SaveAs(str(processed_path.absolute()))
        time.sleep(0.1)

        # 5. HWP 클라이언트 정리
        client.close_document()
        client.cleanup()

        # 성공
        processed = ProcessedFile(
            original=problem,
            processed_path=str(processed_path),
            para_count=len(paras),
            empty_paras_removed=removed
        )

        return {
            "processed_files": [processed],
            "failed_files": []
        }

    except Exception as e:
        return {
            "processed_files": [],
            "failed_files": [(problem, str(e)[:100])]
        }


# ============================================================
# 노드: 배치 생성 및 전처리 Send
# ============================================================

def create_preprocess_tasks(state: WorkflowState):
    """
    배치 생성 및 전처리 작업 Send

    Idris2 스펙: BatchNode → PreprocessWorkerNode (Send)
    최대 20개씩 병렬 실행
    """
    problem_files = state["problem_files"]
    temp_dir = state["temp_dir"]

    # Send: 각 파일을 전처리 워커로 전송
    # LangGraph가 자동으로 최대 20개 병렬 실행 관리
    return [
        Send("preprocess_worker", PreprocessTask(problem=problem, temp_dir=temp_dir))
        for problem in problem_files
    ]


# ============================================================
# 노드: 순차 합병 (InsertFile)
# ============================================================

def merge_with_insertfile(state: WorkflowState) -> dict:
    """
    InsertFile로 전처리된 파일들 순차 합병

    Idris2 스펙: mergeProcessedFiles
    BreakColumn 대기: 0.15초
    """
    template_path = Path(state["template_path"])
    output_path = Path(state["output_path"])
    processed_files = state["processed_files"]

    if not processed_files:
        return {
            "status": "failed",
            "error_message": "No files to merge"
        }

    try:
        # HWP 클라이언트 생성
        target_client = AutomationClient()
        target_hwp = target_client.hwp
        target_hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")

        # 1. 양식 열기
        result = target_client.open_document(str(template_path))
        if not result.success:
            return {
                "status": "failed",
                "error_message": f"Failed to open template: {result.error}"
            }

        # 2. 본문 시작으로
        target_hwp.Run("MoveDocBegin")
        target_hwp.Run("MoveParaBegin")
        time.sleep(0.05)

        # 3. InsertFile로 순차 삽입
        inserted = 0
        for i, proc_file in enumerate(processed_files, 1):
            try:
                # InsertFile
                target_hwp.HAction.GetDefault("InsertFile", target_hwp.HParameterSet.HInsertFile.HSet)
                insert_params = target_hwp.HParameterSet.HInsertFile
                insert_params.HSet.SetItem("FileName", proc_file["processed_path"])
                insert_params.HSet.SetItem("FileFormat", "HWP")
                insert_params.HSet.SetItem("KeepSection", 0)

                if target_hwp.HAction.Execute("InsertFile", insert_params.HSet):
                    inserted += 1

                # BreakColumn (마지막 제외)
                if i < len(processed_files):
                    target_hwp.Run("BreakColumn")
                    time.sleep(0.15)  # Idris2 스펙: breakColumnDelay

            except Exception as e:
                print(f"⚠️  파일 삽입 실패 [{i}]: {str(e)[:50]}")

        # 4. 저장
        output_path.parent.mkdir(parents=True, exist_ok=True)
        target_hwp.SaveAs(str(output_path.absolute()))
        time.sleep(0.5)

        page_count = target_hwp.PageCount

        # 5. HWP 정리
        target_client.close_document()
        target_client.cleanup()

        return {
            "page_count": page_count,
            "inserted_count": inserted,
            "status": "completed"
        }

    except Exception as e:
        return {
            "status": "failed",
            "error_message": str(e)
        }


# ============================================================
# 워크플로우 그래프 생성
# ============================================================

def create_parallel_merge_workflow() -> StateGraph:
    """
    LangGraph Send 기반 병렬 합병 워크플로우 생성

    노드 흐름:
    START → create_preprocess_tasks → [preprocess_worker × N] → merge_with_insertfile → END
    """
    workflow = StateGraph(WorkflowState)

    # 노드 등록
    workflow.add_node("create_preprocess_tasks", create_preprocess_tasks)
    workflow.add_node("preprocess_worker", preprocess_worker)
    workflow.add_node("merge_with_insertfile", merge_with_insertfile)

    # 엣지 정의
    workflow.add_edge(START, "create_preprocess_tasks")
    workflow.add_edge("preprocess_worker", "merge_with_insertfile")
    workflow.add_edge("merge_with_insertfile", END)

    return workflow.compile()


# ============================================================
# 메인 실행 함수
# ============================================================

def run_parallel_merge(
    template_path: Path,
    problem_files: List[ProblemFile],
    output_path: Path
) -> Tuple[bool, int, int]:
    """
    LangGraph 병렬 워크플로우 실행

    Returns: (success, page_count, inserted_count)
    """
    print('=' * 70)
    print('LangGraph Send 병렬 전처리 + InsertFile 합병')
    print('=' * 70)
    print(f'양식: {template_path.name}')
    print(f'문항 수: {len(problem_files)}개')
    print(f'최대 병렬 워커: 20개')

    # 임시 디렉토리 생성
    temp_dir = mkdtemp(prefix="hwp_parallel_")
    print(f'임시 디렉토리: {temp_dir}')

    try:
        # 초기 상태
        initial_state = WorkflowState(
            problem_files=problem_files,
            template_path=str(template_path),
            output_path=str(output_path),
            temp_dir=temp_dir,
            processed_files=[],
            failed_files=[],
            page_count=0,
            inserted_count=0,
            status="initial",
            error_message=""
        )

        # 워크플로우 실행
        print(f'\n워크플로우 시작...\n')
        start_time = time.time()

        workflow = create_parallel_merge_workflow()
        final_state = workflow.invoke(initial_state)

        total_time = time.time() - start_time

        # 결과 출력
        print('\n' + '=' * 70)
        print('결과 요약')
        print('=' * 70)
        print(f'전처리 성공: {len(final_state["processed_files"])}개')
        print(f'전처리 실패: {len(final_state["failed_files"])}개')
        print(f'InsertFile 삽입: {final_state["inserted_count"]}개')
        print(f'최종 페이지: {final_state["page_count"]}')
        print(f'총 소요 시간: {total_time:.1f}초')
        print(f'문항당 평균: {total_time/len(problem_files):.2f}초')

        if final_state["status"] == "completed":
            file_size = output_path.stat().st_size
            print(f'\n파일: {output_path}')
            print(f'크기: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)')
            print('=' * 70)
            return (True, final_state["page_count"], final_state["inserted_count"])
        else:
            print(f'\n❌ 실패: {final_state["error_message"]}')
            print('=' * 70)
            return (False, 0, 0)

    finally:
        # 임시 디렉토리 정리
        try:
            shutil.rmtree(temp_dir)
            print(f'임시 디렉토리 삭제: {temp_dir}')
        except:
            pass
