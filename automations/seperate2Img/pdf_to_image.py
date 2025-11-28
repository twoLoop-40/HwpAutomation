"""
PDF to Image 변환 - pypdfium2 사용

Idris2 명세: Specs/Seperate2Img/Workflow.idr - convertToImage

주요 기능:
- PDF → PNG/JPG 변환
- DPI 설정 (기본 300)
- 다중 페이지 지원 (모든 페이지 변환)
"""

import pypdfium2 as pdfium
from pathlib import Path
from typing import List, Tuple, Optional
from PIL import Image, ImageChops


def trim_image_whitespace(im: Image.Image, padding: int = 10) -> Image.Image:
    """
    이미지 여백 제거 (Auto-Crop)

    Idris2 명세: Workflow.idr - convertToImage 참조

    Args:
        im: PIL 이미지 객체
        padding: 여백에 추가할 패딩 (픽셀)

    Returns:
        여백이 제거된 이미지
    """
    # 배경색 생성 (좌상단 픽셀 색상 기준)
    bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))

    # 배경과의 차이 계산
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)

    # 콘텐츠 영역의 바운딩 박스 계산
    bbox = diff.getbbox()

    if bbox:
        # 패딩 추가
        left, upper, right, lower = bbox
        left = max(0, left - padding)
        upper = max(0, upper - padding)
        right = min(im.size[0], right + padding)
        lower = min(im.size[1], lower + padding)

        return im.crop((left, upper, right, lower))

    return im


def convert_pdf_to_image(
    pdf_path: str,
    output_path_base: str,
    dpi: int = 300,
    format: str = "png",
    trim_whitespace: bool = False,
    verbose: bool = False
) -> Tuple[bool, List[str], Optional[str]]:
    """
    단일 PDF 파일을 이미지(들)로 변환 (모든 페이지)

    Idris2 명세:
    convertSinglePdf : String -> Config -> IO (Bool, List String, Maybe String)

    Args:
        pdf_path: PDF 파일 경로
        output_path_base: 출력 이미지 기본 경로 (확장자 포함/미포함 무관, stem 사용)
        dpi: 해상도 (기본 300)
        format: 이미지 포맷 (png, jpg)
        trim_whitespace: 이미지 여백 제거 여부 (기본 False)
        verbose: 상세 로그 출력

    Returns:
        (success, generated_files_list, error_message)
    """
    generated_files = []
    
    try:
        pdf_path_obj = Path(pdf_path)
        if not pdf_path_obj.exists():
            return False, [], f"파일 없음: {pdf_path}"

        output_base_obj = Path(output_path_base)
        output_dir = output_base_obj.parent
        output_stem = output_base_obj.stem # 확장자 제외한 이름

        if verbose:
            print(f"[PDF→IMG] {pdf_path_obj.name} 처리 중...")

        # pypdfium2로 PDF 열기
        pdf = None
        try:
            pdf = pdfium.PdfDocument(pdf_path)
        except Exception as e:
            return False, [], f"PDF 파일 열기 실패: {str(e)}"

        try:
            n_pages = len(pdf)
            if n_pages == 0:
                return False, [], f"빈 PDF 파일: {pdf_path}"

            # 모든 페이지 순회
            for i, page in enumerate(pdf):
                try:
                    # 파일명 결정
                    # 1페이지짜리: 원본이름.png
                    # 다중 페이지: 원본이름_1.png, 원본이름_2.png ...
                    if n_pages > 1:
                        current_output_filename = f"{output_stem}_{i+1}.{format.lower()}"
                    else:
                        current_output_filename = f"{output_stem}.{format.lower()}"
                    
                    current_output_path = output_dir / current_output_filename

                    # DPI 계산: scale = dpi / 72
                    scale = dpi / 72.0

                    # 비트맵 렌더링
                    bitmap = page.render(scale=scale)

                    # PIL Image로 변환
                    pil_image = bitmap.to_pil()

                    # 여백 제거 (옵션)
                    if trim_whitespace:
                        pil_image = trim_image_whitespace(pil_image, padding=10)

                    # 이미지 저장
                    if format.lower() == "jpg":
                        if pil_image.mode == "RGBA":
                            pil_image = pil_image.convert("RGB")
                        pil_image.save(current_output_path, "JPEG", quality=95)
                    else:
                        pil_image.save(current_output_path, "PNG")
                    
                    # 파일 생성 확인
                    if not current_output_path.exists():
                        # 실패 시 지금까지 생성된 파일 반환할지, 전체 실패 처리할지 결정
                        # 여기서는 계속 진행하지 않고 중단
                        return False, generated_files, f"이미지 파일 생성 실패: {current_output_path}"
                    
                    # 0바이트 체크
                    if current_output_path.stat().st_size == 0:
                         return False, generated_files, f"이미지 변환 실패 (0 바이트): {current_output_path}"

                    generated_files.append(str(current_output_path))
                    
                    if verbose:
                        img_size = current_output_path.stat().st_size / 1024
                        print(f"  - 생성: {current_output_path.name} ({img_size:.1f} KB)")

                except Exception as e:
                    return False, generated_files, f"페이지 {i+1} 변환 실패: {str(e)}"

            return True, generated_files, None

        finally:
            # 리소스 해제 (필수)
            if pdf:
                pdf.close()

    except Exception as e:
        return False, generated_files, f"변환 중 에러: {str(e)}"


