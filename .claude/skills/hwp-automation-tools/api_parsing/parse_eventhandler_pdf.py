"""
EventHandler PDF 파싱 (블록 저장 관련 정보 찾기)
"""
import sys
import codecs
from pathlib import Path

# UTF-8 출력 설정
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

try:
    import pdfplumber
except ImportError:
    print("pdfplumber 설치 필요: pip install pdfplumber")
    sys.exit(1)


def parse_pdf(pdf_path: str, output_path: str):
    """PDF 텍스트 추출"""
    print(f"PDF 파싱 중: {Path(pdf_path).name}")

    with pdfplumber.open(pdf_path) as pdf:
        all_text = []

        for i, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if text:
                all_text.append(f"\n{'='*80}\n")
                all_text.append(f"페이지 {i}\n")
                all_text.append(f"{'='*80}\n\n")
                all_text.append(text)

        # 파일로 저장
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(''.join(all_text))

        print(f"✓ 완료: {len(pdf.pages)}페이지 추출")
        print(f"✓ 저장: {output_path}")


if __name__ == "__main__":
    pdf_file = "HwpBooks/한글오토메이션EventHandler추가_2504.pdf"
    output_file = "HwpIdris/EventHandler_extracted.txt"

    parse_pdf(pdf_file, output_file)
