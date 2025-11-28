"""
Seperate to Image Workflow

Idris2 명세: Specs/Seperate2Img/Workflow.idr
"""

# -*- coding: utf-8 -*-

import shutil
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable

from automations.separator.separator import separate_problems
from automations.separator.types import SeparatorConfig, OutputFormat
from automations.merger.parallel_preprocessor import ParallelPreprocessor, PreprocessConfig
from core.hwp_to_pdf import convert_hwp_to_pdf_parallel
from core.hwpx_converter import ensure_hwp_format
from .pdf_to_image import convert_pdfs_to_images


class Seperate2ImgWorkflow:
    """Seperate2Img 워크플로우 로직"""

    def __init__(self, progress_callback: Optional[Callable[[str], None]] = None):
        self.progress_callback = progress_callback

    def update_progress(self, message: str):
        """진행 상황 업데이트"""
        if self.progress_callback:
            self.progress_callback(message)

    def run(self, input_path: str, output_dir: str, dpi: int = 300, format: str = "png", trim_whitespace: bool = False, cleanup_temp: bool = False) -> Dict[str, Any]:
        """전체 워크플로우 실행

        Idris2 명세: runWorkflowWithSeparateFirst (Specs/Seperate2Img/SeparateAndPreprocess.idr)
        워크플로우: ensureHwpFormat -> separateProblems -> preprocessSeparatedFiles (병렬) -> convertToPdf -> convertToImage
        """

        # 임시 폴더 (전처리, HWP 분리, PDF 변환용)
        temp_dir = Path(output_dir) / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)

        final_dir = Path(output_dir)
        final_dir.mkdir(parents=True, exist_ok=True)

        # 0. HWPX → HWP 변환 (필요시)
        self.update_progress("0/4단계: HWPX 형식 확인 중...")
        hwp_path = ensure_hwp_format(input_path, str(temp_dir))

        if hwp_path is None:
            return {
                "success": False,
                "message": "HWPX 변환 실패 또는 지원하지 않는 파일 형식",
                "success_count": 0,
                "fail_count": 0
            }

        # 1. 분리 (전처리 없이 원본 바로 분리)
        self.update_progress("1/4단계: 문제 분리 중...")
        hwp_files = self._separate_problems(hwp_path, str(temp_dir))

        if not hwp_files:
            return {"success": False, "message": "분리된 파일이 없습니다.", "success_count": 0, "fail_count": 0}

        # 1b. 분리된 파일들에 병렬 전처리 적용
        self.update_progress(f"1b/4단계: 분리된 파일 전처리 중 ({len(hwp_files)}개)...")
        preprocessed_files = self._preprocess_separated_files(hwp_files, str(temp_dir))

        if not preprocessed_files:
            return {
                "success": False,
                "message": f"전처리 실패 (분리: {len(hwp_files)}개, 전처리 성공: 0개)",
                "success_count": 0,
                "fail_count": len(hwp_files)
            }

        # 2. PDF 변환
        self.update_progress(f"2/4단계: PDF 변환 중 ({len(preprocessed_files)}개 파일)...")
        pdf_files = self._convert_to_pdf(preprocessed_files)

        if not pdf_files:
            return {"success": False, "message": "PDF 변환 실패", "success_count": 0, "fail_count": len(hwp_files)}

        # 3. 이미지 변환
        self.update_progress(f"3/4단계: 이미지 변환 중 ({len(pdf_files)}개 파일)...")
        img_results = self._convert_to_image(pdf_files, final_dir, dpi, format, trim_whitespace)
        image_files = [path for success, path, _ in img_results if success and path]

        # 4. 정리 (CleaningUp)
        if cleanup_temp:
            self._cleanup_temp(temp_dir)

        # 결과 반환
        success_count = len(image_files)
        fail_count = max(0, len(hwp_files) - success_count)

        return {
            "success": True,
            "success_count": success_count,
            "fail_count": fail_count,
            "image_files": image_files
        }

    def _preprocess_separated_files(self, hwp_files: List[str], temp_dir: str) -> List[str]:
        """분리된 파일들에 병렬 전처리 적용

        Idris2 명세: preprocessSeparatedFiles (Specs/Seperate2Img/SeparateAndPreprocess.idr)

        각 파일에 대해:
          1. 파일 열기
          2. 1단으로 변환
          3. Para 스캔
          4. 빈 Para 제거 (math-collector 검증된 방식)
          5. 저장
        """
        # 전처리 출력 디렉토리
        preprocess_dir = Path(temp_dir) / "preprocessed"
        preprocess_dir.mkdir(parents=True, exist_ok=True)

        # 병렬 전처리 설정
        config = PreprocessConfig(
            max_workers=min(20, len(hwp_files)),  # 파일 수에 맞게 조정
            output_dir=str(preprocess_dir),
            keep_original=False,  # 원본 불필요
            timeout=30.0
        )

        preprocessor = ParallelPreprocessor(config)

        print(f"\n[병렬 전처리] {len(hwp_files)}개 파일 처리 시작 (워커: {config.max_workers}개)")

        # 병렬 전처리 실행
        success_results, failed_results = preprocessor.preprocess_parallel(hwp_files)

        # 성공한 파일들의 경로만 반환
        preprocessed_paths = [r.preprocessed_path for r in success_results if r.preprocessed_path]

        # 정렬 (파일명 기준)
        preprocessed_paths.sort()

        print(f"[병렬 전처리 완료] 성공: {len(preprocessed_paths)}개, 실패: {len(failed_results)}개\n")

        return preprocessed_paths

    def _separate_problems(self, input_path: str, output_dir: str) -> List[str]:
        """1단계: HWP 파일 분리"""
        sep_config = SeparatorConfig.for_hwpx(input_path, output_dir)
        sep_config.output_format = OutputFormat.HWP
        sep_config.verbose = True

        sep_result = separate_problems(sep_config)
        return sep_result.output_files

    def _convert_to_pdf(self, hwp_files: List[str]) -> List[str]:
        """2단계: HWP → PDF 변환"""
        pdf_results = convert_hwp_to_pdf_parallel(
            hwp_files=hwp_files,
            max_workers=5,
            verbose=True
        )
        return [path for success, path, _ in pdf_results if success and path]

    def _convert_to_image(self, pdf_files: List[str], output_dir: Path, dpi: int, format: str, trim_whitespace: bool) -> List:
        """3단계: PDF → Image 변환"""
        return convert_pdfs_to_images(
            pdf_files=pdf_files,
            output_dir=str(output_dir),
            dpi=dpi,
            format=format,
            trim_whitespace=trim_whitespace,
            verbose=True
        )

    def _cleanup_temp(self, temp_dir: Path):
        """임시 파일 정리"""
        self.update_progress("임시 파일 정리 중...")
        
        # 강제 가비지 컬렉션
        import gc
        gc.collect()
        
        time.sleep(2.0)

        for attempt in range(3):
            try:
                shutil.rmtree(temp_dir)
                print(f"✅ 임시 파일 정리 완료: {temp_dir}")
                return
            except PermissionError as e:
                if attempt < 2:
                    print(f"⚠️  재시도 {attempt + 1}/3: 파일이 사용 중...")
                    time.sleep(1.0)
                else:
                    print(f"⚠️  임시 파일 정리 실패: {e}")
                    print(f"   수동 삭제 필요: {temp_dir}")
            except Exception as e:
                print(f"❌ 임시 파일 정리 실패: {e}")
                return