def convert_pdfs_to_images(
    pdf_files: List[str],
    output_dir: str,
    dpi: int = 300,
    format: str = "png",
    trim_whitespace: bool = False,
    verbose: bool = False
) -> List[Tuple[bool, Optional[str], Optional[str]]]:
    """
    여러 PDF 파일을 이미지로 변환 (다중 페이지 지원)

    Args:
        trim_whitespace: 이미지 여백 제거 여부 (기본 False)

    Returns:
        List of (success, output_path_representative, error_message)
        * output_path_representative: 생성된 첫 번째 이미지 경로 (성공 시)
    """
    if not pdf_files:
        return []

    output_dir_obj = Path(output_dir)
    output_dir_obj.mkdir(parents=True, exist_ok=True)

    if verbose:
        print(f"[PDF→IMG 변환 시작] {len(pdf_files)}개 파일, {dpi} DPI")

    results = []

    for pdf_file in pdf_files:
        pdf_path = Path(pdf_file)
        
        # 기본 출력 경로 (단일 페이지일 경우 사용될 경로)
        output_filename = pdf_path.stem + f".{format.lower()}"
        output_path_base = output_dir_obj / output_filename

        success, generated_files, error = convert_pdf_to_image(
            str(pdf_path),
            str(output_path_base),
            dpi=dpi,
            format=format,
            trim_whitespace=trim_whitespace,
            verbose=verbose
        )

        if success:
            # 성공 시 대표 파일(첫 번째) 반환, 또는 생성된 모든 파일을 반환하고 싶다면 구조 변경 필요
            # 여기서는 기존 인터페이스 호환성을 위해 첫 번째 파일만 대표로 반환하되,
            # 실제로는 generated_files에 모든 파일이 있음.
            # plugin.py에서 이를 활용하려면 results 구조를 바꾸는 게 좋음.
            
            # 하지만 plugin.py는 image_files 리스트만 필요로 함.
            # 따라서 여기서는 (True, "첫번째파일", None) 을 반환하고,
            # plugin.py 에서는 이 리스트를 받아 처리... 가 아니라
            # plugin.py 가 사용하는 convert_to_image는 "image_files = [path for ...]" 를 함.
            # 즉, 1:N 관계가 되면 plugin.py도 수정 필요함.
            
            # 수정 최소화를 위해:
            # convert_pdfs_to_images가 (True, path, None) 튜플을 
            # 생성된 파일 개수만큼 flat하게 반환하도록 변경.
            for gen_file in generated_files:
                results.append((True, gen_file, None))
        else:
            results.append((False, None, error))

    # 통계
    success_count = sum(1 for s, _, _ in results if s)
    fail_count = len(pdf_files) - (len(generated_files) if 'generated_files' in locals() else 0) # 정확한 실패 카운트는 어려움 (1 PDF -> N Img)
    # 단순히 결과 리스트의 성공 수로 카운트

    if verbose:
        print(f"\n[PDF→IMG 완료] 생성된 이미지: {success_count}개")

    return results
